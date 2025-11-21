import request from 'supertest';
import mongoose from 'mongoose';
import app from '../../app';
import database from '../../config/database';
import { Technician } from '../../models/Technician';
import { Customer } from '../../models/Customer';
import { Booking } from '../../models/Booking';

describe('Technicians Controller', () => {
  beforeAll(async () => {
    await database.connect();
  });

  afterAll(async () => {
    await database.disconnect();
  });

  beforeEach(async () => {
    // Clean up before each test
    await Technician.deleteMany({});
  });

  describe('GET /api/technicians', () => {
    test('should return empty array when no technicians exist', async () => {
      const response = await request(app)
        .get('/api/technicians')
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.technicians).toEqual([]);
      expect(response.body.data.pagination.total).toBe(0);
    });

    test('should return technicians sorted by rating and name', async () => {
      const technicians = [
        {
          firstName: 'Alice',
          lastName: 'Johnson',
          email: 'alice@hanasalon.com',
          phone: '+1234567890',
          employeeId: 'EMP001',
          specialties: ['Manicure'],
          skillLevel: 'Senior',
          yearsOfExperience: 5,
          hourlyRate: 45,
          hireDate: '2022-01-01',
          rating: 4.5
        },
        {
          firstName: 'Bob',
          lastName: 'Smith',
          email: 'bob@hanasalon.com',
          phone: '+1234567891',
          employeeId: 'EMP002',
          specialties: ['Pedicure'],
          skillLevel: 'Expert',
          yearsOfExperience: 8,
          hourlyRate: 55,
          hireDate: '2021-06-01',
          rating: 4.8
        }
      ];

      await Technician.create(technicians);

      const response = await request(app)
        .get('/api/technicians')
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.technicians).toHaveLength(2);
      expect(response.body.data.technicians[0].firstName).toBe('Bob'); // Higher rating first
    });

    test('should filter technicians by skill level', async () => {
      await Technician.create([
        {
          firstName: 'Junior',
          lastName: 'Tech',
          email: 'junior@hanasalon.com',
          phone: '+1111111111',
          employeeId: 'EMP001',
          specialties: ['Manicure'],
          skillLevel: 'Junior',
          yearsOfExperience: 1,
          hourlyRate: 25,
          hireDate: '2023-01-01'
        },
        {
          firstName: 'Senior',
          lastName: 'Tech',
          email: 'senior@hanasalon.com',
          phone: '+1111111112',
          employeeId: 'EMP002',
          specialties: ['Pedicure'],
          skillLevel: 'Senior',
          yearsOfExperience: 5,
          hourlyRate: 45,
          hireDate: '2020-01-01'
        }
      ]);

      const response = await request(app)
        .get('/api/technicians?skillLevel=Senior')
        .expect(200);

      expect(response.body.data.technicians).toHaveLength(1);
      expect(response.body.data.technicians[0].skillLevel).toBe('Senior');
    });

    test('should filter technicians by specialty', async () => {
      await Technician.create([
        {
          firstName: 'Manicure',
          lastName: 'Specialist',
          email: 'manicure@hanasalon.com',
          phone: '+1111111111',
          employeeId: 'EMP001',
          specialties: ['Manicure', 'Nail Art'],
          skillLevel: 'Senior',
          yearsOfExperience: 3,
          hourlyRate: 40,
          hireDate: '2022-01-01'
        },
        {
          firstName: 'Pedicure',
          lastName: 'Expert',
          email: 'pedicure@hanasalon.com',
          phone: '+1111111112',
          employeeId: 'EMP002',
          specialties: ['Pedicure'],
          skillLevel: 'Expert',
          yearsOfExperience: 6,
          hourlyRate: 50,
          hireDate: '2020-01-01'
        }
      ]);

      const response = await request(app)
        .get('/api/technicians?specialty=Manicure')
        .expect(200);

      expect(response.body.data.technicians).toHaveLength(1);
      expect(response.body.data.technicians[0].specialties).toContain('Manicure');
    });

    test('should search technicians by name and employee ID', async () => {
      await Technician.create([
        {
          firstName: 'John',
          lastName: 'Doe',
          email: 'john@hanasalon.com',
          phone: '+1111111111',
          employeeId: 'EMP001',
          specialties: ['Manicure'],
          skillLevel: 'Senior',
          yearsOfExperience: 3,
          hourlyRate: 40,
          hireDate: '2022-01-01'
        },
        {
          firstName: 'Jane',
          lastName: 'Smith',
          email: 'jane@hanasalon.com',
          phone: '+1111111112',
          employeeId: 'EMP999',
          specialties: ['Pedicure'],
          skillLevel: 'Expert',
          yearsOfExperience: 6,
          hourlyRate: 50,
          hireDate: '2020-01-01'
        }
      ]);

      const response = await request(app)
        .get('/api/technicians?search=EMP999')
        .expect(200);

      expect(response.body.data.technicians).toHaveLength(1);
      expect(response.body.data.technicians[0].employeeId).toBe('EMP999');
    });
  });

  describe('GET /api/technicians/:id', () => {
    test('should return technician by ID', async () => {
      const technician = await Technician.create({
        firstName: 'Test',
        lastName: 'Technician',
        email: 'test@hanasalon.com',
        phone: '+1234567890',
        employeeId: 'EMP001',
        specialties: ['Manicure', 'Nail Art'],
        skillLevel: 'Senior',
        yearsOfExperience: 5,
        hourlyRate: 45,
        hireDate: '2022-01-01'
      });

      const response = await request(app)
        .get(`/api/technicians/${technician._id}`)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.firstName).toBe('Test');
      expect(response.body.data.employeeId).toBe('EMP001');
      expect(response.body.data.specialties).toContain('Manicure');
    });

    test('should return 404 for non-existent technician', async () => {
      const nonExistentId = new mongoose.Types.ObjectId();
      
      const response = await request(app)
        .get(`/api/technicians/${nonExistentId}`)
        .expect(404);

      expect(response.body.success).toBe(false);
    });
  });

  describe('POST /api/technicians', () => {
    test('should create a new technician', async () => {
      const technicianData = {
        firstName: 'New',
        lastName: 'Technician',
        email: 'new@hanasalon.com',
        phone: '+1234567890',
        employeeId: 'EMP001',
        specialties: ['Manicure', 'Gel Polish'],
        skillLevel: 'Senior',
        certifications: ['Certified Nail Technician'],
        yearsOfExperience: 5,
        hourlyRate: 45,
        hireDate: '2022-01-01'
      };

      const response = await request(app)
        .post('/api/technicians')
        .send(technicianData)
        .expect(201);

      expect(response.body.success).toBe(true);
      expect(response.body.data.firstName).toBe('New');
      expect(response.body.data.employeeId).toBe('EMP001');
      expect(response.body.data.specialties).toContain('Manicure');
      expect(response.body.data.isActive).toBe(true);

      // Verify in database
      const savedTechnician = await Technician.findById(response.body.data._id);
      expect(savedTechnician).toBeTruthy();
      expect(savedTechnician?.employeeId).toBe('EMP001');
    });

    test('should return 400 for missing required fields', async () => {
      const incompleteData = {
        firstName: 'Test'
        // Missing many required fields
      };

      const response = await request(app)
        .post('/api/technicians')
        .send(incompleteData)
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.error).toBe('BAD_REQUEST');
    });

    test('should return 400 for duplicate email', async () => {
      const technicianData = {
        firstName: 'First',
        lastName: 'Technician',
        email: 'duplicate@hanasalon.com',
        phone: '+1234567890',
        employeeId: 'EMP001',
        specialties: ['Manicure'],
        skillLevel: 'Senior',
        yearsOfExperience: 3,
        hourlyRate: 40,
        hireDate: '2022-01-01'
      };

      // Create first technician
      await request(app)
        .post('/api/technicians')
        .send(technicianData)
        .expect(201);

      // Try to create second technician with same email
      const duplicateData = {
        ...technicianData,
        employeeId: 'EMP002'
      };

      const response = await request(app)
        .post('/api/technicians')
        .send(duplicateData)
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.message).toContain('Email already exists');
    });

    test('should return 400 for duplicate employee ID', async () => {
      const technicianData = {
        firstName: 'First',
        lastName: 'Technician',
        email: 'first@hanasalon.com',
        phone: '+1234567890',
        employeeId: 'EMP001',
        specialties: ['Manicure'],
        skillLevel: 'Senior',
        yearsOfExperience: 3,
        hourlyRate: 40,
        hireDate: '2022-01-01'
      };

      // Create first technician
      await request(app)
        .post('/api/technicians')
        .send(technicianData)
        .expect(201);

      // Try to create second technician with same employee ID
      const duplicateData = {
        ...technicianData,
        email: 'second@hanasalon.com'
      };

      const response = await request(app)
        .post('/api/technicians')
        .send(duplicateData)
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.message).toContain('Employee ID already exists');
    });

    test('should validate specialties enum', async () => {
      const technicianData = {
        firstName: 'Test',
        lastName: 'Technician',
        email: 'test@hanasalon.com',
        phone: '+1234567890',
        employeeId: 'EMP001',
        specialties: ['InvalidSpecialty'],
        skillLevel: 'Senior',
        yearsOfExperience: 3,
        hourlyRate: 40,
        hireDate: '2022-01-01'
      };

      const response = await request(app)
        .post('/api/technicians')
        .send(technicianData)
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.message).toContain('Validation error');
    });
  });

  describe('PUT /api/technicians/:id', () => {
    test('should update technician successfully', async () => {
      const technician = await Technician.create({
        firstName: 'Original',
        lastName: 'Name',
        email: 'original@hanasalon.com',
        phone: '+1234567890',
        employeeId: 'EMP001',
        specialties: ['Manicure'],
        skillLevel: 'Junior',
        yearsOfExperience: 1,
        hourlyRate: 25,
        hireDate: '2023-01-01'
      });

      const updateData = {
        skillLevel: 'Senior',
        yearsOfExperience: 3,
        hourlyRate: 40,
        specialties: ['Manicure', 'Nail Art']
      };

      const response = await request(app)
        .put(`/api/technicians/${technician._id}`)
        .send(updateData)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.skillLevel).toBe('Senior');
      expect(response.body.data.hourlyRate).toBe(40);
      expect(response.body.data.specialties).toContain('Nail Art');
      expect(response.body.data.firstName).toBe('Original'); // Unchanged
    });

    test('should not allow updating protected fields', async () => {
      const technician = await Technician.create({
        firstName: 'Test',
        lastName: 'Technician',
        email: 'test@hanasalon.com',
        phone: '+1234567890',
        employeeId: 'EMP001',
        specialties: ['Manicure'],
        skillLevel: 'Senior',
        yearsOfExperience: 3,
        hourlyRate: 40,
        hireDate: '2022-01-01'
      });

      const updateData = {
        _id: 'new-id',
        created_at: '2020-01-01',
        totalBookings: 999,
        completedBookings: 999,
        rating: 1.0
      };

      const response = await request(app)
        .put(`/api/technicians/${technician._id}`)
        .send(updateData)
        .expect(200);

      expect(response.body.success).toBe(true);
      // Protected fields should not be updated
      expect(response.body.data._id).toBe(technician._id.toString());
      expect(response.body.data.totalBookings).toBe(0); // Default value
      expect(response.body.data.rating).toBe(5.0); // Default value
    });
  });

  describe('DELETE /api/technicians/:id', () => {
    test('should soft delete technician (deactivate)', async () => {
      const technician = await Technician.create({
        firstName: 'ToDelete',
        lastName: 'Technician',
        email: 'delete@hanasalon.com',
        phone: '+1234567890',
        employeeId: 'EMP001',
        specialties: ['Manicure'],
        skillLevel: 'Senior',
        yearsOfExperience: 3,
        hourlyRate: 40,
        hireDate: '2022-01-01'
      });

      const response = await request(app)
        .delete(`/api/technicians/${technician._id}`)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.name).toBe('ToDelete Technician');
      expect(response.body.data.employeeId).toBe('EMP001');

      // Verify technician is deactivated, not deleted
      const deactivatedTechnician = await Technician.findById(technician._id);
      expect(deactivatedTechnician).toBeTruthy();
      expect(deactivatedTechnician?.isActive).toBe(false);
    });
  });

  describe('PATCH /api/technicians/:id/reactivate', () => {
    test('should reactivate deactivated technician', async () => {
      const technician = await Technician.create({
        firstName: 'Deactivated',
        lastName: 'Technician',
        email: 'deactivated@hanasalon.com',
        phone: '+1234567890',
        employeeId: 'EMP001',
        specialties: ['Manicure'],
        skillLevel: 'Senior',
        yearsOfExperience: 3,
        hourlyRate: 40,
        hireDate: '2022-01-01',
        isActive: false
      });

      const response = await request(app)
        .patch(`/api/technicians/${technician._id}/reactivate`)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.isActive).toBe(true);

      // Verify in database
      const reactivatedTechnician = await Technician.findById(technician._id);
      expect(reactivatedTechnician?.isActive).toBe(true);
    });
  });

  describe('GET /api/technicians/:id/availability', () => {
    test('should return technician availability', async () => {
      const technician = await Technician.create({
        firstName: 'Available',
        lastName: 'Technician',
        email: 'available@hanasalon.com',
        phone: '+1234567890',
        employeeId: 'EMP001',
        specialties: ['Manicure'],
        skillLevel: 'Senior',
        yearsOfExperience: 3,
        hourlyRate: 40,
        hireDate: '2022-01-01',
        availability: {
          monday: { start: '09:00', end: '17:00', available: true },
          tuesday: { start: '09:00', end: '17:00', available: true },
          wednesday: { start: '09:00', end: '17:00', available: true },
          thursday: { start: '09:00', end: '17:00', available: true },
          friday: { start: '09:00', end: '17:00', available: true },
          saturday: { start: '10:00', end: '16:00', available: true },
          sunday: { start: '10:00', end: '16:00', available: false }
        }
      });

      const response = await request(app)
        .get(`/api/technicians/${technician._id}/availability`)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.technician.name).toBe('Available Technician');
      expect(response.body.data.availability.monday.available).toBe(true);
      expect(response.body.data.availability.sunday.available).toBe(false);
    });

    test('should return 400 for inactive technician', async () => {
      const technician = await Technician.create({
        firstName: 'Inactive',
        lastName: 'Technician',
        email: 'inactive@hanasalon.com',
        phone: '+1234567890',
        employeeId: 'EMP001',
        specialties: ['Manicure'],
        skillLevel: 'Senior',
        yearsOfExperience: 3,
        hourlyRate: 40,
        hireDate: '2022-01-01',
        isActive: false
      });

      const response = await request(app)
        .get(`/api/technicians/${technician._id}/availability`)
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.message).toContain('not active');
    });
  });

  describe('Data Validation', () => {
    test('should validate technician data structure', async () => {
      const technician = await Technician.create({
        firstName: 'Valid',
        lastName: 'Technician',
        email: 'valid@hanasalon.com',
        phone: '+1234567890',
        employeeId: 'EMP001',
        specialties: ['Manicure', 'Nail Art'],
        skillLevel: 'Senior',
        certifications: ['Certified Nail Technician'],
        yearsOfExperience: 5,
        hourlyRate: 45,
        hireDate: '2022-01-01'
      });

      const response = await request(app)
        .get(`/api/technicians/${technician._id}`)
        .expect(200);

      const technicianData = response.body.data;
      
      // Check required fields
      expect(technicianData).toHaveProperty('_id');
      expect(technicianData).toHaveProperty('firstName');
      expect(technicianData).toHaveProperty('lastName');
      expect(technicianData).toHaveProperty('email');
      expect(technicianData).toHaveProperty('phone');
      expect(technicianData).toHaveProperty('employeeId');
      expect(technicianData).toHaveProperty('specialties');
      expect(technicianData).toHaveProperty('skillLevel');
      expect(technicianData).toHaveProperty('yearsOfExperience');
      expect(technicianData).toHaveProperty('hourlyRate');
      expect(technicianData).toHaveProperty('isActive');
      expect(technicianData).toHaveProperty('created_at');
      expect(technicianData).toHaveProperty('updated_at');
      
      // Check default values
      expect(technicianData.rating).toBe(5.0);
      expect(technicianData.totalBookings).toBe(0);
      expect(technicianData.completedBookings).toBe(0);
      expect(technicianData.isActive).toBe(true);
      
      // Check array fields
      expect(Array.isArray(technicianData.specialties)).toBe(true);
      expect(Array.isArray(technicianData.certifications)).toBe(true);
    });
  });

  describe('GET /api/technicians/available', () => {
    beforeEach(async () => {
      await Technician.deleteMany({});
      await Technician.create([
        {
          firstName: 'Active',
          lastName: 'Technician',
          email: 'active@hanasalon.com',
          phone: '+1234567890',
          employeeId: 'EMP001',
          specialties: ['Manicure'],
          skillLevel: 'Senior',
          yearsOfExperience: 3,
          hourlyRate: 40,
          rating: 4.5,
          isActive: true,
          hireDate: '2022-01-01'
        },
        {
          firstName: 'Inactive',
          lastName: 'Technician',
          email: 'inactive@hanasalon.com',
          phone: '+1234567891',
          employeeId: 'EMP002',
          specialties: ['Pedicure'],
          skillLevel: 'Junior',
          yearsOfExperience: 1,
          hourlyRate: 30,
          isActive: false,
          hireDate: '2023-01-01'
        }
      ]);
    });

    test('should return only active technicians', async () => {
      const response = await request(app)
        .get('/api/technicians/available')
        .expect(200);

      expect(response.body).toHaveProperty('success', true);
      expect(response.body.data).toHaveProperty('technicians');
      expect(response.body.data).toHaveProperty('count', 1);
      expect(response.body.data.technicians[0]).toHaveProperty('firstName', 'Active');
      expect(response.body.data.technicians[0]).toHaveProperty('isActive', true);
    });

    test('should sort by rating and firstName', async () => {
      // Add another active technician with higher rating
      await Technician.create({
        firstName: 'Expert',
        lastName: 'Technician',
        email: 'expert@hanasalon.com',
        phone: '+1234567892',
        employeeId: 'EMP003',
        specialties: ['Nail Art'],
        skillLevel: 'Expert',
        yearsOfExperience: 8,
        hourlyRate: 60,
        rating: 4.9,
        isActive: true,
        hireDate: '2020-01-01'
      });

      const response = await request(app)
        .get('/api/technicians/available')
        .expect(200);

      expect(response.body.data.count).toBe(2);
      // Should be sorted by rating desc, then firstName asc
      expect(response.body.data.technicians[0].firstName).toBe('Expert');
      expect(response.body.data.technicians[1].firstName).toBe('Active');
    });
  });

  describe('GET /api/technicians/service/:serviceId', () => {
    let serviceId: string;

    beforeEach(async () => {
      await Technician.deleteMany({});
      serviceId = '507f1f77bcf86cd799439011'; // Mock ObjectId
      
      await Technician.create([
        {
          firstName: 'Qualified',
          lastName: 'Technician',
          email: 'qualified@hanasalon.com',
          phone: '+1234567890',
          employeeId: 'EMP001',
          specialties: ['Manicure', 'Nail Art'],
          skillLevel: 'Expert',
          yearsOfExperience: 5,
          hourlyRate: 50,
          isActive: true,
          hireDate: '2021-01-01'
        },
        {
          firstName: 'Another',
          lastName: 'Technician',
          email: 'another@hanasalon.com',
          phone: '+1234567891',
          employeeId: 'EMP002',
          specialties: ['Pedicure'],
          skillLevel: 'Senior',
          yearsOfExperience: 3,
          hourlyRate: 40,
          isActive: true,
          hireDate: '2022-01-01'
        }
      ]);
    });

    test('should return technicians for service', async () => {
      const response = await request(app)
        .get(`/api/technicians/service/${serviceId}`)
        .expect(200);

      expect(response.body).toHaveProperty('success', true);
      expect(response.body.data).toHaveProperty('serviceId', serviceId);
      expect(response.body.data).toHaveProperty('technicians');
      expect(response.body.data).toHaveProperty('count', 2);
      expect(Array.isArray(response.body.data.technicians)).toBe(true);
    });

    test('should return 400 for empty service ID', async () => {
      const response = await request(app)
        .get('/api/technicians/service/ ')
        .expect(400); // Our function returns 400 for empty service ID
    });

    test('should sort by rating and firstName', async () => {
      const response = await request(app)
        .get(`/api/technicians/service/${serviceId}`)
        .expect(200);

      const technicians = response.body.data.technicians;
      // Should be sorted by rating desc, then firstName asc
      // Both have default rating of 5.0, so sorted by firstName
      expect(technicians[0].firstName).toBe('Another'); // 'Another' comes before 'Qualified'
      expect(technicians[1].firstName).toBe('Qualified');
    });
  });

  describe('POST /api/technicians/:id/check-availability', () => {
    let technicianId: string;

    beforeEach(async () => {
      await Technician.deleteMany({});
      const technician = await Technician.create({
        firstName: 'Available',
        lastName: 'Technician',
        email: 'available@hanasalon.com',
        phone: '+1234567890',
        employeeId: 'EMP001',
        specialties: ['Manicure'],
        skillLevel: 'Senior',
        yearsOfExperience: 3,
        hourlyRate: 40,
        isActive: true,
        hireDate: '2022-01-01'
      });
      technicianId = technician._id.toString();
    });

    test('should check availability successfully', async () => {
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      
      const response = await request(app)
        .post(`/api/technicians/${technicianId}/check-availability`)
        .send({
          date: tomorrow.toISOString().split('T')[0],
          startTime: '10:00',
          duration: 60
        })
        .expect(200);
      expect(response.body).toHaveProperty('success', true);
      expect(response.body.data).toHaveProperty('technicianId', technicianId);
      expect(response.body.data).toHaveProperty('available', true);
      expect(response.body.data).toHaveProperty('conflicts');
      expect(Array.isArray(response.body.data.conflicts)).toBe(true);
    });

    test('should return 400 for missing required fields', async () => {
      const response = await request(app)
        .post(`/api/technicians/${technicianId}/check-availability`)
        .send({
          date: '2024-12-01'
          // Missing startTime and duration
        })
        .expect(400);

      expect(response.body).toHaveProperty('success', false);
      expect(response.body).toHaveProperty('error');
    });

    test('should return 500 for invalid technician ID', async () => {
      const response = await request(app)
        .post('/api/technicians/invalid-id/check-availability')
        .send({
          date: '2025-12-01',
          startTime: '10:00',
          duration: 60
        })
        .expect(500); // Will be internal server error due to invalid ObjectId format

      expect(response.body).toHaveProperty('success', false);
    });
  });

  describe('POST /api/technicians/batch-check-availability', () => {
    let technician1: any;
    let technician2: any;
    let customer: any;

    beforeEach(async () => {
      await Technician.deleteMany({});
      await Customer.deleteMany({});
      await Booking.deleteMany({});

      // Create test technicians
      technician1 = await Technician.create({
        firstName: 'John',
        lastName: 'Doe',
        email: 'john.doe@hanasalon.com',
        phone: '+1234567890',
        employeeId: 'EMP001',
        specialties: ['Manicure', 'Pedicure'],
        skillLevel: 'Senior',
        yearsOfExperience: 5,
        hourlyRate: 50,
        isActive: true,
        hireDate: '2022-01-01'
      });

      technician2 = await Technician.create({
        firstName: 'Jane',
        lastName: 'Smith',
        email: 'jane.smith@hanasalon.com',
        phone: '+1234567891',
        employeeId: 'EMP002',
        specialties: ['Manicure'],
        skillLevel: 'Junior',
        yearsOfExperience: 2,
        hourlyRate: 35,
        isActive: true,
        hireDate: '2023-01-01'
      });

      // Create test customer
      customer = await Customer.create({
        firstName: 'Test',
        lastName: 'Customer',
        email: 'test@example.com',
        phone: '+1987654321'
      });
    });

    test('should check availability for multiple technicians successfully', async () => {
      const response = await request(app)
        .post('/api/technicians/batch-check-availability')
        .send({
          technicianIds: [technician1._id.toString(), technician2._id.toString()],
          date: '2025-12-01',
          startTime: '10:00',
          duration: 60
        })
        .expect(200);

      expect(response.body).toHaveProperty('success', true);
      expect(response.body.data).toHaveProperty('results');
      expect(Array.isArray(response.body.data.results)).toBe(true);
      expect(response.body.data.results).toHaveLength(2);
      
      // Both technicians should be available (no conflicts)
      response.body.data.results.forEach((result: any) => {
        expect(result).toHaveProperty('technicianId');
        expect(result).toHaveProperty('available', true);
        expect([technician1._id.toString(), technician2._id.toString()]).toContain(result.technicianId);
      });
    });

    test('should detect conflicts for busy technicians', async () => {
      // Create a booking that conflicts with the requested time
      await Booking.create({
        customerId: customer._id,
        services: [{
          serviceId: new mongoose.Types.ObjectId(),
          technicianId: technician1._id,
          duration: 60,
          price: 50,
          status: 'initial'
        }],
        appointmentDate: new Date('2025-12-01'),
        startTime: '09:30',
        endTime: '10:30',
        status: 'confirmed',
        totalDuration: 60,
        totalPrice: 50,
        paymentStatus: 'pending',
        confirmationSent: false,
        calendarSyncStatus: 'pending'
      });

      const response = await request(app)
        .post('/api/technicians/batch-check-availability')
        .send({
          technicianIds: [technician1._id.toString(), technician2._id.toString()],
          date: '2025-12-01',
          startTime: '10:00',
          duration: 60
        })
        .expect(200);

      expect(response.body).toHaveProperty('success', true);
      expect(response.body.data.results).toHaveLength(2);

      // Find results for each technician
      const tech1Result = response.body.data.results.find((r: any) => r.technicianId === technician1._id.toString());
      const tech2Result = response.body.data.results.find((r: any) => r.technicianId === technician2._id.toString());

      expect(tech1Result).toHaveProperty('available', false); // Has conflict
      expect(tech2Result).toHaveProperty('available', true);  // No conflict
    });

    test('should return 400 for missing technicianIds', async () => {
      const response = await request(app)
        .post('/api/technicians/batch-check-availability')
        .send({
          date: '2025-12-01',
          startTime: '10:00',
          duration: 60
        })
        .expect(400);

      expect(response.body).toHaveProperty('success', false);
      expect(response.body.message).toContain('Technician IDs array is required');
    });

    test('should return 400 for empty technicianIds array', async () => {
      const response = await request(app)
        .post('/api/technicians/batch-check-availability')
        .send({
          technicianIds: [],
          date: '2025-12-01',
          startTime: '10:00',
          duration: 60
        })
        .expect(400);

      expect(response.body).toHaveProperty('success', false);
      expect(response.body.message).toContain('Technician IDs array is required');
    });

    test('should return 400 for missing required fields', async () => {
      const response = await request(app)
        .post('/api/technicians/batch-check-availability')
        .send({
          technicianIds: [technician1._id.toString()]
        })
        .expect(400);

      expect(response.body).toHaveProperty('success', false);
      expect(response.body.message).toContain('Date, start time, and duration are required');
    });

    test('should handle multiple conflicts correctly', async () => {
      // Create bookings for both technicians
      await Booking.create({
        customerId: customer._id,
        services: [{
          serviceId: new mongoose.Types.ObjectId(),
          technicianId: technician1._id,
          duration: 60,
          price: 50,
          status: 'initial'
        }],
        appointmentDate: new Date('2025-12-01'),
        startTime: '10:00',
        endTime: '11:00',
        status: 'confirmed',
        totalDuration: 60,
        totalPrice: 50,
        paymentStatus: 'pending',
        confirmationSent: false,
        calendarSyncStatus: 'pending'
      });

      await Booking.create({
        customerId: customer._id,
        services: [{
          serviceId: new mongoose.Types.ObjectId(),
          technicianId: technician2._id,
          duration: 90,
          price: 75,
          status: 'initial'
        }],
        appointmentDate: new Date('2025-12-01'),
        startTime: '09:30',
        endTime: '11:00',
        status: 'initial',
        totalDuration: 90,
        totalPrice: 75,
        paymentStatus: 'pending',
        confirmationSent: false,
        calendarSyncStatus: 'pending'
      });

      const response = await request(app)
        .post('/api/technicians/batch-check-availability')
        .send({
          technicianIds: [technician1._id.toString(), technician2._id.toString()],
          date: '2025-12-01',
          startTime: '10:30',
          duration: 60
        })
        .expect(200);

      expect(response.body).toHaveProperty('success', true);
      expect(response.body.data.results).toHaveLength(2);

      // Both technicians should have conflicts
      response.body.data.results.forEach((result: any) => {
        expect(result).toHaveProperty('available', false);
      });
    });

    test('should only check active bookings', async () => {
      // Create a cancelled booking (should not cause conflict)
      await Booking.create({
        customerId: customer._id,
        services: [{
          serviceId: new mongoose.Types.ObjectId(),
          technicianId: technician1._id,
          duration: 60,
          price: 50,
          status: 'initial'
        }],
        appointmentDate: new Date('2025-12-01'),
        startTime: '10:00',
        endTime: '11:00',
        status: 'cancelled', // Cancelled status should not cause conflict
        totalDuration: 60,
        totalPrice: 50,
        paymentStatus: 'pending',
        confirmationSent: false,
        calendarSyncStatus: 'pending'
      });

      const response = await request(app)
        .post('/api/technicians/batch-check-availability')
        .send({
          technicianIds: [technician1._id.toString()],
          date: '2025-12-01',
          startTime: '10:30',
          duration: 60
        })
        .expect(200);

      expect(response.body).toHaveProperty('success', true);
      expect(response.body.data.results[0]).toHaveProperty('available', true); // Should be available since booking is cancelled
    });
  });
});
