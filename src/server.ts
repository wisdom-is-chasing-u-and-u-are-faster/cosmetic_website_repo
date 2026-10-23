// src/server.ts
// Server Boot Entrypoint for Enterprise Online Cosmetic Store Platform

import express from 'express';
import dotenv from 'dotenv';
dotenv.config();

import { createApp } from './app';
import { getDatabase } from './db/database';

const PORT = process.env.PORT || 8000;
const HOST = process.env.HOST || '0.0.0.0';

// Initialize Database
getDatabase();

const app = createApp();

// Static mount reference for static file serving
app.use(express.static('public'));

app.listen(Number(PORT), HOST, () => {
  console.log(`🚀 Cosmetics Store Platform Server running at http://${HOST}:${PORT}`);
});
