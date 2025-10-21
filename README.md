# Module Manager

A Flask app for managing modular zipped applications. Upload zips, auto-extract, organize, and store multiple versions.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Then open: `http://localhost:5000`

## What It Does

1. **Upload & Extract**: Drop a zip file, it auto-extracts and organizes
2. **Auto-Detection**: Detects Python apps, web frontends, configs, requirements
3. **Store System**: Archive modules separately from active ones
4. **File Browser**: View structure and metadata for each module

## Structure Created

```
modules/          # Active modules (working directory)
  └─ your_module/
store/           # Archived copies
  └─ your_module/
  └─ index.json  # Store manifest
uploads/         # Temporary (auto-cleaned)
```

## Features

- Auto-extracts zips into `modules/your_module_name/`
- Detects entry points (main.py, app.py, index.html)
- Flags requirements.txt and config files
- Store system for keeping multiple versions
- Clean UI with file tree viewer
- Metadata tracking (upload date, structure type, etc.)

## Module Detection

The system auto-detects:
- `python_app`: If it finds main.py, app.py, or __main__.py
- `web_frontend`: If it finds index.html
- `unknown`: Everything else
- Tracks: entry point, requirements, config files

## Store Usage

- **Add to Store**: Creates a separate copy in `store/` directory
- **Remove from Store**: Deletes the stored copy
- **Delete Module**: Removes from active `modules/` (store copy persists)

Store index is tracked in `store/index.json` - contains all archived module metadata.

## API Endpoints

- `GET /` - Main page
- `POST /upload` - Upload zip
- `GET /module/<name>` - View module details
- `GET /store` - View store
- `POST /store/add/<name>` - Add to store
- `POST /store/remove/<name>` - Remove from store
- `POST /module/delete/<name>` - Delete module

## Notes

- Max upload: 500MB
- Only .zip files accepted
- Module names auto-sanitized
- Duplicate uploads overwrite existing
- Store copies are independent backups
