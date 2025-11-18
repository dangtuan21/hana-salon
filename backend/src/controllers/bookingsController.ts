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
      filter.technicianId = req.query.technicianId;
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
      .populate('customerId', 'firstName lastName email phone')
      .populate('technicianId', 'firstName lastName employeeId specialties')
      .populate('serviceIds', 'name category duration_minutes price')
      .sort({ appointmentDate: -1, startTime: 1 })
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

// Create new booking
export const createBooking = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  try {
    const {
      customerId,
      technicianId,
      serviceIds,
      appointmentDate,
      startTime,
      endTime,
      notes,
      customerNotes
    } = req.body;

    // Basic validation
    if (!customerId || !technicianId || !serviceIds || !appointmentDate || !startTime || !endTime) {
      ResponseUtil.badRequest(res, 'Missing required fields: customerId, technicianId, serviceIds, appointmentDate, startTime, endTime');
      return;
    }

    // Validate customer exists and is active
    const customer = await Customer.findById(customerId);
    if (!customer || !customer.isActive) {
      ResponseUtil.badRequest(res, 'Invalid or inactive customer');
      return;
    }

    // Validate technician exists and is active
    const technician = await Technician.findById(technicianId);
    if (!technician || !technician.isActive) {
      ResponseUtil.badRequest(res, 'Invalid or inactive technician');
      return;
    }

    // Validate services exist and calculate totals
    const services = await Service.find({ _id: { $in: serviceIds } });
    if (services.length !== serviceIds.length) {
      ResponseUtil.badRequest(res, 'One or more invalid service IDs');
      return;
    }

    const totalDuration = services.reduce((sum, service) => sum + service.duration_minutes, 0);
    const totalPrice = services.reduce((sum, service) => sum + service.price, 0);

    // Calculate duration from start and end time
    const [startHours, startMinutes] = startTime.split(':').map(Number);
    const [endHours, endMinutes] = endTime.split(':').map(Number);
    const calculatedDuration = (endHours * 60 + endMinutes) - (startHours * 60 + startMinutes);

    // Validate time duration matches service duration (allow 15 min buffer)
    if (Math.abs(calculatedDuration - totalDuration) > 15) {
      ResponseUtil.badRequest(res, `Time duration (${calculatedDuration} min) doesn't match service duration (${totalDuration} min)`);
      return;
    }

    const bookingData = {
      customerId,
      technicianId,
      serviceIds,
      appointmentDate: new Date(appointmentDate),
      startTime: startTime.trim(),
      endTime: endTime.trim(),
      totalDuration: calculatedDuration,
      totalPrice,
      notes: notes?.trim(),
      customerNotes: customerNotes?.trim()
    };

    const newBooking = await Booking.create(bookingData);
    
    // Populate the created booking for response
    const populatedBooking = await Booking.findById(newBooking._id)
      .populate('customerId', 'firstName lastName email')
      .populate('technicianId', 'firstName lastName employeeId')
      .populate('serviceIds', 'name price');
    
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
