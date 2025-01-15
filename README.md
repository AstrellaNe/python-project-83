### Hexlet tests and linter status:
[![Actions Status](https://github.com/AstrellaNe/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/AstrellaNe/python-project-83/actions)

### Доступ к приложению на временном сервере (temp test server)
Получить доступ к развернутому приложению по следующему адресу:

[Посмотреть приложение](https://page-analyzer-project-83.onrender.com)


# Page Analyzer

Page Analyzer is a simple web application designed to manage and analyze URLs. It allows users to normalize, validate, and store URLs in a PostgreSQL database, ensuring no duplicates and providing a user-friendly interface.

## Features

- URL Normalization: Automatically adds `https://` to URLs without a protocol and handles input with or without `//`.
- Duplicate Detection: Prevents adding the same URL multiple times.
- Database Management: Add new URLs, view all added URLs, delete specific URLs, and view details of a specific URL.
- Validation and Error Handling: Ensures the URL format is valid and provides user feedback for successful operations and errors.
- User-friendly Interface: Built using Bootstrap for a clean and responsive design.

## How to Run

1. Clone the repository: `git clone https://github.com/AstrellaNe/python-project-83.git && cd python-project-83`
2. Install dependencies using Poetry: `make install`
3. Set up environment variables in a `.env` file:
   ```
   DATABASE_URL=your_database_url
   SECRET_KEY=your_secret_key
   ```
4. Start the application in development mode: `make dev`
5. Start the application in production mode: `make start`
6. Access the application:
   - Development: [http://127.0.0.1:5000](http://127.0.0.1:5000)
   - Production: [http://0.0.0.0:8000](http://0.0.0.0:8000)

## Requirements

- Python 3.10+
- PostgreSQL
- Flask
- Poetry (for dependency management)

## License

This project is open-source and available under the MIT License.




