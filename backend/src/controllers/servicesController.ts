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

export const createService = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  try {
    const {
      name,
      category,
      duration_minutes,
      price,
      description,
      required_skill_level,
      popularity_score
    } = req.body;

    // Basic validation
    if (!name || !category || !duration_minutes || !price) {
      ResponseUtil.badRequest(res, 'Missing required fields: name, category, duration_minutes, price');
      return;
    }

    const serviceData = {
      name: name.trim(),
      category: category.trim(),
      duration_minutes: Number(duration_minutes),
      price: Number(price),
      description: description?.trim(),
      required_skill_level: required_skill_level?.trim(),
      popularity_score: popularity_score ? Number(popularity_score) : undefined
    };

    const newService = await Service.create(serviceData);
    
    logger.info(`Created new service: ${newService.name}`);
    
    ResponseUtil.success(res, newService, 'Service created successfully', 201);
    
  } catch (error: any) {
    logger.error('Error creating service:', error);
    
    if (error.name === 'ValidationError') {
      ResponseUtil.badRequest(res, `Validation error: ${error.message}`);
    } else {
      ResponseUtil.internalError(res, 'Failed to create service');
    }
  }
});

export const updateService = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    const updateData = { ...req.body };

    // Remove fields that shouldn't be updated directly
    delete updateData._id;
    delete updateData.created_at;
    
    // Update the updated_at field
    updateData.updated_at = new Date();

    // Trim string fields if they exist
    if (updateData.name) updateData.name = updateData.name.trim();
    if (updateData.category) updateData.category = updateData.category.trim();
    if (updateData.description) updateData.description = updateData.description.trim();
    if (updateData.required_skill_level) updateData.required_skill_level = updateData.required_skill_level.trim();

    // Convert numeric fields
    if (updateData.duration_minutes) updateData.duration_minutes = Number(updateData.duration_minutes);
    if (updateData.price) updateData.price = Number(updateData.price);
    if (updateData.popularity_score) updateData.popularity_score = Number(updateData.popularity_score);

    const updatedService = await Service.findByIdAndUpdate(
      id,
      updateData,
      { 
        new: true, // Return the updated document
        runValidators: true // Run schema validation
      }
    );

    if (!updatedService) {
      ResponseUtil.notFound(res, 'Service not found');
      return;
    }

    logger.info(`Updated service: ${updatedService.name}`);
    
    ResponseUtil.success(res, updatedService, 'Service updated successfully');
    
  } catch (error: any) {
    logger.error('Error updating service:', error);
    
    if (error.name === 'ValidationError') {
      ResponseUtil.badRequest(res, `Validation error: ${error.message}`);
    } else if (error.name === 'CastError') {
      ResponseUtil.badRequest(res, 'Invalid service ID format');
    } else {
      ResponseUtil.internalError(res, 'Failed to update service');
    }
  }
});

export const deleteService = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    
    const deletedService = await Service.findByIdAndDelete(id);
    
    if (!deletedService) {
      ResponseUtil.notFound(res, 'Service not found');
      return;
    }
    
    logger.info(`Deleted service: ${deletedService.name}`);
    
    ResponseUtil.success(res, {
      id: deletedService._id,
      name: deletedService.name
    }, 'Service deleted successfully');
    
  } catch (error: any) {
    logger.error('Error deleting service:', error);
    
    if (error.name === 'CastError') {
      ResponseUtil.badRequest(res, 'Invalid service ID format');
    } else {
      ResponseUtil.internalError(res, 'Failed to delete service');
    }
  }
});

// Get service by name (for AI service matching)
export const getServiceByName = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  try {
    const { name } = req.params;
    
    if (!name) {
      ResponseUtil.badRequest(res, 'Service name is required');
      return;
    }
    
    // Case-insensitive search with partial matching
    const service = await Service.findOne({
      name: { $regex: new RegExp(name, 'i') }
    });
    
    if (!service) {
      ResponseUtil.notFound(res, `Service with name "${name}" not found`);
      return;
    }
    
    logger.info(`Retrieved service by name: ${service.name}`);
    
    ResponseUtil.success(res, service, 'Service retrieved successfully');
    
  } catch (error) {
    logger.error('Error fetching service by name:', error);
    ResponseUtil.internalError(res, 'Failed to fetch service');
  }
});
