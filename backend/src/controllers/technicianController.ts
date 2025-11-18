import { Request, Response } from 'express';
import { Technician, TechnicianFilters, ApiResponse } from '../types/salon';

// In-memory storage for demo - replace with actual database connection
let technicians: Technician[] = [];

export const getAllTechnicians = async (req: Request<{}, ApiResponse<Technician[]>, {}, TechnicianFilters>, res: Response) => {
  try {
    const { skill_level, available, specialties, rating_min, page = 1, limit = 10 } = req.query;
    
    let filteredTechnicians = [...technicians];
    
    // Apply filters
    if (skill_level) {
      filteredTechnicians = filteredTechnicians.filter(t => t.skill_level === skill_level);
    }
    if (available !== undefined) {
      filteredTechnicians = filteredTechnicians.filter(t => t.is_available === (available === 'true'));
    }
    if (specialties && Array.isArray(specialties)) {
      filteredTechnicians = filteredTechnicians.filter(t => 
        specialties.some(specialty => t.specialties.includes(specialty))
      );
    }
    if (rating_min) {
      filteredTechnicians = filteredTechnicians.filter(t => t.rating >= Number(rating_min));
    }
    
    // Pagination
    const startIndex = (Number(page) - 1) * Number(limit);
    const endIndex = startIndex + Number(limit);
    const paginatedTechnicians = filteredTechnicians.slice(startIndex, endIndex);
    
    res.json({
      success: true,
      data: paginatedTechnicians,
      total: filteredTechnicians.length
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to fetch technicians',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
};

export const getTechnicianById = async (req: Request<{ id: string }>, res: Response) => {
  try {
    const { id } = req.params;
    const technician = technicians.find(t => t._id === id);
    
    if (!technician) {
      return res.status(404).json({
        success: false,
        error: 'Technician not found'
      });
    }
    
    res.json({
      success: true,
      data: technician
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to fetch technician',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
};

export const createTechnician = async (req: Request<{}, ApiResponse<Technician>, Technician>, res: Response) => {
  try {
    const technicianData = req.body;
    
    const newTechnician: Technician = {
      ...technicianData,
      _id: `tech_${Date.now()}`,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    
    technicians.push(newTechnician);
    
    res.status(201).json({
      success: true,
      data: newTechnician,
      message: 'Technician created successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to create technician',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
};

export const updateTechnician = async (req: Request<{ id: string }, ApiResponse<Technician>, Partial<Technician>>, res: Response) => {
  try {
    const { id } = req.params;
    const updates = req.body;
    
    const technicianIndex = technicians.findIndex(t => t._id === id);
    
    if (technicianIndex === -1) {
      return res.status(404).json({
        success: false,
        error: 'Technician not found'
      });
    }
    
    technicians[technicianIndex] = {
      ...technicians[technicianIndex],
      ...updates,
      updated_at: new Date().toISOString()
    };
    
    res.json({
      success: true,
      data: technicians[technicianIndex],
      message: 'Technician updated successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to update technician',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
};

export const deleteTechnician = async (req: Request<{ id: string }>, res: Response) => {
  try {
    const { id } = req.params;
    const technicianIndex = technicians.findIndex(t => t._id === id);
    
    if (technicianIndex === -1) {
      return res.status(404).json({
        success: false,
        error: 'Technician not found'
      });
    }
    
    technicians.splice(technicianIndex, 1);
    
    res.json({
      success: true,
      message: 'Technician deleted successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to delete technician',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
};

export const getTechniciansByService = async (req: Request<{ serviceId: string }>, res: Response) => {
  try {
    const { serviceId } = req.params;
    
    // Find technicians who specialize in this service or have appropriate skill level
    const availableTechnicians = technicians.filter(t => 
      t.is_available && (
        t.specialties.includes(serviceId) || 
        t.skill_level === 'Expert' || 
        t.skill_level === 'Master'
      )
    );
    
    // Sort by specialization and rating
    availableTechnicians.sort((a, b) => {
      const aSpecialist = a.specialties.includes(serviceId) ? 1 : 0;
      const bSpecialist = b.specialties.includes(serviceId) ? 1 : 0;
      
      if (aSpecialist !== bSpecialist) {
        return bSpecialist - aSpecialist; // Specialists first
      }
      
      return b.rating - a.rating; // Higher rating first
    });
    
    res.json({
      success: true,
      data: availableTechnicians,
      total: availableTechnicians.length
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to fetch technicians for service',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
};

export const updateTechnicianAvailability = async (req: Request<{ id: string }, ApiResponse, { is_available: boolean }>, res: Response) => {
  try {
    const { id } = req.params;
    const { is_available } = req.body;
    
    const technicianIndex = technicians.findIndex(t => t._id === id);
    
    if (technicianIndex === -1) {
      return res.status(404).json({
        success: false,
        error: 'Technician not found'
      });
    }
    
    technicians[technicianIndex].is_available = is_available;
    technicians[technicianIndex].updated_at = new Date().toISOString();
    
    res.json({
      success: true,
      data: technicians[technicianIndex],
      message: `Technician availability updated to ${is_available ? 'available' : 'unavailable'}`
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to update technician availability',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
};
