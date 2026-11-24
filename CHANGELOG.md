# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- **[ARCH-10099]** UI Pages + Requirements: Implement Product Availability & Stock Control
  - Real-time stock status badge display ("In Stock", "Only X Left", "Out of Stock") on product detail pages.
  - Dynamic quantity selector clamping strictly limited by available inventory.
  - Dedicated Inventory Service providing `get_product_stock`, `reserve_stock`, and `release_stock`.
  - Atomic stock reservations with HTTP 400 rejection on attempts to reserve quantities exceeding stock.
  - Concurrency race protection to eliminate flash sale overselling.
- **[ARCH-6311]** UI Pages + Requirements: Personalized Skincare Product Finder
  - *Key modifications:*
    - `.jtc/ARCH-6311/cloned_repo/.env.example`
    - `.jtc/ARCH-6311/cloned_repo/docker-compose.yml`
    - `.jtc/ARCH-6311/cloned_repo/db/schema.sql`
    - `.jtc/ARCH-6311/cloned_repo/db/seed.sql`
    - `.jtc/ARCH-6311/cloned_repo/app/__init__.py`
    - `.jtc/ARCH-6311/cloned_repo/app/db.py`
    - `.jtc/ARCH-6311/cloned_repo/app/models.py`
    - `.jtc/ARCH-6311/cloned_repo/app/services/recommendation_engine.py`
