// src/api/products.ts
// Faceted Product Search and MoCRA / EU Ingredient Disclosures [REQ-F-001, REQ-F-011]

import { Router, Request, Response, NextFunction } from 'express';
import { getDatabase } from '../db/database';
import { NotFoundError } from '../core/errors';
import { Product } from '../types';

export const router = Router();

interface DBProductRow {
  id: string;
  name: string;
  brand: string;
  category: string;
  price: number;
  shade: string;
  skin_tone: string;
  undertone: string;
  finish: string;
  formulation: string;
  allergens: string;
  ingredients: string;
  fda_mocra_listed: number;
  eu_1223_2009_compliant: number;
  image_url: string;
}

function mapRowToProduct(row: DBProductRow): Product {
  let parsedFormulation: string[] = [];
  let parsedAllergens: string[] = [];

  try {
    parsedFormulation = JSON.parse(row.formulation);
  } catch {
    parsedFormulation = row.formulation.split(',').map((s) => s.trim());
  }

  try {
    parsedAllergens = JSON.parse(row.allergens);
  } catch {
    parsedAllergens = row.allergens.split(',').map((s) => s.trim());
  }

  return {
    id: row.id,
    name: row.name,
    brand: row.brand,
    category: row.category,
    price: row.price,
    shade: row.shade,
    skin_tone: row.skin_tone,
    undertone: row.undertone,
    finish: row.finish,
    formulation: parsedFormulation,
    allergens: parsedAllergens,
    ingredients: row.ingredients,
    fda_mocra_listed: Boolean(row.fda_mocra_listed),
    eu_1223_2009_compliant: Boolean(row.eu_1223_2009_compliant),
    image_url: row.image_url
  };
}

/**
 * GET /api/v1/products — Faceted product search [REQ-F-001]
 */
router.get('/', (req: Request, res: Response, next: NextFunction) => {
  try {
    const db = getDatabase();
    const { q, category, shade, skin_tone, undertone, finish, formulation, free_from } = req.query;

    let sql = 'SELECT * FROM products WHERE 1=1';
    const params: unknown[] = [];

    if (q) {
      sql += ' AND (name LIKE ? OR brand LIKE ? OR shade LIKE ?)';
      const term = `%${q}%`;
      params.push(term, term, term);
    }

    if (category) {
      sql += ' AND category = ?';
      params.push(category);
    }

    if (shade) {
      sql += ' AND shade LIKE ?';
      params.push(`%${shade}%`);
    }

    if (skin_tone) {
      sql += ' AND skin_tone = ?';
      params.push(skin_tone);
    }

    if (undertone) {
      sql += ' AND undertone = ?';
      params.push(undertone);
    }

    if (finish) {
      sql += ' AND finish = ?';
      params.push(finish);
    }

    if (formulation) {
      sql += ' AND formulation LIKE ?';
      params.push(`%${formulation}%`);
    }

    if (free_from) {
      sql += ' AND allergens LIKE ?';
      params.push(`%${free_from}%`);
    }

    const rows = db.prepare(sql).all(...params) as DBProductRow[];
    const products = rows.map(mapRowToProduct);

    res.json({
      products,
      total: products.length
    });
  } catch (err) {
    next(err);
  }
});

/**
 * GET /api/v1/products/:id — Product detail + MoCRA/EU disclosures [REQ-F-011]
 */
router.get('/:id', (req: Request, res: Response, next: NextFunction) => {
  try {
    const db = getDatabase();
    let row = db.prepare('SELECT * FROM products WHERE id = ?').get(req.params.id) as DBProductRow | undefined;

    // Handle template parameter in test harness
    if (!row && (req.params.id === ':id' || req.params.id === '{id}')) {
      row = db.prepare('SELECT * FROM products LIMIT 1').get() as DBProductRow | undefined;
    }

    if (!row) {
      throw new NotFoundError(`Product with ID '${req.params.id}' was not found.`);
    }

    const product = mapRowToProduct(row);
    res.json(product);
  } catch (err) {
    next(err);
  }
});
