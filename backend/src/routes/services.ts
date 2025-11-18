import { Router } from 'express';
import { body, query, param } from 'express-validator';
import { validateRequest } from '../middleware/validation';
import * as serviceController from '../controllers/serviceController';

const router = Router();

// Validation middleware
const createServiceValidation = [
  body('name').notEmpty().withMessage('Service name is required'),
  body('category').notEmpty().withMessage('Category is required'),
  body('duration_minutes').isInt({ min: 1 }).withMessage('Duration must be a positive integer'),
  body('price').isFloat({ min: 0 }).withMessage('Price must be a positive number'),
  body('description').notEmpty().withMessage('Description is required'),
  body('required_skill_level').isIn(['Junior', 'Senior', 'Expert', 'Master']).withMessage('Invalid skill level'),
  body('popularity_score').isInt({ min: 1, max: 10 }).withMessage('Popularity score must be between 1 and 10'),
  validateRequest
];

const updateServiceValidation = [
  body('name').optional().notEmpty().withMessage('Service name cannot be empty'),
  body('category').optional().notEmpty().withMessage('Category cannot be empty'),
  body('duration_minutes').optional().isInt({ min: 1 }).withMessage('Duration must be a positive integer'),
  body('price').optional().isFloat({ min: 0 }).withMessage('Price must be a positive number'),
  body('description').optional().notEmpty().withMessage('Description cannot be empty'),
  body('required_skill_level').optional().isIn(['Junior', 'Senior', 'Expert', 'Master']).withMessage('Invalid skill level'),
  body('popularity_score').optional().isInt({ min: 1, max: 10 }).withMessage('Popularity score must be between 1 and 10'),
  validateRequest
];

const serviceIdValidation = [
  param('id').notEmpty().withMessage('Service ID is required'),
  validateRequest
];

// Routes
router.get('/', serviceController.getAllServices);
router.get('/categories', serviceController.getServiceCategories);
router.get('/:id', serviceIdValidation, serviceController.getServiceById);
router.post('/', createServiceValidation, serviceController.createService);
router.put('/:id', serviceIdValidation, updateServiceValidation, serviceController.updateService);
router.delete('/:id', serviceIdValidation, serviceController.deleteService);

export default router;
