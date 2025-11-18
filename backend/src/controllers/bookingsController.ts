import { Request, Response } from 'express';
import asyncHandler from 'express-async-handler';
import { Booking } from '@/models/Booking';
import { Customer } from '@/models/Customer';
import { Technician } from '@/models/Technician';
import { Service } from '@/models/Service';
import { ResponseUtil } from '@/utils/response';
import logger from '@/utils/logger';

// Get all bookings
export const getAllBookings = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  try {
    const page = parseInt(req.query.page as string) || 1;
    const limit = parseInt(req.query.limit as string) || 10;
    const skip = (page - 1) * limit;
    
    const filter: any = {};
    
    // Filter by status
    if (req.query.status) {
      filter.status = req.query.status;
    }
    
    // Filter by payment status
    if (req.query.paymentStatus) {
      filter.paymentStatus = req.query.paymentStatus;
    }
    
    // Filter by customer ID
    if (req.query.customerId) {
      filter.customerId = req.query.customerId;
    }
    
    // Filter by technician ID
    if (req.query.technicianId) {
      filter['services.technicianId'] = req.query.technicianId;
    }
    
    // Filter by date range
    if (req.query.startDate || req.query.endDate) {
      filter.appointmentDate = {};
      if (req.query.startDate) {
        filter.appointmentDate.$gte = new Date(req.query.startDate as string);
      }
      if (req.query.endDate) {
        filter.appointmentDate.$lte = new Date(req.query.endDate as string);
      }
    }

    const bookings = await Booking.find(filter)
      .populate('customerId', 'firstName lastName email')
      .populate('services.technicianId', 'firstName lastName employeeId')
      .populate('services.serviceId', 'name price duration_minutes')
      .sort({ created_at: -1 })
      .skip(skip)
      .limit(limit)
      .select('-__v');

    const total = await Booking.countDocuments(filter);
    
    logger.info(`Retrieved ${bookings.length} bookings (page ${page})`);
    
    ResponseUtil.success(res, {
      bookings,
      pagination: {
        page,
        limit,
        total,
        pages: Math.ceil(total / limit)
      }
    }, 'Bookings retrieved successfully');
    
  } catch (error: any) {
    logger.error('Error fetching bookings:', error);
    ResponseUtil.internalError(res, 'Failed to fetch bookings');
  }
});

// Get booking by ID
export const getBookingById = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    
    const booking = await Booking.findById(id)
      .populate('customerId', 'firstName lastName email phone address preferences')
      .populate('technicianId', 'firstName lastName employeeId specialties skillLevel rating')
      .populate('serviceIds', 'name category duration_minutes price description')
      .select('-__v');
    
    if (!booking) {
      ResponseUtil.notFound(res, 'Booking not found');
      return;
    }
    
    logger.info(`Retrieved booking: ${booking._id}`);
    
    ResponseUtil.success(res, booking, 'Booking retrieved successfully');
    
  } catch (error: any) {
    logger.error('Error fetching booking:', error);
    
    if (error.name === 'CastError') {
      ResponseUtil.badRequest(res, 'Invalid booking ID format');
    } else {
      ResponseUtil.internalError(res, 'Failed to fetch booking');
    }
  }
});

// Input validation schema
const validateBookingInput = (data: any) => {
  const errors: string[] = [];

  // Required fields
  if (!data.customerId) errors.push('customerId is required');
  if (!data.services || !Array.isArray(data.services) || data.services.length === 0) {
    errors.push('services array is required and must contain at least one service');
  }
  if (!data.appointmentDate) errors.push('appointmentDate is required');
  if (!data.startTime) errors.push('startTime is required');
  if (!data.endTime) errors.push('endTime is required');

  // Validate time format
  const timeRegex = /^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/;
  if (data.startTime && !timeRegex.test(data.startTime)) {
    errors.push('startTime must be in HH:MM format');
  }
  if (data.endTime && !timeRegex.test(data.endTime)) {
    errors.push('endTime must be in HH:MM format');
  }

  // Validate appointment date
  if (data.appointmentDate) {
    const appointmentDate = new Date(data.appointmentDate);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    if (appointmentDate < today) {
      errors.push('appointmentDate cannot be in the past');
    }
  }

  // Validate services array structure
  if (data.services && Array.isArray(data.services)) {
    data.services.forEach((service: any, index: number) => {
      if (!service.serviceId) errors.push(`services[${index}].serviceId is required`);
      if (!service.technicianId) errors.push(`services[${index}].technicianId is required`);
      if (service.duration && (typeof service.duration !== 'number' || service.duration < 1)) {
        errors.push(`services[${index}].duration must be a positive number`);
      }
      if (service.price && (typeof service.price !== 'number' || service.price < 0)) {
        errors.push(`services[${index}].price must be a non-negative number`);
      }
    });
  }

  // Validate optional fields
  if (data.notes && typeof data.notes !== 'string') {
    errors.push('notes must be a string');
  }
  if (data.customerNotes && typeof data.customerNotes !== 'string') {
    errors.push('customerNotes must be a string');
  }
  if (data.paymentMethod && !['cash', 'card', 'online', 'gift_card'].includes(data.paymentMethod)) {
    errors.push('paymentMethod must be one of: cash, card, online, gift_card');
  }

  return errors;
};

