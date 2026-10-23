// src/db/database.ts
// Database Manager for SQLite & PostgreSQL schema parity

import Database from 'better-sqlite3';
import fs from 'fs';
import path from 'path';

let dbInstance: Database.Database | null = null;

export function getDatabase(dbFilePath?: string): Database.Database {
  if (!dbInstance) {
    const defaultPath = process.env.DATABASE_FILE || 'cosmetics_store.db';
    const finalPath = dbFilePath || (process.env.NODE_ENV === 'test' ? ':memory:' : defaultPath);
    dbInstance = new Database(finalPath);
    dbInstance.pragma('foreign_keys = ON');
    initDatabase(dbInstance);
  }
  return dbInstance;
}

export function initDatabase(db?: Database.Database): void {
  const targetDb = db || getDatabase();
  const rootDir = path.resolve(__dirname, '../../');
  const schemaPath = path.join(rootDir, 'db', 'schema.sql');
  const seedPath = path.join(rootDir, 'db', 'seed.sql');

  if (fs.existsSync(schemaPath)) {
    const schemaSql = fs.readFileSync(schemaPath, 'utf-8');
    targetDb.exec(schemaSql);
  }

  if (fs.existsSync(seedPath)) {
    const seedSql = fs.readFileSync(seedPath, 'utf-8');
    targetDb.exec(seedSql);
  }
}

export function resetDatabaseForTesting(): Database.Database {
  if (dbInstance) {
    try {
      dbInstance.close();
    } catch {}
    dbInstance = null;
  }
  dbInstance = new Database(':memory:');
  dbInstance.pragma('foreign_keys = ON');
  initDatabase(dbInstance);
  return dbInstance;
}
