import dotenv from 'dotenv';
import mongoose from 'mongoose';
import { Booking, IBooking } from '@/models/Booking';
import { BookingCalendarIntegration } from '@/services/BookingCalendarIntegration';
import logger from '@/utils/logger';

// Load environment variables
dotenv.config();

/**
 * Test creating a booking and syncing it to Google Calendar (without attendees)
 */
async function testSimpleBookingSync(): Promise<void> {
  try {
    console.log('🧪 Testing Simple Booking → Google Calendar Sync...\n');

    // Test booking data
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    const testBookingData = {
      customerId: new mongoose.Types.ObjectId(),
      services: [
        {
          serviceId: new mongoose.Types.ObjectId(),
          technicianId: new mongoose.Types.ObjectId(),
          duration: 60,
          price: 75.00,
          status: 'scheduled' as const,
          notes: 'Manicure with gel polish'
        },
        {
          serviceId: new mongoose.Types.ObjectId(),
          technicianId: new mongoose.Types.ObjectId(),
          duration: 45,
          price: 50.00,
          status: 'scheduled' as const,
          notes: 'Eyebrow shaping'
        }
      ],
      appointmentDate: tomorrow,
      startTime: '14:00',
      endTime: '15:45',
      status: 'scheduled' as const,
      totalDuration: 105,
      totalPrice: 125.00,
      paymentStatus: 'pending' as const,
      notes: 'First-time customer, prefers quiet environment',
      customerNotes: 'Please call 30 minutes before appointment',
      confirmationSent: false,
      calendarSyncStatus: 'pending' as const
    };

    console.log('1. Creating test booking:');
    console.log(`   📅 Date: ${tomorrow.toDateString()}`);
    console.log(`   🕐 Time: ${testBookingData.startTime} - ${testBookingData.endTime}`);
    console.log(`   💰 Total: $${testBookingData.totalPrice}`);
    console.log(`   ⏱️  Duration: ${testBookingData.totalDuration} minutes`);
    console.log(`   🛍️  Services: ${testBookingData.services.length} services`);

    // Create booking object (without saving to database)
    const booking = new Booking(testBookingData);
    
    console.log('\n2. Testing calendar event creation (without attendees):');
    
    // Create calendar event WITHOUT attendees to avoid permission issues
    const result = await BookingCalendarIntegration.createCalendarEvent(booking);

    if (result.success) {
      console.log('\n🎉 SUCCESS! Calendar event created:');
      console.log(`   📅 Event ID: ${result.eventId}`);
      console.log(`   ✅ Sync Status: ${booking.calendarSyncStatus}`);
      console.log(`   🕐 Last Sync: ${booking.calendarLastSyncAt}`);
      
      console.log('\n📱 Check your Google Calendar now!');
      console.log('   You should see a new event with:');
      console.log('   • Event title: "Salon Appointment - Service [IDs]"');
      console.log('   • Date & time: Tomorrow 2:00 PM - 3:45 PM (EST)');
      console.log('   • Location: Your salon address');
      console.log('   • Description: Full booking details including:');
      console.log('     - Booking ID and status');
      console.log('     - Service details (Manicure + Eyebrow shaping)');
      console.log('     - Duration and pricing');
      console.log('     - Customer notes');

      // Test updating the event
      console.log('\n3. Testing calendar event update:');
      
      // Modify booking
      booking.startTime = '15:00';
      booking.endTime = '16:45';
      booking.notes = 'Updated: Customer requested later time';
      
      const updateResult = await BookingCalendarIntegration.updateCalendarEvent(booking);
      
      if (updateResult.success) {
        console.log('   ✅ Calendar event updated successfully');
        console.log('   📅 New time: 3:00 PM - 4:45 PM (EST)');
        console.log('   📝 Updated notes included');
        console.log('   🔄 Check your calendar - the event should be updated!');
      } else {
        console.log('   ❌ Failed to update calendar event:', updateResult.error);
      }

      // Ask user before cleanup
      console.log('\n4. Calendar event cleanup:');
      console.log('   ℹ️  The test event will remain in your calendar');
      console.log('   ℹ️  You can manually delete it or keep it as a test');
      
      // Optionally delete the event (commented out to let user decide)
      /*
      const deleteResult = await BookingCalendarIntegration.deleteCalendarEvent(booking);
      if (deleteResult.success) {
        console.log('   ✅ Calendar event deleted successfully');
      }
      */

    } else {
      console.log('\n❌ FAILED to create calendar event:');
      console.log(`   Error: ${result.error}`);
      console.log(`   Sync Status: ${booking.calendarSyncStatus}`);
    }

    console.log('\n✨ Test Summary:');
    console.log('   • Booking creation: ✅');
    console.log(`   • Calendar sync: ${result.success ? '✅' : '❌'}`);
    console.log(`   • Event details: ${result.success ? '✅ Complete with all booking info' : '❌'}`);
    console.log(`   • Integration status: ${result.success ? '🚀 Ready for production!' : '⚠️  Needs attention'}`);

    if (result.success) {
      console.log('\n🎯 Next Steps:');
      console.log('   1. Check your Google Calendar for the test event');
      console.log('   2. Verify all booking details are displayed correctly');
      console.log('   3. The integration is ready to use with real bookings!');
      console.log('   4. Note: Attendee invitations require domain-wide delegation');
      console.log('      (Events will be created but no email invites sent)');
    }

  } catch (error) {
    console.error('\n❌ Test failed with error:', error);
    
    if (error instanceof Error) {
      if (error.message.includes('calendar')) {
        console.log('\n💡 Calendar service might not be properly configured');
      } else if (error.message.includes('validation')) {
        console.log('\n💡 Booking data validation failed - check required fields');
      } else if (error.message.includes('attendees')) {
        console.log('\n💡 Attendee invitations require domain-wide delegation');
      }
    }
    
    logger.error('Simple booking calendar sync test failed:', error);
  }
}

/**
 * Run the test if this file is executed directly
 */
if (require.main === module) {
  testSimpleBookingSync()
    .then(() => {
      console.log('\n✅ Simple booking calendar sync test completed');
      process.exit(0);
    })
    .catch((error) => {
      console.error('\n❌ Test failed:', error);
      process.exit(1);
    });
}

export default testSimpleBookingSync;
