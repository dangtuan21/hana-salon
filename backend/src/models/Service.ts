import mongoose, { Schema, Document, Types } from 'mongoose';

export interface IService extends Document {
  _id: Types.ObjectId;
  name: string;
  category: string;
  duration_minutes: number;
  price: number;
  description?: string;
  required_skill_level?: string;
  popularity_score?: number;
  created_at: Date;
  updated_at: Date;
}

const ServiceSchema = new Schema<IService>({
  name: {
    type: String,
    required: true,
    trim: true
  },
  category: {
    type: String,
    required: true,
    trim: true
  },
  duration_minutes: {
    type: Number,
    required: true,
    min: 1
  },
  price: {
    type: Number,
    required: true,
    min: 0
  },
  description: {
    type: String,
    trim: true
  },
  required_skill_level: {
    type: String,
    trim: true
  },
  popularity_score: {
    type: Number,
    min: 0,
    max: 10
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
  timestamps: false, // We're using our own created_at/updated_at fields
  collection: 'services'
});

// Add indexes for better query performance
ServiceSchema.index({ category: 1 });
ServiceSchema.index({ popularity_score: -1 });
ServiceSchema.index({ name: 'text', description: 'text' });

export const Service = mongoose.model<IService>('Service', ServiceSchema);
