import { Response } from 'express';
import { ApiResponse, ErrorResponse, SuccessResponse } from '@/types';

export class ResponseUtil {
  static success<T>(
    res: Response,
    data: T,
    message?: string,
    statusCode: number = 200
  ): Response<SuccessResponse<T>> {
    return res.status(statusCode).json({
      success: true,
      data,
      message,
      timestamp: new Date().toISOString()
    });
  }

  static error(
    res: Response,
    error: string,
    message?: string,
    statusCode: number = 500
  ): Response<ErrorResponse> {
    return res.status(statusCode).json({
      success: false,
      error,
      message: message || error,
      timestamp: new Date().toISOString(),
      statusCode
    });
  }

  static badRequest(
    res: Response,
    message: string = 'Bad Request'
  ): Response<ErrorResponse> {
    return this.error(res, 'BAD_REQUEST', message, 400);
  }

  static unauthorized(
    res: Response,
    message: string = 'Unauthorized'
  ): Response<ErrorResponse> {
    return this.error(res, 'UNAUTHORIZED', message, 401);
  }

  static forbidden(
    res: Response,
    message: string = 'Forbidden'
  ): Response<ErrorResponse> {
    return this.error(res, 'FORBIDDEN', message, 403);
  }

  static notFound(
    res: Response,
    message: string = 'Resource not found'
  ): Response<ErrorResponse> {
    return this.error(res, 'NOT_FOUND', message, 404);
  }

  static conflict(
    res: Response,
    message: string = 'Conflict'
  ): Response<ErrorResponse> {
    return this.error(res, 'CONFLICT', message, 409);
  }

  static validationError(
    res: Response,
    message: string = 'Validation failed'
  ): Response<ErrorResponse> {
    return this.error(res, 'VALIDATION_ERROR', message, 422);
  }

  static internalError(
    res: Response,
    message: string = 'Internal server error'
  ): Response<ErrorResponse> {
    return this.error(res, 'INTERNAL_ERROR', message, 500);
  }
}