// Validate services array and related data
const validateServicesArray = async (services: any[]) => {
  try {
    const validatedServices = [];
    let totalDuration = 0;
    let totalPrice = 0;
    const technicianIds = new Set();
    const serviceIds = new Set();

    for (let i = 0; i < services.length; i++) {
      const serviceData = services[i];
      
      // Validate service exists
      const service = await Service.findById(serviceData.serviceId);
      if (!service) {
        return { isValid: false, error: `Service not found: ${serviceData.serviceId}` };
      }

      // Validate technician exists and is active
      const technician = await Technician.findById(serviceData.technicianId);
      if (!technician || !technician.isActive) {
        return { isValid: false, error: `Invalid or inactive technician: ${serviceData.technicianId}` };
      }

      // Check if technician has the required skill for this service
      if (service.required_skill_level) {
        const skillLevels = ['Junior', 'Senior', 'Expert', 'Master'];
        const requiredLevel = skillLevels.indexOf(service.required_skill_level);
        const technicianLevel = skillLevels.indexOf(technician.skillLevel);
        
        if (technicianLevel < requiredLevel) {
          return { 
            isValid: false, 
            error: `Technician ${technician.firstName} ${technician.lastName} (${technician.skillLevel}) does not meet required skill level (${service.required_skill_level}) for service ${service.name}` 
          };
        }
      }

      // Use service defaults if duration/price not provided
      const duration = serviceData.duration || service.duration_minutes;
      const price = serviceData.price || service.price;

      validatedServices.push({
        serviceId: serviceData.serviceId,
        technicianId: serviceData.technicianId,
        duration,
        price,
        status: serviceData.status || 'scheduled',
        notes: serviceData.notes || ''
      });

      totalDuration += duration;
      totalPrice += price;
      technicianIds.add(serviceData.technicianId);
      serviceIds.add(serviceData.serviceId);
    }

    // Check for technician conflicts (same technician for overlapping services)
    if (technicianIds.size < services.length) {
      // Same technician assigned to multiple services - need to validate timing
      console.warn('Same technician assigned to multiple services - ensure proper scheduling');
    }

    return {
      isValid: true,
      validatedServices,
      totalDuration,
      totalPrice,
      uniqueTechnicians: technicianIds.size,
      uniqueServices: serviceIds.size
    };

  } catch (error) {
    return { isValid: false, error: `Service validation failed: ${error instanceof Error ? error.message : 'Unknown error'}` };
  }
};

