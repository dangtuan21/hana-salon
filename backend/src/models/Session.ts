import mongoose, { Document, Schema } from 'mongoose';

// Interface for conversation messages
export interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

// Interface for booking state
export interface BookingState {
  customer_name: string;
  customer_phone: string;
  services_requested: string;
  date_requested: string;
  time_requested: string;
  technician_preference: string;
  customerId?: string;
  services: any[];
  appointmentDate?: string;
  startTime?: string;
  endTime?: string;
  status: string;
  totalDuration: number;
  totalPrice: number;
  paymentStatus: string;
  paymentMethod?: string;
  notes?: string;
  customerNotes?: string;
  cancellationReason?: string;
  confirmationSent: boolean;
  rating?: number;
  available_technicians: any[];
  available_services: any[];
  alternative_times: any[];
  booking_id?: string;
}

// Interface for Session document
export interface ISession extends Document {
  session_id: string;
  created_at: Date;
  last_activity: Date;
  messages: ConversationMessage[];
  booking_state: BookingState;
  conversation_complete: boolean;
}

// Conversation Message Schema
const ConversationMessageSchema = new Schema<ConversationMessage>({
  role: {
    type: String,
    enum: ['user', 'assistant'],
    required: true
  },
  content: {
    type: String,
    required: true
  },
  timestamp: {
    type: String,
    required: true
  }
}, { _id: false });

// Booking State Schema
const BookingStateSchema = new Schema<BookingState>({
  customer_name: { type: String, default: '' },
  customer_phone: { type: String, default: '' },
  services_requested: { type: String, default: '' },
  date_requested: { type: String, default: '' },
  time_requested: { type: String, default: '' },
  technician_preference: { type: String, default: '' },
  customerId: { type: String },
  services: { type: Schema.Types.Mixed, default: [] },
  appointmentDate: { type: String },
  startTime: { type: String },
  endTime: { type: String },
  status: { type: String, default: 'initial' },
  totalDuration: { type: Number, default: 0 },
  totalPrice: { type: Number, default: 0.0 },
  paymentStatus: { type: String, default: 'pending' },
  paymentMethod: { type: String },
  notes: { type: String },
  customerNotes: { type: String },
  cancellationReason: { type: String },
  confirmationSent: { type: Boolean, default: false },
  rating: { type: Number },
  available_technicians: { type: Schema.Types.Mixed, default: [] },
  available_services: { type: Schema.Types.Mixed, default: [] },
  alternative_times: { type: Schema.Types.Mixed, default: [] },
  booking_id: { type: String }
}, { _id: false });

// Main Session Schema
const SessionSchema = new Schema<ISession>({
  session_id: {
    type: String,
    required: true,
    unique: true,
    index: true
  },
  created_at: {
    type: Date,
    default: Date.now,
    required: true
  },
  last_activity: {
    type: Date,
    default: Date.now,
    required: true
  },
  messages: {
    type: [ConversationMessageSchema],
    default: []
  },
  booking_state: {
    type: BookingStateSchema,
    required: true
  },
  conversation_complete: {
    type: Boolean,
    default: false
  }
}, {
  timestamps: true,
  collection: 'sessions'
});

// Indexes for performance
SessionSchema.index({ session_id: 1 });
SessionSchema.index({ last_activity: -1 });
SessionSchema.index({ created_at: -1 });
SessionSchema.index({ conversation_complete: 1 });

// TTL index to auto-delete old sessions after 7 days
SessionSchema.index({ last_activity: 1 }, { expireAfterSeconds: 7 * 24 * 60 * 60 });

// Export the model
export const Session = mongoose.model<ISession>('Session', SessionSchema);
export default Session;
