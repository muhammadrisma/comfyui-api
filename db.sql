CREATE TABLE generated_images (
    id SERIAL PRIMARY KEY,
    client_id UUID NOT NULL,
    prompt_id UUID NOT NULL,
    image_output_path TEXT NOT NULL,
    file_size BIGINT,
    file_type TEXT,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);