import { Router } from 'express';
import {
  getAllCustomers,
  getCustomerById,
  createCustomer,
  updateCustomer,
  deleteCustomer,
  reactivateCustomer
} from '@/controllers/customersController';

const router = Router();

// Customer CRUD routes
router.get('/', getAllCustomers);                    // GET /api/customers - Read all
router.post('/', createCustomer);                    // POST /api/customers - Create
router.get('/:id', getCustomerById);                 // GET /api/customers/:id - Read one
router.put('/:id', updateCustomer);                  // PUT /api/customers/:id - Update
router.delete('/:id', deleteCustomer);               // DELETE /api/customers/:id - Soft delete
router.patch('/:id/reactivate', reactivateCustomer); // PATCH /api/customers/:id/reactivate - Reactivate

export default router;
