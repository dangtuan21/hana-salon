import { Request, Response } from 'express';
import asyncHandler from 'express-async-handler';
import { Customer } from '@/models/Customer';
import { ResponseUtil } from '@/utils/response';
import logger from '@/utils/logger';

// Get all customers
export const getAllCustomers = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  try {
    const page = parseInt(req.query.page as string) || 1;
    const limit = parseInt(req.query.limit as string) || 10;
    const skip = (page - 1) * limit;
    
    const filter: any = {};
    
    // Filter by active status
    if (req.query.isActive !== undefined) {
      filter.isActive = req.query.isActive === 'true';
    }
    
    // Search by name or email
    if (req.query.search) {
      const searchRegex = new RegExp(req.query.search as string, 'i');
      filter.$or = [
        { firstName: searchRegex },
        { lastName: searchRegex },
        { email: searchRegex }
      ];
    }

    const customers = await Customer.find(filter)
      .sort({ created_at: -1 })
      .skip(skip)
      .limit(limit)
      .select('-__v');

    const total = await Customer.countDocuments(filter);
    
    logger.info(`Retrieved ${customers.length} customers (page ${page})`);
    
    ResponseUtil.success(res, {
      customers,
      pagination: {
        page,
        limit,
        total,
        pages: Math.ceil(total / limit)
      }
    }, 'Customers retrieved successfully');
    
  } catch (error: any) {
    logger.error('Error fetching customers:', error);
    ResponseUtil.internalError(res, 'Failed to fetch customers');
  }
});

// Get customer by ID
export const getCustomerById = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    
    const customer = await Customer.findById(id)
      .populate('preferences.preferredTechnician', 'firstName lastName specialties')
      .select('-__v');
    
    if (!customer) {
      ResponseUtil.notFound(res, 'Customer not found');
      return;
    }
    
    logger.info(`Retrieved customer: ${customer.firstName} ${customer.lastName || ''} (${customer.phone})`);
    
    ResponseUtil.success(res, customer, 'Customer retrieved successfully');
    
  } catch (error: any) {
    logger.error('Error fetching customer:', error);
    
    if (error.name === 'CastError') {
      ResponseUtil.badRequest(res, 'Invalid customer ID format');
    } else {
      ResponseUtil.internalError(res, 'Failed to fetch customer');
    }
  }
});

// Create new customer
export const createCustomer = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  try {
    const {
      firstName,
      lastName,
      email,
      phone,
      dateOfBirth,
      gender,
      address,
      preferences
    } = req.body;

    // Basic validation - only firstName and phone are required
    if (!firstName || !phone) {
      ResponseUtil.badRequest(res, 'Missing required fields: firstName, phone');
      return;
    }

    const customerData = {
      firstName: firstName.trim(),
      lastName: lastName ? lastName.trim() : undefined,  // Optional
      email: email ? email.trim().toLowerCase() : undefined,  // Optional
      phone: phone.trim(),
      dateOfBirth: dateOfBirth ? new Date(dateOfBirth) : undefined,
      gender: gender?.toLowerCase(),
      address,
      preferences
    };

    const newCustomer = await Customer.create(customerData);
    
    logger.info(`Created new customer: ${newCustomer.firstName} ${newCustomer.lastName || ''} (${newCustomer.phone})`);
    
    ResponseUtil.success(res, newCustomer, 'Customer created successfully', 201);
    
  } catch (error: any) {
    logger.error('Error creating customer:', error);
    
    if (error.name === 'ValidationError') {
      ResponseUtil.badRequest(res, `Validation error: ${error.message}`);
    } else if (error.code === 11000) {
      ResponseUtil.badRequest(res, 'Email already exists');
    } else {
      ResponseUtil.internalError(res, 'Failed to create customer');
    }
  }
});

