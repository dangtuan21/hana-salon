import mongoose, { Schema, Document } from 'mongoose';

// Message interface
interface IMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

// BookingConversation interface
export interface IBookingConversation extends Document {
  sessionId: string;
  customerId?: mongoose.Types.ObjectId;
  bookingId?: mongoose.Types.ObjectId;
  
  messages: IMessage[];
  
  startTime: Date;
  endTime?: Date;
  outcome: 'booking_created' | 'booking_failed' | 'information_only' | 'abandoned';
  
  totalMessages: number;
  conversationDuration: number; // seconds
  
  created_at: Date;
  updated_at: Date;
}

// Message schema
const MessageSchema = new Schema<IMessage>({
  role: {
    type: String,
    required: true,
    enum: ['user', 'assistant']
  },
  content: {
    type: String,
    required: true
  },
  timestamp: {
    type: Date,
    required: true
  }
}, { _id: false });

// BookingConversation schema
const BookingConversationSchema = new Schema<IBookingConversation>({
  sessionId: {
    type: String,
    required: true,
    unique: true,
    index: true
  },
  customerId: {
    type: Schema.Types.ObjectId,
    ref: 'Customer',
    index: true
  },
  bookingId: {
    type: Schema.Types.ObjectId,
    ref: 'Booking',
    index: true
  },
  
  messages: [MessageSchema],
  
  startTime: {
    type: Date,
    required: true,
    index: true
  },
  endTime: {
    type: Date
  },
  outcome: {
    type: String,
    required: true,
    enum: ['booking_created', 'booking_failed', 'information_only', 'abandoned'],
    index: true
  },
  
  totalMessages: {
    type: Number,
    required: true,
    min: 0
  },
  conversationDuration: {
    type: Number,
    required: true,
    min: 0
  },
  
  created_at: {
    type: Date,
    default: Date.now
  },
  updated_at: {
    type: Date,
    default: Date.now
  }
});

// Update the updated_at field before saving
BookingConversationSchema.pre('save', function(next) {
  this.updated_at = new Date();
  next();
});

// Create indexes for better query performance
BookingConversationSchema.index({ sessionId: 1 });
BookingConversationSchema.index({ customerId: 1, startTime: -1 });
BookingConversationSchema.index({ outcome: 1, startTime: -1 });
BookingConversationSchema.index({ startTime: -1 });

const BookingConversation = mongoose.model<IBookingConversation>('BookingConversation', BookingConversationSchema);

export default BookingConversation;
