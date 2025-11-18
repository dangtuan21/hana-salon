export interface BookingRequest {
  booking_request: string;
}

export interface BookingValidation {
  customer_name: string;
  service_type: string;
  date: string;
  time: string;
  validation_status: string;
}

export interface BookingResult extends BookingValidation {
  confirmation_id: string;
  final_response: string;
  messages: string[];
}

export interface StoredBooking extends BookingResult {
  id: string;
  created_at: string;
  status: 'confirmed' | 'failed' | 'pending';
}

export interface NailService {
  category: string;
  services: string[];
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface HealthCheckResponse {
  status: 'healthy' | 'unhealthy';
  timestamp: string;
  uptime: number;
  service: string;
  version: string;
  memory?: {
    rss: number;
    heapTotal: number;
    heapUsed: number;
    external: number;
    arrayBuffers: number;
  };
  environment?: string;
  services?: {
    aiService: string;
    database: string;
  };
}