// Update customer
export const updateCustomer = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    const updateData = { ...req.body };

    // Remove fields that shouldn't be updated directly
    delete updateData._id;
    delete updateData.created_at;
    delete updateData.totalVisits;
    delete updateData.totalSpent;
    delete updateData.loyaltyPoints;
    
    // Update the updated_at field
    updateData.updated_at = new Date();

    // Trim string fields if they exist
    if (updateData.firstName) updateData.firstName = updateData.firstName.trim();
    if (updateData.lastName) updateData.lastName = updateData.lastName.trim();
    if (updateData.email) updateData.email = updateData.email.trim().toLowerCase();
    if (updateData.phone) updateData.phone = updateData.phone.trim();
    if (updateData.gender) updateData.gender = updateData.gender.toLowerCase();

    // Handle date of birth
    if (updateData.dateOfBirth) {
      updateData.dateOfBirth = new Date(updateData.dateOfBirth);
    }

    const updatedCustomer = await Customer.findByIdAndUpdate(
      id,
      updateData,
      { 
        new: true, // Return the updated document
        runValidators: true // Run schema validation
      }
    ).select('-__v');

    if (!updatedCustomer) {
      ResponseUtil.notFound(res, 'Customer not found');
      return;
    }

    logger.info(`Updated customer: ${updatedCustomer.email}`);
    
    ResponseUtil.success(res, updatedCustomer, 'Customer updated successfully');
    
  } catch (error: any) {
    logger.error('Error updating customer:', error);
    
    if (error.name === 'ValidationError') {
      ResponseUtil.badRequest(res, `Validation error: ${error.message}`);
    } else if (error.name === 'CastError') {
      ResponseUtil.badRequest(res, 'Invalid customer ID format');
    } else if (error.code === 11000) {
      ResponseUtil.badRequest(res, 'Email already exists');
    } else {
      ResponseUtil.internalError(res, 'Failed to update customer');
    }
  }
});

// Delete customer (soft delete by setting isActive to false)
export const deleteCustomer = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    
    const deletedCustomer = await Customer.findByIdAndUpdate(
      id,
      { isActive: false, updated_at: new Date() },
      { new: true }
    ).select('_id firstName lastName email');
    
    if (!deletedCustomer) {
      ResponseUtil.notFound(res, 'Customer not found');
      return;
    }
    
    logger.info(`Deactivated customer: ${deletedCustomer.email}`);
    
    ResponseUtil.success(res, {
      id: deletedCustomer._id,
      name: `${deletedCustomer.firstName} ${deletedCustomer.lastName}`,
      email: deletedCustomer.email
    }, 'Customer deactivated successfully');
    
  } catch (error: any) {
    logger.error('Error deleting customer:', error);
    
    if (error.name === 'CastError') {
      ResponseUtil.badRequest(res, 'Invalid customer ID format');
    } else {
      ResponseUtil.internalError(res, 'Failed to delete customer');
    }
  }
});

// Reactivate customer
export const reactivateCustomer = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  try {
    const { id } = req.params;
    
    const reactivatedCustomer = await Customer.findByIdAndUpdate(
      id,
      { isActive: true, updated_at: new Date() },
      { new: true }
    ).select('_id firstName lastName email isActive');
    
    if (!reactivatedCustomer) {
      ResponseUtil.notFound(res, 'Customer not found');
      return;
    }
    
    logger.info(`Reactivated customer: ${reactivatedCustomer.email}`);
    
    ResponseUtil.success(res, reactivatedCustomer, 'Customer reactivated successfully');
    
  } catch (error: any) {
    logger.error('Error reactivating customer:', error);
    
    if (error.name === 'CastError') {
      ResponseUtil.badRequest(res, 'Invalid customer ID format');
    } else {
      ResponseUtil.internalError(res, 'Failed to reactivate customer');
    }
  }
});

// Get customer by phone number (for AI service)
export const getCustomerByPhone = asyncHandler(async (req: Request, res: Response): Promise<void> => {
  try {
    const { phone } = req.params;
    
    if (!phone) {
      ResponseUtil.badRequest(res, 'Phone number is required');
      return;
    }
    
    // Clean phone number (remove spaces, dashes, etc.)
    const cleanPhone = phone.replace(/[\s\-\(\)]/g, '');
    
    const customer = await Customer.findOne({
      phone: { $regex: new RegExp(cleanPhone, 'i') }
    }).select('_id firstName lastName email phone isActive preferences');
    
    if (!customer) {
      ResponseUtil.notFound(res, `Customer with phone "${phone}" not found`);
      return;
    }
    
    logger.info(`Retrieved customer by phone: ${customer.firstName} ${customer.lastName}`);
    
    ResponseUtil.success(res, customer, 'Customer retrieved successfully');
    
  } catch (error) {
    logger.error('Error fetching customer by phone:', error);
    ResponseUtil.internalError(res, 'Failed to fetch customer');
  }
});
