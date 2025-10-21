# Module Manager - Quick Start

## Install & Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Open browser to: **http://localhost:5000**

## First Upload

1. Click "Choose File" and select `test_module.zip` (included)
2. Click "Upload & Extract"
3. Module appears in the grid below
4. Click "View" to see structure and metadata
5. Click "Add to Store" to archive it

## What Happens

When you upload a zip:
1. **Extracts** to `modules/module_name/`
2. **Detects** structure (Python app, web frontend, etc.)
3. **Catalogs** entry points, requirements, config files
4. **Stores** metadata in `.module_metadata.json`

## Use Cases

- **Modular App Development**: Keep different app modules separated and organized
- **Version Management**: Store snapshots in the Store while working on active versions
- **Quick Deployment**: Upload zipped apps and they auto-organize
- **Multi-Project Management**: Work with multiple isolated modules

## Key Directories

```
modules/       # Active working modules
store/         # Archived versions (independent copies)
uploads/       # Temporary staging (auto-cleanup)
```

## Store vs Active

- **Active Modules** (`modules/`): Your working directory
- **Store** (`store/`): Backup/archive copies
- Deleting an active module doesn't affect the store
- You can have the same module in both places

## Customize

Edit `app.py` to:
- Change auto-detection logic (`detect_module_structure`)
- Add custom organization rules (`organize_module`)
- Modify file placement patterns
- Add new module types

## Port/Host

Default: `localhost:5000`

Change in `app.py` last line:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

Use `host='0.0.0.0'` to allow network access.
