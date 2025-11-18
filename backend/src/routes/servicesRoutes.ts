import { Router } from 'express';
import {
  getAllServices,
  getServiceById
} from '@/controllers/servicesController';

const router = Router();

// Services routes
router.get('/', getAllServices);
router.get('/:id', getServiceById);

export default router;
