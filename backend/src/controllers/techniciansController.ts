import { Request, Response } from 'express';
import asyncHandler from 'express-async-handler';
import { Technician } from '@/models/Technician';
import { ResponseUtil } from '@/utils/response';
import logger from '@/utils/logger';

// Get all technicians
export const getAllTechnicians = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  try {
    const page = parseInt(req.query.page as string) || 1;
    const limit = parseInt(req.query.limit as string) || 10;
    const skip = (page - 1) * limit;
    
    const filter: any = {};
    
    // Filter by active status
    if (req.query.isActive !== undefined) {
      filter.isActive = req.query.isActive === 'true';
    }
    
    // Filter by skill level
    if (req.query.skillLevel) {
      filter.skillLevel = req.query.skillLevel;
    }
    
    // Filter by specialties
    if (req.query.specialty) {
      filter.specialties = { $in: [req.query.specialty] };
    }
    
    // Search by name or employee ID
    if (req.query.search) {
      const searchRegex = new RegExp(req.query.search as string, 'i');
      filter.$or = [
        { firstName: searchRegex },
        { lastName: searchRegex },
        { employeeId: searchRegex }
      ];
    }

    const technicians = await Technician.find(filter)
      .sort({ rating: -1, firstName: 1 })
      .skip(skip)
      .limit(limit)
      .select('-__v');

    const total = await Technician.countDocuments(filter);
    
    logger.info(`Retrieved ${technicians.length} technicians (page ${page})`);
    
    ResponseUtil.success(res, {
      technicians,
      pagination: {
        page,
        limit,
        total,
        pages: Math.ceil(total / limit)
      }
    }, 'Technicians retrieved successfully');
    
  } catch (error: any) {
    logger.error('Error fetching technicians:', error);
    ResponseUtil.internalError(res, 'Failed to fetch technicians');
  }
});

// Get technician by ID
export const getTechnicianById = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    
    const technician = await Technician.findById(id).select('-__v');
    
    if (!technician) {
      ResponseUtil.notFound(res, 'Technician not found');
      return;
    }
    
    logger.info(`Retrieved technician: ${technician.employeeId}`);
    
    ResponseUtil.success(res, technician, 'Technician retrieved successfully');
    
  } catch (error: any) {
    logger.error('Error fetching technician:', error);
    
    if (error.name === 'CastError') {
      ResponseUtil.badRequest(res, 'Invalid technician ID format');
    } else {
      ResponseUtil.internalError(res, 'Failed to fetch technician');
    }
  }
});

// Create new technician
export const createTechnician = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  try {
    const {
      firstName,
      lastName,
      email,
      phone,
      employeeId,
      specialties,
      skillLevel,
      certifications,
      yearsOfExperience,
      hourlyRate,
      availability,
      hireDate
    } = req.body;

    // Basic validation
    if (!firstName || !lastName || !email || !phone || !employeeId || !specialties || !skillLevel || yearsOfExperience === undefined || !hourlyRate || !hireDate) {
      ResponseUtil.badRequest(res, 'Missing required fields: firstName, lastName, email, phone, employeeId, specialties, skillLevel, yearsOfExperience, hourlyRate, hireDate');
      return;
    }

    const technicianData = {
      firstName: firstName.trim(),
      lastName: lastName.trim(),
      email: email.trim().toLowerCase(),
      phone: phone.trim(),
      employeeId: employeeId.trim().toUpperCase(),
      specialties: Array.isArray(specialties) ? specialties : [specialties],
      skillLevel,
      certifications: certifications || [],
      yearsOfExperience: Number(yearsOfExperience),
      hourlyRate: Number(hourlyRate),
      availability: availability || {},
      hireDate: new Date(hireDate)
    };

    const newTechnician = await Technician.create(technicianData);
    
    logger.info(`Created new technician: ${newTechnician.employeeId}`);
    
    ResponseUtil.success(res, newTechnician, 'Technician created successfully', 201);
    
  } catch (error: any) {
    logger.error('Error creating technician:', error);
    
    if (error.name === 'ValidationError') {
      ResponseUtil.badRequest(res, `Validation error: ${error.message}`);
    } else if (error.code === 11000) {
      if (error.keyPattern?.email) {
        ResponseUtil.badRequest(res, 'Email already exists');
      } else if (error.keyPattern?.employeeId) {
        ResponseUtil.badRequest(res, 'Employee ID already exists');
      } else {
        ResponseUtil.badRequest(res, 'Duplicate entry');
      }
    } else {
      ResponseUtil.internalError(res, 'Failed to create technician');
    }
  }
});