// Create new booking
export const createBooking = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  try {
    const {
      customerId,
      services,
      appointmentDate,
      startTime,
      endTime,
      notes,
      customerNotes,
      paymentMethod
    } = req.body;

    // Input validation
    const validationErrors = validateBookingInput(req.body);
    if (validationErrors.length > 0) {
      ResponseUtil.badRequest(res, `Validation errors: ${validationErrors.join(', ')}`);
      return;
    }

    // Validate customer exists and is active
    const customer = await Customer.findById(customerId);
    if (!customer || !customer.isActive) {
      ResponseUtil.badRequest(res, 'Invalid or inactive customer');
      return;
    }

    // Validate and process services
    const serviceValidation = await validateServicesArray(services);
    if (!serviceValidation.isValid) {
      ResponseUtil.badRequest(res, serviceValidation.error);
      return;
    }

    const { validatedServices, totalDuration, totalPrice } = serviceValidation;
    
    // Ensure we have valid totals
    if (typeof totalDuration !== 'number' || typeof totalPrice !== 'number') {
      ResponseUtil.badRequest(res, 'Invalid service duration or price calculation');
      return;
    }

    // Calculate duration from start and end time
    const [startHours, startMinutes] = startTime.split(':').map(Number);
    const [endHours, endMinutes] = endTime.split(':').map(Number);
    const calculatedDuration = (endHours * 60 + endMinutes) - (startHours * 60 + startMinutes);

    // Validate time logic
    if (calculatedDuration <= 0) {
      ResponseUtil.badRequest(res, 'End time must be after start time');
      return;
    }

    // Validate time duration matches service duration (allow 15 min buffer)
    if (Math.abs(calculatedDuration - totalDuration) > 15) {
      ResponseUtil.badRequest(res, `Time duration (${calculatedDuration} min) doesn't match service duration (${totalDuration} min)`);
      return;
    }

    const bookingData = {
      customerId,
      services: validatedServices,
      appointmentDate: new Date(appointmentDate),
      startTime: startTime.trim(),
      endTime: endTime.trim(),
      totalDuration: calculatedDuration,
      totalPrice,
      paymentMethod,
      notes: notes?.trim(),
      customerNotes: customerNotes?.trim()
    };

    const newBooking = await Booking.create(bookingData);
    
    // Populate the created booking for response
    const populatedBooking = await Booking.findById(newBooking._id)
      .populate('customerId', 'firstName lastName email')
      .populate('services.technicianId', 'firstName lastName employeeId')
      .populate('services.serviceId', 'name price duration_minutes');
    
    logger.info(`Created new booking: ${newBooking._id}`);
    
    ResponseUtil.success(res, populatedBooking, 'Booking created successfully', 201);
    
  } catch (error: any) {
    logger.error('Error creating booking:', error);
    
    if (error.name === 'ValidationError') {
      ResponseUtil.badRequest(res, `Validation error: ${error.message}`);
    } else {
      ResponseUtil.internalError(res, 'Failed to create booking');
    }
  }
});

// Update booking
export const updateBooking = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    const updateData = { ...req.body };

    // Remove fields that shouldn't be updated directly
    delete updateData._id;
    delete updateData.created_at;
    
    // Update the updated_at field
    updateData.updated_at = new Date();

    // Handle date fields
    if (updateData.appointmentDate) {
      updateData.appointmentDate = new Date(updateData.appointmentDate);
    }

    // Trim string fields if they exist
    if (updateData.startTime) updateData.startTime = updateData.startTime.trim();
    if (updateData.endTime) updateData.endTime = updateData.endTime.trim();
    if (updateData.notes) updateData.notes = updateData.notes.trim();
    if (updateData.customerNotes) updateData.customerNotes = updateData.customerNotes.trim();
    if (updateData.technicianNotes) updateData.technicianNotes = updateData.technicianNotes.trim();
    if (updateData.cancellationReason) updateData.cancellationReason = updateData.cancellationReason.trim();

    // Convert numeric fields
    if (updateData.totalDuration !== undefined) updateData.totalDuration = Number(updateData.totalDuration);
    if (updateData.totalPrice !== undefined) updateData.totalPrice = Number(updateData.totalPrice);

    // If services are being updated, recalculate totals
    if (updateData.serviceIds) {
      const services = await Service.find({ _id: { $in: updateData.serviceIds } });
      if (services.length !== updateData.serviceIds.length) {
        ResponseUtil.badRequest(res, 'One or more invalid service IDs');
        return;
      }
      updateData.totalPrice = services.reduce((sum, service) => sum + service.price, 0);
    }

    const updatedBooking = await Booking.findByIdAndUpdate(
      id,
      updateData,
      { 
        new: true, // Return the updated document
        runValidators: true // Run schema validation
      }
    )
      .populate('customerId', 'firstName lastName email')
      .populate('technicianId', 'firstName lastName employeeId')
      .populate('serviceIds', 'name price')
      .select('-__v');

    if (!updatedBooking) {
      ResponseUtil.notFound(res, 'Booking not found');
      return;
    }

    logger.info(`Updated booking: ${updatedBooking._id}`);
    
    ResponseUtil.success(res, updatedBooking, 'Booking updated successfully');
    
  } catch (error: any) {
    logger.error('Error updating booking:', error);
    
    if (error.name === 'ValidationError') {
      ResponseUtil.badRequest(res, `Validation error: ${error.message}`);
    } else if (error.name === 'CastError') {
      ResponseUtil.badRequest(res, 'Invalid booking ID format');
    } else {
      ResponseUtil.internalError(res, 'Failed to update booking');
    }
  }
});

