-- Устанавливаем кодировку
SET client_encoding = 'UTF8';
SET search_path TO public;

-- Создаём таблицу URLs
CREATE TABLE public.urls (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Создаём таблицу проверок URL
CREATE TABLE public.url_checks (
    id SERIAL PRIMARY KEY,
    url_id INTEGER NOT NULL REFERENCES public.urls(id) ON DELETE CASCADE,
    status_code INTEGER,
    h1 TEXT,
    title TEXT,
    description TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Гранты (разрешения) для пользователя admin
GRANT ALL ON TABLE public.urls TO admin;
GRANT ALL ON TABLE public.url_checks TO admin;
GRANT ALL ON SEQUENCE public.url_checks_id_seq TO admin;
