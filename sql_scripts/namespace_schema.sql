
-- Table: standards
CREATE TABLE IF NOT EXISTS standards (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    description TEXT
);

-- Table: categories
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    standard_id INTEGER REFERENCES standards(id),
    description TEXT
);

-- Table: subcategories
CREATE TABLE IF NOT EXISTS subcategories (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    category_id INTEGER REFERENCES categories(id),
    UNIQUE(name, category_id),
    description TEXT
);

-- Table: metric_definitions
CREATE TABLE IF NOT EXISTS metric_definitions (
    id SERIAL PRIMARY KEY,
    unified_key VARCHAR UNIQUE NOT NULL,
    subcategory_id INTEGER REFERENCES subcategories(id),
    source_keys TEXT[],
    tags TEXT[]
);
