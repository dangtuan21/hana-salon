// Test Google Calendar Integration
require('dotenv').config();

async function testCalendarIntegration() {
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

    // Test 2: Import and initialize calendar service
    console.log('\n2. Testing calendar service initialization:');
    
    // Dynamic import to handle ES modules
    const { isCalendarEnabled } = await import('./dist/config/calendar.js');
    const CalendarServiceFactory = (await import('./dist/services/CalendarServiceFactory.js')).default;

    if (isCalendarEnabled()) {
      console.log('   ✅ Calendar configuration loaded successfully');
    } else {
      console.log('   ❌ Calendar configuration failed to load');
      return;
    }

    // Test 3: Test calendar connection
    console.log('\n3. Testing Google Calendar API connection:');
    const connectionTest = await CalendarServiceFactory.testConnection();
    
    if (connectionTest) {
      console.log('   ✅ Successfully connected to Google Calendar API');
      console.log('   ✅ Service account has access to the calendar');
    } else {
      console.log('   ❌ Failed to connect to Google Calendar API');
      console.log('   💡 Check: Service account permissions, calendar sharing, API enabled');
      return;
    }

    // Test 4: Check if service is available
    console.log('\n4. Testing calendar service availability:');
    const isAvailable = CalendarServiceFactory.isAvailable();
    
    if (isAvailable) {
      console.log('   ✅ Calendar service is available and ready to use');
    } else {
      console.log('   ❌ Calendar service is not available');
      return;
    }

    console.log('\n🎉 All tests passed! Google Calendar integration is working correctly.');
    console.log('\n📅 Your salon bookings will now automatically sync to Google Calendar:');
    console.log(`   📧 Service Account: ${process.env.GOOGLE_CALENDAR_SERVICE_ACCOUNT_EMAIL}`);
    console.log(`   📅 Calendar ID: ${process.env.GOOGLE_CALENDAR_CALENDAR_ID}`);
    console.log(`   🌍 Timezone: ${process.env.GOOGLE_CALENDAR_TIMEZONE}`);

  } catch (error) {
    console.error('\n❌ Test failed with error:', error.message);
    
    if (error.message.includes('Cannot resolve module')) {
      console.log('\n💡 The backend needs to be built first. Run: npm run build');
    } else if (error.message.includes('authentication')) {
      console.log('\n💡 Check your service account credentials and private key format');
    } else if (error.message.includes('calendar')) {
      console.log('\n💡 Check that the calendar is shared with your service account');
    }
  }
}

// Run the test
testCalendarIntegration();
