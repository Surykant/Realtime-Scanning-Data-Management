# Realtime Scanning Data Management API

A robust FastAPI-based solution for managing CSV data ingestion, dynamic table creation, folder monitoring, and secure user management. Designed to handle high-volume CSV files with dynamic table structures, image handling, and advanced dashboard analytics.

---

## 🚀 Features

- User authentication with JWT
- Dynamic creation of database tables based on CSV or JSON schema
- Folder watcher that monitors folders (including network paths) for new CSV files
- Automatic data ingestion into MySQL with batching
- Configurable destination for processed files
- API for searching records in any table
- Retrieve base64-encoded images dynamically
- Dashboard analytics:  
  - Total rows  
  - Rows today  
  - Scanner-wise counts with flexible date filters
- Graceful watcher start/stop and folder activation/deactivation
- Extensible and modular architecture

---

## ✅ Installation

1. Clone the repository  
   ```bash
   git clone https://github.com/your-repo/realtime-scanning-data-management.git
   cd realtime-scanning-data-management

2. Create and activate a virtual environment
	python -m venv venv
	source venv/bin/activate   # Linux/Mac  
	.\venv\Scripts\activate    # Windows

3. Install dependencies
	pip install -r requirements.txt

4. Setup environment variables in .env
	DATABASE_URL=mysql+pymysql://username:password@host:port/dbname
	COPY_FILE_PATH=D:\Backup\CSV_Files\

## ▶️ Running Locally
	uvicorn main:app --host 0.0.0.0 --port 8000 --reload

##📚 API Endpoints

##✅ Authentication

	POST /auth/register – Create a new user

	POST /auth/login – Get JWT access token


##📁 Folder Management

POST /folders/add – Add and start folder watcher

POST /folders/{folder_id}/deactivate – Deactivate folder after processing remaining CSVs

DELETE /folders/delete/{folder_id} – Delete folder and stop watcher

##🧱 Table Operations

POST /tables/create – Create new table from JSON schema

GET /tables/list – Get list of all tables

POST /tables/delete/{table_name} – Delete a table

GET /tables/get-columns/{table_name} – Get column names of a table

GET /tables/count-rows – Get total row count (accurate count)

GET /tables/count-today – Get today’s row count

GET /tables/count-scannerwise – Get row count per scanner ID

GET /tables/count-scannerwise-today – Get today’s row count per scanner ID

GET /tables/search-record – Search data from a specific table column

##🖼️ Image Operations

GET /tables/image – Return base64 of image by providing csv_path and front_side_image

##⚡ Notes

1. Watcher supports both local and network paths (e.g., \\192.168.1.31\d\Scan Data\S1)

2.System fields automatically added:

	ScannerID, Processed, CreatedAt, CsvPath

3. For performance, CSV data is inserted in batches of 1000 rows

##📁 Project Structure
.
├── app
│   ├── database          # DB connection, models, and schema
│   ├── services          # Business logic (watcher, ingest CSV, dashboard analytics)
│   └── appsettings       # Configuration loader
├── routes                # API route definitions
├── main.py               # FastAPI entry point
├── .env                  # Environment variables
├── requirements.txt
└── README.md

##📊 Monitoring & Logs

1.Logging configured via logging module

2.Logs can be redirected to a file by configuring a logging handler
