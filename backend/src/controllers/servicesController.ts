import { Request, Response } from 'express';
import { Service, IService } from '@/models/Service';
import { ResponseUtil } from '@/utils/response';
import { asyncHandler } from '@/middleware/errorHandler';
import logger from '@/utils/logger';

export const getAllServices = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  try {
    const services = await Service.find({}).sort({ category: 1, name: 1 });
    
    logger.info(`Retrieved ${services.length} services from MongoDB`);
    
    ResponseUtil.success(res, {
      services,
      count: services.length
    }, 'Services retrieved successfully');
    
  } catch (error) {
    logger.error('Error fetching services:', error);
    ResponseUtil.internalError(res, 'Failed to fetch services');
  }
});

export const getServiceById = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    
    const service = await Service.findById(id);
    
    if (!service) {
      ResponseUtil.notFound(res, 'Service not found');
      return;
    }
    
    logger.info(`Retrieved service: ${service.name}`);
    
    ResponseUtil.success(res, service, 'Service retrieved successfully');
    
  } catch (error) {
    logger.error('Error fetching service by ID:', error);
    ResponseUtil.internalError(res, 'Failed to fetch service');
  }
});
