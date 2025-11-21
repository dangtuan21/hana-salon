import { google, calendar_v3 } from 'googleapis';
import { JWT } from 'google-auth-library';
import { IBooking } from '@/models/Booking';
import logger from '@/utils/logger';

export interface CalendarEventData {
  summary: string;
  description: string;
  start: {
    dateTime: string;
    timeZone: string;
  };
  end: {
    dateTime: string;
    timeZone: string;
  };
  attendees?: Array<{
    email: string;
    displayName?: string;
  }>;
  location?: string;
  status?: 'confirmed' | 'tentative' | 'cancelled';
}

export interface CalendarConfig {
  serviceAccountEmail: string;
  privateKey: string;
  calendarId: string;
  timeZone: string;
  salonLocation?: string;
}

export class GoogleCalendarService {
  private calendar!: calendar_v3.Calendar;
  private config: CalendarConfig;

  constructor(config: CalendarConfig) {
    this.config = config;
    this.initializeCalendar();
  }

  private initializeCalendar(): void {
    try {
      // Create JWT client for service account authentication
      const jwtClient = new JWT({
        email: this.config.serviceAccountEmail,
        key: this.config.privateKey.replace(/\\n/g, '\n'),
        scopes: ['https://www.googleapis.com/auth/calendar'],
      });

      // Initialize Google Calendar API
      this.calendar = google.calendar({ version: 'v3', auth: jwtClient });
      
      logger.info('Google Calendar service initialized successfully');
    } catch (error) {
      logger.error('Failed to initialize Google Calendar service:', error);
      throw new Error('Google Calendar initialization failed');
    }
  }

  /**
   * Convert booking data to Google Calendar event format
   */
  private bookingToCalendarEvent(booking: IBooking, customerEmail?: string, technicianEmails?: string[], populatedData?: any): CalendarEventData {
    // Create appointment datetime in the correct timezone
    const appointmentDate = new Date(booking.appointmentDate);
    const [startHours, startMinutes] = booking.startTime.split(':');
    const [endHours, endMinutes] = booking.endTime.split(':');

    // Create date strings in the format YYYY-MM-DD to avoid timezone issues
    const dateStr = appointmentDate.toISOString().split('T')[0]; // Gets YYYY-MM-DD
    
    // Create datetime strings in the calendar's timezone
    const startTimeStr = `${startHours?.padStart(2, '0') || '00'}:${startMinutes?.padStart(2, '0') || '00'}:00`;
    const endTimeStr = `${endHours?.padStart(2, '0') || '00'}:${endMinutes?.padStart(2, '0') || '00'}:00`;
    
    const startDateTime = `${dateStr}T${startTimeStr}`;
    const endDateTime = `${dateStr}T${endTimeStr}`;

    // Create service summary with actual service names
    let serviceNames = 'Services';
    if (populatedData?.services) {
      serviceNames = populatedData.services.map((service: any) => service.name || 'Service').join(' & ');
    } else {
      // Fallback to service count if no populated data
      serviceNames = booking.services.length === 1 ? 'Service' : `${booking.services.length} Services`;
    }
    const summary = `Hana Salon Appointment - ${serviceNames}`;

    // Create detailed description
    const description = this.createEventDescription(booking, populatedData);

    // Create attendees list
    const attendees: Array<{ email: string; displayName?: string }> = [];
    if (customerEmail) {
      attendees.push({ email: customerEmail, displayName: 'Customer' });
    }
    if (technicianEmails) {
      technicianEmails.forEach((email, index) => {
        attendees.push({ email, displayName: `Technician ${index + 1}` });
      });
    }

    // Map booking status to calendar status
    const calendarStatus = this.mapBookingStatusToCalendarStatus(booking.status);

    const eventData: CalendarEventData = {
      summary,
      description,
      start: {
        dateTime: startDateTime,
        timeZone: this.config.timeZone,
      },
      end: {
        dateTime: endDateTime,
        timeZone: this.config.timeZone,
      },
      status: calendarStatus,
    };

    if (attendees.length > 0) {
      eventData.attendees = attendees;
    }

    if (this.config.salonLocation) {
      eventData.location = this.config.salonLocation;
    }

    return eventData;
  }

