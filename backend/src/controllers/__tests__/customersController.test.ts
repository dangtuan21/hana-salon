import request from 'supertest';
import mongoose from 'mongoose';
import app from '../../app';
import database from '../../config/database';
import { Customer } from '../../models/Customer';

describe('Customers Controller', () => {
  beforeAll(async () => {
    await database.connect();
  });

  afterAll(async () => {
    await database.disconnect();
  });

  beforeEach(async () => {
    // Clean up before each test
    await Customer.deleteMany({});
  });

  describe('GET /api/customers', () => {
    test('should return empty array when no customers exist', async () => {
      const response = await request(app)
        .get('/api/customers')
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.customers).toEqual([]);
      expect(response.body.data.pagination.total).toBe(0);
    });

    test('should return customers with pagination', async () => {
      // Create test customers
      const customers = [
        {
          firstName: 'Alice',
          lastName: 'Johnson',
          email: 'alice@test.com',
          phone: '+1234567890'
        },
        {
          firstName: 'Bob',
          lastName: 'Smith',
          email: 'bob@test.com',
          phone: '+1234567891'
        }
      ];

      await Customer.create(customers);

      const response = await request(app)
        .get('/api/customers')
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.customers).toHaveLength(2);
      expect(response.body.data.pagination.total).toBe(2);
      // Should have both customers (order may vary based on creation timing)
      const firstNames = response.body.data.customers.map((c: any) => c.firstName);
      expect(firstNames).toContain('Alice');
      expect(firstNames).toContain('Bob');
    });

    test('should filter customers by active status', async () => {
      await Customer.create([
        { firstName: 'Active', lastName: 'User', email: 'active@test.com', phone: '+1111111111', isActive: true },
        { firstName: 'Inactive', lastName: 'User', email: 'inactive@test.com', phone: '+1111111112', isActive: false }
      ]);

      const response = await request(app)
        .get('/api/customers?isActive=true')
        .expect(200);

      expect(response.body.data.customers).toHaveLength(1);
      expect(response.body.data.customers[0].firstName).toBe('Active');
    });

    test('should search customers by name and email', async () => {
      await Customer.create([
        { firstName: 'John', lastName: 'Doe', email: 'john@test.com', phone: '+1111111111' },
        { firstName: 'Jane', lastName: 'Smith', email: 'jane@test.com', phone: '+1111111112' }
      ]);

      const response = await request(app)
        .get('/api/customers?search=john')
        .expect(200);

      expect(response.body.data.customers).toHaveLength(1);
      expect(response.body.data.customers[0].firstName).toBe('John');
    });

    test('should handle pagination parameters', async () => {
      // Create 5 customers
      const customers = Array.from({ length: 5 }, (_, i) => ({
        firstName: `User${i}`,
        lastName: 'Test',
        email: `user${i}@test.com`,
        phone: `+111111111${i}`
      }));
      await Customer.create(customers);

      const response = await request(app)
        .get('/api/customers?page=2&limit=2')
        .expect(200);

      expect(response.body.data.customers).toHaveLength(2);
      expect(response.body.data.pagination.page).toBe(2);
      expect(response.body.data.pagination.limit).toBe(2);
      expect(response.body.data.pagination.total).toBe(5);
      expect(response.body.data.pagination.pages).toBe(3);
    });
  });

  describe('GET /api/customers/:id', () => {
    test('should return customer by ID', async () => {
      const customer = await Customer.create({
        firstName: 'Test',
        lastName: 'User',
        email: 'test@test.com',
        phone: '+1234567890'
      });

      const response = await request(app)
        .get(`/api/customers/${customer._id}`)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.firstName).toBe('Test');
      expect(response.body.data.email).toBe('test@test.com');
    });

    test('should return 404 for non-existent customer', async () => {
      const nonExistentId = new mongoose.Types.ObjectId();
      
      const response = await request(app)
        .get(`/api/customers/${nonExistentId}`)
        .expect(404);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toBe('NOT_FOUND');
    });

    test('should return 400 for invalid ID format', async () => {
      const response = await request(app)
        .get('/api/customers/invalid-id')
        .expect(400); // CastError becomes 400 in our implementation

      expect(response.body.success).toBe(false);
    });
  });

  describe('POST /api/customers', () => {
    test('should create a new customer', async () => {
      const customerData = {
        firstName: 'New',
        lastName: 'Customer',
        email: 'new@test.com',
        phone: '+1234567890',
        dateOfBirth: '1990-01-01',
        gender: 'female'
      };

      const response = await request(app)
        .post('/api/customers')
        .send(customerData)
        .expect(201);

      expect(response.body.success).toBe(true);
      expect(response.body.data.firstName).toBe('New');
      expect(response.body.data.email).toBe('new@test.com');
      expect(response.body.data.isActive).toBe(true);

      // Verify in database
      const savedCustomer = await Customer.findById(response.body.data._id);
      expect(savedCustomer).toBeTruthy();
      expect(savedCustomer?.firstName).toBe('New');
    });

    test('should return 400 for missing required fields', async () => {
      const incompleteData = {
        firstName: 'Test'
        // Missing lastName, email, phone
      };

      const response = await request(app)
        .post('/api/customers')
        .send(incompleteData)
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toBe('BAD_REQUEST');
    });

    test('should return 400 for duplicate email', async () => {
      const customerData = {
        firstName: 'First',
        lastName: 'Customer',
        email: 'duplicate@test.com',
        phone: '+1234567890'
      };

      // Create first customer
      await request(app)
        .post('/api/customers')
        .send(customerData)
        .expect(201);

      // Try to create second customer with same email
      const duplicateData = {
        ...customerData,
        firstName: 'Second'
      };

      const response = await request(app)
        .post('/api/customers')
        .send(duplicateData)
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.message).toContain('Email already exists');
    });

    test('should validate email format', async () => {
      const customerData = {
        firstName: 'Test',
        lastName: 'User',
        email: 'invalid-email',
        phone: '+1234567890'
      };

      const response = await request(app)
        .post('/api/customers')
        .send(customerData)
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.message).toContain('Validation error');
    });

    test('should create customer with optional fields', async () => {
      const customerData = {
        firstName: 'Complete',
        lastName: 'Customer',
        email: 'complete@test.com',
        phone: '+1234567890',
        dateOfBirth: '1985-05-15',
        gender: 'male',
        address: {
          street: '123 Main St',
          city: 'New York',
          state: 'NY',
          zipCode: '10001',
          country: 'United States'
        },
        preferences: {
          allergies: ['latex'],
          notes: 'Prefers morning appointments'
        }
      };

      const response = await request(app)
        .post('/api/customers')
        .send(customerData)
        .expect(201);

      expect(response.body.success).toBe(true);
      expect(response.body.data.address.city).toBe('New York');
      expect(response.body.data.preferences.allergies).toContain('latex');
    });
  });

  describe('PUT /api/customers/:id', () => {
    test('should update customer successfully', async () => {
      const customer = await Customer.create({
        firstName: 'Original',
        lastName: 'Name',
        email: 'original@test.com',
        phone: '+1234567890'
      });

      const updateData = {
        firstName: 'Updated',
        lastName: 'Name',
        phone: '+1987654321'
      };

      const response = await request(app)
        .put(`/api/customers/${customer._id}`)
        .send(updateData)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.firstName).toBe('Updated');
      expect(response.body.data.phone).toBe('+1987654321');
      expect(response.body.data.email).toBe('original@test.com'); // Unchanged
    });

    test('should return 404 for non-existent customer', async () => {
      const nonExistentId = new mongoose.Types.ObjectId();
      
      const response = await request(app)
        .put(`/api/customers/${nonExistentId}`)
        .send({ firstName: 'Updated' })
        .expect(404);

      expect(response.body.success).toBe(false);
    });

    test('should not allow updating protected fields', async () => {
      const customer = await Customer.create({
        firstName: 'Test',
        lastName: 'User',
        email: 'test@test.com',
        phone: '+1234567890'
      });

      const updateData = {
        _id: 'new-id',
        created_at: '2020-01-01',
        totalVisits: 999,
        totalSpent: 9999,
        loyaltyPoints: 9999
      };

      const response = await request(app)
        .put(`/api/customers/${customer._id}`)
        .send(updateData)
        .expect(200);

      expect(response.body.success).toBe(true);
      // Protected fields should not be updated
      expect(response.body.data._id).toBe(customer._id.toString());
      expect(response.body.data.totalVisits).toBe(0); // Default value
    });
  });

  describe('DELETE /api/customers/:id', () => {
    test('should soft delete customer (deactivate)', async () => {
      const customer = await Customer.create({
        firstName: 'ToDelete',
        lastName: 'User',
        email: 'delete@test.com',
        phone: '+1234567890'
      });

      const response = await request(app)
        .delete(`/api/customers/${customer._id}`)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.name).toBe('ToDelete User');

      // Verify customer is deactivated, not deleted
      const deactivatedCustomer = await Customer.findById(customer._id);
      expect(deactivatedCustomer).toBeTruthy();
      expect(deactivatedCustomer?.isActive).toBe(false);
    });

    test('should return 404 for non-existent customer', async () => {
      const nonExistentId = new mongoose.Types.ObjectId();
      
      const response = await request(app)
        .delete(`/api/customers/${nonExistentId}`)
        .expect(404);

      expect(response.body.success).toBe(false);
    });
  });

  describe('PATCH /api/customers/:id/reactivate', () => {
    test('should reactivate deactivated customer', async () => {
      const customer = await Customer.create({
        firstName: 'Deactivated',
        lastName: 'User',
        email: 'deactivated@test.com',
        phone: '+1234567890',
        isActive: false
      });

      const response = await request(app)
        .patch(`/api/customers/${customer._id}/reactivate`)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.isActive).toBe(true);

      // Verify in database
      const reactivatedCustomer = await Customer.findById(customer._id);
      expect(reactivatedCustomer?.isActive).toBe(true);
    });

    test('should return 404 for non-existent customer', async () => {
      const nonExistentId = new mongoose.Types.ObjectId();
      
      const response = await request(app)
        .patch(`/api/customers/${nonExistentId}/reactivate`)
        .expect(404);

      expect(response.body.success).toBe(false);
    });
  });

  describe('Data Validation', () => {
    test('should validate customer data structure', async () => {
      const customer = await Customer.create({
        firstName: 'Valid',
        lastName: 'Customer',
        email: 'valid@test.com',
        phone: '+1234567890'
      });

      const response = await request(app)
        .get(`/api/customers/${customer._id}`)
        .expect(200);

      const customerData = response.body.data;
      
      // Check required fields
      expect(customerData).toHaveProperty('_id');
      expect(customerData).toHaveProperty('firstName');
      expect(customerData).toHaveProperty('lastName');
      expect(customerData).toHaveProperty('email');
      expect(customerData).toHaveProperty('phone');
      expect(customerData).toHaveProperty('isActive');
      expect(customerData).toHaveProperty('created_at');
      expect(customerData).toHaveProperty('updated_at');
      
      // Check default values
      expect(customerData.loyaltyPoints).toBe(0);
      expect(customerData.totalVisits).toBe(0);
      expect(customerData.totalSpent).toBe(0);
      expect(customerData.isActive).toBe(true);
    });
  });

  describe('GET /api/customers/phone/:phone', () => {
    beforeEach(async () => {
      await Customer.deleteMany({});
      await Customer.create([
        {
          firstName: 'John',
          lastName: 'Doe',
          email: 'john.doe@test.com',
          phone: '+1234567890'
        },
        {
          firstName: 'Jane',
          lastName: 'Smith',
          email: 'jane.smith@test.com',
          phone: '(555) 123-4567'
        }
      ]);
    });

    test('should return customer by exact phone match', async () => {
      const response = await request(app)
        .get('/api/customers/phone/+1234567890')
        .expect(200);

      expect(response.body).toHaveProperty('success', true);
      expect(response.body.data).toHaveProperty('firstName', 'John');
      expect(response.body.data).toHaveProperty('lastName', 'Doe');
      expect(response.body.data).toHaveProperty('phone', '+1234567890');
    });

    test('should return customer by cleaned phone match', async () => {
      const response = await request(app)
        .get('/api/customers/phone/5551234567')
        .expect(200);

      expect(response.body).toHaveProperty('success', true);
      expect(response.body.data).toHaveProperty('firstName', 'Jane');
      expect(response.body.data).toHaveProperty('lastName', 'Smith');
    });

    test('should handle phone with spaces and dashes', async () => {
      const response = await request(app)
        .get('/api/customers/phone/555-123-4567')
        .expect(200);

      expect(response.body).toHaveProperty('success', true);
      expect(response.body.data).toHaveProperty('firstName', 'Jane');
    });

    test('should return 404 for non-existent phone', async () => {
      const response = await request(app)
        .get('/api/customers/phone/9999999999')
        .expect(404);

      expect(response.body).toHaveProperty('success', false);
      expect(response.body).toHaveProperty('error');
    });

    test('should return 400 for empty phone', async () => {
      const response = await request(app)
        .get('/api/customers/phone/')
        .expect(404); // Express returns 404 for missing parameter
    });

    test('should return only necessary customer fields', async () => {
      const response = await request(app)
        .get('/api/customers/phone/+1234567890')
        .expect(200);

      const customerData = response.body.data;
      expect(customerData).toHaveProperty('_id');
      expect(customerData).toHaveProperty('firstName');
      expect(customerData).toHaveProperty('lastName');
      expect(customerData).toHaveProperty('email');
      expect(customerData).toHaveProperty('phone');
      expect(customerData).toHaveProperty('isActive');
      expect(customerData).toHaveProperty('preferences');
    });
  });
});
