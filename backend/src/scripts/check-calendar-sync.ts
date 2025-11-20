import dotenv from 'dotenv';
import mongoose from 'mongoose';
import { Booking } from '@/models/Booking';
import CalendarServiceFactory from '@/services/CalendarServiceFactory';
import logger from '@/utils/logger';

// Load environment variables
dotenv.config();

/**
 * Script to check for calendar sync inconsistencies
 * Identifies stale calendar events that don't match current bookings
 */
async function checkCalendarSync() {
  try {
    // Connect to MongoDB
    await mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/hana-salon');
    console.log('✅ Connected to MongoDB');

    // Get calendar service
    const calendarService = CalendarServiceFactory.getInstance();
    if (!calendarService) {
      console.log('❌ Calendar service not configured');
      return;
    }

    // Get all active bookings from database
    const bookings = await Booking.find({ 
      status: { $ne: 'cancelled' },
      appointmentDate: { $gte: new Date() } // Only future bookings
    }).populate('customerId services.serviceId services.technicianId');

    console.log(`📋 Found ${bookings.length} active bookings in database`);

    // Get calendar events for the next 30 days
    const startDate = new Date();
    const endDate = new Date();
    endDate.setDate(endDate.getDate() + 30);

    const calendarEvents = await calendarService.getEventsInRange(startDate, endDate);
    console.log(`📅 Found ${calendarEvents.length} events in Google Calendar`);

    // Check for inconsistencies
    const inconsistencies = [];

    // Check for calendar events without matching bookings
    for (const event of calendarEvents) {
      if (event.summary?.includes('Hana Salon')) {
        // Extract booking ID from event description
        const bookingIdMatch = event.description?.match(/Booking ID: ([a-f0-9]{24})/);
        if (bookingIdMatch) {
          const bookingId = bookingIdMatch[1];
          const matchingBooking = bookings.find(b => b._id.toString() === bookingId);
          
          if (!matchingBooking) {
            inconsistencies.push({
              type: 'stale_calendar_event',
              eventId: event.id,
              bookingId,
              eventSummary: event.summary,
              eventStart: event.start?.dateTime || event.start?.date
            });
          }
        }
      }
    }

    // Check for bookings without calendar events
    for (const booking of bookings) {
      if (booking.calendarEventId) {
        const matchingEvent = calendarEvents.find(e => e.id === booking.calendarEventId);
        if (!matchingEvent) {
          inconsistencies.push({
            type: 'missing_calendar_event',
            bookingId: booking._id.toString(),
            calendarEventId: booking.calendarEventId,
            appointmentDate: booking.appointmentDate,
            startTime: booking.startTime
          });
        }
      }
    }

    // Report inconsistencies
    if (inconsistencies.length === 0) {
      console.log('✅ No calendar sync inconsistencies found');
    } else {
      console.log(`❌ Found ${inconsistencies.length} calendar sync inconsistencies:`);
      
      inconsistencies.forEach((issue, index) => {
        console.log(`\n${index + 1}. ${issue.type.toUpperCase()}:`);
        if (issue.type === 'stale_calendar_event') {
          console.log(`   📅 Calendar Event ID: ${issue.eventId}`);
          console.log(`   🆔 Booking ID: ${issue.bookingId} (NOT FOUND IN DATABASE)`);
          console.log(`   📝 Event: ${issue.eventSummary}`);
          console.log(`   🕐 Time: ${issue.eventStart}`);
        } else {
          console.log(`   🆔 Booking ID: ${issue.bookingId}`);
          console.log(`   📅 Missing Calendar Event ID: ${issue.calendarEventId}`);
          console.log(`   🕐 Appointment: ${issue.appointmentDate} ${issue.startTime}`);
        }
      });

      console.log('\n🔧 Recommended actions:');
      console.log('   1. Delete stale calendar events manually');
      console.log('   2. Re-sync missing calendar events');
      console.log('   3. Update booking calendarSyncStatus accordingly');
    }

  } catch (error) {
    logger.error('Error checking calendar sync:', error);
  } finally {
    await mongoose.disconnect();
    console.log('✅ Disconnected from MongoDB');
  }
}

// Run the check
checkCalendarSync().catch(console.error);