  /**
   * Create user-friendly event description from booking data
   */
  private createEventDescription(booking: IBooking, populatedData?: any): string {
    const lines: string[] = [];
    
    // Booking ID for reference
    lines.push(`🆔 Booking ID: ${booking._id}`);
    
    // Customer information
    if (populatedData?.customer) {
      const customer = populatedData.customer;
      lines.push(`👤 Customer: ${customer.firstName || ''} ${customer.lastName || ''}`.trim());
      if (customer.phone) {
        lines.push(`📞 Phone: ${customer.phone}`);
      }
      if (customer.email) {
        lines.push(`📧 Email: ${customer.email}`);
      }
    }
    lines.push('');
    
    // Services section
    lines.push('💅 Services:');
    booking.services.forEach((service, index) => {
      const serviceName = populatedData?.services?.[index]?.name || 'Service';
      const technicianName = populatedData?.technicians?.[index] 
        ? `${populatedData.technicians[index].firstName || ''} ${populatedData.technicians[index].lastName || ''}`.trim()
        : 'Technician';
      
      const duration = this.formatDuration(service.duration);
      lines.push(`• ${serviceName} with ${technicianName} - ${duration} ($${service.price.toFixed(2)})`);
      
      if (service.notes) {
        lines.push(`  📝 ${service.notes}`);
      }
    });
    lines.push('');
    
    // Summary information
    lines.push(`⏰ Total Duration: ${this.formatDuration(booking.totalDuration)}`);
    lines.push(`💰 Total Price: $${booking.totalPrice.toFixed(2)}`);
    lines.push(`💳 Payment: ${this.formatPaymentStatus(booking.paymentStatus)}`);
    lines.push(`📅 Status: ${this.formatBookingStatus(booking.status)}`);
    
    // Notes section
    if (booking.notes || booking.customerNotes) {
      lines.push('');
      if (booking.notes) {
        lines.push(`📝 Notes: ${booking.notes}`);
      }
      if (booking.customerNotes) {
        lines.push(`💬 Customer Notes: ${booking.customerNotes}`);
      }
    }

    return lines.join('\n');
  }

  /**
   * Format duration in a user-friendly way
   */
  private formatDuration(minutes: number): string {
    if (minutes < 60) {
      return `${minutes}min`;
    }
    
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    
    if (remainingMinutes === 0) {
      return `${hours}h`;
    }
    
    return `${hours}h ${remainingMinutes}min`;
  }

  /**
   * Format payment status in a user-friendly way
   */
  private formatPaymentStatus(status: string): string {
    switch (status.toLowerCase()) {
      case 'pending': return 'Pending';
      case 'paid': return 'Paid ✅';
      case 'refunded': return 'Refunded';
      case 'failed': return 'Failed ❌';
      default: return status;
    }
  }

  /**
   * Format booking status in a user-friendly way
   */
  private formatBookingStatus(status: string): string {
    switch (status.toLowerCase()) {
      case 'initial': return 'Initial 📅';
      case 'confirmed': return 'Confirmed ✅';
      case 'in_progress': return 'In Progress 🔄';
      case 'completed': return 'Completed ✅';
      case 'cancelled': return 'Cancelled ❌';
      case 'no_show': return 'No Show ⚠️';
      default: return status;
    }
  }

  /**
   * Map booking status to Google Calendar event status
   */
  private mapBookingStatusToCalendarStatus(bookingStatus: string): 'confirmed' | 'tentative' | 'cancelled' {
    switch (bookingStatus) {
      case 'confirmed':
      case 'in_progress':
      case 'completed':
        return 'confirmed';
      case 'initial':
        return 'tentative';
      case 'cancelled':
      case 'no_show':
        return 'cancelled';
      default:
        return 'tentative';
    }
  }

