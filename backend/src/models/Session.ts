import mongoose, { Document, Schema } from 'mongoose';

// Interface for conversation messages
export interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

// Interface for Session document
export interface ISession extends Document {
  session_id: string;
  created_at: Date;
  last_activity: Date;
  messages: ConversationMessage[];
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
