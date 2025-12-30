CREATE TABLE measurements (
    id SERIAL PRIMARY KEY,
    ic_name TEXT NOT NULL,
    ground_pin INTEGER NOT NULL,
    voltages FLOAT[] NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
