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
