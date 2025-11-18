export interface Service {
  _id?: string;
  name: string;
  category: string;
  duration_minutes: number;
  price: number;
  description: string;
  required_skill_level: string;
  popularity_score: number;
  created_at?: string;
  updated_at?: string;
}

export interface Technician {
  _id?: string;
  name: string;
  skill_level: string;
  specialties: string[]; // Service IDs
  rating: number;
  years_experience: number;
  hourly_rate: number;
  available_days: string[];
  work_hours: {
    start: string;
    end: string;
  };
  is_available: boolean;
  bio: string;
  phone?: string;
  email?: string;
  created_at?: string;
  updated_at?: string;
}

export interface Customer {
  _id?: string;
  name: string;
  phone: string;
  email?: string;
  preferences?: {
    preferred_technician?: string;
    preferred_services?: string[];
    notes?: string;
  };
  booking_history?: string[]; // Booking IDs
  created_at?: string;
  updated_at?: string;
}

export interface Booking {
  _id?: string;
  customer_id: string;
  service_id: string;
  technician_id: string;
  date: string;
  time: string;
  duration_minutes: number;
  total_cost: number;
  status: 'pending' | 'confirmed' | 'completed' | 'cancelled' | 'no_show';
  confirmation_id: string;
  notes?: string;
  created_at?: string;
  updated_at?: string;
}

export interface SkillLevel {
  level: 'Junior' | 'Senior' | 'Expert' | 'Master';
  description: string;
  premium_percentage: number;
}

export interface ServiceCategory {
  name: string;
  description: string;
  services: string[]; // Service IDs
}

// API Response types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
  total?: number;
}

export interface PaginationParams {
  page?: number;
  limit?: number;
  sort?: string;
  order?: 'asc' | 'desc';
}

export interface ServiceFilters extends PaginationParams {
  category?: string;
  skill_level?: string;
  price_min?: number;
  price_max?: number;
}

export interface TechnicianFilters extends PaginationParams {
  skill_level?: string;
  available?: boolean;
  specialties?: string[];
  rating_min?: number;
}
