import { Request, Response } from 'express';
import { Customer, ApiResponse, PaginationParams } from '../types/salon';

// In-memory storage for demo - replace with actual database connection
let customers: Customer[] = [];

export const getAllCustomers = async (req: Request<{}, ApiResponse<Customer[]>, {}, PaginationParams>, res: Response) => {
  try {
    const { page = 1, limit = 10, sort = 'created_at', order = 'desc' } = req.query;
    
    let sortedCustomers = [...customers];
    
    // Apply sorting
    sortedCustomers.sort((a, b) => {
      const aValue = a[sort as keyof Customer] as string;
      const bValue = b[sort as keyof Customer] as string;
      
      if (order === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });
    
    // Pagination
    const startIndex = (Number(page) - 1) * Number(limit);
    const endIndex = startIndex + Number(limit);
    const paginatedCustomers = sortedCustomers.slice(startIndex, endIndex);
    
    res.json({
      success: true,
      data: paginatedCustomers,
      total: customers.length
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to fetch customers',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
};

export const getCustomerById = async (req: Request<{ id: string }>, res: Response) => {
  try {
    const { id } = req.params;
    const customer = customers.find(c => c._id === id);
    
    if (!customer) {
      return res.status(404).json({
        success: false,
        error: 'Customer not found'
      });
    }
    
    res.json({
      success: true,
      data: customer
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to fetch customer',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
};

export const getCustomerByPhone = async (req: Request<{ phone: string }>, res: Response) => {
  try {
    const { phone } = req.params;
    const customer = customers.find(c => c.phone === phone);
    
    if (!customer) {
      return res.status(404).json({
        success: false,
        error: 'Customer not found'
      });
    }
    
    res.json({
      success: true,
      data: customer
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to fetch customer',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
};

export const createCustomer = async (req: Request<{}, ApiResponse<Customer>, Customer>, res: Response) => {
  try {
    const customerData = req.body;
    
    // Check if customer with this phone already exists
    const existingCustomer = customers.find(c => c.phone === customerData.phone);
    if (existingCustomer) {
      return res.status(409).json({
        success: false,
        error: 'Customer with this phone number already exists'
      });
    }
    
    const newCustomer: Customer = {
      ...customerData,
      _id: `customer_${Date.now()}`,
      booking_history: [],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    
    customers.push(newCustomer);
    
    res.status(201).json({
      success: true,
      data: newCustomer,
      message: 'Customer created successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to create customer',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
};

export const updateCustomer = async (req: Request<{ id: string }, ApiResponse<Customer>, Partial<Customer>>, res: Response) => {
  try {
    const { id } = req.params;
    const updates = req.body;
    
    const customerIndex = customers.findIndex(c => c._id === id);
    
    if (customerIndex === -1) {
      return res.status(404).json({
        success: false,
        error: 'Customer not found'
      });
    }
    
    // Check if phone number is being updated and if it conflicts
    if (updates.phone && updates.phone !== customers[customerIndex].phone) {
      const existingCustomer = customers.find(c => c.phone === updates.phone && c._id !== id);
      if (existingCustomer) {
        return res.status(409).json({
          success: false,
          error: 'Another customer with this phone number already exists'
        });
      }
    }
    
    customers[customerIndex] = {
      ...customers[customerIndex],
      ...updates,
      updated_at: new Date().toISOString()
    };
    
    res.json({
      success: true,
      data: customers[customerIndex],
      message: 'Customer updated successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to update customer',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
};

export const deleteCustomer = async (req: Request<{ id: string }>, res: Response) => {
  try {
    const { id } = req.params;
    const customerIndex = customers.findIndex(c => c._id === id);
    
    if (customerIndex === -1) {
      return res.status(404).json({
        success: false,
        error: 'Customer not found'
      });
    }
    
    customers.splice(customerIndex, 1);
    
    res.json({
      success: true,
      message: 'Customer deleted successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to delete customer',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
};

export const searchCustomers = async (req: Request<{}, ApiResponse<Customer[]>, {}, { q: string } & PaginationParams>, res: Response) => {
  try {
    const { q, page = 1, limit = 10 } = req.query;
    
    if (!q) {
      return res.status(400).json({
        success: false,
        error: 'Search query is required'
      });
    }
    
    const searchTerm = q.toLowerCase();
    const filteredCustomers = customers.filter(c => 
      c.name.toLowerCase().includes(searchTerm) ||
      c.phone.includes(searchTerm) ||
      (c.email && c.email.toLowerCase().includes(searchTerm))
    );
    
    // Pagination
    const startIndex = (Number(page) - 1) * Number(limit);
    const endIndex = startIndex + Number(limit);
    const paginatedCustomers = filteredCustomers.slice(startIndex, endIndex);
    
    res.json({
      success: true,
      data: paginatedCustomers,
      total: filteredCustomers.length
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to search customers',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
};

export const addBookingToCustomer = async (req: Request<{ id: string }, ApiResponse, { booking_id: string }>, res: Response) => {
  try {
    const { id } = req.params;
    const { booking_id } = req.body;
    
    const customerIndex = customers.findIndex(c => c._id === id);
    
    if (customerIndex === -1) {
      return res.status(404).json({
        success: false,
        error: 'Customer not found'
      });
    }
    
    if (!customers[customerIndex].booking_history) {
      customers[customerIndex].booking_history = [];
    }
    
    customers[customerIndex].booking_history!.push(booking_id);
    customers[customerIndex].updated_at = new Date().toISOString();
    
    res.json({
      success: true,
      message: 'Booking added to customer history'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to add booking to customer',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
};
