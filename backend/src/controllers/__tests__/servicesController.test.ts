import request from 'supertest';
import app from '../../server';
import database from '../../config/database';
import { Service } from '../../models/Service';

describe('Services Controller', () => {
  beforeAll(async () => {
    await database.connect();
  });

  afterAll(async () => {
    await database.disconnect();
  });

  describe('GET /api/services', () => {
    test('should return all services with 200 status', async () => {
      const response = await request(app)
        .get('/api/services')
        .expect(200);

      expect(response.body).toHaveProperty('success', true);
      expect(response.body).toHaveProperty('data');
      expect(response.body.data).toHaveProperty('services');
      expect(response.body.data).toHaveProperty('count');
      expect(Array.isArray(response.body.data.services)).toBe(true);
      expect(response.body.data.count).toBe(response.body.data.services.length);
    });

    test('should return empty array when no services exist', async () => {
      // Temporarily remove all services
      const originalServices = await Service.find({});
      await Service.deleteMany({});

      const response = await request(app)
        .get('/api/services')
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.services).toEqual([]);
      expect(response.body.data.count).toBe(0);
      expect(response.body.message).toBe('Services retrieved successfully');

      // Restore original services
      if (originalServices.length > 0) {
        await Service.insertMany(originalServices);
      }
    });

    test('should return services with correct structure', async () => {
      const response = await request(app)
        .get('/api/services')
        .expect(200);

      if (response.body.data.services.length > 0) {
        const service = response.body.data.services[0];
        expect(service).toHaveProperty('_id');
        expect(service).toHaveProperty('name');
        expect(service).toHaveProperty('category');
        expect(service).toHaveProperty('duration_minutes');
        expect(service).toHaveProperty('price');
        expect(service).toHaveProperty('description');
        expect(service).toHaveProperty('required_skill_level');
        expect(service).toHaveProperty('popularity_score');
        expect(service).toHaveProperty('created_at');
        expect(service).toHaveProperty('updated_at');
      }
    });

    test('should return services sorted by category and name', async () => {
      const response = await request(app)
        .get('/api/services')
        .expect(200);

      const services = response.body.data.services;
      if (services.length > 1) {
        for (let i = 1; i < services.length; i++) {
          const prev = services[i - 1];
          const curr = services[i];
          
          if (prev.category === curr.category) {
            expect(prev.name.localeCompare(curr.name)).toBeLessThanOrEqual(0);
          } else {
            expect(prev.category.localeCompare(curr.category)).toBeLessThanOrEqual(0);
          }
        }
      }
    });
  });


  describe('GET /api/services/:id', () => {
    test('should return specific service by valid ID', async () => {
      // First get all services to get a valid ID
      const servicesResponse = await request(app).get('/api/services');
      const services = servicesResponse.body.data.services;
      
      if (services.length > 0) {
        const serviceId = services[0]._id;
        
        const response = await request(app)
          .get(`/api/services/${serviceId}`)
          .expect(200);

        expect(response.body.success).toBe(true);
        expect(response.body.data._id).toBe(serviceId);
        expect(response.body.data).toHaveProperty('name');
        expect(response.body.data).toHaveProperty('category');
      }
    });

    test('should return 404 for non-existent service ID', async () => {
      const fakeId = '507f1f77bcf86cd799439011'; // Valid ObjectId format but non-existent
      
      const response = await request(app)
        .get(`/api/services/${fakeId}`)
        .expect(404);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toBe('NOT_FOUND');
    });

    test('should return 500 for invalid ObjectId format', async () => {
      const invalidId = 'invalid-id-format';
      
      const response = await request(app)
        .get(`/api/services/${invalidId}`)
        .expect(500);

      expect(response.body.success).toBe(false);
    });

    test('should return 404 when no services exist in database', async () => {
      // Temporarily remove all services
      const originalServices = await Service.find({});
      await Service.deleteMany({});

      const fakeId = '507f1f77bcf86cd799439011'; // Valid ObjectId format
      
      const response = await request(app)
        .get(`/api/services/${fakeId}`)
        .expect(404);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toBe('NOT_FOUND');
      expect(response.body.message).toBe('Service not found');

      // Restore original services
      if (originalServices.length > 0) {
        await Service.insertMany(originalServices);
      }
    });
  });

  describe('Data Validation', () => {
    test('should return services with valid data types', async () => {
      const response = await request(app)
        .get('/api/services')
        .expect(200);

      response.body.data.services.forEach((service: any) => {
        expect(typeof service._id).toBe('string');
        expect(typeof service.name).toBe('string');
        expect(typeof service.category).toBe('string');
        expect(typeof service.duration_minutes).toBe('number');
        expect(typeof service.price).toBe('number');
        expect(typeof service.description).toBe('string');
        expect(typeof service.required_skill_level).toBe('string');
        expect(typeof service.popularity_score).toBe('number');
        expect(typeof service.created_at).toBe('string');
        expect(typeof service.updated_at).toBe('string');
      });
    });

    test('should handle empty services array gracefully', async () => {
      // Temporarily remove all services
      const originalServices = await Service.find({});
      await Service.deleteMany({});

      const response = await request(app)
        .get('/api/services')
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.services).toEqual([]);
      expect(response.body.data.count).toBe(0);
      
      // Should not throw any errors when iterating over empty array
      response.body.data.services.forEach((service: any) => {
        // This should never execute but won't throw
        expect(service).toBeDefined();
      });

      // Restore original services
      if (originalServices.length > 0) {
        await Service.insertMany(originalServices);
      }
    });

    test('should return services with valid value ranges', async () => {
      const response = await request(app)
        .get('/api/services')
        .expect(200);

      response.body.data.services.forEach((service: any) => {
        expect(service.duration_minutes).toBeGreaterThan(0);
        expect(service.duration_minutes).toBeLessThan(300); // 5 hours max
        expect(service.price).toBeGreaterThan(0);
        expect(service.price).toBeLessThan(500); // Reasonable upper bound
        expect(service.popularity_score).toBeGreaterThanOrEqual(0);
        expect(service.popularity_score).toBeLessThanOrEqual(10);
        expect(service.name.length).toBeGreaterThan(0);
        expect(service.category.length).toBeGreaterThan(0);
      });
    });
  });

  describe('Response Format', () => {
    test('should return consistent response format for all endpoints', async () => {
      const endpoints = [
        '/api/services'
      ];

      for (const endpoint of endpoints) {
        const response = await request(app).get(endpoint);
        
        expect(response.body).toHaveProperty('success');
        expect(response.body).toHaveProperty('timestamp');
        expect(typeof response.body.success).toBe('boolean');
        expect(typeof response.body.timestamp).toBe('string');
        
        if (response.body.success) {
          expect(response.body).toHaveProperty('data');
          expect(response.body).toHaveProperty('message');
        } else {
          expect(response.body).toHaveProperty('error');
        }
      }
    });

    test('should include proper timestamps', async () => {
      const response = await request(app)
        .get('/api/services')
        .expect(200);

      const timestamp = new Date(response.body.timestamp);
      expect(timestamp).toBeInstanceOf(Date);
      expect(timestamp.getTime()).not.toBeNaN();
      
      // Timestamp should be recent (within last minute)
      const now = new Date();
      const timeDiff = now.getTime() - timestamp.getTime();
      expect(timeDiff).toBeLessThan(60000); // 1 minute
    });
  });
});
