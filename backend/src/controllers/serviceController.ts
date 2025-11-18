import { Request, Response } from 'express';
import { Service, ServiceFilters, ApiResponse } from '../types/salon';

// In-memory storage for demo - replace with actual database connection
let services: Service[] = [];

export const getAllServices = async (req: Request<{}, ApiResponse<Service[]>, {}, ServiceFilters>, res: Response) => {
  try {
    const { category, skill_level, price_min, price_max, page = 1, limit = 10 } = req.query;
    
    let filteredServices = [...services];
    
    // Apply filters
    if (category) {
      filteredServices = filteredServices.filter(s => s.category === category);
    }
    if (skill_level) {
      filteredServices = filteredServices.filter(s => s.required_skill_level === skill_level);
    }
    if (price_min) {
      filteredServices = filteredServices.filter(s => s.price >= Number(price_min));
    }
    if (price_max) {
      filteredServices = filteredServices.filter(s => s.price <= Number(price_max));
    }
    
    // Pagination
    const startIndex = (Number(page) - 1) * Number(limit);
    const endIndex = startIndex + Number(limit);
    const paginatedServices = filteredServices.slice(startIndex, endIndex);
    
    res.json({
      success: true,
      data: paginatedServices,
      total: filteredServices.length
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to fetch services',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
};

export const getServiceById = async (req: Request<{ id: string }>, res: Response) => {
  try {
    const { id } = req.params;
    const service = services.find(s => s._id === id);
    
    if (!service) {
      return res.status(404).json({
        success: false,
        error: 'Service not found'
      });
    }
    
    res.json({
      success: true,
      data: service
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to fetch service',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
};

export const createService = async (req: Request<{}, ApiResponse<Service>, Service>, res: Response) => {
  try {
    const serviceData = req.body;
    
    const newService: Service = {
      ...serviceData,
      _id: `service_${Date.now()}`,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    
    services.push(newService);
    
    res.status(201).json({
      success: true,
      data: newService,
      message: 'Service created successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to create service',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
};

export const updateService = async (req: Request<{ id: string }, ApiResponse<Service>, Partial<Service>>, res: Response) => {
  try {
    const { id } = req.params;
    const updates = req.body;
    
    const serviceIndex = services.findIndex(s => s._id === id);
    
    if (serviceIndex === -1) {
      return res.status(404).json({
        success: false,
        error: 'Service not found'
      });
    }
    
    services[serviceIndex] = {
      ...services[serviceIndex],
      ...updates,
      updated_at: new Date().toISOString()
    };
    
    res.json({
      success: true,
      data: services[serviceIndex],
      message: 'Service updated successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to update service',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
};

export const deleteService = async (req: Request<{ id: string }>, res: Response) => {
  try {
    const { id } = req.params;
    const serviceIndex = services.findIndex(s => s._id === id);
    
    if (serviceIndex === -1) {
      return res.status(404).json({
        success: false,
        error: 'Service not found'
      });
    }
    
    services.splice(serviceIndex, 1);
    
    res.json({
      success: true,
      message: 'Service deleted successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to delete service',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
};

export const getServiceCategories = async (req: Request, res: Response) => {
  try {
    const categories = [...new Set(services.map(s => s.category))];
    
    res.json({
      success: true,
      data: categories
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to fetch categories',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
};
