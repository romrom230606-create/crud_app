ALTER TABLE products
  ADD COLUMN email VARCHAR(255),
  ADD COLUMN birth_date DATE,
  ADD COLUMN code VARCHAR(100);
-- ensure sku exists; if not, previous migration should have created it
