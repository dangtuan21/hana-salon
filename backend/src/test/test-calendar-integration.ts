import dotenv from 'dotenv';
import { getCalendarConfig, isCalendarEnabled } from '@/config/calendar';
import CalendarServiceFactory from '@/services/CalendarServiceFactory';
import logger from '@/utils/logger';

// Load environment variables
dotenv.config();

/**
 * Test Google Calendar Integration
 */
async function testCalendarIntegration(): Promise<void> {
  try {
    console.log('🔧 Testing Google Calendar Integration...\n');

    // Test 1: Check environment variables
    console.log('1. Checking environment variables:');
    const requiredVars = [
      'GOOGLE_CALENDAR_SERVICE_ACCOUNT_EMAIL',
      'GOOGLE_CALENDAR_PRIVATE_KEY',
      'GOOGLE_CALENDAR_CALENDAR_ID',
      'GOOGLE_CALENDAR_TIMEZONE'
    ];

    let allVarsPresent = true;
    requiredVars.forEach(varName => {
      const value = process.env[varName];
      if (value) {
        console.log(`   ✅ ${varName}: ${varName.includes('PRIVATE_KEY') ? '[HIDDEN]' : value}`);
      } else {
        console.log(`   ❌ ${varName}: Missing`);
        allVarsPresent = false;
      }
    });

    if (!allVarsPresent) {
      console.log('\n❌ Some environment variables are missing. Please check your .env file.');
      return;
    }

    // Test 2: Test calendar configuration loading
    console.log('\n2. Testing calendar configuration:');
    
    if (isCalendarEnabled()) {
      console.log('   ✅ Calendar configuration loaded successfully');
      
      const config = getCalendarConfig();
      if (config) {
        console.log(`   ✅ Service Account: ${config.serviceAccountEmail}`);
        console.log(`   ✅ Calendar ID: ${config.calendarId}`);
        console.log(`   ✅ Timezone: ${config.timeZone}`);
        if (config.salonLocation) {
          console.log(`   ✅ Salon Location: ${config.salonLocation}`);
        }
      }
    } else {
      console.log('   ❌ Calendar configuration failed to load');
      return;
    }

    // Test 3: Test calendar service initialization
    console.log('\n3. Testing calendar service initialization:');
    
    const calendarService = CalendarServiceFactory.getInstance();
    if (calendarService) {
      console.log('   ✅ Calendar service initialized successfully');
    } else {
      console.log('   ❌ Failed to initialize calendar service');
      return;
    }

    // Test 4: Test Google Calendar API connection
    console.log('\n4. Testing Google Calendar API connection:');
    
    const connectionTest = await CalendarServiceFactory.testConnection();
    if (connectionTest) {
      console.log('   ✅ Successfully connected to Google Calendar API');
      console.log('   ✅ Service account has access to the calendar');
    } else {
      console.log('   ❌ Failed to connect to Google Calendar API');
      console.log('   💡 Check: Service account permissions, calendar sharing, API enabled');
      return;
    }

    // Test 5: Check if service is available
    console.log('\n5. Testing calendar service availability:');
    
    const isAvailable = CalendarServiceFactory.isAvailable();
    if (isAvailable) {
      console.log('   ✅ Calendar service is available and ready to use');
    } else {
      console.log('   ❌ Calendar service is not available');
      return;
    }

    // Test 6: Test conflict checking (optional)
    console.log('\n6. Testing conflict detection:');
    
    try {
      const testDate = new Date();
      testDate.setDate(testDate.getDate() + 1); // Tomorrow
      
      if (calendarService) {
        const conflicts = await calendarService.checkForConflicts(
          new Date(testDate.setHours(10, 0, 0, 0)),
          new Date(testDate.setHours(11, 0, 0, 0))
        );
        
        console.log(`   ✅ Conflict detection working (found ${conflicts.length} events)`);
      }
    } catch (error) {
      console.log('   ⚠️  Conflict detection test failed (this is optional)');
    }

    // Success summary
    console.log('\n🎉 All tests passed! Google Calendar integration is working correctly.');
    console.log('\n📅 Your salon bookings will now automatically sync to Google Calendar:');
    console.log(`   📧 Service Account: ${process.env.GOOGLE_CALENDAR_SERVICE_ACCOUNT_EMAIL}`);
    console.log(`   📅 Calendar ID: ${process.env.GOOGLE_CALENDAR_CALENDAR_ID}`);
    console.log(`   🌍 Timezone: ${process.env.GOOGLE_CALENDAR_TIMEZONE}`);
    
    if (process.env.SALON_LOCATION) {
      console.log(`   📍 Location: ${process.env.SALON_LOCATION}`);
    }

    console.log('\n✨ Next steps:');
    console.log('   1. Create bookings using your booking API');
    console.log('   2. Use BookingCalendarIntegration.createCalendarEvent() to sync');
    console.log('   3. Check your Google Calendar for the events!');

  } catch (error) {
    console.error('\n❌ Test failed with error:', error);
    
    if (error instanceof Error) {
      if (error.message.includes('authentication')) {
        console.log('\n💡 Check your service account credentials and private key format');
      } else if (error.message.includes('calendar')) {
        console.log('\n💡 Check that the calendar is shared with your service account');
      } else if (error.message.includes('API')) {
        console.log('\n💡 Check that Google Calendar API is enabled in your project');
      }
    }
    
    logger.error('Calendar integration test failed:', error);
  }
}

/**
 * Run the test if this file is executed directly
 */
if (require.main === module) {
  testCalendarIntegration()
    .then(() => {
      console.log('\n✅ Test completed');
      process.exit(0);
    })
    .catch((error) => {
      console.error('\n❌ Test failed:', error);
      process.exit(1);
    });
}

export default testCalendarIntegration;
