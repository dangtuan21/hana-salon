import { Router, Request, Response } from 'express';
import healthRoutes from './healthRoutes';
import servicesRoutes from './servicesRoutes';
import customersRoutes from './customersRoutes';
import techniciansRoutes from './techniciansRoutes';
import bookingsRoutes from './bookingsRoutes';
import conversationRoutes from './bookingConversationRoutes';

const router = Router();

// Mount route modules
router.use('/', healthRoutes);
router.use('/services', servicesRoutes);
router.use('/customers', customersRoutes);
router.use('/technicians', techniciansRoutes);
router.use('/bookings', bookingsRoutes);
router.use('/bookingConversations', conversationRoutes);

// API info endpoint
router.get('/', (req: Request, res: Response) => {
  res.json({
    success: true,
    message: 'Hana AI Backend API',
    data: {
      version: '1.0.0',
      status: 'running',
      timestamp: new Date().toISOString(),
      endpoints: {
        health: '/api/health',
        services: '/api/services',
        customers: '/api/customers',
        technicians: '/api/technicians',
        bookings: '/api/bookings',
        bookingConversations: '/api/bookingConversations',
        documentation: '/api-docs'
      }
    }
  });
});

export default router;
