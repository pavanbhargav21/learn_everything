Got it. I'll update the backend code to use the `session_scope` context manager as described. Here's how the backend modifications and complete files will look:

### `upload.py` (Backend)

```python
from flask_restful import Resource, reqparse
from flask import request, jsonify
from your_project import db
from your_project.models import Workflow, WorkflowMaster, KeyNameMapping, VolumeMatrix
from your_project.utils import process_plugin_master, process_workflow_master, process_key_names, process_volumes
from your_project.session_manager import session_scope

class UploadExcel(Resource):
    def post(self):
        # Parse the file from the request
        parser = reqparse.RequestParser()
        parser.add_argument('file', type='file', location='files', required=True)
        args = parser.parse_args()
        
        file = args['file']
        if not file:
            return {'message': 'No file provided'}, 400
        
        # Handle the file upload and processing
        try:
            with session_scope() as session:
                results = self.process_file(file, session)
            return jsonify(results)
        except Exception as e:
            return {'message': str(e)}, 500

    def process_file(self, file, session):
        # Load the Excel file and process sheets
        # Assuming you have a utility function to read and process Excel sheets
        plugin_master_data = process_plugin_master(file)
        workflow_master_data = process_workflow_master(file)
        key_names_data = process_key_names(file)
        volumes_data = process_volumes(file)
        
        results = {
            'plugin_master': self.process_plugin_master_data(plugin_master_data, session),
            'workflow_master': self.process_workflow_master_data(workflow_master_data, session),
            'key_names': self.process_key_names_data(key_names_data, session),
            'volumes': self.process_volumes_data(volumes_data, session),
        }
        return results
    
    def process_plugin_master_data(self, data, session):
        # Process Plugin Master sheet
        result = {'success': [], 'errors': []}
        for row in data:
            workflow_name = row.get('workflow_name')
            if not workflow_name:
                result['errors'].append(f"Missing workflow name in row: {row}")
                continue
            
            existing = session.query(Workflow).filter_by(name=workflow_name).first()
            if existing:
                continue  # Skip if it already exists
            
            # Add new entry
            new_workflow = Workflow(name=workflow_name, system=row.get('system'))
            session.add(new_workflow)
            result['success'].append(workflow_name)
        
        return result

    def process_workflow_master_data(self, data, session):
        # Process Workflow Master sheet
        result = {'success': [], 'errors': [], 'missing_workflow_names': []}
        for row in data:
            workflow_name = row.get('workflow_name')
            if not workflow_name:
                result['errors'].append(f"Missing workflow name in row: {row}")
                continue
            
            existing = session.query(Workflow).filter_by(name=workflow_name).first()
            if not existing:
                result['missing_workflow_names'].append(workflow_name)
                continue
            
            # Check for duplicates and add to whitelist
            existing_whitelist = session.query(WorkflowMaster).filter_by(
                workflow_name=workflow_name,
                virtual_url=row.get('virtual_url'),
                environment=row.get('environment'),
                window_titles=row.get('window_titles')
            ).first()
            
            if existing_whitelist:
                continue  # Skip if it already exists
            
            # Add new entry
            new_entry = WorkflowMaster(
                workflow_name=workflow_name,
                virtual_url=row.get('virtual_url'),
                environment=row.get('environment'),
                window_titles=row.get('window_titles')
            )
            session.add(new_entry)
            result['success'].append(workflow_name)
        
        return result

    def process_key_names_data(self, data, session):
        # Process Key Names sheet
        result = {'success': [], 'errors': [], 'missing_workflow_names': []}
        for row in data:
            workflow_name = row.get('workflow_name')
            if not workflow_name:
                result['errors'].append(f"Missing workflow name in row: {row}")
                continue
            
            existing = session.query(Workflow).filter_by(name=workflow_name).first()
            if not existing:
                result['missing_workflow_names'].append(workflow_name)
                continue
            
            # Check for duplicates and add to key name mapping
            existing_key_name = session.query(KeyNameMapping).filter_by(
                workflow_name=workflow_name,
                key_name=row.get('key_name'),
                layout=row.get('layout'),
                remarks=row.get('remarks')
            ).first()
            
            if existing_key_name:
                continue  # Skip if it already exists
            
            # Add new entry
            new_entry = KeyNameMapping(
                workflow_name=workflow_name,
                key_name=row.get('key_name'),
                layout=row.get('layout'),
                remarks=row.get('remarks')
            )
            session.add(new_entry)
            result['success'].append(workflow_name)
        
        return result

    def process_volumes_data(self, data, session):
        # Process Volumes sheet
        result = {'success': [], 'errors': [], 'missing_workflow_names': []}
        for row in data:
            workflow_name = row.get('workflow_name')
            if not workflow_name:
                result['errors'].append(f"Missing workflow name in row: {row}")
                continue
            
            existing = session.query(Workflow).filter_by(name=workflow_name).first()
            if not existing:
                result['missing_workflow_names'].append(workflow_name)
                continue
            
            # Check for duplicates and add to volume matrix
            existing_volume = session.query(VolumeMatrix).filter_by(
                workflow_name=workflow_name,
                pattern=row.get('pattern'),
                key_names=row.get('key_names'),
                key_type=row.get('key_type'),
                layout=row.get('layout')
            ).first()
            
            if existing_volume:
                continue  # Skip if it already exists
            
            # Add new entry
            new_entry = VolumeMatrix(
                workflow_name=workflow_name,
                pattern=row.get('pattern'),
                key_names=row.get('key_names'),
                key_type=row.get('key_type'),
                layout=row.get('layout')
            )
            session.add(new_entry)
            result['success'].append(workflow_name)
        
        return result
```

