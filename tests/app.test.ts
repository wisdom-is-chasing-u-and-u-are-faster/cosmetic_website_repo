// tests/app.test.ts
// Express App and Static View Mount Tests [ARCH-5134-AC1]

import request from 'supertest';
import { createApp } from '../src/app';
import { resetDatabaseForTesting } from '../src/db/database';

describe('App Server & Static Prototype Views', () => {
  let app: ReturnType<typeof createApp>;

  beforeEach(() => {
    resetDatabaseForTesting();
    app = createApp();
  });

  test('GET /health returns 200 OK service readiness', async () => {
    const res = await request(app).get('/health');
    expect(res.status).toBe(200);
    expect(res.body.status).toBe('ok');
    expect(res.body.runtime).toContain('Node.js');
  });

  test('[ARCH-5134-AC1] UI pages are served statically from /pages/*.html', async () => {
    const resHome = await request(app).get('/pages/homepage.html');
    expect(resHome.status).toBe(200);
    expect(resHome.header['content-type']).toContain('text/html');

    const resPLP = await request(app).get('/pages/product-listing.html');
    expect(resPLP.status).toBe(200);

    const resCheckout = await request(app).get('/pages/checkout.html');
    expect(resCheckout.status).toBe(200);

    const resApiJs = await request(app).get('/js/api.js');
    expect(resApiJs.status).toBe(200);
    expect(resApiJs.text).toContain('StoreAPI');
  });
});
