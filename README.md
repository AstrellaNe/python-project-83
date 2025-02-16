### Hexlet tests and linter status:
[![Actions Status](https://github.com/AstrellaNe/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/AstrellaNe/python-project-83/actions)
[![CI](https://github.com/AstrellaNe/python-project-83/actions/workflows/ci.yml/badge.svg)](https://github.com/AstrellaNe/python-project-83/actions/workflows/ci.yml)
[![Maintainability](https://api.codeclimate.com/v1/badges/ca36f4e239b9247b92fa/maintainability)](https://codeclimate.com/github/AstrellaNe/python-project-83/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/ca36f4e239b9247b92fa/test_coverage)](https://codeclimate.com/github/AstrellaNe/python-project-83/test_coverage)

### Access to the deployed application
[View application (Render)](https://page-analyzer-project-83.onrender.com)

---

# Page Analyzer

**Page Analyzer** is a web application for analyzing web pages.  
It allows checking website availability and analyzing **SEO data**.

## 🔹 Key Features
- **Website availability analysis** – performs an HTTP request and checks the response status.
- **SEO analysis** – extracts the title (`<title>`), main heading (`<h1>`), and description (`meta description`).
- **PostgreSQL database** – stores checked URLs and their history of checks.
- **Duplicate protection** – prevents adding the same URL multiple times.
- **Error logging** – displays a message if the site is unavailable.

---

## 🚀 How to Run

### 🔹 Local Run
1. **Clone the repository**:
   ```sh
   git clone https://github.com/AstrellaNe/python-project-83.git
   cd python-project-83
   ```
2. **Install dependencies**:
   ```sh
   make install
   ```
3. **Set up environment variables (`.env`)**:
   ```sh
   DATABASE_URL=postgresql://user:password@localhost:5432/database
   SECRET_KEY=your_secret_key
   ```
4. **Create database tables**:
   ```sh
   make build
   ```
5. **Run the application**:
   - In **development** (Flask + Debug Mode):  
     ```sh
     make dev
     ```
   - In **production** (Gunicorn + PostgreSQL):  
     ```sh
     make start
     ```

6. **Open in browser**:
   - **Locally**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
   - **Deployed application**: [https://page-analyzer-project-83.onrender.com](https://page-analyzer-project-83.onrender.com)

---

## 📌 Requirements
- Python 3.10+
- PostgreSQL
- Flask, Requests, BeautifulSoup
- Poetry (dependency management)

---

## 📜 License
This project is available under the MIT license.

