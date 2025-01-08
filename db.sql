CREATE TABLE generated_images (
    id SERIAL PRIMARY KEY,
    client_id UUID NOT NULL,
    prompt_id UUID NOT NULL,
    image_data BYTEA NOT NULL,
    image_url TEXT,
    file_size BIGINT,
    file_type TEXT,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
);