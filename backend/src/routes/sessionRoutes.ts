import { Router } from 'express';
import {
  createSession,
  getSession,
  updateSession,
  deleteSession,
  getAllSessions,
  cleanupOldSessions,
  getSessionStats
} from '../controllers/sessionsController';

const router = Router();

// Session CRUD operations
router.post('/', createSession);           // POST /api/sessions
router.get('/stats', getSessionStats);     // GET /api/sessions/stats (before /:sessionId)
router.get('/', getAllSessions);          // GET /api/sessions
router.get('/:sessionId', getSession);    // GET /api/sessions/:sessionId
router.put('/:sessionId', updateSession); // PUT /api/sessions/:sessionId
router.delete('/:sessionId', deleteSession); // DELETE /api/sessions/:sessionId

// Session management operations
router.delete('/cleanup', cleanupOldSessions); // DELETE /api/sessions/cleanup

export default router;
