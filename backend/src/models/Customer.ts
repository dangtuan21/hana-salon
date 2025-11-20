import mongoose, { Document, Schema } from 'mongoose';

// Customer interface
export interface ICustomer extends Document {
  _id: mongoose.Types.ObjectId;
  firstName: string;
  lastName?: string;  // Make optional
  email?: string;     // Make optional
  phone: string;
  dateOfBirth?: Date;
  gender?: 'male' | 'female' | 'other' | 'prefer_not_to_say';
  address?: {
    street?: string;
    city?: string;
    state?: string;
    zipCode?: string;
    country?: string;
  };
  preferences?: {
    preferredTechnician?: mongoose.Types.ObjectId;
    allergies?: string[];
    notes?: string;
  };
  loyaltyPoints?: number;
  totalVisits?: number;
  totalSpent?: number;
  isActive: boolean;
  created_at: Date;
  updated_at: Date;
}

// Customer schema
const CustomerSchema = new Schema<ICustomer>({
  firstName: {
    type: String,
    required: [true, 'First name is required'],
    trim: true,
    maxlength: [50, 'First name cannot exceed 50 characters']
  },
  lastName: {
    type: String,
    required: false,  // Make lastName optional
    trim: true,
    maxlength: [50, 'Last name cannot exceed 50 characters']
  },
  email: {
    type: String,
    required: false,  // Make email optional
    unique: true,
    sparse: true,     // Allow multiple empty values for unique field
    trim: true,
    lowercase: true,
    match: [/^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/, 'Please enter a valid email']
  },
  phone: {
    type: String,
    required: [true, 'Phone number is required'],
    trim: true,
    match: [/^(\d{3}-\d{3}-\d{4}|\d+|\+\d+|[\d\s\-\(\)]+)$/, 'Please enter a valid phone number']
  },
  dateOfBirth: {
    type: Date,
    validate: {
      validator: function(date: Date) {
        return !date || date <= new Date();
      },
      message: 'Date of birth cannot be in the future'
    }
  },
  gender: {
    type: String,
    enum: ['male', 'female', 'other', 'prefer_not_to_say'],
    lowercase: true
  },
  address: {
    street: {
      type: String,
      trim: true,
      maxlength: [100, 'Street address cannot exceed 100 characters']
    },
    city: {
      type: String,
      trim: true,
      maxlength: [50, 'City cannot exceed 50 characters']
    },
    state: {
      type: String,
      trim: true,
      maxlength: [50, 'State cannot exceed 50 characters']
    },
    zipCode: {
      type: String,
      trim: true,
      maxlength: [20, 'Zip code cannot exceed 20 characters']
    },
    country: {
      type: String,
      trim: true,
      maxlength: [50, 'Country cannot exceed 50 characters'],
      default: 'United States'
    }
  },
  preferences: {
    preferredTechnician: {
      type: Schema.Types.ObjectId,
      ref: 'Technician'
    },
    allergies: [{
      type: String,
      trim: true
    }],
    notes: {
      type: String,
      trim: true,
      maxlength: [500, 'Notes cannot exceed 500 characters']
    }
  },
  loyaltyPoints: {
    type: Number,
    default: 0,
    min: [0, 'Loyalty points cannot be negative']
  },
  totalVisits: {
    type: Number,
    default: 0,
    min: [0, 'Total visits cannot be negative']
  },
  totalSpent: {
    type: Number,
    default: 0,
    min: [0, 'Total spent cannot be negative']
  },
  isActive: {
    type: Boolean,
    default: true
  },
  created_at: {
    type: Date,
    default: Date.now
  },
  updated_at: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' }
});

// Indexes for better query performance
CustomerSchema.index({ email: 1 }, { unique: true, sparse: true });  // Sparse index for optional email
CustomerSchema.index({ phone: 1 });
CustomerSchema.index({ firstName: 1, lastName: 1 });
CustomerSchema.index({ isActive: 1 });
CustomerSchema.index({ created_at: -1 });

// Virtual for full name
CustomerSchema.virtual('fullName').get(function() {
  return this.lastName ? `${this.firstName} ${this.lastName}` : this.firstName;
});

// Pre-save middleware to format phone and update timestamp
CustomerSchema.pre('save', function(next) {
  // Format phone number consistently
  if (this.phone) {
    const digits = this.phone.replace(/\D/g, ''); // Remove all non-digits
    if (digits.length === 10) {
      this.phone = `${digits.slice(0, 3)}-${digits.slice(3, 6)}-${digits.slice(6)}`;
    } else if (digits.length < 10) {
      // For phone numbers less than 10 digits, preserve original format (trim only)
      this.phone = this.phone.trim();
    } else {
      // For phone numbers longer than 10 digits, keep as digits only
      this.phone = digits;
    }
  }
  
  this.updated_at = new Date();
  next();
});

// Export the model
export const Customer = mongoose.model<ICustomer>('Customer', CustomerSchema);
export default Customer;
