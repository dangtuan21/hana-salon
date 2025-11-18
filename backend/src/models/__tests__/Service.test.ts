import { Service, IService } from '../Service';
import database from '../../config/database';

describe.skip('Service Model', () => {
  beforeAll(async () => {
    await database.connect();
  });

  afterAll(async () => {
    await database.disconnect();
  });

  describe('Service Schema Validation', () => {
    test('should create a valid service', async () => {
      const serviceData = {
        name: 'Test Manicure',
        category: 'Test Services',
        duration_minutes: 45,
        price: 35,
        description: 'Test service description',
        required_skill_level: 'Junior',
        popularity_score: 8
      };

      const service = new Service(serviceData);
      const savedService = await service.save();

      expect(savedService._id).toBeDefined();
      expect(savedService.name).toBe(serviceData.name);
      expect(savedService.category).toBe(serviceData.category);
      expect(savedService.duration_minutes).toBe(serviceData.duration_minutes);
      expect(savedService.price).toBe(serviceData.price);
      expect(savedService.description).toBe(serviceData.description);
      expect(savedService.required_skill_level).toBe(serviceData.required_skill_level);
      expect(savedService.popularity_score).toBe(serviceData.popularity_score);

      // Clean up
      await Service.findByIdAndDelete(savedService._id);
    });

    test('should require name field', async () => {
      const serviceData = {
        category: 'Test Services',
        duration_minutes: 45,
        price: 35
      };

      const service = new Service(serviceData);
      
      await expect(service.save()).rejects.toThrow();
    });

    test('should require category field', async () => {
      const serviceData = {
        name: 'Test Manicure',
        duration_minutes: 45,
        price: 35
      };

      const service = new Service(serviceData);
      
      await expect(service.save()).rejects.toThrow();
    });

    test('should require duration_minutes field', async () => {
      const serviceData = {
        name: 'Test Manicure',
        category: 'Test Services',
        price: 35
      };

      const service = new Service(serviceData);
      
      await expect(service.save()).rejects.toThrow();
    });

    test('should require price field', async () => {
      const serviceData = {
        name: 'Test Manicure',
        category: 'Test Services',
        duration_minutes: 45
      };

      const service = new Service(serviceData);
      
      await expect(service.save()).rejects.toThrow();
    });

    test('should validate minimum duration_minutes', async () => {
      const serviceData = {
        name: 'Test Manicure',
        category: 'Test Services',
        duration_minutes: 0, // Invalid: should be > 0
        price: 35
      };

      const service = new Service(serviceData);
      
      await expect(service.save()).rejects.toThrow();
    });

    test('should validate minimum price', async () => {
      const serviceData = {
        name: 'Test Manicure',
        category: 'Test Services',
        duration_minutes: 45,
        price: -5 // Invalid: should be >= 0
      };

      const service = new Service(serviceData);
      
      await expect(service.save()).rejects.toThrow();
    });

    test('should validate popularity_score range', async () => {
      const serviceData = {
        name: 'Test Manicure',
        category: 'Test Services',
        duration_minutes: 45,
        price: 35,
        popularity_score: 15 // Invalid: should be <= 10
      };

      const service = new Service(serviceData);
      
      await expect(service.save()).rejects.toThrow();
    });

    test('should trim whitespace from string fields', async () => {
      const serviceData = {
        name: '  Test Manicure  ',
        category: '  Test Services  ',
        duration_minutes: 45,
        price: 35,
        description: '  Test description  ',
        required_skill_level: '  Junior  '
      };

      const service = new Service(serviceData);
      const savedService = await service.save();

      expect(savedService.name).toBe('Test Manicure');
      expect(savedService.category).toBe('Test Services');
      expect(savedService.description).toBe('Test description');
      expect(savedService.required_skill_level).toBe('Junior');

      // Clean up
      await Service.findByIdAndDelete(savedService._id);
    });

    test('should set default timestamps', async () => {
      const serviceData = {
        name: 'Test Manicure',
        category: 'Test Services',
        duration_minutes: 45,
        price: 35
      };

      const service = new Service(serviceData);
      const savedService = await service.save();

      expect(savedService.created_at).toBeDefined();
      expect(savedService.updated_at).toBeDefined();
      expect(savedService.created_at).toBeInstanceOf(Date);
      expect(savedService.updated_at).toBeInstanceOf(Date);

      // Clean up
      await Service.findByIdAndDelete(savedService._id);
    });
  });

  describe('Service Model Methods', () => {
    let testService: IService;

    beforeEach(async () => {
      const serviceData = {
        name: 'Test Service',
        category: 'Test Category',
        duration_minutes: 60,
        price: 50,
        description: 'Test description',
        required_skill_level: 'Senior',
        popularity_score: 7
      };

      testService = await Service.create(serviceData);
    });

    afterEach(async () => {
      if (testService?._id) {
        await Service.findByIdAndDelete(testService._id);
      }
    });

    test('should find service by id', async () => {
      const foundService = await Service.findById(testService._id);
      
      expect(foundService).toBeTruthy();
      expect(foundService?.name).toBe(testService.name);
      expect(foundService?.category).toBe(testService.category);
    });

    test('should update service', async () => {
      const updatedData = {
        name: 'Updated Service Name',
        price: 75
      };

      const updatedService = await Service.findByIdAndUpdate(
        testService._id,
        updatedData,
        { new: true }
      );

      expect(updatedService?.name).toBe(updatedData.name);
      expect(updatedService?.price).toBe(updatedData.price);
      expect(updatedService?.category).toBe(testService.category); // Should remain unchanged
    });

    test('should delete service', async () => {
      await Service.findByIdAndDelete(testService._id);
      
      const deletedService = await Service.findById(testService._id);
      expect(deletedService).toBeNull();
      
      // Prevent cleanup from running since we already deleted
      testService._id = undefined as any;
    });
  });

  describe('Service Model Queries', () => {
    const testServices = [
      {
        name: 'Basic Manicure',
        category: 'Basic Services',
        duration_minutes: 30,
        price: 25,
        popularity_score: 8
      },
      {
        name: 'Gel Manicure',
        category: 'Advanced Services',
        duration_minutes: 60,
        price: 55,
        popularity_score: 9
      },
      {
        name: 'Luxury Spa Treatment',
        category: 'Luxury Services',
        duration_minutes: 120,
        price: 100,
        popularity_score: 6
      }
    ];

    beforeAll(async () => {
      await Service.insertMany(testServices);
    });

    afterAll(async () => {
      await Service.deleteMany({
        name: { $in: testServices.map(s => s.name) }
      });
    });

    test('should find services by category', async () => {
      const basicServices = await Service.find({ category: 'Basic Services' });
      
      expect(basicServices).toHaveLength(1);
      expect(basicServices[0]?.name).toBe('Basic Manicure');
    });

    test('should find services by price range', async () => {
      const affordableServices = await Service.find({
        price: { $lte: 50 }
      });
      
      expect(affordableServices.length).toBeGreaterThanOrEqual(2);
    });

    test('should sort services by popularity', async () => {
      const servicesByPopularity = await Service.find({
        name: { $in: testServices.map(s => s.name) }
      }).sort({ popularity_score: -1 });
      
      expect(servicesByPopularity.length).toBeGreaterThanOrEqual(2);
      expect(servicesByPopularity[0]?.popularity_score).toBeGreaterThanOrEqual(
        servicesByPopularity[1]?.popularity_score || 0
      );
    });

    test('should get distinct categories', async () => {
      const categories = await Service.distinct('category');
      
      expect(categories).toContain('Basic Services');
      expect(categories).toContain('Advanced Services');
      expect(categories).toContain('Luxury Services');
    });
  });
});