// Update technician
export const updateTechnician = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    const updateData = { ...req.body };

    // Remove fields that shouldn't be updated directly
    delete updateData._id;
    delete updateData.created_at;
    delete updateData.totalBookings;
    delete updateData.completedBookings;
    delete updateData.rating; // Rating should be calculated separately
    
    // Update the updated_at field
    updateData.updated_at = new Date();

    // Trim string fields if they exist
    if (updateData.firstName) updateData.firstName = updateData.firstName.trim();
    if (updateData.lastName) updateData.lastName = updateData.lastName.trim();
    if (updateData.email) updateData.email = updateData.email.trim().toLowerCase();
    if (updateData.phone) updateData.phone = updateData.phone.trim();
    if (updateData.employeeId) updateData.employeeId = updateData.employeeId.trim().toUpperCase();

    // Convert numeric fields
    if (updateData.yearsOfExperience !== undefined) updateData.yearsOfExperience = Number(updateData.yearsOfExperience);
    if (updateData.hourlyRate !== undefined) updateData.hourlyRate = Number(updateData.hourlyRate);

    // Handle date fields
    if (updateData.hireDate) {
      updateData.hireDate = new Date(updateData.hireDate);
    }

    // Handle specialties array
    if (updateData.specialties && !Array.isArray(updateData.specialties)) {
      updateData.specialties = [updateData.specialties];
    }

    const updatedTechnician = await Technician.findByIdAndUpdate(
      id,
      updateData,
      { 
        new: true, // Return the updated document
        runValidators: true // Run schema validation
      }
    ).select('-__v');

    if (!updatedTechnician) {
      ResponseUtil.notFound(res, 'Technician not found');
      return;
    }

    logger.info(`Updated technician: ${updatedTechnician.employeeId}`);
    
    ResponseUtil.success(res, updatedTechnician, 'Technician updated successfully');
    
  } catch (error: any) {
    logger.error('Error updating technician:', error);
    
    if (error.name === 'ValidationError') {
      ResponseUtil.badRequest(res, `Validation error: ${error.message}`);
    } else if (error.name === 'CastError') {
      ResponseUtil.badRequest(res, 'Invalid technician ID format');
    } else if (error.code === 11000) {
      if (error.keyPattern?.email) {
        ResponseUtil.badRequest(res, 'Email already exists');
      } else if (error.keyPattern?.employeeId) {
        ResponseUtil.badRequest(res, 'Employee ID already exists');
      } else {
        ResponseUtil.badRequest(res, 'Duplicate entry');
      }
    } else {
      ResponseUtil.internalError(res, 'Failed to update technician');
    }
  }
});

// Delete technician (soft delete by setting isActive to false)
export const deleteTechnician = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    
    const deletedTechnician = await Technician.findByIdAndUpdate(
      id,
      { isActive: false, updated_at: new Date() },
      { new: true }
    ).select('_id firstName lastName employeeId email');
    
    if (!deletedTechnician) {
      ResponseUtil.notFound(res, 'Technician not found');
      return;
    }
    
    logger.info(`Deactivated technician: ${deletedTechnician.employeeId}`);
    
    ResponseUtil.success(res, {
      id: deletedTechnician._id,
      name: `${deletedTechnician.firstName} ${deletedTechnician.lastName}`,
      employeeId: deletedTechnician.employeeId,
      email: deletedTechnician.email
    }, 'Technician deactivated successfully');
    
  } catch (error: any) {
    logger.error('Error deleting technician:', error);
    
    if (error.name === 'CastError') {
      ResponseUtil.badRequest(res, 'Invalid technician ID format');
    } else {
      ResponseUtil.internalError(res, 'Failed to delete technician');
    }
  }
});

