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
      url: 'http://localhost:3060',
      description: 'Development server'
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
    }
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
