CREATE TABLE IF NOT EXISTS listings_enriched (
  apn VARCHAR(64) PRIMARY KEY,
  full_address VARCHAR(255),
  price INT,
  beds INT,
  baths INT,
  sqft INT,
  price_per_sqft INT,
  status VARCHAR(32),
  flood_zone VARCHAR(16),
  avg_rain_inches DECIMAL(6,2)
);