// Reactivate technician
export const reactivateTechnician = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    
    const reactivatedTechnician = await Technician.findByIdAndUpdate(
      id,
      { isActive: true, updated_at: new Date() },
      { new: true }
    ).select('_id firstName lastName employeeId email isActive');
    
    if (!reactivatedTechnician) {
      ResponseUtil.notFound(res, 'Technician not found');
      return;
    }
    
    logger.info(`Reactivated technician: ${reactivatedTechnician.employeeId}`);
    
    ResponseUtil.success(res, reactivatedTechnician, 'Technician reactivated successfully');
    
  } catch (error: any) {
    logger.error('Error reactivating technician:', error);
    
    if (error.name === 'CastError') {
      ResponseUtil.badRequest(res, 'Invalid technician ID format');
    } else {
      ResponseUtil.internalError(res, 'Failed to reactivate technician');
    }
  }
});

// Get technician availability
export const getTechnicianAvailability = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    
    const technician = await Technician.findById(id).select('firstName lastName employeeId availability isActive');
    
    if (!technician) {
      ResponseUtil.notFound(res, 'Technician not found');
      return;
    }
    
    if (!technician.isActive) {
      ResponseUtil.badRequest(res, 'Technician is not active');
      return;
    }
    
    logger.info(`Retrieved availability for technician: ${technician.employeeId}`);
    
    ResponseUtil.success(res, {
      technician: {
        id: technician._id,
        name: `${technician.firstName} ${technician.lastName}`,
        employeeId: technician.employeeId
      },
      availability: technician.availability
    }, 'Technician availability retrieved successfully');
    
  } catch (error: any) {
    logger.error('Error fetching technician availability:', error);
    
    if (error.name === 'CastError') {
      ResponseUtil.badRequest(res, 'Invalid technician ID format');
    } else {
      ResponseUtil.internalError(res, 'Failed to fetch technician availability');
    }
  }
});

// Get available technicians (active only)
export const getAvailableTechnicians = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  try {
    const technicians = await Technician.find({ 
      isActive: true 
    })
    .sort({ rating: -1, firstName: 1 })
    .select('firstName lastName employeeId specialties skillLevel rating isActive');
    
    logger.info(`Retrieved ${technicians.length} available technicians`);
    
    ResponseUtil.success(res, {
      technicians,
      count: technicians.length
    }, 'Available technicians retrieved successfully');
    
  } catch (error) {
    logger.error('Error fetching available technicians:', error);
    ResponseUtil.internalError(res, 'Failed to fetch available technicians');
  }
});

// Get technicians for a specific service
export const getTechniciansForService = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  try {
    const { serviceId } = req.params;
    
    if (!serviceId) {
      ResponseUtil.badRequest(res, 'Service ID is required');
      return;
    }
    
    // For now, return all active technicians
    // TODO: Implement service-specific technician matching based on specialties
    const technicians = await Technician.find({ 
      isActive: true 
    })
    .sort({ rating: -1, firstName: 1 })
    .select('firstName lastName employeeId specialties skillLevel rating');
    
    logger.info(`Retrieved ${technicians.length} technicians for service ${serviceId}`);
    
    ResponseUtil.success(res, {
      serviceId,
      technicians,
      count: technicians.length
    }, 'Technicians for service retrieved successfully');
    
  } catch (error) {
    logger.error('Error fetching technicians for service:', error);
    ResponseUtil.internalError(res, 'Failed to fetch technicians for service');
  }
});

