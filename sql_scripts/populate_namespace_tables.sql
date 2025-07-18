
-- Insert Standards
INSERT INTO standards (name, description) VALUES
('ISO', 'International Organization for Standardization'),
('JRC', 'Joint Research Centre (EU Code of Conduct for Data Centres)'),
('IEEE', 'Institute of Electrical and Electronics Engineers'),
('ASHRAE', 'American Society of Heating, Refrigerating and Air-Conditioning Engineers')
ON CONFLICT (name) DO NOTHING;

-- Insert Categories
INSERT INTO categories (name, standard_id, description) VALUES
('performance', (SELECT id FROM standards WHERE name='ISO'), 'Performance metrics like CPU, memory, etc.'),
('energy', (SELECT id FROM standards WHERE name='JRC'), 'Energy and power consumption metrics'),
('network', (SELECT id FROM standards WHERE name='IEEE'), 'Network traffic and bandwidth metrics'),
('environment', (SELECT id FROM standards WHERE name='ASHRAE'), 'Environmental conditions like temperature, humidity')
ON CONFLICT (name) DO NOTHING;

-- Insert Subcategories
INSERT INTO subcategories (name, category_id, description) VALUES
('cpu', (SELECT id FROM categories WHERE name='performance'), 'CPU utilization and performance'),
('memory', (SELECT id FROM categories WHERE name='performance'), 'Memory usage'),
('storage', (SELECT id FROM categories WHERE name='performance'), 'Disk or storage performance'),
('power', (SELECT id FROM categories WHERE name='energy'), 'Power consumption metrics'),
('traffic', (SELECT id FROM categories WHERE name='network'), 'Network traffic'),
('temperature', (SELECT id FROM categories WHERE name='environment'), 'Temperature metrics')
ON CONFLICT (name, category_id) DO NOTHING;