  /**
   * Create a new calendar event for a booking
   */
  async createBookingEvent(
    booking: IBooking,
    customerEmail?: string,
    technicianEmails?: string[],
    populatedData?: any
  ): Promise<string | null> {
    try {
      const eventData = this.bookingToCalendarEvent(booking, customerEmail, technicianEmails, populatedData);
      
      const response = await this.calendar.events.insert({
        calendarId: this.config.calendarId,
        requestBody: eventData,
        sendUpdates: 'all', // Send email notifications to attendees
      });

      const eventId = response.data.id;
      logger.info(`Calendar event created successfully: ${eventId} for booking ${booking._id}`);
      
      return eventId || null;
    } catch (error) {
      logger.error(`Failed to create calendar event for booking ${booking._id}:`, error);
      return null;
    }
  }

  /**
   * Update an existing calendar event
   */
  async updateBookingEvent(
    eventId: string,
    booking: IBooking,
    customerEmail?: string,
    technicianEmails?: string[],
    populatedData?: any
  ): Promise<boolean> {
    try {
      const eventData = this.bookingToCalendarEvent(booking, customerEmail, technicianEmails, populatedData);
      
      await this.calendar.events.update({
        calendarId: this.config.calendarId,
        eventId: eventId,
        requestBody: eventData,
        sendUpdates: 'all',
      });

      logger.info(`Calendar event updated successfully: ${eventId} for booking ${booking._id}`);
      return true;
    } catch (error) {
      logger.error(`Failed to update calendar event ${eventId} for booking ${booking._id}:`, error);
      return false;
    }
  }

  /**
   * Delete a calendar event
   */
  async deleteBookingEvent(eventId: string, bookingId: string): Promise<boolean> {
    try {
      await this.calendar.events.delete({
        calendarId: this.config.calendarId,
        eventId: eventId,
        sendUpdates: 'all',
      });

      logger.info(`Calendar event deleted successfully: ${eventId} for booking ${bookingId}`);
      return true;
    } catch (error) {
      logger.error(`Failed to delete calendar event ${eventId} for booking ${bookingId}:`, error);
      return false;
    }
  }

  /**
   * Get calendar event by ID
   */
  async getBookingEvent(eventId: string): Promise<calendar_v3.Schema$Event | null> {
    try {
      const response = await this.calendar.events.get({
        calendarId: this.config.calendarId,
        eventId: eventId,
      });

      return response.data;
    } catch (error) {
      logger.error(`Failed to get calendar event ${eventId}:`, error);
      return null;
    }
  }

  /**
   * Check for scheduling conflicts
   */
  async checkForConflicts(
    startDateTime: Date,
    endDateTime: Date,
    excludeEventId?: string
  ): Promise<calendar_v3.Schema$Event[]> {
    try {
      const response = await this.calendar.events.list({
        calendarId: this.config.calendarId,
        timeMin: startDateTime.toISOString(),
        timeMax: endDateTime.toISOString(),
        singleEvents: true,
        orderBy: 'startTime',
      });

      const events = response.data.items || [];
      
      // Filter out the excluded event if provided
      const conflictingEvents = events.filter(event => 
        event.id !== excludeEventId && 
        event.status !== 'cancelled'
      );

      return conflictingEvents;
    } catch (error) {
      logger.error('Failed to check for calendar conflicts:', error);
      return [];
    }
  }

  /**
   * Get events for a specific date range
   */
  async getEventsInRange(
    startDate: Date,
    endDate: Date
  ): Promise<calendar_v3.Schema$Event[]> {
    try {
      const response = await this.calendar.events.list({
        calendarId: this.config.calendarId,
        timeMin: startDate.toISOString(),
        timeMax: endDate.toISOString(),
        singleEvents: true,
        orderBy: 'startTime',
      });

      return response.data.items || [];
    } catch (error) {
      logger.error('Failed to get calendar events in range:', error);
      return [];
    }
  }

  /**
   * Test calendar connection
   */
  async testConnection(): Promise<boolean> {
    try {
      await this.calendar.calendars.get({
        calendarId: this.config.calendarId,
      });
      
      logger.info('Google Calendar connection test successful');
      return true;
    } catch (error) {
      logger.error('Google Calendar connection test failed:', error);
      return false;
    }
  }
}

export default GoogleCalendarService;