### `view.vue` (Frontend)

```vue
<template>
  <div>
    <v-tabs v-model="activeTab" fixed-tabs>
      <v-tab v-for="(item, index) in items" :key="index">{{ item }}</v-tab>
    </v-tabs>
    <v-btn @click="openUploadDialog">Upload Excel</v-btn>

    <v-dialog v-model="uploadDialogVisible" max-width="600">
      <v-card>
        <v-card-title class="title-bold-stylish">
          Please ensure your Excel file has the following format
        </v-card-title>
        <v-card-subtitle class="text-center">
          <v-btn @click="downloadTemplate" class="excel-bold-stylish">
            Download Template
          </v-btn>
        </v-card-subtitle>
        <v-card-text>
          <v-file-input @change="handleFileUpload" accept=".xlsx" label="Select File" />
        </v-card-text>
        <v-card-actions>
          <v-btn @click="uploadFile" :loading="isUploading" :disabled="isUploading">
            Upload
          </v-btn>
          <v-btn @click="closeUploadDialog">Cancel</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar" :color="snackbarColor">
      {{ snackbarText }}
    </v-snackbar>
  </div>
</template>

<script>
import axios from '../axios';
import EventBus from '../eventBus';

export default {
  data() {
    return {
      items: ['Workflow Master', 'Keyname Mapping', 'Volume Matrix'],
      activeTab: 0,
      storeDialogVisible: false,
      uploadDialogVisible: false,
      file: null,
      isUploading: false,
      snackbar: false,
      snackbarText: '',
      snackbarColor: 'success',
    };
  },
  methods: {
    openUploadDialog() {
      this.uploadDialogVisible = true;
    },
    closeUploadDialog() {
      this.uploadDialogVisible = false;
      this.file = null;
    },
    downloadTemplate() {
      const link = document.createElement('a');
      link.href = '/template.xlsx';
      link.download = 'template.xlsx';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    },
    handleFileUpload(event) {
      const fileInput = event.target;
      if (fileInput.files.length > 0) {
        this.file = fileInput.files[0];
      } else {
        this.file = null;
      }
    },
    async uploadFile() {
      if (!this.file) {
        this.showSnackbar('Please select a file', 'error');
        return;
      }

      this.isUploading = true;
      const formData = new FormData();
      formData.append('file', this.file);

      try {
        const response = await axios.post('/api/upload_excel/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });

        if (response.data) {
          this.showSnackbar('Upload Successful', 'success');
          EventBus.$emit('data-uploaded', response.data);
        } else {
          this.showSnackbar('Unexpected response Format', 'error');
        }
      } catch (error)












You're correct; in the code, I used `.capitalize()` to adjust the column names. This method might not be appropriate if your actual column names in the Excel sheets have specific capitalization requirements and no spaces. Given that your column names have a specific format (e.g., `WorkflowName`, `System`), they should be directly matched without altering their capitalization.

Here’s the revised code with the column names matched exactly as specified:

### Backend (Flask)

**`upload_excel.py`**
```python
from flask_restful import Resource, reqparse
from flask import request
import pandas as pd
from app import session_scope
from models import Workflow, Whitelist, KeyNameMapping, VolumeMatrix

