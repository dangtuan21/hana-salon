import { Router } from 'express';
import {
  getAllServices,
  getServiceById,
  createService,
  updateService,
  deleteService
} from '@/controllers/servicesController';

const router = Router();

// Services CRUD routes
router.get('/', getAllServices);          // GET /api/services - Read all
router.post('/', createService);          // POST /api/services - Create
router.get('/:id', getServiceById);       // GET /api/services/:id - Read one
router.put('/:id', updateService);        // PUT /api/services/:id - Update
router.delete('/:id', deleteService);     // DELETE /api/services/:id - Delete

export default router;
