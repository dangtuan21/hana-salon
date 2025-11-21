import { Request, Response } from 'express';
import asyncHandler from 'express-async-handler';
import BookingConversation, { IBookingConversation } from '../models/BookingConversation';
import { ResponseUtil } from '../utils/response';
import mongoose from 'mongoose';

export class BookingConversationController {
  
  /**
   * Create new conversation
   * POST /api/booking-conversations
   */
  createConversation = asyncHandler(async (req: Request, res: Response): Promise<void> => {
    const {
      sessionId,
      customerId,
      bookingId,
      messages,
      startTime,
      endTime,
      outcome,
      totalMessages,
      conversationDuration
    } = req.body;

    // Validate required fields
    if (!sessionId || !messages || !startTime || !outcome || totalMessages === undefined || conversationDuration === undefined) {
      ResponseUtil.validationError(res, 'Missing required fields: sessionId, messages, startTime, outcome, totalMessages, conversationDuration');
      return;
    }

    // Check if conversation already exists
    const existingConversation = await BookingConversation.findOne({ sessionId });
    if (existingConversation) {
      ResponseUtil.conflict(res, `Conversation with sessionId "${sessionId}" already exists`);
      return;
    }

    // Create new conversation
    const conversationData: Partial<IBookingConversation> = {
      sessionId,
      messages,
      startTime: new Date(startTime),
      outcome,
      totalMessages,
      conversationDuration
    };

    // Add optional fields if provided
    if (customerId) conversationData.customerId = new mongoose.Types.ObjectId(customerId);
    if (bookingId) conversationData.bookingId = new mongoose.Types.ObjectId(bookingId);
    if (endTime) conversationData.endTime = new Date(endTime);

    const conversation = new BookingConversation(conversationData);
    await conversation.save();

    ResponseUtil.success(res, conversation, 'Conversation created successfully', 201);
  });

  /**
   * Get conversation by sessionId
   * GET /api/booking-conversations/:sessionId
   */
  getConversation = asyncHandler(async (req: Request, res: Response): Promise<void> => {
    const { sessionId } = req.params;

    const conversation = await BookingConversation.findOne({ sessionId })
      .populate('customerId', 'firstName lastName email phone')
      .populate('bookingId', 'appointmentDate startTime endTime status totalPrice');

    if (!conversation) {
      ResponseUtil.notFound(res, `Conversation with sessionId "${sessionId}" not found`);
      return;
    }

    ResponseUtil.success(res, conversation, 'Conversation retrieved successfully');
  });


  /**
   * Get conversations for a specific customer
   * GET /api/booking-conversations/customer/:customerId
   */
  getCustomerConversations = asyncHandler(async (req: Request, res: Response): Promise<void> => {
    const { customerId } = req.params;
    const page = parseInt(req.query.page as string) || 1;
    const limit = parseInt(req.query.limit as string) || 10;
    const outcome = req.query.outcome as string;

    // Build query
    const query: any = { customerId: new mongoose.Types.ObjectId(customerId) };
    if (outcome) {
      query.outcome = outcome;
    }

    // Get total count for pagination
    const total = await BookingConversation.countDocuments(query);
    const pages = Math.ceil(total / limit);
    const skip = (page - 1) * limit;

    // Get conversations
    const conversations = await BookingConversation.find(query)
      .populate('bookingId', 'appointmentDate startTime endTime status totalPrice')
      .sort({ startTime: -1 })
      .skip(skip)
      .limit(limit);

    const responseData = {
      conversations,
      pagination: {
        page,
        limit,
        total,
        pages
      }
    };

    ResponseUtil.success(res, responseData, 'Customer conversations retrieved successfully');
  });
}
