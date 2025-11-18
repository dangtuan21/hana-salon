import { Request, Response } from 'express';
import { ResponseUtil } from '@/utils/response';
import { HealthCheckResponse } from '@/types';
import { asyncHandler } from '@/middleware/errorHandler';
import database from '@/config/database';

export const healthCheck = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  const uptime = process.uptime();
  const version = process.env.npm_package_version || '1.0.0';
  const environment = process.env.NODE_ENV || 'development';

  const healthData: HealthCheckResponse = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: Math.floor(uptime),
    version,
    environment,
    services: {
      database: database.getConnectionStatus() ? 'connected' : 'disconnected',
      aiService: 'disconnected' // Will be updated when AI service integration is added
    }
  };

  ResponseUtil.success(res, healthData, 'Service is healthy');
});

export const readinessCheck = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  // Add more comprehensive checks here (database connectivity, external services, etc.)
  const isReady = true; // This should be based on actual service dependencies

  if (isReady) {
    ResponseUtil.success(res, { ready: true }, 'Service is ready');
  } else {
    ResponseUtil.error(res, 'SERVICE_NOT_READY', 'Service is not ready', 503);
  }
});

export const livenessCheck = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  // Simple liveness check - if this endpoint responds, the service is alive
  ResponseUtil.success(res, { alive: true }, 'Service is alive');
});
