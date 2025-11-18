import { Router } from 'express';
import { body, param, query } from 'express-validator';
import { validateRequest } from '../middleware/validation';
import * as customerController from '../controllers/customerController';

const router = Router();

// Validation middleware
const createCustomerValidation = [
  body('name').notEmpty().withMessage('Customer name is required'),
  body('phone').isMobilePhone('any').withMessage('Valid phone number is required'),
  body('email').optional().isEmail().withMessage('Valid email is required'),
  validateRequest
];

const updateCustomerValidation = [
  body('name').optional().notEmpty().withMessage('Customer name cannot be empty'),
  body('phone').optional().isMobilePhone('any').withMessage('Valid phone number is required'),
  body('email').optional().isEmail().withMessage('Valid email is required'),
  validateRequest
];

const customerIdValidation = [
  param('id').notEmpty().withMessage('Customer ID is required'),
  validateRequest
];

const phoneValidation = [
  param('phone').isMobilePhone('any').withMessage('Valid phone number is required'),
  validateRequest
];

const searchValidation = [
  query('q').notEmpty().withMessage('Search query is required'),
  validateRequest
];

const addBookingValidation = [
  body('booking_id').notEmpty().withMessage('Booking ID is required'),
  validateRequest
];

// Routes
router.get('/', customerController.getAllCustomers);
router.get('/search', searchValidation, customerController.searchCustomers);
router.get('/phone/:phone', phoneValidation, customerController.getCustomerByPhone);
router.get('/:id', customerIdValidation, customerController.getCustomerById);
router.post('/', createCustomerValidation, customerController.createCustomer);
router.put('/:id', customerIdValidation, updateCustomerValidation, customerController.updateCustomer);
router.put('/:id/bookings', customerIdValidation, addBookingValidation, customerController.addBookingToCustomer);
router.delete('/:id', customerIdValidation, customerController.deleteCustomer);

export default router;
