import { IBooking } from '@/models/Booking';
import CalendarServiceFactory from './CalendarServiceFactory';
import logger from '@/utils/logger';

export interface BookingCalendarData {
  customerEmail?: string;
  technicianEmails?: string[];
  populatedData?: {
    customer?: any;
    services?: any[] | undefined;
    technicians?: any[] | undefined;
  };
}

/**
 * Service to handle booking-calendar integration
 */
export class BookingCalendarIntegration {
  /**
   * Create calendar event for a new booking
   */
  static async createCalendarEvent(
    booking: IBooking,
    calendarData?: BookingCalendarData
  ): Promise<{ success: boolean; eventId?: string; error?: string }> {
    const calendarService = CalendarServiceFactory.getInstance();
    
    if (!calendarService) {
      // Update booking to indicate calendar is disabled
      booking.calendarSyncStatus = 'disabled';
      return { success: true }; // Don't fail booking creation if calendar is disabled
    }

    try {
      const eventId = await calendarService.createBookingEvent(
        booking,
        calendarData?.customerEmail,
        calendarData?.technicianEmails,
        calendarData?.populatedData
      );

      if (eventId) {
        booking.calendarEventId = eventId;
        booking.calendarSyncStatus = 'synced';
        booking.calendarLastSyncAt = new Date();
        
        logger.info(`Calendar event created for booking ${booking._id}: ${eventId}`);
        return { success: true, eventId };
      } else {
        booking.calendarSyncStatus = 'failed';
        return { success: false, error: 'Failed to create calendar event' };
      }
    } catch (error) {
      logger.error(`Error creating calendar event for booking ${booking._id}:`, error);
      booking.calendarSyncStatus = 'failed';
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  }

  /**
   * Update calendar event for an existing booking
   */
  static async updateCalendarEvent(
    booking: IBooking,
    calendarData?: BookingCalendarData
  ): Promise<{ success: boolean; error?: string }> {
    const calendarService = CalendarServiceFactory.getInstance();
    
    if (!calendarService || !booking.calendarEventId) {
      booking.calendarSyncStatus = booking.calendarEventId ? 'failed' : 'disabled';
      return { success: true }; // Don't fail booking update if calendar is disabled
    }

    try {
      const success = await calendarService.updateBookingEvent(
        booking.calendarEventId!,
        booking,
        calendarData?.customerEmail,
        calendarData?.technicianEmails,
        calendarData?.populatedData
      );

      if (success) {
        booking.calendarSyncStatus = 'synced';
        booking.calendarLastSyncAt = new Date();
        
        logger.info(`Calendar event updated for booking ${booking._id}: ${booking.calendarEventId}`);
        return { success: true };
      } else {
        booking.calendarSyncStatus = 'failed';
        return { success: false, error: 'Failed to update calendar event' };
      }
    } catch (error) {
      logger.error(`Error updating calendar event for booking ${booking._id}:`, error);
      booking.calendarSyncStatus = 'failed';
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  }

  /**
   * Delete calendar event for a cancelled booking
   */
  static async deleteCalendarEvent(
    booking: IBooking
  ): Promise<{ success: boolean; error?: string }> {
    const calendarService = CalendarServiceFactory.getInstance();
    
    if (!calendarService || !booking.calendarEventId) {
      return { success: true }; // Nothing to delete
    }

    try {
      const success = await calendarService.deleteBookingEvent(
        booking.calendarEventId!,
        booking._id.toString()
      );

      if (success) {
        delete booking.calendarEventId;
        booking.calendarSyncStatus = 'disabled';
        booking.calendarLastSyncAt = new Date();
        
        logger.info(`Calendar event deleted for booking ${booking._id}`);
        return { success: true };
      } else {
        booking.calendarSyncStatus = 'failed';
        return { success: false, error: 'Failed to delete calendar event' };
      }
    } catch (error) {
      logger.error(`Error deleting calendar event for booking ${booking._id}:`, error);
      booking.calendarSyncStatus = 'failed';
      return { success: false, error: error instanceof Error ? error.message : 'Unknown error' };
    }
  }

  /**
   * Sync booking with calendar (create or update as needed)
   */
  static async syncBookingWithCalendar(
    booking: IBooking,
    calendarData?: BookingCalendarData
  ): Promise<{ success: boolean; eventId?: string; error?: string }> {
    if (booking.calendarEventId) {
      const result = await this.updateCalendarEvent(booking, calendarData);
      return { ...result, eventId: booking.calendarEventId };
    } else {
      return await this.createCalendarEvent(booking, calendarData);
    }
  }

  /**
   * Check for calendar conflicts
   */
  static async checkForConflicts(
    appointmentDate: Date,
    startTime: string,
    endTime: string,
    excludeBookingId?: string
  ): Promise<{ hasConflicts: boolean; conflictingEvents?: any[] }> {
    const calendarService = CalendarServiceFactory.getInstance();
    
    if (!calendarService) {
      return { hasConflicts: false };
    }

    try {
      // Create datetime objects
      const [startHours, startMinutes] = startTime.split(':');
      const [endHours, endMinutes] = endTime.split(':');

      const startDateTime = new Date(appointmentDate);
      startDateTime.setHours(parseInt(startHours || '0'), parseInt(startMinutes || '0'), 0, 0);

      const endDateTime = new Date(appointmentDate);
      endDateTime.setHours(parseInt(endHours || '0'), parseInt(endMinutes || '0'), 0, 0);

      // Get existing booking's calendar event ID to exclude
      let excludeEventId: string | undefined;
      if (excludeBookingId) {
        // This would need to be implemented to look up the calendar event ID
        // from the booking ID in the database
      }

      const conflictingEvents = await calendarService.checkForConflicts(
        startDateTime,
        endDateTime,
        excludeEventId
      );

      return {
        hasConflicts: conflictingEvents.length > 0,
        conflictingEvents
      };
    } catch (error) {
      logger.error('Error checking for calendar conflicts:', error);
      return { hasConflicts: false };
    }
  }

  /**
   * Retry failed calendar syncs
   */
  static async retryFailedSyncs(bookings: IBooking[]): Promise<void> {
    const failedBookings = bookings.filter(booking => 
      booking.calendarSyncStatus === 'failed' || 
      booking.calendarSyncStatus === 'pending'
    );

    logger.info(`Retrying calendar sync for ${failedBookings.length} bookings`);

    for (const booking of failedBookings) {
      try {
        await this.syncBookingWithCalendar(booking);
        // Note: In a real implementation, you'd want to save the booking here
        // await booking.save();
      } catch (error) {
        logger.error(`Failed to retry calendar sync for booking ${booking._id}:`, error);
      }
    }
  }

  /**
   * Get calendar sync status summary
   */
  static getCalendarSyncSummary(bookings: IBooking[]): {
    total: number;
    synced: number;
    pending: number;
    failed: number;
    disabled: number;
  } {
    const summary = {
      total: bookings.length,
      synced: 0,
      pending: 0,
      failed: 0,
      disabled: 0
    };

    bookings.forEach(booking => {
      switch (booking.calendarSyncStatus) {
        case 'synced':
          summary.synced++;
          break;
        case 'pending':
          summary.pending++;
          break;
        case 'failed':
          summary.failed++;
          break;
        case 'disabled':
          summary.disabled++;
          break;
      }
    });

    return summary;
  }
}

export default BookingCalendarIntegration;