class UploadExcel(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files', required=True)

    def post(self):
        args = self.parser.parse_args()
        file = args['file']
        
        if file and allowed_file(file.filename):
            try:
                with session_scope() as session:
                    # Read the Excel file
                    excel_data = pd.read_excel(file, sheet_name=None)
                    
                    results = {}
                    
                    # Process Plugin Master sheet
                    plugin_master_data = excel_data.get('PLUGIN_MASTER')
                    if plugin_master_data is not None:
                        if 'WorkflowName' in plugin_master_data.columns and 'System' in plugin_master_data.columns:
                            for _, row in plugin_master_data.iterrows():
                                workflow_name = row['WorkflowName']
                                system = row['System']
                                if not session.query(Workflow).filter_by(workflow_name=workflow_name).first():
                                    new_workflow = Workflow(workflow_name=workflow_name, system=system)
                                    session.add(new_workflow)
                    
                    # Process Workflow Master sheet
                    workflow_master_data = excel_data.get('WORKFLOW_MASTER')
                    if workflow_master_data is not None:
                        if all(col in workflow_master_data.columns for col in ['WorkflowName', 'WorkflowUrl', 'Environment', 'WindowTitles']):
                            for _, row in workflow_master_data.iterrows():
                                workflow_name = row['WorkflowName']
                                if session.query(Workflow).filter_by(workflow_name=workflow_name).first():
                                    if not session.query(Whitelist).filter_by(
                                        workflow_name=workflow_name,
                                        workflow_url=row['WorkflowUrl'],
                                        environment=row['Environment'],
                                        window_titles=row['WindowTitles']
                                    ).first():
                                        new_whitelist = Whitelist(
                                            workflow_name=workflow_name,
                                            workflow_url=row['WorkflowUrl'],
                                            environment=row['Environment'],
                                            window_titles=row['WindowTitles']
                                        )
                                        session.add(new_whitelist)
                                else:
                                    if 'missing_workflow_names' not in results:
                                        results['missing_workflow_names'] = []
                                    results['missing_workflow_names'].append(workflow_name)
                    
                    # Process Key Names sheet
                    key_names_data = excel_data.get('KEY_NAMES')
                    if key_names_data is not None:
                        if all(col in key_names_data.columns for col in ['WorkflowName', 'KeyName', 'Layout', 'Remarks']):
                            for _, row in key_names_data.iterrows():
                                workflow_name = row['WorkflowName']
                                if session.query(Workflow).filter_by(workflow_name=workflow_name).first():
                                    if not session.query(KeyNameMapping).filter_by(
                                        workflow_name=workflow_name,
                                        key_name=row['KeyName'],
                                        layout=row['Layout'],
                                        remarks=row['Remarks']
                                    ).first():
                                        new_keyname = KeyNameMapping(
                                            workflow_name=workflow_name,
                                            key_name=row['KeyName'],
                                            layout=row['Layout'],
                                            remarks=row['Remarks']
                                        )
                                        session.add(new_keyname)
                                else:
                                    if 'missing_workflow_names' not in results:
                                        results['missing_workflow_names'] = []
                                    results['missing_workflow_names'].append(workflow_name)
                    
                    # Process Volumes sheet
                    volumes_data = excel_data.get('VOLUMES')
                    if volumes_data is not None:
                        if all(col in volumes_data.columns for col in ['WorkflowName', 'Pattern', 'KeyName', 'KeyType', 'Layout']):
                            for _, row in volumes_data.iterrows():
                                workflow_name = row['WorkflowName']
                                if session.query(Workflow).filter_by(workflow_name=workflow_name).first():
                                    if not session.query(VolumeMatrix).filter_by(
                                        workflow_name=workflow_name,
                                        pattern=row['Pattern'],
                                        key_name=row['KeyName'],
                                        key_type=row['KeyType'],
                                        layout=row['Layout']
                                    ).first():
                                        new_volume = VolumeMatrix(
                                            workflow_name=workflow_name,
                                            pattern=row['Pattern'],
                                            key_name=row['KeyName'],
                                            key_type=row['KeyType'],
                                            layout=row['Layout']
                                        )
                                        session.add(new_volume)
                                else:
                                    if 'missing_workflow_names' not in results:
                                        results['missing_workflow_names'] = []
                                    results['missing_workflow_names'].append(workflow_name)
                    
                    return {'status': 'success', 'data': results}, 200
            
            except Exception as e:
                return {'status': 'error', 'message': str(e)}, 500

def allowed_file(filename):
    allowed_extensions = {'xls', 'xlsx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
```

### Summary of Updates:
- **Column Names Matching:** Ensured the column names are used exactly as provided, with no modifications to capitalization or spacing.

























**Instructions for Uploading Data**

1. **Do Not Alter Sheet Names or Column Names**:
   - The sheet names and column names in this workbook are crucial for processing your data. Do not change them.

2. **Entering Data**:
   - Enter your data in the specified sheets according to the column headings provided.

3. **Workflow Names**:
   - If you are adding a new workflow name, ensure that the workflow name already exists in the 'Plugin Master' sheet.
   - You must list any new workflow names in the 'Plugin Master' sheet. This is necessary for your data to be accepted.

4. **Saving Your File**:
   - Save your changes and ensure that the file is saved in `.xlsx` format before uploading it.

**Thank you for following these instructions.**






<template>
  <v-container>
    <v-file-input
      v-model="file"
      label="Upload File"
      @change="handleFileUpload"
      accept=".csv, .xlsx, .xls"
    ></v-file-input>
    
    <!-- Display Success and Error Messages -->
    <v-dialog v-model="dialog" max-width="600">
      <v-card>
        <v-card-title>
          <span class="headline">Upload Results</span>
        </v-card-title>
        <v-card-text>
          <v-alert v-if="results.errors.length" type="error">
            <ul>
              <li v-for="(error, index) in results.errors" :key="index">
                Row {{ error.row }}: {{ error.error }}
              </li>
            </ul>
          </v-alert>
          
          <v-alert v-if="results.success.length" type="success">
            Successfully processed {{ results.success.length }} rows.
          </v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="dialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
export default {
  data() {
    return {
      file: null,
      dialog: false,
      results: {
        success: [],
        errors: []
      }
    };
  },
  methods: {
    async handleFileUpload() {
      const formData = new FormData();
      formData.append('file', this.file);

      try {
        const response = await fetch('/upload', {
          method: 'POST',
          body: formData
        });
        const data = await response.json();
        
        this.results = data;
        this.dialog = true;
      } catch (error) {
        console.error('Error uploading file:', error);
      }
    }
  }
};
</script>






<template>
  <v-container>
    <v-file-input
      v-model="file"
      label="Upload File"
      @change="handleFileUpload"
      accept=".csv, .xlsx, .xls"
    ></v-file-input>
    
    <!-- Display Success and Error Messages -->
    <v-dialog v-model="dialog" max-width="600">
      <v-card>
        <v-card-title>
          <span class="headline">Upload Results</span>
        </v-card-title>
        <v-card-text>
          <v-alert v-if="results.errors.length" type="error">
            <ul>
              <li v-for="(error, index) in results.errors" :key="index">
                Row {{ error.row }}: {{ error.error }}
              </li>
            </ul>
          </v-alert>
          
          <v-alert v-if="results.success.length" type="success">
            Successfully processed {{ results.success.length }} rows.
          </v-alert>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="dialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
export default {
  data() {
    return {
      file: null,
      dialog: false,
      results: {
        success: [],
        errors: []
      }
    };
  },
  methods: {
    async handleFileUpload() {
      const formData = new FormData();
      formData.append('file', this.file);

      try {
        const response = await fetch('/upload', {
          method: 'POST',
          body: formData
        });
        const data = await response.json();
        
        this.results = data;
        this.dialog = true;
      } catch (error) {
        console.error('Error uploading file:', error);
      }
    }
  }
};
</script>




import os
import pandas as pd
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify
from flask_restful import Resource
from flask_cors import cross_origin
from datetime import datetime

# ... other necessary imports and Flask setup ...

class KeyNameMappingUploadResource(Resource):
    @cross_origin()
    def post(self):
        if 'file' not in request.files:
            return jsonify({'message': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'message': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join('/tmp', filename)
            file.save(file_path)
            
            results = {'success': [], 'errors': []}
            
            try:
                df = pd.read_excel(file_path) if filename.endswith(('xlsx', 'xls')) else pd.read_csv(file_path)
                
                with session_scope() as session:
                    for index, row in df.iterrows():
                        try:
                            workflow = session.query(Workflow).filter_by(workflow_name=row['workflowname']).first()
                            if workflow:
                                existing_mapping = session.query(KeyNameMapping).filter_by(
                                    workflow_id=workflow.id,
                                    activity_key_name=row['keyname']
                                ).first()
                                if not existing_mapping:
                                    new_mapping = KeyNameMapping(
                                        workflow_id=workflow.id,
                                        activity_key_name=row['keyname'],
                                        activity_key_layout=row['layout'],
                                        remarks=row['remarks'],
                                        is_active=True,
                                        created_date=datetime.utcnow()
                                    )
                                    session.add(new_mapping)
                                    results['success'].append(row.to_dict())
                                else:
                                    results['errors'].append({
                                        'row': index,
                                        'error': 'Duplicate key name mapping'
                                    })
                            else:
                                results['errors'].append({
                                    'row': index,
                                    'error': 'Workflow not found'
                                })
                        except Exception as e:
                            results['errors'].append({
                                'row': index,
                                'error': str(e)
                            })
                
                os.remove(file_path)
                return jsonify(results), 200
            
            except Exception as e:
                os.remove(file_path)
                return jsonify({'message': f'Error processing file: {str(e)}'}), 500
        
        return jsonify({'message': 'File type not allowed'}), 400

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'xlsx', 'xls'}

api.add_resource(KeyNameMappingUploadResource, '/upload')



import os
import pandas as pd
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify
from flask_restful import Resource
from flask_cors import cross_origin
from datetime import datetime

class VolumeMatrixUploadResource(Resource):
    @cross_origin()
    def post(self):
        if 'file' not in request.files:
            return jsonify({'message': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'message': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join('/tmp', filename)
            file.save(file_path)
            
            results = {'success': [], 'errors': []}
            
            try:
                df = pd.read_excel(file_path) if filename.endswith(('xlsx', 'xls')) else pd.read_csv(file_path)
                
                with session_scope() as session:
                    for index, row in df.iterrows():
                        try:
                            workflow = session.query(Workflow).filter_by(workflow_name=row['workflowname']).first()
                            if workflow:
                                existing_volume = session.query(VolumeMatrix).filter_by(
                                    workflow_id=workflow.id,
                                    pattern=row['pattern'],
                                    activity_key_name=row['volumekey']
                                ).first()
                                if not existing_volume:
                                    new_volume = VolumeMatrix(
                                        workflow_id=workflow.id,
                                        pattern=row['pattern'],
                                        activity_key_name=row['volumekey'],
                                        activity_key_type=row['type'],
                                        activity_key_layout=row['layout'],
                                        is_active=True,
                                        created_date=datetime.utcnow()
                                    )
                                    session.add(new_volume)
                                    results['success'].append(row.to_dict())
                                else:
                                    results['errors'].append({
                                        'row': index,
                                        'error': 'Duplicate volume matrix entry'
                                    })
                            else:
                                results['errors'].append({
                                    'row': index,
                                    'error': 'Workflow not found'
                                })
                        except Exception as e:
                            results['errors'].append({
                                'row': index,
                                'error': str(e)
                            })
                
                os.remove(file_path)
                return jsonify(results), 200
            
            except Exception as e:
                os.remove(file_path)
                return jsonify({'message': f'Error processing file: {str(e)}'}), 500
        
        return jsonify({'message': 'File type not allowed'}), 400

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'xlsx', 'xls'}

api.add_resource(VolumeMatrixUploadResource, '/upload')






import os
import pandas as pd
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify
from flask_restful import Resource
from flask_cors import cross_origin
from datetime import datetime

class WorkflowUploadResource(Resource):
    @cross_origin()
    def post(self):
        if 'file' not in request.files:
            return jsonify({'message': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'message': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join('/tmp', filename)
            file.save(file_path)
            
            results = {'success': [], 'errors': []}
            
            try:
                df = pd.read_excel(file_path) if filename.endswith(('xlsx', 'xls')) else pd.read_csv(file_path)
                
                with session_scope() as session:
                    for index, row in df.iterrows():
                        try:
                            existing_workflow = session.query(Workflow).filter_by(workflow_name=row['workflow name']).first()
                            if not existing_workflow:
                                new_workflow = Workflow(
                                    workflow_name=row['workflow name'],
                                    system_name=row['workflow url'].split('://')[1].split('.')[0],
                                    created_date=datetime.utcnow()
                                )
                                session.add(new_workflow)
                                results['success'].append(row.to_dict())
                            else:
                                results['errors'].append({
                                    'row': index,
                                    'error': 'Duplicate workflow entry'
                                })
                            
                            existing_whitelist = session.query(Whitelist).filter_by(workflow_name=row['workflow name']).first()
                            if not existing_whitelist:
                                new_whitelist = Whitelist(
                                    workflow_name=row['workflow name'],
                                    workflow_url=row['workflow url'],
                                    environment=row['environment'],
                                    window_titles=row['window titles'],
                                    is_active=True,
                                    created_date=datetime.utcnow()
                                )
                                session.add(new_whitelist)
                            else:
                                results['errors'].append({
                                    'row': index,
                                    'error': 'Duplicate whitelist entry'
                                })
                        
                        except Exception as e:
                            results['errors'].append({
                                'row': index,
                                'error': str(e)
                            })
                
                os.remove(file_path)
                return jsonify({'message': f'Error processing file: {str(e)}'}), 500
        
        return jsonify({'message': 'File type not allowed'}), 400

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'xlsx', 'xls'}

api.add_resource(WorkflowUploadResource, '/upload')













To implement the Excel Upload functionality as you've described, we'll need to make changes to both the frontend and backend code. Let's start with the frontend changes:

1. First, we'll modify the `WorkflowMaster.vue` file to include the Excel Upload button and its functionality:

```vue
<template>
  <v-card>
    <!-- ... existing code ... -->
    <v-toolbar color="black">
      <!-- ... existing code ... -->
      <v-spacer></v-spacer>

      <v-btn
        class="excel-bold-stylish"
        @click="openUploadDialog"
      >
        {{ uploadButtonText }}
        <v-icon
          icon="mdi-file-upload"
          color="red"
          end
        ></v-icon>
      </v-btn>
    </v-toolbar>

    <!-- ... existing code ... -->

    <v-dialog v-model="uploadDialogVisible" max-width="500px">
      <v-card>
        <v-card-title>Upload {{ uploadButtonText }}</v-card-title>
        <v-card-text>
          <p>Please ensure your Excel file has the following columns:</p>
          <ul>
            <li v-for="column in requiredColumns" :key="column">{{ column }}</li>
          </ul>
          <v-file-input
            v-model="file"
            label="Select Excel File"
            accept=".xlsx, .xls, .csv"
            @change="handleFileUpload"
          ></v-file-input>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="uploadFile" :loading="isUploading">Upload</v-btn>
          <v-btn color="error" @click="closeUploadDialog">Cancel</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar" :color="snackbarColor">
      {{ snackbarText }}
    </v-snackbar>
  </v-card>
</template>

<script>
import axios from '../axios';
// ... existing imports ...

export default {
  // ... existing code ...

  data() {
    return {
      // ... existing data ...
      uploadDialogVisible: false,
      file: null,
      isUploading: false,
      snackbar: false,
      snackbarText: '',
      snackbarColor: 'success',
    };
  },

  computed: {
    uploadButtonText() {
      const texts = ['Upload Workflows', 'Upload Keynames', 'Upload Volumes'];
      return texts[this.activeTab];
    },
    requiredColumns() {
      const columns = [
        ['workflow name', 'workflow url', 'window titles', 'environment'],
        ['workflowname', 'keyname', 'layout', 'remarks'],
        ['workflowname', 'pattern', 'volumekey', 'type', 'layout']
      ];
      return columns[this.activeTab];
    }
  },

  methods: {
    // ... existing methods ...

    openUploadDialog() {
      this.uploadDialogVisible = true;
    },

    closeUploadDialog() {
      this.uploadDialogVisible = false;
      this.file = null;
    },

    handleFileUpload(file) {
      this.file = file;
    },

    async uploadFile() {
      if (!this.file) {
        this.showSnackbar('Please select a file', 'error');
        return;
      }

      this.isUploading = true;

      const formData = new FormData();
      formData.append('file', this.file);

      try {
        const endpoint = ['/api/workflows/upload', '/api/keynamemapping/upload', '/api/volumematrix/upload'][this.activeTab];
        const response = await axios.post(endpoint, formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });

        this.showSnackbar(response.data.message, 'success');
        this.closeUploadDialog();
        
        // Refresh the data
        if (this.activeTab === 0) this.fetchWorkflowNames();
        else if (this.activeTab === 1) EventBus.$emit('keynamemapping-added');
        else if (this.activeTab === 2) EventBus.$emit('volume-added');
      } catch (error) {
        this.showSnackbar(error.response?.data?.message || 'Upload failed', 'error');
      } finally {
        this.isUploading = false;
      }
    },

    showSnackbar(text, color) {
      this.snackbarText = text;
      this.snackbarColor = color;
      this.snackbar = true;
    }
  }
};
</script>
```

Now, let's update the backend to handle file uploads for each tab:

1. First, install the necessary packages:
```
pip install pandas openpyxl
```

2. Update `workflows.py`:

```python
from flask import request, jsonify
from werkzeug.utils import secure_filename
import pandas as pd
import os

# ... existing code ...

class WorkflowUploadResource(Resource):
    @cross_origin()
    def post(self):
        if 'file' not in request.files:
            return jsonify({'message': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'message': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join('/tmp', filename)
            file.save(file_path)
            
            try:
                df = pd.read_excel(file_path) if filename.endswith(('xlsx', 'xls')) else pd.read_csv(file_path)
                
                with session_scope() as session:
                    for _, row in df.iterrows():
                        existing_workflow = session.query(Workflow).filter_by(workflow_name=row['workflow name']).first()
                        if not existing_workflow:
                            new_workflow = Workflow(
                                workflow_name=row['workflow name'],
                                system_name=row['workflow url'].split('://')[1].split('.')[0],
                                created_date=datetime.utcnow()
                            )
                            session.add(new_workflow)
                        
                        existing_whitelist = session.query(Whitelist).filter_by(workflow_name=row['workflow name']).first()
                        if not existing_whitelist:
                            new_whitelist = Whitelist(
                                workflow_name=row['workflow name'],
                                workflow_url=row['workflow url'],
                                environment=row['environment'],
                                window_titles=row['window titles'],
                                is_active=True,
                                created_date=datetime.utcnow()
                            )
                            session.add(new_whitelist)
                
                os.remove(file_path)
                return jsonify({'message': 'File uploaded and processed successfully'}), 200
            
            except Exception as e:
                os.remove(file_path)
                return jsonify({'message': f'Error processing file: {str(e)}'}), 500
        
        return jsonify({'message': 'File type not allowed'}), 400

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'xlsx', 'xls'}

api.add_resource(WorkflowUploadResource, '/upload')
```

3. Update `keynamemapping.py`:

```python
# ... existing imports ...
import pandas as pd
import os
from werkzeug.utils import secure_filename

# ... existing code ...

class KeyNameMappingUploadResource(Resource):
    @cross_origin()
    def post(self):
        if 'file' not in request.files:
            return jsonify({'message': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'message': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join('/tmp', filename)
            file.save(file_path)
            
            try:
                df = pd.read_excel(file_path) if filename.endswith(('xlsx', 'xls')) else pd.read_csv(file_path)
                
                with session_scope() as session:
                    for _, row in df.iterrows():
                        workflow = session.query(Workflow).filter_by(workflow_name=row['workflowname']).first()
                        if workflow:
                            existing_mapping = session.query(KeyNameMapping).filter_by(
                                workflow_id=workflow.id,
                                activity_key_name=row['keyname']
                            ).first()
                            if not existing_mapping:
                                new_mapping = KeyNameMapping(
                                    workflow_id=workflow.id,
                                    activity_key_name=row['keyname'],
                                    activity_key_layout=row['layout'],
                                    remarks=row['remarks'],
                                    is_active=True,
                                    created_date=datetime.utcnow()
                                )
                                session.add(new_mapping)
                
                os.remove(file_path)
                return jsonify({'message': 'File uploaded and processed successfully'}), 200
            
            except Exception as e:
                os.remove(file_path)
                return jsonify({'message': f'Error processing file: {str(e)}'}), 500
        
        return jsonify({'message': 'File type not allowed'}), 400

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'xlsx', 'xls'}

api.add_resource(KeyNameMappingUploadResource, '/upload')
```

4. Update `volumematrix.py`:

```python
# ... existing imports ...
import pandas as pd
import os
from werkzeug.utils import secure_filename

# ... existing code ...

class VolumeMatrixUploadResource(Resource):
    @cross_origin()
    def post(self):
        if 'file' not in request.files:
            return jsonify({'message': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'message': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join('/tmp', filename)
            file.save(file_path)
            
            try:
                df = pd.read_excel(file_path) if filename.endswith(('xlsx', 'xls')) else pd.read_csv(file_path)
                
                with session_scope() as session:
                    for _, row in df.iterrows():
                        workflow = session.query(Workflow).filter_by(workflow_name=row['workflowname']).first()
                        if workflow:
                            existing_volume = session.query(VolumeMatrix).filter_by(
                                workflow_id=workflow.id,
                                pattern=row['pattern'],
                                activity_key_name=row['volumekey']
                            ).first()
                            if not existing_volume:
                                new_volume = VolumeMatrix(
                                    workflow_id=workflow.id,
                                    pattern=row['pattern'],
                                    activity_key_name=row['volumekey'],
                                    activity_key_type=row['type'],
                                    activity_key_layout=row['layout'],
                                    is_active=True,
                                    created_date=datetime.utcnow()
                                )
                                session.add(new_volume)
                
                os.remove(file_path)
                return jsonify({'message': 'File uploaded and processed successfully'}), 200
            
            except Exception as e:
                os.remove(file_path)
                return jsonify({'message': f'Error processing file: {str(e)}'}), 500
        
        return jsonify({'message': 'File type not allowed'}), 400

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv', 'xlsx', 'xls'}

api.add_resource(VolumeMatrixUploadResource, '/upload')
```

These changes will:

1. Add an "Upload" button that changes its text based on the active tab.
2. Open a dialog when the upload button is clicked, showing the required columns for the file.
3. Allow the user to select and upload an Excel or CSV file.
4. Process the uploaded file on the backend, adding new entries to the database while ignoring duplicates.
5. Show a loading indicator during the upload process.
6. Display success or error messages using a snackbar.
7. Refresh the data after a successful upload.

Make sure to test these changes thoroughly and adjust as needed for your specific requirements and environment.