// Check technician availability for a specific date/time
export const checkTechnicianAvailability = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  try {
    const technicianId = req.params.id; // Use 'id' parameter name to match route /:id/check-availability
    const { date, startTime, duration } = req.body;
    
    if (!technicianId || !date || !startTime || !duration) {
      ResponseUtil.badRequest(res, 'Technician ID, date, start time, and duration are required');
      return;
    }
    
    // Import Booking model to check conflicts
    const { Booking } = await import('@/models/Booking');
    
    // Parse the date and time
    const appointmentDate = new Date(date);
    const [hours, minutes] = startTime.split(':').map(Number);
    const startDateTime = new Date(appointmentDate);
    startDateTime.setHours(hours, minutes, 0, 0);
    
    const endDateTime = new Date(startDateTime);
    endDateTime.setMinutes(endDateTime.getMinutes() + duration);
    
    // Check for existing bookings that conflict
    const conflicts = await Booking.find({
      'services.technicianId': technicianId,
      appointmentDate: {
        $gte: new Date(appointmentDate.setHours(0, 0, 0, 0)),
        $lt: new Date(appointmentDate.setHours(23, 59, 59, 999))
      },
      status: { $in: ['initial', 'confirmed', 'in_progress'] }
    }).populate('services.serviceId', 'name duration_minutes');
    
    // Check for time conflicts
    let hasConflict = false;
    const conflictDetails = [];
    
    for (const booking of conflicts) {
      const bookingStart = new Date(`${booking.appointmentDate.toDateString()} ${booking.startTime}`);
      const bookingEnd = new Date(`${booking.appointmentDate.toDateString()} ${booking.endTime}`);
      
      // Check if times overlap
      if ((startDateTime < bookingEnd) && (endDateTime > bookingStart)) {
        hasConflict = true;
        conflictDetails.push({
          bookingId: booking._id,
          startTime: booking.startTime,
          endTime: booking.endTime,
          services: booking.services
        });
      }
    }
    
    logger.info(`Checked availability for technician ${technicianId} on ${date} at ${startTime}`);
    
    ResponseUtil.success(res, {
      technicianId,
      date,
      startTime,
      duration,
      available: !hasConflict,
      conflicts: conflictDetails
    }, hasConflict ? 'Technician has conflicts' : 'Technician is available');
    
  } catch (error) {
    logger.error('Error checking technician availability:', error);
    ResponseUtil.internalError(res, 'Failed to check technician availability');
  }
});

// Batch check technician availability for multiple technicians
export const batchCheckTechnicianAvailability = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  try {
    const { technicianIds, date, startTime, duration } = req.body;
    
    if (!technicianIds || !Array.isArray(technicianIds) || technicianIds.length === 0) {
      ResponseUtil.badRequest(res, 'Technician IDs array is required');
      return;
    }
    
    if (!date || !startTime || !duration) {
      ResponseUtil.badRequest(res, 'Date, start time, and duration are required');
      return;
    }
    
    // Import Booking model to check conflicts
    const { Booking } = await import('@/models/Booking');
    
    // Parse the date and time
    const appointmentDate = new Date(date);
    const [hours, minutes] = startTime.split(':').map(Number);
    const startDateTime = new Date(appointmentDate);
    startDateTime.setHours(hours, minutes, 0, 0);
    
    const endDateTime = new Date(startDateTime);
    endDateTime.setMinutes(endDateTime.getMinutes() + duration);
    
    // Get all bookings for the date that involve any of the technicians
    const conflicts = await Booking.find({
      'services.technicianId': { $in: technicianIds },
      appointmentDate: {
        $gte: new Date(appointmentDate.setHours(0, 0, 0, 0)),
        $lt: new Date(appointmentDate.setHours(23, 59, 59, 999))
      },
      status: { $in: ['initial', 'confirmed', 'in_progress'] }
    }).populate('services.serviceId', 'name duration_minutes');
    
    // Check availability for each technician
    const results = [];
    
    for (const technicianId of technicianIds) {
      let hasConflict = false;
      
      // Check if this technician has any conflicts
      for (const booking of conflicts) {
        // Check if this technician is involved in this booking
        const technicianInvolved = booking.services.some(
          (service: any) => service.technicianId.toString() === technicianId
        );
        
        if (technicianInvolved) {
          const bookingStart = new Date(`${booking.appointmentDate.toDateString()} ${booking.startTime}`);
          const bookingEnd = new Date(`${booking.appointmentDate.toDateString()} ${booking.endTime}`);
          
          // Check if times overlap
          if ((startDateTime < bookingEnd) && (endDateTime > bookingStart)) {
            hasConflict = true;
            break;
          }
        }
      }
      
      results.push({
        technicianId,
        available: !hasConflict
      });
    }
    
    logger.info(`Batch checked availability for ${technicianIds.length} technicians on ${date} at ${startTime}`);
    
    ResponseUtil.success(res, {
      date,
      startTime,
      duration,
      results
    }, `Batch availability check completed for ${technicianIds.length} technicians`);
    
  } catch (error) {
    logger.error('Error in batch technician availability check:', error);
    ResponseUtil.internalError(res, 'Failed to check batch technician availability');
  }
});
