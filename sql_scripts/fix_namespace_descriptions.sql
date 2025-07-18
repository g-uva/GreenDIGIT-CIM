
-- Update or Insert Standards with Descriptions
INSERT INTO standards (name, description) VALUES
('ISO', 'International Organization for Standardization – Covers computing performance, availability, etc.'),
('JRC', 'Joint Research Centre – EU Code of Conduct for Energy Efficiency in Data Centres'),
('IEEE', 'Institute of Electrical and Electronics Engineers – Network, traffic, and signal standards'),
('ASHRAE', 'American Society of Heating, Refrigerating and Air-Conditioning Engineers – Environmental norms')
ON CONFLICT (name) DO UPDATE SET description = EXCLUDED.description;

-- Update or Insert Categories with Descriptions
INSERT INTO categories (name, standard_id, description) VALUES
('performance', (SELECT id FROM standards WHERE name='ISO'), 'Performance-related computing metrics (CPU, memory, etc.)'),
('energy', (SELECT id FROM standards WHERE name='JRC'), 'Energy consumption and power efficiency metrics'),
('network', (SELECT id FROM standards WHERE name='IEEE'), 'Network traffic, bandwidth, and utilization metrics'),
('environment', (SELECT id FROM standards WHERE name='ASHRAE'), 'Environmental conditions such as temperature, humidity')
ON CONFLICT (name) DO UPDATE SET description = EXCLUDED.description;

-- Update or Insert Subcategories with Descriptions
INSERT INTO subcategories (name, category_id, description) VALUES
('cpu', (SELECT id FROM categories WHERE name='performance'), 'Central processing unit utilization and load'),
('memory', (SELECT id FROM categories WHERE name='performance'), 'RAM usage and memory load'),
('storage', (SELECT id FROM categories WHERE name='performance'), 'Disk or storage read/write and usage levels'),
('power', (SELECT id FROM categories WHERE name='energy'), 'Power draw, usage, or loss metrics'),
('traffic', (SELECT id FROM categories WHERE name='network'), 'Incoming/outgoing data flow'),
('temperature', (SELECT id FROM categories WHERE name='environment'), 'Ambient or internal temperature')
ON CONFLICT (name, category_id) DO UPDATE SET description = EXCLUDED.description;
