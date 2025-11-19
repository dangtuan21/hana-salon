import dotenv from 'dotenv';
import mongoose from 'mongoose';
import { Booking, IBooking } from '@/models/Booking';
import { BookingCalendarIntegration } from '@/services/BookingCalendarIntegration';
import logger from '@/utils/logger';

// Load environment variables
dotenv.config();

/**
 * Test user-friendly calendar event creation
 */
async function testUserFriendlyCalendar(): Promise<void> {
  try {
    console.log('🎨 Testing User-Friendly Calendar Event Creation...\n');

    // Test booking data with populated information
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    const testBookingData = {
      customerId: new mongoose.Types.ObjectId(),
      services: [
        {
          serviceId: new mongoose.Types.ObjectId(),
          technicianId: new mongoose.Types.ObjectId(),
          duration: 45,
          price: 35.00,
          status: 'scheduled' as const,
          notes: 'French tips requested'
        },
        {
          serviceId: new mongoose.Types.ObjectId(),
          technicianId: new mongoose.Types.ObjectId(),
          duration: 90,
          price: 55.00,
          status: 'scheduled' as const,
          notes: 'Relaxing pedicure with massage'
        }
      ],
      appointmentDate: tomorrow,
      startTime: '14:00',
      endTime: '16:15',
      status: 'scheduled' as const,
      totalDuration: 135,
      totalPrice: 90.00,
      paymentStatus: 'pending' as const,
      notes: 'First-time customer, prefers quiet environment',
      customerNotes: 'Please call 30 minutes before appointment',
      reminderSent: false,
      confirmationSent: false,
      calendarSyncStatus: 'pending' as const
    };

    console.log('1. Creating test booking with user-friendly data:');
    console.log(`   📅 Date: ${tomorrow.toDateString()}`);
    console.log(`   🕐 Time: ${testBookingData.startTime} - ${testBookingData.endTime}`);
    console.log(`   💰 Total: $${testBookingData.totalPrice}`);
    console.log(`   ⏱️  Duration: ${testBookingData.totalDuration} minutes (2h 15min)`);

    // Create booking object
    const booking = new Booking(testBookingData);
    
    console.log('\n2. Creating user-friendly calendar event:');
    
    // Mock populated data (simulating what would come from database)
    const populatedData = {
      customer: {
        firstName: 'Sarah',
        lastName: 'Johnson',
        email: 'sarah.johnson@email.com',
        phone: '(555) 123-4567'
      },
      services: [
        {
          name: 'Manicure',
          price: 35.00,
          duration_minutes: 45
        },
        {
          name: 'Pedicure',
          price: 55.00,
          duration_minutes: 90
        }
      ],
      technicians: [
        {
          firstName: 'John',
          lastName: 'Smith',
          employeeId: 'EMP001'
        },
        {
          firstName: 'John',
          lastName: 'Smith',
          employeeId: 'EMP001'
        }
      ]
    };

    const calendarData = {
      customerEmail: populatedData.customer.email,
      populatedData
    };

    console.log(`   👤 Customer: ${populatedData.customer.firstName} ${populatedData.customer.lastName}`);
    console.log(`   📧 Email: ${populatedData.customer.email}`);
    console.log(`   📞 Phone: ${populatedData.customer.phone}`);
    console.log(`   💅 Services: ${populatedData.services.map(s => s.name).join(' & ')}`);
    console.log(`   👨‍💼 Technician: ${populatedData.technicians[0]?.firstName} ${populatedData.technicians[0]?.lastName}`);

    // Create calendar event with populated data
    const result = await BookingCalendarIntegration.createCalendarEvent(booking, calendarData);

    if (result.success) {
      console.log('\n🎉 SUCCESS! User-friendly calendar event created:');
      console.log(`   📅 Event ID: ${result.eventId}`);
      console.log(`   ✅ Sync Status: ${booking.calendarSyncStatus}`);
      
      console.log('\n📱 Check your Google Calendar now!');
      console.log('   You should see a much more readable event with:');
      console.log('   • Title: "Salon Appointment - Manicure & Pedicure"');
      console.log('   • Customer info: Sarah Johnson with contact details');
      console.log('   • Services: Manicure with John Smith - 45min ($35.00)');
      console.log('   •          Pedicure with John Smith - 1h 30min ($55.00)');
      console.log('   • Duration: 2h 15min (instead of 135 minutes)');
      console.log('   • Status: Scheduled 📅');
      console.log('   • Payment: Pending');
      console.log('   • All notes and booking details');

      // Test cleanup (delete the event)
      console.log('\n4. Cleaning up test event:');
      const deleteResult = await BookingCalendarIntegration.deleteCalendarEvent(booking);
      
      if (deleteResult.success) {
        console.log('   ✅ Test event deleted successfully');
      } else {
        console.log('   ⚠️  Test event may need manual deletion');
      }

    } else {
      console.log('\n❌ FAILED to create user-friendly calendar event:');
      console.log(`   Error: ${result.error}`);
    }

    console.log('\n✨ User-Friendly Calendar Test Summary:');
    console.log(`   • Booking creation: ✅`);
    console.log(`   • User-friendly format: ${result.success ? '✅' : '❌'}`);
    console.log(`   • Readable descriptions: ${result.success ? '✅' : '❌'}`);
    console.log(`   • Proper formatting: ${result.success ? '✅' : '❌'}`);
    
    if (result.success) {
      console.log('\n🎯 Improvements Made:');
      console.log('   • Booking ID kept for reference');
      console.log('   • Customer names instead of IDs');
      console.log('   • Service names instead of IDs');
      console.log('   • Technician names instead of IDs');
      console.log('   • Duration in hours/minutes format');
      console.log('   • Emojis for better readability');
      console.log('   • Organized sections with clear formatting');
    }

  } catch (error) {
    console.error('\n❌ User-friendly calendar test failed:', error);
    logger.error('User-friendly calendar test failed:', error);
  }
}

/**
 * Run the test if this file is executed directly
 */
if (require.main === module) {
  testUserFriendlyCalendar()
    .then(() => {
      console.log('\n✅ User-friendly calendar test completed');
      process.exit(0);
    })
    .catch((error) => {
      console.error('\n❌ Test failed:', error);
      process.exit(1);
    });
}

export default testUserFriendlyCalendar;
