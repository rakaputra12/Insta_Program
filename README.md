# Software Engineering

Raka Adita


## Query to build the Database


``` sql
CREATE TABLE scheduled_posts (
    id SERIAL PRIMARY KEY,
    post_type VARCHAR(50) NOT NULL,
    caption TEXT NOT NULL,
    hashtags TEXT NOT NULL,
    media_path TEXT NOT NULL,
    scheduled_time TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'pending'
);
```