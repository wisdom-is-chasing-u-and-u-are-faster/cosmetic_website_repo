// src/core/errors.ts
// RFC-7807 Problem Details Error Classes and Middleware [REQ-F-014]

import { Request, Response, NextFunction } from 'express';
import { RFC7807ProblemDetails } from '../types';

export class AppError extends Error {
  public readonly statusCode: number;
  public readonly type: string;
  public readonly title: string;
  public readonly detail: string;
  public readonly invalidParams?: Array<{ name: string; reason: string }>;

  constructor(
    statusCode: number,
    title: string,
    detail: string,
    type: string = 'about:blank',
    invalidParams?: Array<{ name: string; reason: string }>
  ) {
    super(detail);
    this.statusCode = statusCode;
    this.title = title;
    this.detail = detail;
    this.type = type;
    this.invalidParams = invalidParams;
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

export class NotFoundError extends AppError {
  constructor(detail: string) {
    super(404, 'Resource Not Found', detail, 'https://api.cosmetics.example/errors/not-found');
  }
}

export class BadRequestError extends AppError {
  constructor(detail: string, invalidParams?: Array<{ name: string; reason: string }>) {
    super(400, 'Bad Request', detail, 'https://api.cosmetics.example/errors/bad-request', invalidParams);
  }
}

export class ConflictError extends AppError {
  constructor(detail: string) {
    super(409, 'Conflict', detail, 'https://api.cosmetics.example/errors/conflict');
  }
}

export class UnauthorizedError extends AppError {
  constructor(detail: string = 'Authentication or signature verification failed') {
    super(401, 'Unauthorized', detail, 'https://api.cosmetics.example/errors/unauthorized');
  }
}

export function errorHandler(
  err: Error | AppError,
  req: Request,
  res: Response,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  next: NextFunction
): void {
  if (err instanceof AppError) {
    const payload: RFC7807ProblemDetails = {
      type: err.type,
      title: err.title,
      status: err.statusCode,
      detail: err.detail,
      instance: req.originalUrl,
      ...(err.invalidParams ? { invalid_params: err.invalidParams } : {})
    };
    res.status(err.statusCode).contentType('application/problem+json').json(payload);
    return;
  }

  // Internal Server Error Fallback
  const payload: RFC7807ProblemDetails = {
    type: 'about:blank',
    title: 'Internal Server Error',
    status: 500,
    detail: err.message || 'An unexpected error occurred.',
    instance: req.originalUrl
  };
  res.status(500).contentType('application/problem+json').json(payload);
}
