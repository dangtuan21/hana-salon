import request from 'supertest';
import express from 'express';
import { healthCheck, readinessCheck, livenessCheck } from '../healthController';

const app = express();
app.get('/health', healthCheck);
app.get('/ready', readinessCheck);
app.get('/live', livenessCheck);

describe('Health Controller', () => {
  describe('GET /health', () => {
    it('should return health status', async () => {
      const response = await request(app)
        .get('/health')
        .expect(200);

      expect(response.body).toMatchObject({
        success: true,
        message: 'Service is healthy',
        data: {
          status: 'healthy',
          version: expect.any(String),
          environment: expect.any(String),
          uptime: expect.any(Number)
        }
      });
    });
  });

  describe('GET /ready', () => {
    it('should return readiness status', async () => {
      const response = await request(app)
        .get('/ready')
        .expect(200);

      expect(response.body).toMatchObject({
        success: true,
        message: 'Service is ready',
        data: {
          ready: true
        }
      });
    });
  });

  describe('GET /live', () => {
    it('should return liveness status', async () => {
      const response = await request(app)
        .get('/live')
        .expect(200);

      expect(response.body).toMatchObject({
        success: true,
        message: 'Service is alive',
        data: {
          alive: true
        }
      });
    });
  });
});
