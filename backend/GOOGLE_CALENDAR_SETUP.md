# Google Calendar Integration Setup Guide

This guide will help you set up Google Calendar integration for your Hana AI salon booking system.

## Prerequisites

- Google Cloud Platform account
- Google Calendar API enabled
- Service Account with Calendar API permissions

## Step 1: Google Cloud Setup

### 1.1 Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your project ID

### 1.2 Enable Google Calendar API
1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google Calendar API"
3. Click on it and press "Enable"

### 1.3 Create Service Account
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in the service account details:
   - Name: `hana-ai-calendar-service`
   - Description: `Service account for Hana AI calendar integration`
4. Click "Create and Continue"
5. Skip role assignment for now (click "Continue")
6. Click "Done"

### 1.4 Generate Service Account Key
1. In the Credentials page, find your service account
2. Click on the service account email
3. Go to the "Keys" tab
4. Click "Add Key" > "Create New Key"
5. Select "JSON" format
6. Download the key file and keep it secure

### 1.5 Share Calendar with Service Account
1. Open Google Calendar
2. Go to your calendar settings (click the gear icon)
3. Select the calendar you want to integrate with
4. In "Share with specific people", add your service account email
5. Give it "Make changes to events" permission
6. Copy the Calendar ID from the calendar settings

## Step 2: Backend Configuration

### 2.1 Environment Variables
Copy your `.env.example` to `.env` and update the following variables:

```bash
# Google Calendar Integration
GOOGLE_CALENDAR_SERVICE_ACCOUNT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
GOOGLE_CALENDAR_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n"
GOOGLE_CALENDAR_CALENDAR_ID=your-calendar-id@group.calendar.google.com
GOOGLE_CALENDAR_TIMEZONE=America/New_York
SALON_LOCATION=Your Salon Address, City, State
```

**Important Notes:**
- Replace `your-service-account@your-project.iam.gserviceaccount.com` with your actual service account email
- Replace `YOUR_PRIVATE_KEY_HERE` with the private key from your downloaded JSON file
- Replace `your-calendar-id@group.calendar.google.com` with your actual calendar ID
- Update the timezone to match your salon's location
- Set your salon's physical address for location information

### 2.2 Private Key Format
The private key should be formatted as a single line with `\n` for line breaks:
```
"-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n"
```

## Step 3: Usage in Your Application

### 3.1 Basic Integration
The calendar integration is automatically handled when you create, update, or delete bookings:

```typescript
import { BookingCalendarIntegration } from '@/services/BookingCalendarIntegration';

// Create booking with calendar event
const booking = new Booking(bookingData);
await booking.save();

// Sync with calendar
const result = await BookingCalendarIntegration.createCalendarEvent(booking, {
  customerEmail: 'customer@example.com',
  technicianEmails: ['tech1@salon.com', 'tech2@salon.com']
});

if (result.success) {
  console.log('Calendar event created:', result.eventId);
} else {
  console.error('Calendar sync failed:', result.error);
}
```

### 3.2 Update Booking
```typescript
// Update booking
booking.startTime = '10:00';
booking.endTime = '11:30';
await booking.save();

// Sync changes to calendar
await BookingCalendarIntegration.updateCalendarEvent(booking, {
  customerEmail: 'customer@example.com',
  technicianEmails: ['tech1@salon.com']
});
```

### 3.3 Cancel Booking
```typescript
// Cancel booking
booking.status = 'cancelled';
await booking.save();

// Remove from calendar
await BookingCalendarIntegration.deleteCalendarEvent(booking);
```

## Step 4: Testing the Integration

### 4.1 Test Calendar Connection
```typescript
import CalendarServiceFactory from '@/services/CalendarServiceFactory';

// Test connection
const isConnected = await CalendarServiceFactory.testConnection();
console.log('Calendar connected:', isConnected);
```

### 4.2 Check Integration Status
```typescript
// Check if calendar is enabled
import { isCalendarEnabled } from '@/config/calendar';

if (isCalendarEnabled()) {
  console.log('Calendar integration is enabled');
} else {
  console.log('Calendar integration is disabled');
}
```

## Step 5: Monitoring and Troubleshooting

### 5.1 Calendar Sync Status
Each booking has calendar sync tracking:
- `calendarEventId`: Google Calendar event ID
- `calendarSyncStatus`: 'pending' | 'synced' | 'failed' | 'disabled'
- `calendarLastSyncAt`: Last sync timestamp

### 5.2 Retry Failed Syncs
```typescript
// Get bookings with failed syncs
const failedBookings = await Booking.find({ 
  calendarSyncStatus: { $in: ['failed', 'pending'] } 
});

// Retry syncing
await BookingCalendarIntegration.retryFailedSyncs(failedBookings);
```

### 5.3 Common Issues

**Issue: "Calendar integration is disabled"**
- Check that all environment variables are set correctly
- Verify the service account email and private key

**Issue: "Failed to create calendar event"**
- Ensure the service account has access to the calendar
- Check that the Calendar API is enabled
- Verify the calendar ID is correct

**Issue: "Authentication failed"**
- Check the private key format (should include `\n` for line breaks)
- Ensure the service account key is valid and not expired

## Step 6: Advanced Features

### 6.1 Conflict Detection
```typescript
// Check for scheduling conflicts
const conflicts = await BookingCalendarIntegration.checkForConflicts(
  new Date('2024-01-15'),
  '10:00',
  '11:30'
);

if (conflicts.hasConflicts) {
  console.log('Scheduling conflict detected');
}
```

### 6.2 Calendar Event Customization
You can customize calendar events by modifying the `GoogleCalendarService.bookingToCalendarEvent()` method to include:
- Custom event titles
- Additional attendees
- Reminders
- Event colors
- Custom descriptions

## Security Considerations

1. **Keep credentials secure**: Never commit the `.env` file to version control
2. **Limit service account permissions**: Only grant necessary Calendar API access
3. **Rotate keys regularly**: Generate new service account keys periodically
4. **Monitor API usage**: Keep track of Calendar API quota usage

## Support

If you encounter issues:
1. Check the application logs for detailed error messages
2. Verify your Google Cloud Console settings
3. Test the calendar connection using the provided test methods
4. Ensure all environment variables are correctly formatted

The integration is designed to be resilient - if calendar sync fails, booking operations will still succeed, and you can retry the sync later.
