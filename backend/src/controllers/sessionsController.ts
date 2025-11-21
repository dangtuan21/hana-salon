import { Request, Response } from 'express';
import asyncHandler from 'express-async-handler';
import { Session, ISession } from '../models/Session';
import { ResponseUtil } from '../utils/response';

/**
 * Create a new session
 * POST /api/sessions
 */
export const createSession = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  const sessionData = req.body;

  // Validate required fields
  if (!sessionData.session_id) {
    ResponseUtil.error(res, 'SESSION_ID_REQUIRED', 'Session ID is required', 400);
    return;
  }

  // Check if session already exists
  const existingSession = await Session.findOne({ session_id: sessionData.session_id });
  if (existingSession) {
    ResponseUtil.error(res, 'SESSION_EXISTS', 'Session with this ID already exists', 409);
    return;
  }

  // Create new session
  const session = new Session({
    session_id: sessionData.session_id,
    created_at: sessionData.created_at ? new Date(sessionData.created_at) : new Date(),
    last_activity: sessionData.last_activity ? new Date(sessionData.last_activity) : new Date(),
    messages: sessionData.messages || [],
    conversation_complete: sessionData.conversation_complete || false
  });

  const savedSession = await session.save();

  ResponseUtil.success(res, savedSession, 'Session created successfully', 201);
});

/**
 * Get session by ID
 * GET /api/sessions/:sessionId
 */
export const getSession = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  const { sessionId } = req.params;

  const session = await Session.findOne({ session_id: sessionId });

  if (!session) {
    ResponseUtil.error(res, 'SESSION_NOT_FOUND', 'Session not found', 404);
    return;
  }

  // Update last activity
  session.last_activity = new Date();
  await session.save();

  ResponseUtil.success(res, session, 'Session retrieved successfully');
});

/**
 * Update session by ID
 * PUT /api/sessions/:sessionId
 */
export const updateSession = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  const { sessionId } = req.params;
  const updateData = req.body;

  // Find and update session
  const session = await Session.findOne({ session_id: sessionId });

  if (!session) {
    ResponseUtil.error(res, 'SESSION_NOT_FOUND', 'Session not found', 404);
    return;
  }

  // Update fields
  if (updateData.messages !== undefined) {
    session.messages = updateData.messages;
  }
  if (updateData.conversation_complete !== undefined) {
    session.conversation_complete = updateData.conversation_complete;
  }
  
  // Always update last activity
  session.last_activity = new Date();

  const updatedSession = await session.save();

  ResponseUtil.success(res, updatedSession, 'Session updated successfully');
});

/**
 * Delete session by ID
 * DELETE /api/sessions/:sessionId
 */
export const deleteSession = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  const { sessionId } = req.params;

  const session = await Session.findOneAndDelete({ session_id: sessionId });

  if (!session) {
    ResponseUtil.error(res, 'SESSION_NOT_FOUND', 'Session not found', 404);
    return;
  }

  ResponseUtil.success(res, null, 'Session deleted successfully');
});

/**
 * Get all sessions (for debugging/admin)
 * GET /api/sessions
 */
export const getAllSessions = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  const page = parseInt(req.query.page as string) || 1;
  const limit = parseInt(req.query.limit as string) || 10;
  const skip = (page - 1) * limit;

  // Get sessions with pagination
  const sessions = await Session.find()
    .sort({ last_activity: -1 })
    .skip(skip)
    .limit(limit);

  const total = await Session.countDocuments();

  const response = {
    sessions,
    pagination: {
      page,
      limit,
      total,
      pages: Math.ceil(total / limit)
    }
  };

  ResponseUtil.success(res, response, 'Sessions retrieved successfully');
});

/**
 * Clean up old sessions
 * DELETE /api/sessions/cleanup
 */
export const cleanupOldSessions = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  const maxAgeHours = parseInt(req.query.maxAgeHours as string) || 24;
  const cutoffTime = new Date(Date.now() - maxAgeHours * 60 * 60 * 1000);

  const result = await Session.deleteMany({
    last_activity: { $lt: cutoffTime },
    conversation_complete: true
  });

  ResponseUtil.success(res, {
    deletedCount: result.deletedCount,
    cutoffTime,
    maxAgeHours
  }, `Cleaned up ${result.deletedCount} old sessions`);
});

/**
 * Get session statistics
 * GET /api/sessions/stats
 */
export const getSessionStats = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  const totalSessions = await Session.countDocuments();
  const activeSessions = await Session.countDocuments({ conversation_complete: false });
  const completedSessions = await Session.countDocuments({ conversation_complete: true });

  // Sessions created in last 24 hours
  const last24Hours = new Date(Date.now() - 24 * 60 * 60 * 1000);
  const recentSessions = await Session.countDocuments({ created_at: { $gte: last24Hours } });

  const stats = {
    totalSessions,
    activeSessions,
    completedSessions,
    recentSessions,
    completionRate: totalSessions > 0 ? (completedSessions / totalSessions) : 0
  };

  ResponseUtil.success(res, stats, 'Session statistics retrieved successfully');
});
