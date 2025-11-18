import express from 'express';
import compression from 'compression';
import morgan from 'morgan';
import dotenv from 'dotenv';
import cors from 'cors';
import https from 'https';
import http from 'http';
import fs from 'fs';
import path from 'path';
import swaggerUi from 'swagger-ui-express';
import swaggerSpec from '@/config/swagger';
import { corsOptions, helmetConfig, createRateLimiter } from '@/middleware/security';
import { errorHandler, notFoundHandler } from '@/middleware/errorHandler';
import routes from '@/routes';
import logger from '@/utils/logger';
import database from '@/config/database';

// Load environment variables
dotenv.config();

const app = express();
const PORT = parseInt(process.env.PORT || '8060', 10);
const HTTPS_PORT = parseInt(process.env.HTTPS_PORT || '8443', 10);
const HOST = process.env.HOST || 'localhost';
const API_PREFIX = process.env.API_PREFIX || '/api';
const ENABLE_HTTPS = process.env.ENABLE_HTTPS === 'true' || process.env.NODE_ENV === 'production';

// Trust proxy for rate limiting and IP detection
app.set('trust proxy', 1);

// Security middleware
app.use(helmetConfig);
app.use(cors(corsOptions));
app.use(createRateLimiter());

// General middleware
app.use(compression());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Logging middleware
if (process.env.NODE_ENV !== 'test') {
  app.use(morgan('combined', {
    stream: {
      write: (message: string) => logger.info(message.trim())
    }
  }));
}

// Swagger Documentation
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec, {
  customCss: '.swagger-ui .topbar { display: none }',
  customSiteTitle: 'Hana AI Backend API Documentation',
  swaggerOptions: {
    persistAuthorization: true,
    displayRequestDuration: true
  }
}));

// Swagger JSON endpoint
app.get('/api-docs.json', (req, res) => {
  res.setHeader('Content-Type', 'application/json');
  res.send(swaggerSpec);
});

// Routes
app.use(API_PREFIX, routes);

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    success: true,
    message: 'Hana AI Backend Server',
    version: '1.0.0',
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development',
    apiPrefix: API_PREFIX
  });
});

// Error handling middleware (must be last)
app.use(notFoundHandler);
app.use(errorHandler);

// SSL Certificate paths
const getSSLOptions = () => {
  const certPath = path.join(__dirname, '..', 'ssl', 'certificate.pem');
  const keyPath = path.join(__dirname, '..', 'ssl', 'private-key.pem');
  
  try {
    if (fs.existsSync(certPath) && fs.existsSync(keyPath)) {
      return {
        key: fs.readFileSync(keyPath),
        cert: fs.readFileSync(certPath)
      };
    }
  } catch (error) {
    logger.warn('SSL certificates not found or invalid:', error);
  }
  
  return null;
};

// Initialize database connection and start server
const startServer = async (): Promise<void> => {
  try {
    // Connect to MongoDB
    await database.connect();
    
    const servers: any[] = [];
    
    // Start HTTP server
    const httpServer = http.createServer(app);
    httpServer.listen(PORT, () => {
      logger.info(`🚀 HTTP Server running on http://localhost:${PORT}`);
      logger.info(`📚 API documentation available at http://localhost:${PORT}${API_PREFIX}`);
      logger.info(`📖 Swagger UI: http://localhost:${PORT}/api-docs`);
      logger.info(`🏥 Health check: http://localhost:${PORT}${API_PREFIX}/health`);
      logger.info(`🗄️  Services API: http://localhost:${PORT}${API_PREFIX}/services`);
    });
    servers.push(httpServer);

    // Start HTTPS server if enabled and certificates are available
    if (ENABLE_HTTPS) {
      const sslOptions = getSSLOptions();
      
      if (sslOptions) {
        const httpsServer = https.createServer(sslOptions, app);
        httpsServer.listen(HTTPS_PORT, () => {
          logger.info(`🔒 HTTPS Server running on https://localhost:${HTTPS_PORT}`);
          logger.info(`📚 Secure API documentation available at https://localhost:${HTTPS_PORT}${API_PREFIX}`);
          logger.info(`📖 Secure Swagger UI: https://localhost:${HTTPS_PORT}/api-docs`);
        });
        servers.push(httpsServer);
      } else {
        logger.warn('⚠️  HTTPS enabled but SSL certificates not found. Running HTTP only.');
        logger.info('💡 To enable HTTPS, ensure ssl/certificate.pem and ssl/private-key.pem exist');
      }
    }

    logger.info(`🌍 Environment: ${process.env.NODE_ENV || 'development'}`);
    logger.info(`🔐 HTTPS: ${ENABLE_HTTPS ? 'Enabled' : 'Disabled'}`);

    // Graceful shutdown handling
    const gracefulShutdown = async (signal: string): Promise<void> => {
      logger.info(`${signal} received, shutting down gracefully`);
      
      // Close all servers
      const shutdownPromises = servers.map(server => 
        new Promise<void>((resolve) => {
          server.close(() => resolve());
        })
      );
      
      await Promise.all(shutdownPromises);
      
      try {
        await database.disconnect();
        logger.info('Process terminated');
        process.exit(0);
      } catch (error) {
        logger.error('Error during shutdown:', error);
        process.exit(1);
      }
    };

    process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
    process.on('SIGINT', () => gracefulShutdown('SIGINT'));
    
  } catch (error) {
    logger.error('Failed to start server:', error);
    process.exit(1);
  }
};

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  logger.error('Uncaught Exception:', error);
  process.exit(1);
});

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

startServer();

export default app;
