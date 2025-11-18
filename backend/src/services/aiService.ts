import axios from 'axios';
import { BookingResult, BookingValidation } from '../types/booking';

const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://localhost:8060';

// Process complete booking through AI service
export const processBooking = async (bookingRequest: string): Promise<BookingResult> => {
  try {
    const response = await axios.post(`${AI_SERVICE_URL}/process-booking`, {
      booking_request: bookingRequest,
    }, {
      timeout: 30000, // 30 seconds timeout
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    return response.data;
  } catch (error) {
    console.error('AI Service error:', error instanceof Error ? error.message : 'Unknown error');
    
    if (axios.isAxiosError(error) && error.code === 'ECONNREFUSED') {
      throw new Error('AI service is not available. Please ensure the Python service is running on port 8000.');
    }
    
    throw new Error(`AI service error: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
};

// Validate booking only (without full processing)
export const validateBookingOnly = async (bookingRequest: string): Promise<BookingValidation> => {
  try {
    const response = await axios.post(`${AI_SERVICE_URL}/validate-booking`, {
      booking_request: bookingRequest,
    }, {
      timeout: 15000, // 15 seconds timeout
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    return response.data;
  } catch (error) {
    console.error('AI Service validation error:', error instanceof Error ? error.message : 'Unknown error');
    
    if (axios.isAxiosError(error) && error.code === 'ECONNREFUSED') {
      throw new Error('AI service is not available. Please ensure the Python service is running on port 8000.');
    }
    
    throw new Error(`AI service validation error: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
};

// Health check for AI service
export const healthCheck = async (): Promise<{ status: string; error?: string }> => {
  try {
    const response = await axios.get(`${AI_SERVICE_URL}/health`, {
      timeout: 5000,
    });
    
    return response.data;
  } catch (error) {
    return {
      status: 'unhealthy',
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
};
