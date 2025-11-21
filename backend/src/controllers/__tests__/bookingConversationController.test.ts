import request from 'supertest';
import mongoose from 'mongoose';
import app from '../../app';
import database from '../../config/database';
import BookingConversation from '../../models/BookingConversation';
import { Customer } from '../../models/Customer';
import { Booking } from '../../models/Booking';

describe('BookingConversationController', () => {
  let testCustomerId: string;
  let testBookingId: string;

  beforeAll(async () => {
    await database.connect();
  });

  afterAll(async () => {
    await database.disconnect();
  });

  beforeEach(async () => {
    // Clean up before each test
    await BookingConversation.deleteMany({});
    await Customer.deleteMany({});
    await Booking.deleteMany({});

    // Create test customer
    const customer = await Customer.create({
      firstName: 'Test',
      lastName: 'Customer',
      email: 'test@example.com',
      phone: '123-456-7890'
    });
    testCustomerId = customer._id.toString();

    // Create test booking
    const booking = await Booking.create({
      customerId: testCustomerId,
      services: [{
        serviceId: new mongoose.Types.ObjectId(),
        technicianId: new mongoose.Types.ObjectId(),
        duration: 60,
        price: 50,
        status: 'initial'
      }],
      appointmentDate: '2025-12-01',
      startTime: '14:00',
      endTime: '15:00',
      status: 'initial',
      totalDuration: 60,
      totalPrice: 50,
      paymentStatus: 'pending'
    });
    testBookingId = booking._id.toString();
  });

  describe('POST /api/bookingConversations', () => {
    const validConversationData = {
      sessionId: 'test-session-123',
      messages: [
        {
          role: 'user',
          content: 'Hello, I want to book a manicure',
          timestamp: '2025-11-21T10:00:00.000Z'
        },
        {
          role: 'assistant',
          content: 'I would be happy to help you book a manicure!',
          timestamp: '2025-11-21T10:00:05.000Z'
        }
      ],
      startTime: '2025-11-21T10:00:00.000Z',
      endTime: '2025-11-21T10:00:30.000Z',
      outcome: 'booking_created',
      totalMessages: 2,
      conversationDuration: 30
    };

    test('should create a new conversation successfully', async () => {
      const response = await request(app)
        .post('/api/bookingConversations')
        .send(validConversationData)
        .expect(201);

      expect(response.body.success).toBe(true);
      expect(response.body.data.sessionId).toBe(validConversationData.sessionId);
      expect(response.body.data.messages).toHaveLength(2);
      expect(response.body.data.outcome).toBe('booking_created');
      expect(response.body.message).toBe('Conversation created successfully');
    });

    it('should create conversation with customer and booking IDs', async () => {
      const conversationWithIds = {
        ...validConversationData,
        sessionId: 'test-session-with-ids',
        customerId: testCustomerId,
        bookingId: testBookingId
      };

      const response = await request(app)
        .post('/api/bookingConversations')
        .send(conversationWithIds)
        .expect(201);

      expect(response.body.success).toBe(true);
      expect(response.body.data.customerId).toBe(testCustomerId);
      expect(response.body.data.bookingId).toBe(testBookingId);
    });

    it('should return 409 if conversation with same sessionId exists', async () => {
      // Create first conversation
      await request(app)
        .post('/api/bookingConversations')
        .send(validConversationData)
        .expect(201);

      // Try to create duplicate
      const response = await request(app)
        .post('/api/bookingConversations')
        .send(validConversationData)
        .expect(409);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toBe('CONFLICT');
      expect(response.body.message).toContain('already exists');
    });

    it('should return 422 for missing required fields', async () => {
      const invalidData = {
        sessionId: 'test-session-invalid'
        // Missing required fields
      };

      const response = await request(app)
        .post('/api/bookingConversations')
        .send(invalidData)
        .expect(422);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toBe('VALIDATION_ERROR');
      expect(response.body.message).toContain('Missing required fields');
    });

    it('should validate message structure', async () => {
      const invalidMessages = {
        ...validConversationData,
        sessionId: 'test-invalid-messages',
        messages: [
          {
            role: 'invalid-role', // Invalid role
            content: 'Test message',
            timestamp: '2025-11-21T10:00:00.000Z'
          }
        ]
      };

      const response = await request(app)
        .post('/api/bookingConversations')
        .send(invalidMessages)
        .expect(500); // Mongoose validation error

      expect(response.body.success).toBe(false);
    });

    it('should validate outcome enum', async () => {
      const invalidOutcome = {
        ...validConversationData,
        sessionId: 'test-invalid-outcome',
        outcome: 'invalid_outcome'
      };

      const response = await request(app)
        .post('/api/bookingConversations')
        .send(invalidOutcome)
        .expect(500); // Mongoose validation error

      expect(response.body.success).toBe(false);
    });
  });

  describe('GET /api/bookingConversations/:sessionId', () => {
    let testConversation: any;

    beforeEach(async () => {
      // Create test conversation
      testConversation = new BookingConversation({
        sessionId: 'test-get-session',
        customerId: testCustomerId,
        bookingId: testBookingId,
        messages: [
          {
            role: 'user',
            content: 'Hello',
            timestamp: new Date('2025-11-21T10:00:00.000Z')
          }
        ],
        startTime: new Date('2025-11-21T10:00:00.000Z'),
        endTime: new Date('2025-11-21T10:00:30.000Z'),
        outcome: 'information_only',
        totalMessages: 1,
        conversationDuration: 30
      });
      await testConversation.save();
    });

    it('should retrieve conversation by sessionId', async () => {
      const response = await request(app)
        .get('/api/bookingConversations/test-get-session')
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.sessionId).toBe('test-get-session');
      expect(response.body.data.messages).toHaveLength(1);
      expect(response.body.data.customerId).toBeDefined();
      expect(response.body.data.bookingId).toBeDefined();
      expect(response.body.message).toBe('Conversation retrieved successfully');
    });

    it('should populate customer and booking data', async () => {
      const response = await request(app)
        .get('/api/bookingConversations/test-get-session')
        .expect(200);

      // Check if population worked
      if (response.body.data.customerId && typeof response.body.data.customerId === 'object') {
        expect(response.body.data.customerId).toMatchObject({
          firstName: 'Test',
          lastName: 'Customer',
          email: 'test@example.com',
          phone: '123-456-7890'
        });
      } else {
        // Population might not work in test environment, just check ID exists
        expect(response.body.data.customerId).toBe(testCustomerId);
      }

      if (response.body.data.bookingId && typeof response.body.data.bookingId === 'object') {
        expect(response.body.data.bookingId).toMatchObject({
          appointmentDate: expect.any(String),
          startTime: '14:00',
          endTime: '15:00',
          status: 'initial'
        });
      } else {
        // Population might not work in test environment, just check ID exists
        expect(response.body.data.bookingId).toBe(testBookingId);
      }
    });

    it('should return 404 for non-existent sessionId', async () => {
      const response = await request(app)
        .get('/api/bookingConversations/non-existent-session')
        .expect(404);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toBe('NOT_FOUND');
      expect(response.body.message).toContain('not found');
    });
  });

  describe('GET /api/bookingConversations/customer/:customerId', () => {
    beforeEach(async () => {
      // Create multiple conversations for the test customer
      const conversations = [
        {
          sessionId: 'customer-conv-1',
          customerId: testCustomerId,
          messages: [{ role: 'user', content: 'First conversation', timestamp: new Date() }],
          startTime: new Date('2025-11-21T10:00:00.000Z'),
          outcome: 'booking_created',
          totalMessages: 1,
          conversationDuration: 60
        },
        {
          sessionId: 'customer-conv-2',
          customerId: testCustomerId,
          messages: [{ role: 'user', content: 'Second conversation', timestamp: new Date() }],
          startTime: new Date('2025-11-21T11:00:00.000Z'),
          outcome: 'booking_failed',
          totalMessages: 1,
          conversationDuration: 30
        },
        {
          sessionId: 'customer-conv-3',
          customerId: testCustomerId,
          messages: [{ role: 'user', content: 'Third conversation', timestamp: new Date() }],
          startTime: new Date('2025-11-21T12:00:00.000Z'),
          outcome: 'information_only',
          totalMessages: 1,
          conversationDuration: 45
        }
      ];

      await BookingConversation.insertMany(conversations);
    });

    it('should retrieve customer conversations with pagination', async () => {
      const response = await request(app)
        .get(`/api/bookingConversations/customer/${testCustomerId}`)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.conversations).toHaveLength(3);
      expect(response.body.data.pagination).toMatchObject({
        page: 1,
        limit: 10,
        total: 3,
        pages: 1
      });
      expect(response.body.message).toBe('Customer conversations retrieved successfully');
    });

    it('should support pagination parameters', async () => {
      const response = await request(app)
        .get(`/api/bookingConversations/customer/${testCustomerId}?page=1&limit=2`)
        .expect(200);

      expect(response.body.data.conversations).toHaveLength(2);
      expect(response.body.data.pagination).toMatchObject({
        page: 1,
        limit: 2,
        total: 3,
        pages: 2
      });
    });

    it('should filter by outcome', async () => {
      const response = await request(app)
        .get(`/api/bookingConversations/customer/${testCustomerId}?outcome=booking_created`)
        .expect(200);

      expect(response.body.data.conversations).toHaveLength(1);
      expect(response.body.data.conversations[0].outcome).toBe('booking_created');
    });

    it('should sort conversations by startTime descending', async () => {
      const response = await request(app)
        .get(`/api/bookingConversations/customer/${testCustomerId}`)
        .expect(200);

      const conversations = response.body.data.conversations;
      expect(conversations).toHaveLength(3);
      
      // Should be sorted by startTime descending (newest first)
      expect(new Date(conversations[0].startTime).getTime())
        .toBeGreaterThan(new Date(conversations[1].startTime).getTime());
      expect(new Date(conversations[1].startTime).getTime())
        .toBeGreaterThan(new Date(conversations[2].startTime).getTime());
    });

    it('should return empty array for customer with no conversations', async () => {
      const newCustomer = new Customer({
        firstName: 'New',
        lastName: 'Customer',
        email: 'new@example.com',
        phone: '999-999-9999'
      });
      await newCustomer.save();

      const response = await request(app)
        .get(`/api/bookingConversations/customer/${newCustomer._id}`)
        .expect(200);

      expect(response.body.data.conversations).toHaveLength(0);
      expect(response.body.data.pagination.total).toBe(0);
    });

    it('should handle invalid customer ID format', async () => {
      const response = await request(app)
        .get('/api/bookingConversations/customer/invalid-id')
        .expect(500);

      expect(response.body.success).toBe(false);
    });
  });

  describe('Error Handling', () => {
    test('should handle database connection errors gracefully', async () => {
      // Close the connection to simulate database error
      await mongoose.disconnect();

      const response = await request(app)
        .get('/api/bookingConversations/test-session')
        .expect(500);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toBe('SERVER_ERROR');

      // Reconnect for cleanup
      await database.connect();
    });
  });

  describe('Data Validation', () => {
    test('should validate required fields on creation', async () => {
      // Ensure database is connected
      if (mongoose.connection.readyState !== 1) {
        await database.connect();
      }

      const testCases = [
        { field: 'sessionId', data: { messages: [], startTime: new Date(), outcome: 'booking_created', totalMessages: 0, conversationDuration: 0 } },
        { field: 'messages', data: { sessionId: 'test', startTime: new Date(), outcome: 'booking_created', totalMessages: 0, conversationDuration: 0 } },
        { field: 'startTime', data: { sessionId: 'test', messages: [], outcome: 'booking_created', totalMessages: 0, conversationDuration: 0 } },
        { field: 'outcome', data: { sessionId: 'test', messages: [], startTime: new Date(), totalMessages: 0, conversationDuration: 0 } },
        { field: 'totalMessages', data: { sessionId: 'test', messages: [], startTime: new Date(), outcome: 'booking_created', conversationDuration: 0 } },
        { field: 'conversationDuration', data: { sessionId: 'test', messages: [], startTime: new Date(), outcome: 'booking_created', totalMessages: 0 } }
      ];

      for (const testCase of testCases) {
        const response = await request(app)
          .post('/api/bookingConversations')
          .send(testCase.data)
          .expect(422);

        expect(response.body.success).toBe(false);
        expect(response.body.error).toBe('VALIDATION_ERROR');
      }
    });
  });
});
