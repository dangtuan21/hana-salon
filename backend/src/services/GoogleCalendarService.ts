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
  private bookingToCalendarEvent(booking: IBooking, customerEmail?: string, technicianEmails?: string[]): CalendarEventData {
    // Create appointment datetime
    const appointmentDate = new Date(booking.appointmentDate);
    const [startHours, startMinutes] = booking.startTime.split(':');
    const [endHours, endMinutes] = booking.endTime.split(':');

    const startDateTime = new Date(appointmentDate);
    startDateTime.setHours(parseInt(startHours || '0'), parseInt(startMinutes || '0'), 0, 0);

    const endDateTime = new Date(appointmentDate);
    endDateTime.setHours(parseInt(endHours || '0'), parseInt(endMinutes || '0'), 0, 0);

    // Create service summary
    const serviceNames = booking.services.map(service => `Service ${service.serviceId}`).join(', ');
    const summary = `Salon Appointment - ${serviceNames}`;

    // Create detailed description
    const description = this.createEventDescription(booking);

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
        dateTime: startDateTime.toISOString(),
        timeZone: this.config.timeZone,
      },
      end: {
        dateTime: endDateTime.toISOString(),
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
   * Create detailed event description from booking data
   */
  private createEventDescription(booking: IBooking): string {
    const lines: string[] = [];
    
    lines.push(`Booking ID: ${booking._id}`);
    lines.push(`Status: ${booking.status}`);
    lines.push(`Total Duration: ${booking.totalDuration} minutes`);
    lines.push(`Total Price: $${booking.totalPrice.toFixed(2)}`);
    lines.push('');
    
    lines.push('Services:');
    booking.services.forEach((service, index) => {
      lines.push(`${index + 1}. Service ID: ${service.serviceId}`);
      lines.push(`   Technician ID: ${service.technicianId}`);
      lines.push(`   Duration: ${service.duration} minutes`);
      lines.push(`   Price: $${service.price.toFixed(2)}`);
      if (service.notes) {
        lines.push(`   Notes: ${service.notes}`);
      }
      lines.push('');
    });

    if (booking.notes) {
      lines.push(`General Notes: ${booking.notes}`);
    }

    if (booking.customerNotes) {
      lines.push(`Customer Notes: ${booking.customerNotes}`);
    }

    lines.push('');
    lines.push(`Payment Status: ${booking.paymentStatus}`);
    if (booking.paymentMethod) {
      lines.push(`Payment Method: ${booking.paymentMethod}`);
    }

    return lines.join('\n');
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
      case 'scheduled':
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
    technicianEmails?: string[]
  ): Promise<string | null> {
    try {
      const eventData = this.bookingToCalendarEvent(booking, customerEmail, technicianEmails);
      
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
    technicianEmails?: string[]
  ): Promise<boolean> {
    try {
      const eventData = this.bookingToCalendarEvent(booking, customerEmail, technicianEmails);
      
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