// Cancel booking
export const cancelBooking = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    const { cancellationReason } = req.body;
    
    const cancelledBooking = await Booking.findByIdAndUpdate(
      id,
      { 
        status: 'cancelled',
        cancellationReason: cancellationReason?.trim(),
        updated_at: new Date()
      },
      { new: true }
    )
      .populate('customerId', 'firstName lastName email')
      .populate('technicianId', 'firstName lastName employeeId')
      .select('_id status appointmentDate startTime totalPrice cancellationReason');
    
    if (!cancelledBooking) {
      ResponseUtil.notFound(res, 'Booking not found');
      return;
    }
    
    logger.info(`Cancelled booking: ${cancelledBooking._id}`);
    
    ResponseUtil.success(res, cancelledBooking, 'Booking cancelled successfully');
    
  } catch (error: any) {
    logger.error('Error cancelling booking:', error);
    
    if (error.name === 'CastError') {
      ResponseUtil.badRequest(res, 'Invalid booking ID format');
    } else {
      ResponseUtil.internalError(res, 'Failed to cancel booking');
    }
  }
});

// Complete booking
export const completeBooking = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    const { technicianNotes, paymentMethod } = req.body;
    
    const completedBooking = await Booking.findByIdAndUpdate(
      id,
      { 
        status: 'completed',
        paymentStatus: 'paid',
        paymentMethod: paymentMethod || 'cash',
        technicianNotes: technicianNotes?.trim(),
        updated_at: new Date()
      },
      { new: true }
    )
      .populate('customerId', 'firstName lastName email')
      .populate('technicianId', 'firstName lastName employeeId')
      .select('-__v');
    
    if (!completedBooking) {
      ResponseUtil.notFound(res, 'Booking not found');
      return;
    }
    
    logger.info(`Completed booking: ${completedBooking._id}`);
    
    ResponseUtil.success(res, completedBooking, 'Booking completed successfully');
    
  } catch (error: any) {
    logger.error('Error completing booking:', error);
    
    if (error.name === 'CastError') {
      ResponseUtil.badRequest(res, 'Invalid booking ID format');
    } else {
      ResponseUtil.internalError(res, 'Failed to complete booking');
    }
  }
});

// Add rating to booking
export const rateBooking = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    const { score, comment } = req.body;
    
    if (!score || score < 1 || score > 5) {
      ResponseUtil.badRequest(res, 'Rating score must be between 1 and 5');
      return;
    }
    
    const ratedBooking = await Booking.findByIdAndUpdate(
      id,
      { 
        rating: {
          score: Number(score),
          comment: comment?.trim(),
          ratedAt: new Date()
        },
        updated_at: new Date()
      },
      { new: true }
    )
      .populate('customerId', 'firstName lastName')
      .populate('technicianId', 'firstName lastName employeeId')
      .select('_id rating status appointmentDate');
    
    if (!ratedBooking) {
      ResponseUtil.notFound(res, 'Booking not found');
      return;
    }
    
    logger.info(`Added rating to booking: ${ratedBooking._id}`);
    
    ResponseUtil.success(res, ratedBooking, 'Booking rated successfully');
    
  } catch (error: any) {
    logger.error('Error rating booking:', error);
    
    if (error.name === 'CastError') {
      ResponseUtil.badRequest(res, 'Invalid booking ID format');
    } else {
      ResponseUtil.internalError(res, 'Failed to rate booking');
    }
  }
});

// Delete booking (hard delete - use with caution)
export const deleteBooking = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    
    const deletedBooking = await Booking.findByIdAndDelete(id)
      .select('_id appointmentDate startTime status');
    
    if (!deletedBooking) {
      ResponseUtil.notFound(res, 'Booking not found');
      return;
    }
    
    logger.info(`Deleted booking: ${deletedBooking._id}`);
    
    ResponseUtil.success(res, {
      id: deletedBooking._id,
      appointmentDate: deletedBooking.appointmentDate,
      startTime: deletedBooking.startTime,
      status: deletedBooking.status
    }, 'Booking deleted successfully');
    
  } catch (error: any) {
    logger.error('Error deleting booking:', error);
    
    if (error.name === 'CastError') {
      ResponseUtil.badRequest(res, 'Invalid booking ID format');
    } else {
      ResponseUtil.internalError(res, 'Failed to delete booking');
    }
  }
});
