// src/app.ts
// Express Application Assembly with Static View Mounts and Middleware

import express, { Express, Request, Response } from 'express';
import cors from 'cors';
import path from 'path';
import fs from 'fs';

import { router as productsRouter } from './api/products';
import { router as promotionsRouter } from './api/promotions';
import { router as checkoutRouter } from './api/checkout';
import { router as ordersRouter } from './api/orders';
import { router as returnsRouter } from './api/returns';
import { router as accountRouter } from './api/account';
import { router as webhooksRouter } from './api/webhooks';
import { errorHandler } from './core/errors';

export function createApp(): Express {
  const app = express();

  // Basic Middlewares
  app.use(cors());
  app.use(express.json());
  app.use(express.urlencoded({ extended: true }));

  // Health Probe
  app.get('/health', (req: Request, res: Response) => {
    res.json({
      status: 'ok',
      service: 'cosmetics-store-api',
      runtime: 'Node.js (TypeScript / Express)',
      version: '1.0.0'
    });
  });

  // REST API Routers
  app.use('/api/v1/products', productsRouter);
  app.use('/api/v1/promotions', promotionsRouter);
  app.use('/api/v1/checkout', checkoutRouter);
  app.use('/api/v1/orders', ordersRouter);
  app.use('/api/v1/returns', returnsRouter);
  app.use('/api/v1/account', accountRouter);
  app.use('/api/v1/webhooks', webhooksRouter);

  // Static Assets and HTML Prototype Mounts
  const publicDir = path.resolve(__dirname, '../public');
  if (fs.existsSync(publicDir)) {
    const pagesDir = path.join(publicDir, 'pages');
    if (fs.existsSync(pagesDir)) {
      app.use('/pages', express.static(pagesDir));
    }

    const cssDir = path.join(publicDir, 'css');
    if (fs.existsSync(cssDir)) {
      app.use('/css', express.static(cssDir));
    }

    const jsDir = path.join(publicDir, 'js');
    if (fs.existsSync(jsDir)) {
      app.use('/js', express.static(jsDir));
    }

    app.use(express.static(publicDir));

    app.get('/', (req: Request, res: Response) => {
      const indexFile = path.join(publicDir, 'index.html');
      const homePage = path.join(publicDir, 'pages', 'homepage.html');
      if (fs.existsSync(indexFile)) {
        res.sendFile(indexFile);
      } else if (fs.existsSync(homePage)) {
        res.sendFile(homePage);
      } else {
        res.json({ message: 'Cosmetics Store API Online' });
      }
    });
  }

  // RFC-7807 Error Handler
  app.use(errorHandler);

  return app;
}
