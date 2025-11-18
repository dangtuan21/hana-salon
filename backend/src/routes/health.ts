import { Router, Request, Response } from 'express';
import { HealthCheckResponse } from '../types/booking';

const router = Router();

// Health check endpoint
router.get('/', (req: Request, res: Response) => {
  const healthResponse: HealthCheckResponse = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    service: 'hana-ai-backend',
    version: '1.0.0',
  };

  res.json(healthResponse);
});

// Detailed health check
router.get('/detailed', (req: Request, res: Response) => {
  const healthResponse: HealthCheckResponse = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    service: 'hana-ai-backend',
    version: '1.0.0',
    memory: process.memoryUsage(),
    environment: process.env.NODE_ENV || 'development',
    services: {
      aiService: 'connected', // TODO: Add actual health check
      database: 'not_configured', // TODO: Add when database is added
    },
  };

  res.json(healthResponse);
});

export default router;
