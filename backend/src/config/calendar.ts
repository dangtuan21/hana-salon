import { CalendarConfig } from '@/services/GoogleCalendarService';
import logger from '@/utils/logger';

/**
 * Google Calendar configuration
 */
export const getCalendarConfig = (): CalendarConfig | null => {
  try {
    const serviceAccountEmail = process.env.GOOGLE_CALENDAR_SERVICE_ACCOUNT_EMAIL;
    const privateKey = process.env.GOOGLE_CALENDAR_PRIVATE_KEY;
    const calendarId = process.env.GOOGLE_CALENDAR_CALENDAR_ID || 'primary';
    const timeZone = process.env.GOOGLE_CALENDAR_TIMEZONE || 'America/New_York';
    const salonLocation = process.env.SALON_LOCATION;

    if (!serviceAccountEmail || !privateKey) {
      logger.warn('Google Calendar credentials not configured. Calendar integration will be disabled.');
      return null;
    }

    const config: CalendarConfig = {
      serviceAccountEmail,
      privateKey,
      calendarId,
      timeZone,
    };

    if (salonLocation) {
      config.salonLocation = salonLocation;
    }

    return config;
  } catch (error) {
    logger.error('Failed to load Google Calendar configuration:', error);
    return null;
  }
};

/**
 * Check if Google Calendar is enabled
 */
export const isCalendarEnabled = (): boolean => {
  return getCalendarConfig() !== null;
};

export default {
  getCalendarConfig,
  isCalendarEnabled,
};
