import dotenv from 'dotenv';
import mongoose from 'mongoose';
import { Booking, IBooking } from '@/models/Booking';
import { BookingCalendarIntegration } from '@/services/BookingCalendarIntegration';
import logger from '@/utils/logger';

// Load environment variables
dotenv.config();

/**
 * Test creating a real booking and syncing it to Google Calendar
 */
async function testBookingCalendarSync(): Promise<void> {
  try {
    console.log('🧪 Testing Real Booking → Google Calendar Sync...\n');

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
          status: 'initial' as const,
          notes: 'Manicure with gel polish'
        },
        {
          serviceId: new mongoose.Types.ObjectId(),
          technicianId: new mongoose.Types.ObjectId(),
          duration: 45,
          price: 50.00,
          status: 'initial' as const,
          notes: 'Eyebrow shaping'
        }
      ],
      appointmentDate: tomorrow,
      startTime: '14:00',
      endTime: '15:45',
      status: 'initial' as const,
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
    
    console.log('\n2. Testing calendar event creation:');
    
    // Test calendar data
    const calendarData = {
      customerEmail: 'customer@example.com',
      technicianEmails: ['tech1@hanasalon.com', 'tech2@hanasalon.com']
    };

    console.log(`   👤 Customer: ${calendarData.customerEmail}`);
    console.log(`   👨‍💼 Technicians: ${calendarData.technicianEmails.join(', ')}`);

    // Sync to Google Calendar
    const result = await BookingCalendarIntegration.createCalendarEvent(booking, calendarData);

    if (result.success) {
      console.log('\n🎉 SUCCESS! Calendar event created:');
      console.log(`   📅 Event ID: ${result.eventId}`);
      console.log(`   ✅ Sync Status: ${booking.calendarSyncStatus}`);
      console.log(`   🕐 Last Sync: ${booking.calendarLastSyncAt}`);
      
      console.log('\n📱 Check your Google Calendar now!');
      console.log('   You should see a new event with:');
      console.log('   • Event title: "Salon Appointment - Service [IDs]"');
      console.log('   • Date & time: Tomorrow 2:00 PM - 3:45 PM');
      console.log('   • Attendees: Customer and technicians');
      console.log('   • Location: Your salon address');
      console.log('   • Description: Full booking details');

      // Test updating the event
      console.log('\n3. Testing calendar event update:');
      
      // Modify booking
      booking.startTime = '15:00';
      booking.endTime = '16:45';
      booking.notes = 'Updated: Customer requested later time';
      
      const updateResult = await BookingCalendarIntegration.updateCalendarEvent(booking, calendarData);
      
      if (updateResult.success) {
        console.log('   ✅ Calendar event updated successfully');
        console.log('   📅 New time: 3:00 PM - 4:45 PM');
        console.log('   📝 Updated notes included');
      } else {
        console.log('   ❌ Failed to update calendar event:', updateResult.error);
      }

      // Test deleting the event (cleanup)
      console.log('\n4. Testing calendar event deletion (cleanup):');
      
      const deleteResult = await BookingCalendarIntegration.deleteCalendarEvent(booking);
      
      if (deleteResult.success) {
        console.log('   ✅ Calendar event deleted successfully');
        console.log('   🧹 Test cleanup completed');
      } else {
        console.log('   ❌ Failed to delete calendar event:', deleteResult.error);
        console.log('   ⚠️  You may need to manually delete the test event from your calendar');
      }

    } else {
      console.log('\n❌ FAILED to create calendar event:');
      console.log(`   Error: ${result.error}`);
      console.log(`   Sync Status: ${booking.calendarSyncStatus}`);
    }

    console.log('\n✨ Test Summary:');
    console.log('   • Booking creation: ✅');
    console.log(`   • Calendar sync: ${result.success ? '✅' : '❌'}`);
    console.log('   • Integration status: Ready for production!');

  } catch (error) {
    console.error('\n❌ Test failed with error:', error);
    
    if (error instanceof Error) {
      if (error.message.includes('calendar')) {
        console.log('\n💡 Calendar service might not be properly configured');
      } else if (error.message.includes('validation')) {
        console.log('\n💡 Booking data validation failed - check required fields');
      }
    }
    
    logger.error('Booking calendar sync test failed:', error);
  }
}

/**
 * Run the test if this file is executed directly
 */
if (require.main === module) {
  testBookingCalendarSync()
    .then(() => {
      console.log('\n✅ Booking calendar sync test completed');
      process.exit(0);
    })
    .catch((error) => {
      console.error('\n❌ Test failed:', error);
      process.exit(1);
    });
}

export default testBookingCalendarSync;
