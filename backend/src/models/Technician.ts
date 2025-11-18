import mongoose, { Document, Schema } from 'mongoose';

// Technician interface
export interface ITechnician extends Document {
  _id: mongoose.Types.ObjectId;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  employeeId: string;
  specialties: string[];
  skillLevel: 'Junior' | 'Senior' | 'Expert' | 'Master';
  certifications?: string[];
  yearsOfExperience: number;
  hourlyRate: number;
  availability: {
    monday: { start: string; end: string; available: boolean };
    tuesday: { start: string; end: string; available: boolean };
    wednesday: { start: string; end: string; available: boolean };
    thursday: { start: string; end: string; available: boolean };
    friday: { start: string; end: string; available: boolean };
    saturday: { start: string; end: string; available: boolean };
    sunday: { start: string; end: string; available: boolean };
  };
  rating: number;
  totalBookings: number;
  completedBookings: number;
  isActive: boolean;
  hireDate: Date;
  created_at: Date;
  updated_at: Date;
}

// Technician schema
const TechnicianSchema = new Schema<ITechnician>({
  firstName: {
    type: String,
    required: [true, 'First name is required'],
    trim: true,
    maxlength: [50, 'First name cannot exceed 50 characters']
  },
  lastName: {
    type: String,
    required: [true, 'Last name is required'],
    trim: true,
    maxlength: [50, 'Last name cannot exceed 50 characters']
  },
  email: {
    type: String,
    required: [true, 'Email is required'],
    unique: true,
    trim: true,
    lowercase: true,
    match: [/^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/, 'Please enter a valid email']
  },
  phone: {
    type: String,
    required: [true, 'Phone number is required'],
    trim: true,
    match: [/^[\+]?[1-9][\d]{0,15}$/, 'Please enter a valid phone number']
  },
  employeeId: {
    type: String,
    required: [true, 'Employee ID is required'],
    unique: true,
    trim: true,
    uppercase: true
  },
  specialties: [{
    type: String,
    required: true,
    trim: true,
    enum: [
      'Manicure',
      'Pedicure', 
      'Nail Art',
      'Gel Polish',
      'Acrylic Nails',
      'Dip Powder',
      'Nail Extensions',
      'Nail Repair',
      'Cuticle Care',
      'Hand Massage',
      'Foot Massage'
    ]
  }],
  skillLevel: {
    type: String,
    required: [true, 'Skill level is required'],
    enum: ['Junior', 'Senior', 'Expert', 'Master']
  },
  certifications: [{
    type: String,
    trim: true
  }],
  yearsOfExperience: {
    type: Number,
    required: [true, 'Years of experience is required'],
    min: [0, 'Years of experience cannot be negative'],
    max: [50, 'Years of experience cannot exceed 50']
  },
  hourlyRate: {
    type: Number,
    required: [true, 'Hourly rate is required'],
    min: [10, 'Hourly rate must be at least $10'],
    max: [200, 'Hourly rate cannot exceed $200']
  },
  availability: {
    monday: {
      start: { type: String, default: '09:00' },
      end: { type: String, default: '17:00' },
      available: { type: Boolean, default: true }
    },
    tuesday: {
      start: { type: String, default: '09:00' },
      end: { type: String, default: '17:00' },
      available: { type: Boolean, default: true }
    },
    wednesday: {
      start: { type: String, default: '09:00' },
      end: { type: String, default: '17:00' },
      available: { type: Boolean, default: true }
    },
    thursday: {
      start: { type: String, default: '09:00' },
      end: { type: String, default: '17:00' },
      available: { type: Boolean, default: true }
    },
    friday: {
      start: { type: String, default: '09:00' },
      end: { type: String, default: '17:00' },
      available: { type: Boolean, default: true }
    },
    saturday: {
      start: { type: String, default: '10:00' },
      end: { type: String, default: '16:00' },
      available: { type: Boolean, default: true }
    },
    sunday: {
      start: { type: String, default: '10:00' },
      end: { type: String, default: '16:00' },
      available: { type: Boolean, default: false }
    }
  },
  rating: {
    type: Number,
    default: 5.0,
    min: [1, 'Rating must be at least 1'],
    max: [5, 'Rating cannot exceed 5']
  },
  totalBookings: {
    type: Number,
    default: 0,
    min: [0, 'Total bookings cannot be negative']
  },
  completedBookings: {
    type: Number,
    default: 0,
    min: [0, 'Completed bookings cannot be negative']
  },
  isActive: {
    type: Boolean,
    default: true
  },
  hireDate: {
    type: Date,
    required: [true, 'Hire date is required'],
    validate: {
      validator: function(date: Date) {
        return date <= new Date();
      },
      message: 'Hire date cannot be in the future'
    }
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
TechnicianSchema.index({ email: 1 }, { unique: true });
TechnicianSchema.index({ employeeId: 1 }, { unique: true });
TechnicianSchema.index({ specialties: 1 });
TechnicianSchema.index({ skillLevel: 1 });
TechnicianSchema.index({ isActive: 1 });
TechnicianSchema.index({ rating: -1 });

// Virtual for full name
TechnicianSchema.virtual('fullName').get(function() {
  return `${this.firstName} ${this.lastName}`;
});

// Virtual for completion rate
TechnicianSchema.virtual('completionRate').get(function() {
  if (this.totalBookings === 0) return 0;
  return Math.round((this.completedBookings / this.totalBookings) * 100);
});

// Pre-save middleware to update the updated_at field
TechnicianSchema.pre('save', function(next) {
  this.updated_at = new Date();
  next();
});

// Export the model
export const Technician = mongoose.model<ITechnician>('Technician', TechnicianSchema);
export default Technician;
