import { Router } from 'express';
import {
  getAllBookings,
  getBookingById,
  createBooking,
  updateBooking,
  cancelBooking,
  completeBooking,
  rateBooking,
  deleteBooking
} from '@/controllers/bookingsController';

const router = Router();

// Booking CRUD routes
router.get('/', getAllBookings);                    // GET /api/bookings - Read all
router.post('/', createBooking);                    // POST /api/bookings - Create
router.get('/:id', getBookingById);                 // GET /api/bookings/:id - Read one
router.put('/:id', updateBooking);                  // PUT /api/bookings/:id - Update
router.delete('/:id', deleteBooking);               // DELETE /api/bookings/:id - Hard delete

// Booking status management
router.patch('/:id/cancel', cancelBooking);         // PATCH /api/bookings/:id/cancel - Cancel booking
router.patch('/:id/complete', completeBooking);     // PATCH /api/bookings/:id/complete - Complete booking
router.patch('/:id/rate', rateBooking);             // PATCH /api/bookings/:id/rate - Add rating

export default router;
