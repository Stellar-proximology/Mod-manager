from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
import os
import zipfile
import shutil
import json
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MODULES_FOLDER'] = 'modules'
app.config['STORE_FOLDER'] = 'store'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max

# Ensure directories exist
for folder in [app.config['UPLOAD_FOLDER'], app.config['MODULES_FOLDER'], app.config['STORE_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

ALLOWED_EXTENSIONS = {'zip'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_store_index():
    """Load the store index JSON"""
    index_path = os.path.join(app.config['STORE_FOLDER'], 'index.json')
    if os.path.exists(index_path):
        with open(index_path, 'r') as f:
            return json.load(f)
    return {'modules': []}

def save_store_index(data):
    """Save the store index JSON"""
    index_path = os.path.join(app.config['STORE_FOLDER'], 'index.json')
    with open(index_path, 'w') as f:
        json.dump(data, f, indent=2)

def detect_module_structure(extracted_path):
    """Detect what kind of module this is based on structure"""
    structure = {
        'type': 'unknown',
        'entry_point': None,
        'has_requirements': False,
        'has_config': False,
        'files': []
    }
    
    for root, dirs, files in os.walk(extracted_path):
        rel_root = os.path.relpath(root, extracted_path)
        for file in files:
            rel_path = os.path.join(rel_root, file) if rel_root != '.' else file
            structure['files'].append(rel_path)
            
            # Detect entry points
            if file in ['main.py', 'app.py', '__main__.py']:
                structure['entry_point'] = rel_path
                structure['type'] = 'python_app'
            elif file in ['index.html', 'index.htm']:
                structure['type'] = 'web_frontend'
                structure['entry_point'] = rel_path
            elif file == 'requirements.txt':
                structure['has_requirements'] = True
            elif file in ['config.json', 'config.yaml', 'config.yml', 'settings.json']:
                structure['has_config'] = True
    
    return structure

def organize_module(module_name, extracted_path, structure):
    """Organize extracted module into appropriate location"""
    target_path = os.path.join(app.config['MODULES_FOLDER'], module_name)
    
    # Remove target if exists
    if os.path.exists(target_path):
        shutil.rmtree(target_path)
    
    # Move to modules folder
    shutil.move(extracted_path, target_path)
    
    return target_path

@app.route('/')
def index():
    """Main page showing current modules"""
    modules = []
    store_index = load_store_index()
    
    # Get active modules
    if os.path.exists(app.config['MODULES_FOLDER']):
        for item in os.listdir(app.config['MODULES_FOLDER']):
            module_path = os.path.join(app.config['MODULES_FOLDER'], item)
            if os.path.isdir(module_path):
                # Check if in store
                in_store = any(m['name'] == item for m in store_index['modules'])
                modules.append({
                    'name': item,
                    'path': module_path,
                    'in_store': in_store
                })
    
    return render_template('index.html', modules=modules, store_count=len(store_index['modules']))

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle zip file upload and extraction"""
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        module_name = request.form.get('module_name', '')
        
        # Use provided name or derive from filename
        if not module_name:
            module_name = filename.rsplit('.', 1)[0]
        
        module_name = secure_filename(module_name)
        
        # Save uploaded file
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)
        
        try:
            # Extract zip
            extract_path = os.path.join(app.config['UPLOAD_FOLDER'], f'extracted_{module_name}')
            os.makedirs(extract_path, exist_ok=True)
            
            with zipfile.ZipFile(upload_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            
            # Detect structure
            structure = detect_module_structure(extract_path)
            
            # Organize module
            final_path = organize_module(module_name, extract_path, structure)
            
            # Save metadata
            metadata = {
                'name': module_name,
                'uploaded': datetime.now().isoformat(),
                'structure': structure,
                'path': final_path
            }
            
            metadata_path = os.path.join(final_path, '.module_metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Clean up
            os.remove(upload_path)
            
            flash(f'Module "{module_name}" uploaded and organized successfully!', 'success')
            
        except Exception as e:
            flash(f'Error processing zip: {str(e)}', 'error')
            # Clean up on error
            if os.path.exists(upload_path):
                os.remove(upload_path)
            if os.path.exists(extract_path):
                shutil.rmtree(extract_path)
        
        return redirect(url_for('index'))
    
    flash('Invalid file type. Only .zip files allowed.', 'error')
    return redirect(url_for('index'))

@app.route('/module/<module_name>')
def view_module(module_name):
    """View module details"""
    module_path = os.path.join(app.config['MODULES_FOLDER'], module_name)
    
    if not os.path.exists(module_path):
        flash('Module not found', 'error')
        return redirect(url_for('index'))
    
    # Load metadata
    metadata_path = os.path.join(module_path, '.module_metadata.json')
    metadata = {}
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
    
    # Get file tree
    file_tree = []
    for root, dirs, files in os.walk(module_path):
        rel_root = os.path.relpath(root, module_path)
        level = rel_root.count(os.sep)
        for file in files:
            if file != '.module_metadata.json':
                file_tree.append({
                    'name': file,
                    'path': os.path.join(rel_root, file) if rel_root != '.' else file,
                    'level': level
                })
    
    return render_template('module.html', module_name=module_name, metadata=metadata, file_tree=file_tree)

@app.route('/store')
def store():
    """View store modules"""
    store_index = load_store_index()
    return render_template('store.html', modules=store_index['modules'])

@app.route('/store/add/<module_name>', methods=['POST'])
def add_to_store(module_name):
    """Add a module to the store"""
    module_path = os.path.join(app.config['MODULES_FOLDER'], module_name)
    
    if not os.path.exists(module_path):
        return jsonify({'error': 'Module not found'}), 404
    
    # Load metadata
    metadata_path = os.path.join(module_path, '.module_metadata.json')
    metadata = {}
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
    
    # Copy to store
    store_path = os.path.join(app.config['STORE_FOLDER'], module_name)
    if os.path.exists(store_path):
        shutil.rmtree(store_path)
    
    shutil.copytree(module_path, store_path)
    
    # Update store index
    store_index = load_store_index()
    
    # Remove if already exists
    store_index['modules'] = [m for m in store_index['modules'] if m['name'] != module_name]
    
    # Add new entry
    store_index['modules'].append({
        'name': module_name,
        'added': datetime.now().isoformat(),
        'metadata': metadata
    })
    
    save_store_index(store_index)
    
    flash(f'Module "{module_name}" added to store!', 'success')
    return jsonify({'success': True})

@app.route('/store/remove/<module_name>', methods=['POST'])
def remove_from_store(module_name):
    """Remove a module from the store"""
    store_index = load_store_index()
    store_index['modules'] = [m for m in store_index['modules'] if m['name'] != module_name]
    save_store_index(store_index)
    
    # Remove directory
    store_path = os.path.join(app.config['STORE_FOLDER'], module_name)
    if os.path.exists(store_path):
        shutil.rmtree(store_path)
    
    flash(f'Module "{module_name}" removed from store!', 'success')
    return jsonify({'success': True})

@app.route('/module/delete/<module_name>', methods=['POST'])
def delete_module(module_name):
    """Delete a module"""
    module_path = os.path.join(app.config['MODULES_FOLDER'], module_name)
    
    if os.path.exists(module_path):
        shutil.rmtree(module_path)
        flash(f'Module "{module_name}" deleted!', 'success')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
