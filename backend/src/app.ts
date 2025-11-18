import express from 'express';
import compression from 'compression';
import morgan from 'morgan';
import dotenv from 'dotenv';
import cors from 'cors';
import swaggerUi from 'swagger-ui-express';
import swaggerSpec from '@/config/swagger';
import { corsOptions, helmetConfig, createRateLimiter } from '@/middleware/security';
import { errorHandler, notFoundHandler } from '@/middleware/errorHandler';
import routes from '@/routes';
import logger from '@/utils/logger';

// Load environment variables
dotenv.config();

// Create Express application
const app = express();
const API_PREFIX = process.env.API_PREFIX || '/api';

// Trust proxy for accurate IP addresses
app.set('trust proxy', 1);

// Security middleware
app.use(helmetConfig);
app.use(cors(corsOptions));

// Rate limiting
const rateLimiter = createRateLimiter();
app.use(rateLimiter);

// Compression middleware
app.use(compression());

// Request logging
if (process.env.NODE_ENV !== 'test') {
  app.use(morgan('combined', { stream: { write: (message) => logger.info(message.trim()) } }));
}

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Swagger documentation
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec, {
  explorer: true,
  customCss: '.swagger-ui .topbar { display: none }',
  customSiteTitle: 'Hana AI API Documentation'
}));

// Health check endpoint (root level)
app.get('/', (req, res) => {
  res.json({
    success: true,
    message: 'Hana AI Backend Server',
    data: {
      status: 'running',
      version: '1.0.0',
      timestamp: new Date().toISOString(),
      environment: process.env.NODE_ENV || 'development'
    }
  });
});

// API routes
app.use(API_PREFIX, routes);

// Error handling middleware (must be last)
app.use(notFoundHandler);
app.use(errorHandler);

export default app;
