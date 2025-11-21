import request from 'supertest';
import app from '../../app';
import { Session } from '../../models/Session';
import database from '../../config/database';

describe('Sessions Controller', () => {
  beforeAll(async () => {
    await database.connect();
  });

  afterAll(async () => {
    await database.disconnect();
  });

  beforeEach(async () => {
    // Clean up sessions before each test
    await Session.deleteMany({});
  });

  describe('POST /api/sessions', () => {
    test('should create a new session successfully', async () => {
      const sessionData = {
        session_id: 'test-session-123',
        messages: [],
        booking_state: {
          customer_name: '',
          customer_phone: '',
          status: 'initial'
        },
        conversation_complete: false
      };

      const response = await request(app)
        .post('/api/sessions')
        .send(sessionData)
        .expect(201);

      expect(response.body.success).toBe(true);
      expect(response.body.data.session_id).toBe('test-session-123');
      expect(response.body.data.messages).toEqual([]);
      expect(response.body.data.conversation_complete).toBe(false);

      // Verify session was saved to database
      const savedSession = await Session.findOne({ session_id: 'test-session-123' });
      expect(savedSession).toBeTruthy();
      expect(savedSession?.session_id).toBe('test-session-123');
    });

    test('should return 400 if session_id is missing', async () => {
      const sessionData = {
        messages: [],
        booking_state: {},
        conversation_complete: false
      };

      const response = await request(app)
        .post('/api/sessions')
        .send(sessionData)
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toBe('SESSION_ID_REQUIRED');
    });

    test('should return 409 if session already exists', async () => {
      // Create a session first
      const existingSession = new Session({
        session_id: 'existing-session',
        messages: [],
        booking_state: {},
        conversation_complete: false
      });
      await existingSession.save();

      const sessionData = {
        session_id: 'existing-session',
        messages: [],
        booking_state: {},
        conversation_complete: false
      };

      const response = await request(app)
        .post('/api/sessions')
        .send(sessionData)
        .expect(409);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toBe('SESSION_EXISTS');
    });
  });

  describe('GET /api/sessions/:sessionId', () => {
    test('should retrieve session by ID successfully', async () => {
      // Create a test session
      const testSession = new Session({
        session_id: 'test-get-session',
        messages: [
          {
            role: 'user',
            content: 'Hello',
            timestamp: new Date().toISOString()
          }
        ],
        booking_state: {
          customer_name: 'John Doe',
          customer_phone: '555-1234'
        },
        conversation_complete: false
      });
      await testSession.save();

      const response = await request(app)
        .get('/api/sessions/test-get-session')
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.session_id).toBe('test-get-session');
      expect(response.body.data.messages).toHaveLength(1);
      expect(response.body.data.messages[0].content).toBe('Hello');
      expect(response.body.data.booking_state.customer_name).toBe('John Doe');
    });

    test('should return 404 if session not found', async () => {
      const response = await request(app)
        .get('/api/sessions/non-existent-session')
        .expect(404);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toBe('SESSION_NOT_FOUND');
    });

    test('should update last_activity when retrieving session', async () => {
      // Create a test session with old timestamp
      const oldTimestamp = new Date(Date.now() - 60000); // 1 minute ago
      const testSession = new Session({
        session_id: 'test-activity-update',
        messages: [],
        booking_state: {},
        conversation_complete: false,
        last_activity: oldTimestamp
      });
      await testSession.save();

      await request(app)
        .get('/api/sessions/test-activity-update')
        .expect(200);

      // Check that last_activity was updated
      const updatedSession = await Session.findOne({ session_id: 'test-activity-update' });
      expect(updatedSession?.last_activity.getTime()).toBeGreaterThan(oldTimestamp.getTime());
    });
  });

  describe('PUT /api/sessions/:sessionId', () => {
    test('should update session successfully', async () => {
      // Create a test session
      const testSession = new Session({
        session_id: 'test-update-session',
        messages: [],
        booking_state: { customer_name: '' },
        conversation_complete: false
      });
      await testSession.save();

      const updateData = {
        messages: [
          {
            role: 'user',
            content: 'Updated message',
            timestamp: new Date().toISOString()
          }
        ],
        booking_state: {
          customer_name: 'Jane Doe',
          customer_phone: '555-5678'
        },
        conversation_complete: true
      };

      const response = await request(app)
        .put('/api/sessions/test-update-session')
        .send(updateData)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.messages).toHaveLength(1);
      expect(response.body.data.messages[0].content).toBe('Updated message');
      expect(response.body.data.booking_state.customer_name).toBe('Jane Doe');
      expect(response.body.data.conversation_complete).toBe(true);

      // Verify session was updated in database
      const updatedSession = await Session.findOne({ session_id: 'test-update-session' });
      expect(updatedSession?.conversation_complete).toBe(true);
      expect(updatedSession?.booking_state.customer_name).toBe('Jane Doe');
    });

    test('should return 404 if session not found for update', async () => {
      const updateData = {
        messages: [],
        booking_state: {},
        conversation_complete: true
      };

      const response = await request(app)
        .put('/api/sessions/non-existent-session')
        .send(updateData)
        .expect(404);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toBe('SESSION_NOT_FOUND');
    });
  });

  describe('DELETE /api/sessions/:sessionId', () => {
    test('should delete session successfully', async () => {
      // Create a test session
      const testSession = new Session({
        session_id: 'test-delete-session',
        messages: [],
        booking_state: {},
        conversation_complete: false
      });
      await testSession.save();

      const response = await request(app)
        .delete('/api/sessions/test-delete-session')
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.message).toBe('Session deleted successfully');

      // Verify session was deleted from database
      const deletedSession = await Session.findOne({ session_id: 'test-delete-session' });
      expect(deletedSession).toBeNull();
    });

    test('should return 404 if session not found for deletion', async () => {
      const response = await request(app)
        .delete('/api/sessions/non-existent-session')
        .expect(404);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toBe('SESSION_NOT_FOUND');
    });
  });

  describe('GET /api/sessions', () => {
    test('should retrieve all sessions with pagination', async () => {
      // Create multiple test sessions
      const sessions = [];
      for (let i = 1; i <= 15; i++) {
        sessions.push({
          session_id: `test-session-${i}`,
          messages: [],
          booking_state: {},
          conversation_complete: i % 2 === 0 // Every other session is complete
        });
      }
      await Session.insertMany(sessions);

      const response = await request(app)
        .get('/api/sessions?page=1&limit=10')
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.sessions).toHaveLength(10);
      expect(response.body.data.pagination.total).toBe(15);
      expect(response.body.data.pagination.pages).toBe(2);
      expect(response.body.data.pagination.page).toBe(1);
      expect(response.body.data.pagination.limit).toBe(10);
    });

    test('should use default pagination values', async () => {
      // Create a few test sessions
      const sessions = Array.from({ length: 5 }, (_, i) => ({
        session_id: `default-session-${i}`,
        messages: [],
        booking_state: {},
        conversation_complete: false
      }));
      await Session.insertMany(sessions);

      const response = await request(app)
        .get('/api/sessions')
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.sessions).toHaveLength(5);
      expect(response.body.data.pagination.page).toBe(1);
      expect(response.body.data.pagination.limit).toBe(10);
    });
  });

  describe('GET /api/sessions/stats', () => {
    test('should return session statistics', async () => {
      // Create test sessions with different states
      const sessions = [
        {
          session_id: 'active-1',
          messages: [],
          booking_state: {},
          conversation_complete: false,
          created_at: new Date()
        },
        {
          session_id: 'active-2',
          messages: [],
          booking_state: {},
          conversation_complete: false,
          created_at: new Date()
        },
        {
          session_id: 'completed-1',
          messages: [],
          booking_state: {},
          conversation_complete: true,
          created_at: new Date()
        },
        {
          session_id: 'old-session',
          messages: [],
          booking_state: {},
          conversation_complete: true,
          created_at: new Date(Date.now() - 25 * 60 * 60 * 1000) // 25 hours ago
        }
      ];
      await Session.insertMany(sessions);

      const response = await request(app)
        .get('/api/sessions/stats')
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.totalSessions).toBe(4);
      expect(response.body.data.activeSessions).toBe(2);
      expect(response.body.data.completedSessions).toBe(2);
      expect(response.body.data.recentSessions).toBe(3); // Created in last 24 hours
      expect(response.body.data.completionRate).toBe(0.5); // 2/4 = 0.5
    });

    test('should handle empty database for stats', async () => {
      const response = await request(app)
        .get('/api/sessions/stats')
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.totalSessions).toBe(0);
      expect(response.body.data.activeSessions).toBe(0);
      expect(response.body.data.completedSessions).toBe(0);
      expect(response.body.data.recentSessions).toBe(0);
      expect(response.body.data.completionRate).toBe(0);
    });
  });
});
