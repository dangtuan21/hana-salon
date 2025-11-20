import { Router } from 'express';
import {
  getAllTechnicians,
  getTechnicianById,
  createTechnician,
  updateTechnician,
  deleteTechnician,
  reactivateTechnician,
  getTechnicianAvailability,
  getAvailableTechnicians,
  getTechniciansForService,
  checkTechnicianAvailability,
  batchCheckTechnicianAvailability
} from '@/controllers/techniciansController';

const router = Router();

// Technician CRUD routes
router.get('/', getAllTechnicians);                           // GET /api/technicians - Read all
router.get('/available', getAvailableTechnicians);            // GET /api/technicians/available - Get active technicians (for AI)
router.post('/', createTechnician);                           // POST /api/technicians - Create
router.get('/service/:serviceId', getTechniciansForService);  // GET /api/technicians/service/:serviceId - Get for service (for AI)
router.post('/batch-check-availability', batchCheckTechnicianAvailability); // POST /api/technicians/batch-check-availability - Batch check availability (for AI)
router.post('/:id/check-availability', checkTechnicianAvailability); // POST /api/technicians/:id/check-availability - Check availability (for AI)
router.get('/:id/availability', getTechnicianAvailability);   // GET /api/technicians/:id/availability - Get availability
router.get('/:id', getTechnicianById);                        // GET /api/technicians/:id - Read one
router.put('/:id', updateTechnician);                         // PUT /api/technicians/:id - Update
router.delete('/:id', deleteTechnician);                      // DELETE /api/technicians/:id - Soft delete
router.patch('/:id/reactivate', reactivateTechnician);        // PATCH /api/technicians/:id/reactivate - Reactivate

export default router;
