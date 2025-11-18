import { Router } from 'express';
import {
  getAllTechnicians,
  getTechnicianById,
  createTechnician,
  updateTechnician,
  deleteTechnician,
  reactivateTechnician,
  getTechnicianAvailability
} from '@/controllers/techniciansController';

const router = Router();

// Technician CRUD routes
router.get('/', getAllTechnicians);                           // GET /api/technicians - Read all
router.post('/', createTechnician);                           // POST /api/technicians - Create
router.get('/:id', getTechnicianById);                        // GET /api/technicians/:id - Read one
router.put('/:id', updateTechnician);                         // PUT /api/technicians/:id - Update
router.delete('/:id', deleteTechnician);                      // DELETE /api/technicians/:id - Soft delete
router.patch('/:id/reactivate', reactivateTechnician);        // PATCH /api/technicians/:id/reactivate - Reactivate
router.get('/:id/availability', getTechnicianAvailability);   // GET /api/technicians/:id/availability - Get availability

export default router;
