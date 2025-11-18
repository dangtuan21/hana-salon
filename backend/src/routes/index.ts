import { Router, Request, Response } from 'express';
import healthRoutes from './healthRoutes';

const router = Router();

// Mount route modules
router.use('/', healthRoutes);

// API info endpoint
router.get('/', (req: Request, res: Response) => {
  res.json({
    success: true,
    message: 'Hana AI Backend API',
    data: {
      version: '1.0.0',
      endpoints: {
        health: '/api/health',
        ready: '/api/ready',
        live: '/api/live',
        documentation: '/api-docs'
      }
    },
    timestamp: new Date().toISOString()
  });
});

export default router;
