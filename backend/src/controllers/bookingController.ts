import { Request, Response } from 'express';
import { v4 as uuidv4 } from 'uuid';
import * as aiService from '../services/aiService';
import { StoredBooking, NailService, ApiResponse, BookingRequest } from '../types/booking';

// In-memory storage for demo (replace with database in production)
const bookings = new Map<string, StoredBooking>();

// Process a complete booking request
export const processBooking = async (req: Request<{}, ApiResponse, BookingRequest>, res: Response) => {
  try {
    const { booking_request } = req.body;
    
    console.log(`📝 Processing booking: ${booking_request}`);
    
    // Call AI service to process the booking
    const result = await aiService.processBooking(booking_request);
    
    // Store booking in memory (replace with database)
    const bookingId = uuidv4();
    const storedBooking: StoredBooking = {
      id: bookingId,
      ...result,
      created_at: new Date().toISOString(),
      status: result.validation_status.includes('VALID') ? 'confirmed' : 'failed',
    };
    
    bookings.set(bookingId, storedBooking);
    
    res.json({
      success: true,
      data: {
        booking_id: bookingId,
        ...result,
      },
    });
    
  } catch (error) {
    console.error('Error processing booking:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to process booking',
      message: error instanceof Error ? error.message : 'Unknown error',
    });
  }
};

// Get booking status by ID
export const getBookingStatus = async (req: Request<{ bookingId: string }>, res: Response) => {
  try {
    const { bookingId } = req.params;
    
    const booking = bookings.get(bookingId);
    
    if (!booking) {
      return res.status(404).json({
        success: false,
        error: 'Booking not found',
      });
    }
    
    res.json({
      success: true,
      data: booking,
    });
    
  } catch (error) {
    console.error('Error getting booking status:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get booking status',
      message: error instanceof Error ? error.message : 'Unknown error',
    });
  }
};

// Validate booking request without processing
export const validateBooking = async (req: Request<{}, ApiResponse, BookingRequest>, res: Response) => {
  try {
    const { booking_request } = req.body;
    
    console.log(`🔍 Validating booking: ${booking_request}`);
    
    // Call AI service to validate only
    const result = await aiService.validateBookingOnly(booking_request);
    
    res.json({
      success: true,
      data: result,
    });
    
  } catch (error) {
    console.error('Error validating booking:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to validate booking',
      message: error instanceof Error ? error.message : 'Unknown error',
    });
  }
};

// Get available nail services
export const getAvailableServices = async (req: Request, res: Response) => {
  try {
    const services: NailService[] = [
      {
        category: 'Basic Services',
        services: ['Manicure', 'Pedicure'],
      },
      {
        category: 'Advanced Services',
        services: ['Gel Manicure', 'Gel Pedicure', 'Acrylic Nails', 'Nail Extensions'],
      },
      {
        category: 'Specialty Services',
        services: ['Nail Art/Design', 'French Manicure', 'Dip Powder Nails'],
      },
    ];
    
    res.json({
      success: true,
      data: services,
    });
    
  } catch (error) {
    console.error('Error getting services:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to get services',
      message: error instanceof Error ? error.message : 'Unknown error',
    });
  }
};
