import { Router } from 'express';
import { body, param } from 'express-validator';
import { validateRequest } from '../middleware/validation';
import * as technicianController from '../controllers/technicianController';

const router = Router();

// Validation middleware
const createTechnicianValidation = [
  body('name').notEmpty().withMessage('Technician name is required'),
  body('skill_level').isIn(['Junior', 'Senior', 'Expert', 'Master']).withMessage('Invalid skill level'),
  body('specialties').isArray().withMessage('Specialties must be an array'),
  body('rating').isFloat({ min: 0, max: 5 }).withMessage('Rating must be between 0 and 5'),
  body('years_experience').isInt({ min: 0 }).withMessage('Years of experience must be a non-negative integer'),
  body('hourly_rate').isFloat({ min: 0 }).withMessage('Hourly rate must be a positive number'),
  body('available_days').isArray().withMessage('Available days must be an array'),
  body('work_hours.start').matches(/^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/).withMessage('Invalid start time format (HH:MM)'),
  body('work_hours.end').matches(/^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/).withMessage('Invalid end time format (HH:MM)'),
  body('is_available').isBoolean().withMessage('Availability must be a boolean'),
  body('bio').notEmpty().withMessage('Bio is required'),
  validateRequest
];

const updateTechnicianValidation = [
  body('name').optional().notEmpty().withMessage('Technician name cannot be empty'),
  body('skill_level').optional().isIn(['Junior', 'Senior', 'Expert', 'Master']).withMessage('Invalid skill level'),
  body('specialties').optional().isArray().withMessage('Specialties must be an array'),
  body('rating').optional().isFloat({ min: 0, max: 5 }).withMessage('Rating must be between 0 and 5'),
  body('years_experience').optional().isInt({ min: 0 }).withMessage('Years of experience must be a non-negative integer'),
  body('hourly_rate').optional().isFloat({ min: 0 }).withMessage('Hourly rate must be a positive number'),
  body('available_days').optional().isArray().withMessage('Available days must be an array'),
  body('work_hours.start').optional().matches(/^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/).withMessage('Invalid start time format (HH:MM)'),
  body('work_hours.end').optional().matches(/^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/).withMessage('Invalid end time format (HH:MM)'),
  body('is_available').optional().isBoolean().withMessage('Availability must be a boolean'),
  body('bio').optional().notEmpty().withMessage('Bio cannot be empty'),
  validateRequest
];

const technicianIdValidation = [
  param('id').notEmpty().withMessage('Technician ID is required'),
  validateRequest
];

const serviceIdValidation = [
  param('serviceId').notEmpty().withMessage('Service ID is required'),
  validateRequest
];

const availabilityValidation = [
  body('is_available').isBoolean().withMessage('Availability must be a boolean'),
  validateRequest
];

// Routes
router.get('/', technicianController.getAllTechnicians);
router.get('/:id', technicianIdValidation, technicianController.getTechnicianById);
router.get('/service/:serviceId', serviceIdValidation, technicianController.getTechniciansByService);
router.post('/', createTechnicianValidation, technicianController.createTechnician);
router.put('/:id', technicianIdValidation, updateTechnicianValidation, technicianController.updateTechnician);
router.put('/:id/availability', technicianIdValidation, availabilityValidation, technicianController.updateTechnicianAvailability);
router.delete('/:id', technicianIdValidation, technicianController.deleteTechnician);

export default router;
