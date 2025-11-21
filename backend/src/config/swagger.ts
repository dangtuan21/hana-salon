import swaggerJsdoc from 'swagger-jsdoc';
import { SwaggerDefinition } from 'swagger-jsdoc';

const swaggerDefinition: SwaggerDefinition = {
  openapi: '3.0.0',
  info: {
    title: 'Hana AI Backend API',
    version: '1.0.0',
    description: 'A comprehensive API for the Hana AI salon booking system built with Node.js, Express, and TypeScript',
    contact: {
      name: 'Hana AI Team',
      email: 'support@hana-ai.com'
    },
    license: {
      name: 'MIT',
      url: 'https://opensource.org/licenses/MIT'
    }
  },
  servers: [
    {
      url: 'http://localhost:8060',
      description: 'Development HTTP server'
    },
    {
      url: 'https://localhost:8443',
      description: 'Development HTTPS server (self-signed certificate)'
    },
    {
      url: 'https://api.hana-ai.com',
      description: 'Production server'
    }
  ],
  tags: [
    {
      name: 'Health',
      description: 'Health check and monitoring endpoints'
    },
    {
      name: 'API Info',
      description: 'API information and documentation'
    },
    {
      name: 'Services',
      description: 'Salon services management - CRUD operations for managing nail care services'
    },
    {
      name: 'Customers',
      description: 'Customer management endpoints'
    },
    {
      name: 'Technicians',
      description: 'Technician management endpoints'
    },
    {
      name: 'Bookings',
      description: 'Booking management endpoints'
    },
    {
      name: 'Sessions',
      description: 'LLM conversation session management endpoints'
    },
  ]
};

const options = {
  definition: swaggerDefinition,
  apis: [
    './src/docs/swagger/*.yaml'
  ]
};

export const swaggerSpec = swaggerJsdoc(options);
export default swaggerSpec;
