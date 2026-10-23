// tests/database.test.ts
// Unit Tests for Database Initialization and Schema Integrity [ARCH-5134-AC5]

import { resetDatabaseForTesting } from '../src/db/database';

describe('Database Tier & Schema Validation', () => {
  let db: ReturnType<typeof resetDatabaseForTesting>;

  beforeEach(() => {
    db = resetDatabaseForTesting();
  });

  test('[ARCH-5134-AC5] Schema tables are properly created and seeded', () => {
    const tables = db.prepare("SELECT name FROM sqlite_master WHERE type='table'").all() as Array<{ name: string }>;
    const tableNames = tables.map((t) => t.name);

    expect(tableNames).toContain('products');
    expect(tableNames).toContain('inventory');
    expect(tableNames).toContain('reservations');
    expect(tableNames).toContain('promotions');
    expect(tableNames).toContain('orders');
    expect(tableNames).toContain('order_items');
    expect(tableNames).toContain('returns');
    expect(tableNames).toContain('idempotency_keys');
    expect(tableNames).toContain('audit_logs');
  });

  test('Baseline seed products and inventory are present', () => {
    const products = db.prepare('SELECT count(*) as count FROM products').get() as { count: number };
    const inventory = db.prepare('SELECT count(*) as count FROM inventory').get() as { count: number };

    expect(products.count).toBeGreaterThanOrEqual(4);
    expect(inventory.count).toBeGreaterThanOrEqual(4);
  });
});
