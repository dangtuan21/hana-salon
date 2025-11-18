import { Router, Request, Response } from 'express';
import healthRoutes from './healthRoutes';
import servicesRoutes from './servicesRoutes';

const router = Router();

// Mount route modules
router.use('/', healthRoutes);
router.use('/services', servicesRoutes);

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
        services: '/api/services',
        documentation: '/api-docs'
      }
    },
    timestamp: new Date().toISOString()
  });
});

export default router;
