import GoogleCalendarService from './GoogleCalendarService';
import { getCalendarConfig, isCalendarEnabled } from '@/config/calendar';
import logger from '@/utils/logger';

/**
 * Calendar service factory - creates and manages calendar service instance
 */
class CalendarServiceFactory {
  private static instance: GoogleCalendarService | null = null;
  private static initialized = false;

  /**
   * Get calendar service instance
   */
  static getInstance(): GoogleCalendarService | null {
    if (!this.initialized) {
      this.initialize();
    }
    return this.instance;
  }

  /**
   * Initialize calendar service
   */
  private static initialize(): void {
    this.initialized = true;

    if (!isCalendarEnabled()) {
      logger.info('Google Calendar integration is disabled - missing configuration');
      return;
    }

    try {
      const config = getCalendarConfig();
      if (config) {
        this.instance = new GoogleCalendarService(config);
        logger.info('Google Calendar service initialized successfully');
      }
    } catch (error) {
      logger.error('Failed to initialize Google Calendar service:', error);
      this.instance = null;
    }
  }

  /**
   * Test calendar connection
   */
  static async testConnection(): Promise<boolean> {
    const service = this.getInstance();
    if (!service) {
      return false;
    }

    return await service.testConnection();
  }

  /**
   * Check if calendar service is available
   */
  static isAvailable(): boolean {
    return this.getInstance() !== null;
  }

  /**
   * Reset instance (useful for testing)
   */
  static reset(): void {
    this.instance = null;
    this.initialized = false;
  }
}

export default CalendarServiceFactory;
