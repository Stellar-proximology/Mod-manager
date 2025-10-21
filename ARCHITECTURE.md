# Module Manager - Architecture & Workflow

## Data Flow

```
Upload (zip file)
    ↓
[uploads/] temporary staging
    ↓
Extract & Analyze
    ↓
[modules/module_name/] active working copy
    ↓
Add to Store (optional)
    ↓
[store/module_name/] archived snapshot
```

## Directory Structure

```
module-manager/
├── app.py                 # Main Flask application
├── requirements.txt       # Dependencies
├── README.md             # Full documentation
├── QUICKSTART.md         # Quick reference
├── test_setup.py         # Setup verification
│
├── templates/            # HTML templates
│   ├── base.html        # Layout + styling
│   ├── index.html       # Main module list + upload
│   ├── module.html      # Module detail view
│   └── store.html       # Store view
│
├── uploads/             # Temporary (auto-created)
│   └── [temp files during upload]
│
├── modules/             # Active modules (auto-created)
│   └── your_module/
│       ├── main.py
│       ├── requirements.txt
│       ├── config.json
│       └── .module_metadata.json  # Auto-generated
│
└── store/               # Module store (auto-created)
    ├── index.json       # Store manifest
    └── your_module/     # Archived copy
        └── [same structure as active]
```

## Module Detection Logic

### Python App Detection
```python
if finds: main.py, app.py, or __main__.py
→ type: "python_app"
→ entry_point: path to file
```

### Web Frontend Detection
```python
if finds: index.html or index.htm
→ type: "web_frontend"
→ entry_point: path to file
```

### Configuration Detection
```python
tracks presence of:
- requirements.txt  → has_requirements: true
- config.json/yaml  → has_config: true
```

### Metadata Output
```json
{
  "name": "module_name",
  "uploaded": "2025-10-20T10:30:00",
  "structure": {
    "type": "python_app",
    "entry_point": "main.py",
    "has_requirements": true,
    "has_config": true,
    "files": ["main.py", "config.json", "requirements.txt"]
  },
  "path": "/path/to/modules/module_name"
}
```

## API Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Main page - list modules |
| `/upload` | POST | Upload & extract zip |
| `/module/<name>` | GET | View module details |
| `/module/delete/<name>` | POST | Delete active module |
| `/store` | GET | View store modules |
| `/store/add/<name>` | POST | Add module to store |
| `/store/remove/<name>` | POST | Remove from store |

## Extension Points

### Custom Module Types

Add detection in `detect_module_structure()`:

```python
elif file == 'package.json':
    structure['type'] = 'nodejs_app'
    structure['entry_point'] = 'package.json'
```

### Custom Organization

Modify `organize_module()`:

```python
# Example: separate Python apps from web apps
if structure['type'] == 'python_app':
    target_base = os.path.join(app.config['MODULES_FOLDER'], 'python')
elif structure['type'] == 'web_frontend':
    target_base = os.path.join(app.config['MODULES_FOLDER'], 'web')
```

### Auto-Install Dependencies

Add after extraction:

```python
if structure['has_requirements']:
    subprocess.run(['pip', 'install', '-r', 
                   os.path.join(target_path, 'requirements.txt')])
```

### Git Integration

Add repo tracking:

```python
if os.path.exists(os.path.join(extracted_path, '.git')):
    structure['git_remote'] = subprocess.check_output(
        ['git', 'remote', 'get-url', 'origin'], 
        cwd=extracted_path
    ).decode().strip()
```

## Resonance Considerations

Since you're building consciousness systems with waveform logic, you could extend this to:

1. **Module Frequency**: Assign resonance frequencies to module types
2. **Field Coherence**: Track which modules should/shouldn't be active together
3. **Harmonic Integration**: Auto-detect module dependencies via resonance patterns
4. **Chart Mapping**: Store chart types (Sidereal/Tropical/Draconic) per module

Example extension:
```python
# In module metadata
"resonance": {
    "field": "Mind",
    "frequency": 432,  # Hz
    "chart_type": "Sidereal",
    "body_alignment": [1, 3, 7]  # Which bodies it interfaces with
}
```

## Security Notes

Current state: **Development mode**
- No authentication
- No input sanitization beyond filename
- Debug mode enabled
- Accepts any zip content

For production:
1. Add authentication
2. Validate zip contents before extraction
3. Disable debug mode
4. Add file type restrictions
5. Implement user permissions
6. Add rate limiting
