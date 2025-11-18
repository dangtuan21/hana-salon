import { Router } from 'express';
import { body, validationResult } from 'express-validator';
import * as bookingController from '../controllers/bookingController';

const router = Router();

// Validation middleware for booking requests
const validateBooking = [
  body('booking_request')
    .notEmpty()
    .withMessage('Booking request is required')
    .isLength({ min: 10, max: 500 })
    .withMessage('Booking request must be between 10 and 500 characters'),
  
  (req: any, res: any, next: any) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Validation failed',
        details: errors.array(),
      });
    }
    next();
  },
];

// Routes
router.post('/process', validateBooking, bookingController.processBooking);
router.get('/status/:bookingId', bookingController.getBookingStatus);
router.get('/services', bookingController.getAvailableServices);
router.post('/validate', validateBooking, bookingController.validateBooking);

export default router;
