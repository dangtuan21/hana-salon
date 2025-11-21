import mongoose, { Document, Schema } from 'mongoose';

// Service-Technician pair interface
export interface IServiceTechnicianPair {
  serviceId: mongoose.Types.ObjectId;
  technicianId: mongoose.Types.ObjectId;
  duration: number; // Duration for this specific service
  price: number; // Price for this specific service
  status?: 'initial' | 'in_progress' | 'completed';
  notes?: string; // Service-specific notes
}

// Booking interface
export interface IBooking extends Document {
  _id: mongoose.Types.ObjectId;
  customerId: mongoose.Types.ObjectId;
  services: IServiceTechnicianPair[]; // Array of service-technician pairs
  appointmentDate: Date;
  startTime: string;
  endTime: string;
  status: 'initial' | 'confirmed' | 'in_progress' | 'completed' | 'cancelled' | 'no_show';
  totalDuration: number; // Sum of all service durations
  totalPrice: number; // Sum of all service prices
  paymentStatus: 'pending' | 'paid' | 'refunded' | 'failed';
  paymentMethod?: 'cash' | 'card' | 'online' | 'gift_card';
  notes?: string; // General booking notes
  customerNotes?: string;
  cancellationReason?: string;
  confirmationSent: boolean;
  calendarEventId?: string; // Google Calendar event ID
  calendarSyncStatus: 'pending' | 'synced' | 'failed' | 'disabled';
  calendarLastSyncAt?: Date;
  rating?: {
    score: number;
    comment?: string;
    ratedAt: Date;
  };
  created_at: Date;
  updated_at: Date;
}

// Service-Technician pair schema
const ServiceTechnicianPairSchema = new Schema<IServiceTechnicianPair>({
  serviceId: {
    type: Schema.Types.ObjectId,
    ref: 'Service',
    required: [true, 'Service ID is required']
  },
  technicianId: {
    type: Schema.Types.ObjectId,
    ref: 'Technician',
    required: [true, 'Technician ID is required']
  },
  duration: {
    type: Number,
    required: [true, 'Service duration is required'],
    min: [1, 'Duration must be at least 1 minute']
  },
  price: {
    type: Number,
    required: [true, 'Service price is required'],
    min: [0, 'Price cannot be negative']
  },
  status: {
    type: String,
    enum: ['initial', 'in_progress', 'completed'],
    default: 'initial'
  },
  notes: {
    type: String,
    maxlength: [500, 'Service notes cannot exceed 500 characters']
  }
}, { _id: false }); // Don't create separate _id for subdocuments

// Booking schema
const BookingSchema = new Schema<IBooking>({
  customerId: {
    type: Schema.Types.ObjectId,
    ref: 'Customer',
    required: [true, 'Customer ID is required']
  },
  services: {
    type: [ServiceTechnicianPairSchema],
    required: [true, 'At least one service is required'],
    validate: {
      validator: function(services: IServiceTechnicianPair[]) {
        return services.length > 0;
      },
      message: 'At least one service must be provided'
    }
  },
  appointmentDate: {
    type: Date,
    required: [true, 'Appointment date is required'],
    validate: {
      validator: function(date: Date) {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        return date >= today;
      },
      message: 'Appointment date cannot be in the past'
    }
  },
  startTime: {
    type: String,
    required: [true, 'Start time is required'],
    match: [/^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/, 'Start time must be in HH:MM format']
  },
  endTime: {
    type: String,
    required: [true, 'End time is required'],
    match: [/^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/, 'End time must be in HH:MM format']
  },
  status: {
    type: String,
    required: [true, 'Status is required'],
    enum: ['initial', 'confirmed', 'in_progress', 'completed', 'cancelled', 'no_show'],
    default: 'initial'
  },
  totalDuration: {
    type: Number,
    required: [true, 'Total duration is required'],
    min: [15, 'Total duration must be at least 15 minutes'],
    max: [480, 'Total duration cannot exceed 8 hours']
  },
  totalPrice: {
    type: Number,
    required: [true, 'Total price is required'],
    min: [0, 'Total price cannot be negative']
  },
  paymentStatus: {
    type: String,
    required: [true, 'Payment status is required'],
    enum: ['pending', 'paid', 'refunded', 'failed'],
    default: 'pending'
  },
  paymentMethod: {
    type: String,
    enum: ['cash', 'card', 'online', 'gift_card']
  },
  notes: {
    type: String,
    trim: true,
    maxlength: [500, 'Notes cannot exceed 500 characters']
  },
  customerNotes: {
    type: String,
    trim: true,
    maxlength: [300, 'Customer notes cannot exceed 300 characters']
  },
  cancellationReason: {
    type: String,
    trim: true,
    maxlength: [200, 'Cancellation reason cannot exceed 200 characters']
  },
  confirmationSent: {
    type: Boolean,
    default: false
  },
  calendarEventId: {
    type: String,
    trim: true
  },
  calendarSyncStatus: {
    type: String,
    enum: ['pending', 'synced', 'failed', 'disabled'],
    default: 'pending'
  },
  calendarLastSyncAt: {
    type: Date
  },
  rating: {
    score: {
      type: Number,
      min: [1, 'Rating must be at least 1'],
      max: [5, 'Rating cannot exceed 5']
    },
    comment: {
      type: String,
      trim: true,
      maxlength: [300, 'Rating comment cannot exceed 300 characters']
    },
    ratedAt: {
      type: Date,
      default: Date.now
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
BookingSchema.index({ customerId: 1 });
BookingSchema.index({ 'services.technicianId': 1 }); // Index for technician queries
BookingSchema.index({ 'services.serviceId': 1 }); // Index for service queries
BookingSchema.index({ appointmentDate: 1 });
BookingSchema.index({ status: 1 });
BookingSchema.index({ paymentStatus: 1 });
BookingSchema.index({ appointmentDate: 1, 'services.technicianId': 1 }); // Compound index for scheduling
BookingSchema.index({ created_at: -1 });

// Virtual for appointment datetime
BookingSchema.virtual('appointmentDateTime').get(function() {
  const date = new Date(this.appointmentDate);
  const [hours, minutes] = this.startTime.split(':');
  date.setHours(parseInt(hours || '0'), parseInt(minutes || '0'), 0, 0);
  return date;
});

// Virtual for duration in hours
BookingSchema.virtual('durationHours').get(function() {
  return Math.round((this.totalDuration / 60) * 100) / 100;
});

// Pre-save middleware to update the updated_at field
BookingSchema.pre('save', function(next) {
  this.updated_at = new Date();
  next();
});

// Pre-save validation for time logic
BookingSchema.pre('save', function(next) {
  const startTimeParts = this.startTime.split(':');
  const endTimeParts = this.endTime.split(':');
  
  const startHours = parseInt(startTimeParts[0] || '0');
  const startMinutes = parseInt(startTimeParts[1] || '0');
  const endHours = parseInt(endTimeParts[0] || '0');
  const endMinutes = parseInt(endTimeParts[1] || '0');
  
  const startTotalMinutes = startHours * 60 + startMinutes;
  const endTotalMinutes = endHours * 60 + endMinutes;
  
  if (endTotalMinutes <= startTotalMinutes) {
    return next(new Error('End time must be after start time'));
  }
  
  const calculatedDuration = endTotalMinutes - startTotalMinutes;
  if (Math.abs(this.totalDuration - calculatedDuration) > 5) {
    return next(new Error('Total duration must match the time difference between start and end time'));
  }
  
  next();
});

// Export the model
export const Booking = mongoose.model<IBooking>('Booking', BookingSchema);
export default Booking;
