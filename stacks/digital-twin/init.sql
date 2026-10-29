SET TIME ZONE 'UTC';

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS device_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS manufacturers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    country VARCHAR(100),
    website TEXT
);

CREATE TABLE IF NOT EXISTS suppliers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    website TEXT
);

CREATE TABLE IF NOT EXISTS rooms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    floor INTEGER,
    description TEXT
);

CREATE TABLE IF NOT EXISTS purchases (
    id SERIAL PRIMARY KEY,
    supplier_id INTEGER REFERENCES suppliers(id),
    order_date DATE NOT NULL,
    arrival_date DATE,
    order_number VARCHAR(255),
    total_price NUMERIC(12, 2),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS devices (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    device_type_id INTEGER NOT NULL REFERENCES device_types(id),
    manufacturer_id INTEGER REFERENCES manufacturers(id),
    room_id INTEGER REFERENCES rooms(id) ON DELETE SET NULL,
    purchase_id INTEGER REFERENCES purchases(id) ON DELETE SET NULL,
    model_number VARCHAR(255),
    serial_number VARCHAR(255),
    ip_address VARCHAR(45),
    mac_address VARCHAR(17),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    status VARCHAR(50) NOT NULL DEFAULT 'operational',
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS components (
    id SERIAL PRIMARY KEY,
    component_type VARCHAR(100) NOT NULL,
    manufacturer_id INTEGER REFERENCES manufacturers(id),
    purchase_id INTEGER REFERENCES purchases(id) ON DELETE SET NULL,
    model_number VARCHAR(255),
    specifications JSONB,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS device_components (
    device_id INTEGER NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    component_id INTEGER NOT NULL REFERENCES components(id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (device_id, component_id)
);

CREATE TABLE IF NOT EXISTS device_relationships (
    parent_device_id INTEGER NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    child_device_id INTEGER NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    relationship_type VARCHAR(100) NOT NULL,
    PRIMARY KEY (parent_device_id, child_device_id),
    CHECK (parent_device_id <> child_device_id)
);

CREATE TABLE IF NOT EXISTS sensor_readings (
    id BIGSERIAL PRIMARY KEY,
    device_id INTEGER NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reading_type VARCHAR(100) NOT NULL,
    value NUMERIC NOT NULL
);

CREATE INDEX IF NOT EXISTS sensor_readings_device_time_idx
    ON sensor_readings (device_id, timestamp DESC);

CREATE TABLE IF NOT EXISTS device_state_history (
    id BIGSERIAL PRIMARY KEY,
    device_id INTEGER NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    state VARCHAR(100) NOT NULL,
    value TEXT
);

CREATE INDEX IF NOT EXISTS device_state_history_device_time_idx
    ON device_state_history (device_id, timestamp DESC);

INSERT INTO device_types (name, description) VALUES
    ('Hub/Controller', 'Automation controllers and protocol bridges'),
    ('Light', 'Smart bulbs, strips, switches and dimmers'),
    ('Plug/Outlet', 'Smart plugs, outlets and power strips'),
    ('Sensor', 'Environmental, motion and safety sensors'),
    ('Camera', 'Security cameras and video doorbells'),
    ('Computer', 'Desktop computers, servers and workstations'),
    ('Network Gear', 'Routers, switches and access points'),
    ('Microcontroller', 'Programmable embedded boards'),
    ('Single-Board Computer', 'Compact general-purpose computers')
ON CONFLICT (name) DO NOTHING;

INSERT INTO manufacturers (name, country, website) VALUES
    ('Aqara', 'China', 'https://www.aqara.com'),
    ('Apple', 'USA', 'https://www.apple.com'),
    ('Espressif Systems', 'China', 'https://www.espressif.com'),
    ('Philips', 'Netherlands', 'https://www.philips-hue.com'),
    ('Raspberry Pi', 'UK', 'https://www.raspberrypi.com'),
    ('TP-Link', 'China', 'https://www.tp-link.com'),
    ('Ubiquiti', 'USA', 'https://www.ui.com')
ON CONFLICT (name) DO NOTHING;

INSERT INTO suppliers (name, website) VALUES
    ('Amazon', 'https://www.amazon.com'),
    ('DigiKey', 'https://www.digikey.com'),
    ('Mouser Electronics', 'https://www.mouser.com'),
    ('Direct from Manufacturer', NULL)
ON CONFLICT (name) DO NOTHING;

INSERT INTO rooms (name, floor, description) VALUES
    ('Living Room', 1, 'Main living area'),
    ('Kitchen', 1, 'Kitchen and dining area'),
    ('Office', 1, 'Workspace'),
    ('Server Closet', 1, 'Network and server equipment')
ON CONFLICT (name) DO NOTHING;
