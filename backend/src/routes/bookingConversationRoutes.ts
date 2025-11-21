import express from 'express';
import { BookingConversationController } from '../controllers/bookingConversationController';

const router = express.Router();
const controller = new BookingConversationController();

// Phase 1 Essential Endpoints

// Store new conversation
router.post('/', controller.createConversation);

// Retrieve conversation by session ID
router.get('/:sessionId', controller.getConversation);

// Get customer conversation history
router.get('/customer/:customerId', controller.getCustomerConversations);

export default router;
