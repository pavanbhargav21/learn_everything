from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import jwt_required
from ..models import db, Whitelist, Workflow

bp = Blueprint('whitelists', __name__, url_prefix='/api/whitelists')
api = Api(bp)

class WhitelistResource(Resource):
    @jwt_required()
    def get(self):
        whitelists = Whitelist.query.all()
        data = [{
            'id': w.id,
            'workflowid': w.workflowid,
            'workflowname': Workflow.query.get(w.workflowid).workflowname,
            'url': w.url,
            'system': w.system,
            'layout': w.layout,
            'created_date': w.created_date,
            'updated_date': w.updated_date
        } for w in whitelists]
        return jsonify(data)

    @jwt_required()
    def post(self):
        data = request.get_json()
        new_whitelist = Whitelist(
            workflowid=data['workflowid'],
            url=data['url'],
            system=data['system'],
            layout=data['layout']
        )
        db.session.add(new_whitelist)
        db.session.commit()
        return jsonify({'message': 'Whitelist entry created successfully'}), 201

class WhitelistDetailResource(Resource):
    @jwt_required()
    def put(self, id):
        data = request.get_json()
        whitelist = Whitelist.query.get(id)
        if not whitelist:
            return {'message': 'Whitelist entry not found'}, 404

        whitelist.workflowid = data['workflowid']
        whitelist.url = data['url']
        whitelist.system = data['system']
        whitelist.layout = data['layout']
        whitelist.updated_date = datetime.utcnow()

        db.session.commit()
        return {'message': 'Whitelist entry updated successfully'}, 200

    @jwt_required()
    def delete(self, id):
        whitelist = Whitelist.query.get(id)
        if not whitelist:
            return {'message': 'Whitelist entry not found'}, 404

        db.session.delete(whitelist)
        db.session.commit()
        return {'message': 'Whitelist entry deleted successfully'}, 200

api.add_resource(WhitelistResource, '/')
api.add_resource(WhitelistDetailResource, '/<int:id>')


++++++++++-------------------

from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required
from ..models import db, Workflow

bp = Blueprint('workflows', __name__, url_prefix='/api/workflows')
api = Api(bp)

class WorkflowResource(Resource):
    @jwt_required()
    def get(self):
        workflows = Workflow.query.all()
        data = [{'id': w.id, 'workflowname': w.workflowname, 'system': w.system} for w in workflows]
        return jsonify(data)

    @jwt_required()
    def post(self):
        data = request.get_json()
        new_workflow = Workflow(
            workflowname=data['workflowname'],
            system=data['system']
        )
        db.session.add(new_workflow)
        db.session.commit()
        return jsonify({'message': 'Workflow created successfully'}), 201

api.add_resource(WorkflowResource, '/')


+++++++++


from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required
from werkzeug.security import check_password_hash, generate_password_hash
from ..models import db, User

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity={'username': user.username})
        return jsonify(access_token=access_token), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201



+++++++++----------(++++++

import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'mysecretkey')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///mydatabase.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwtsecretkey')



-------

from app import create_app, db
from app.models import User, Workflow, Whitelist

app = create_app()

@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)


---------------------------------------+++------++

Certainly! Here's how you can structure your backend with best practices in mind, including proper project structure, authentication, separation of concerns, and maintaining code quality. We'll use Flask, SQLAlchemy, and Flask-JWT-Extended for authentication.

### Project Structure

Here is a suggested project structure:

```
my_flask_app/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth_routes.py
│   │   ├── workflow_routes.py
│   │   ├── whitelist_routes.py
│   ├── config.py
│   ├── utils.py
├── migrations/
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_workflows.py
│   ├── test_whitelists.py
├── .env
├── requirements.txt
├── run.py
```

### Backend Code

#### `run.py`

```python
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
```

#### `app/__init__.py`

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from .config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)
    
    from .routes import auth_routes, workflow_routes, whitelist_routes
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(workflow_routes.bp)
    app.register_blueprint(whitelist_routes.bp)
    
    return app
```

#### `app/config.py`

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
```

#### `app/models.py`

```python
from . import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)

class Workflow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workflowname = db.Column(db.String(50), nullable=False)
    system = db.Column(db.String(50), nullable=False)

class Whitelist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workflowid = db.Column(db.Integer, db.ForeignKey('workflow.id'), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    system = db.Column(db.String(50), nullable=False)
    layout = db.Column(db.String(50), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

#### `app/routes/__init__.py`

```python
# Initialize Blueprints
```

#### `app/routes/auth_routes.py`

```python
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from ..models import db, User

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "User already exists"}), 400
    
    new_user = User(username=username, password_hash=generate_password_hash(password))
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully"}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"message": "Invalid credentials"}), 401
    
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200
```

#### `app/routes/workflow_routes.py`

```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..models import db, Workflow

bp = Blueprint('workflows', __name__, url_prefix='/api/workflows')

@bp.route('', methods=['GET', 'POST'])
@jwt_required()
def handle_workflows():
    if request.method == 'GET':
        workflows = Workflow.query.all()
        return jsonify([{'id': w.id, 'workflowname': w.workflowname, 'system': w.system} for w in workflows])
    elif request.method == 'POST':
        data = request.get_json()
        new_workflow = Workflow(workflowname=data['workflowname'], system=data['system'])
        db.session.add(new_workflow)
        db.session.commit()
        return jsonify({'message': 'Workflow added successfully'}), 201
```

#### `app/routes/whitelist_routes.py`

```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ..models import db, Whitelist, Workflow

bp = Blueprint('whitelists', __name__, url_prefix='/api/whitelists')

@bp.route('', methods=['GET', 'POST'])
@jwt_required()
def handle_whitelists():
    if request.method == 'GET':
        whitelists = Whitelist.query.all()
        return jsonify([{
            'id': w.id,
            'workflowid': w.workflowid,
            'workflowname': Workflow.query.get(w.workflowid).workflowname,
            'url': w.url,
            'system': w.system,
            'layout': w.layout,
            'created_date': w.created_date,
            'updated_date': w.updated_date
        } for w in whitelists])
    elif request.method == 'POST':
        data = request.get_json()
        new_whitelist = Whitelist(
            workflowid=data['workflowid'],
            url=data['url'],
            system=data['system'],
            layout=data['layout'],
            created_date=data.get('created_date', datetime.utcnow()),
            updated_date=data.get('updated_date', datetime.utcnow())
        )
        db.session.add(new_whitelist)
        db.session.commit()
        return jsonify({'message': 'Whitelist entry added successfully'}), 201

@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_whitelist(id):
    data = request.get_json()
    whitelist = Whitelist.query.get(id)
    if whitelist is None:
        return jsonify({'message': 'Whitelist entry not found'}), 404

    whitelist.workflowid = data.get('workflowid', whitelist.workflowid)
    whitelist.url = data.get('url', whitelist.url)
    whitelist.system = data.get('system', whitelist.system)
    whitelist.layout = data.get('layout', whitelist.layout)
    whitelist.updated_date = data.get('updated_date', datetime.utcnow())

    db.session.commit()
    return jsonify({'message': 'Whitelist entry updated successfully'}), 200

@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_whitelist(id):
    whitelist = Whitelist.query.get(id)
    if whitelist is None:
        return jsonify({'message': 'Whitelist entry not found'}), 404

    db.session.delete(whitelist)
    db.session.commit()
    return jsonify({'message': 'Whitelist entry deleted successfully'}), 200
```

### Explanation

1. **Project Structure:**
   - Organized into folders for routes, models, and configuration, allowing for scalable and maintainable code.

2. **Authentication:**
   - Handled using `Flask-JWT-Extended`.
   - Routes for user registration and login, generating JWT tokens upon successful authentication.

3. **Database Models:**
   - Separate `models.py` file for defining database models.
   - `User` model for authentication, `Workflow` model for workflows, and `Whitelist` model for whitelists.

4. **Routes:**
   - Split into separate modules for different functionalities (auth, workflows, whitelists).
   - `jwt_required` decorator to protect routes and ensure only authenticated users can access them.

5. **Configuration:**
   - Configuration settings in `config.py` for database URI and JWT secret key.
   - Environment variables stored in a `.env` file for sensitive information.

6. **Initialization:**
   - `create_app` function to initialize the Flask app, setup extensions, and register blueprints.

By following this structure, you ensure your backend is well-organized, secure, and scalable. You can further enhance this by adding unit tests in the `tests` directory to cover various functionalities and edge cases.












<template>
  <v-container>
    <v-data-table :headers="headers" :items="whitelists" item-key="id">
      <template v-slot:item.actions="{ item }">
        <v-icon small @click="editItem(item)">mdi-pencil</v-icon>
        <v-icon small @click="deleteItem(item.id)">mdi-delete</v-icon>
      </template>
    </v-data-table>

    <v-dialog v-model="dialog" max-width="600px">
      <v-card>
        <v-card-title>Edit Whitelist</v-card-title>
        <v-card-text>
          <v-autocomplete
            v-model="editedItem.workflow"
            :items="workflows"
            item-text="workflowname"
            item-value="id"
            label="Workflow Name"
            return-object
          ></v-autocomplete>
          <v-text-field v-model="editedItem.url" label="URL"></v-text-field>
          <v-text-field v-model="editedItem.system" label="System"></v-text-field>
          <v-text-field v-model="editedItem.layout" label="Layout"></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-btn color="blue darken-1" @click="saveChanges">Save</v-btn>
          <v-btn color="red darken-1" @click="closeDialog">Cancel</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      whitelists: [],
      headers: [
        { text: 'Workflow Name', align: 'start', value: 'workflowname' },
        { text: 'URL', value: 'url' },
        { text: 'System', value: 'system' },
        { text: 'Layout', value: 'layout' },
        { text: 'Actions', value: 'actions', sortable: false }
      ],
      dialog: false,
      editedItem: {
        id: null,
        workflow: null,
        url: '',
        system: '',
        layout: ''
      },
      workflows: []
    };
  },
  created() {
    this.fetchData();
  },
  methods: {
    fetchData() {
      axios.get('/api/whitelists')
        .then(response => {
          this.whitelists = response.data;
        });
      axios.get('/api/workflows')
        .then(response => {
          this.workflows = response.data;
        });
    },
    editItem(item) {
      this.editedItem = {
        ...item,
        workflow: this.workflows.find(w => w.id === item.workflowid)
      };
      this.dialog = true;
    },
    saveChanges() {
      axios.put(`/api/whitelists/${this.editedItem.id}`, {
        workflowid: this.editedItem.workflow.id,
        url: this.editedItem.url,
        system: this.editedItem.system,
        layout: this.editedItem.layout,
        updated_date: new Date()
      }).then(() => {
        this.fetchData();
        this.closeDialog();
      });
    },
    deleteItem(id) {
      axios.delete(`/api/whitelists/${id}`).then(() => {
        this.fetchData();
      });
    },
    closeDialog() {
      this.dialog = false;
      this.editedItem = {
        id: null,
        workflow: null,
        url: '',
        system: '',
        layout: ''
      };
    }
  }
}
</script>




















----------------------------------------


To ensure the whitelist table in the database is updated correctly when an item is edited in the app store, we'll make some adjustments to the logic both on the frontend and backend. Here's a detailed explanation:

### Frontend Adjustments

We need to ensure that the `workflowid` is sent to the backend whenever a whitelist item is edited. This is already done in the example provided, but let's clarify it further.

#### `AppStore.vue`

```vue
<template>
  <v-container>
    <v-data-table :headers="headers" :items="whitelists" item-key="id">
      <template v-slot:item.actions="{ item }">
        <v-icon small @click="editItem(item)">mdi-pencil</v-icon>
      </template>
    </v-data-table>

    <v-dialog v-model="dialog" max-width="600px">
      <v-card>
        <v-card-title>Edit Whitelist</v-card-title>
        <v-card-text>
          <v-autocomplete
            v-model="editedItem.workflow"
            :items="workflows"
            item-text="workflowname"
            item-value="id"
            label="Workflow Name"
            return-object
          ></v-autocomplete>
          <v-text-field v-model="editedItem.url" label="URL"></v-text-field>
          <v-text-field v-model="editedItem.system" label="System"></v-text-field>
          <v-text-field v-model="editedItem.layout" label="Layout"></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-btn color="blue darken-1" @click="saveChanges">Save</v-btn>
          <v-btn color="red darken-1" @click="closeDialog">Cancel</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      whitelists: [],
      headers: [
        { text: 'Workflow Name', align: 'start', value: 'workflowname' },
        { text: 'URL', value: 'url' },
        { text: 'System', value: 'system' },
        { text: 'Layout', value: 'layout' },
        { text: 'Actions', value: 'actions', sortable: false }
      ],
      dialog: false,
      editedItem: {
        id: null,
        workflow: null,
        url: '',
        system: '',
        layout: ''
      },
      workflows: []
    };
  },
  created() {
    this.fetchData();
  },
  methods: {
    fetchData() {
      axios.get('/api/whitelists')
        .then(response => {
          this.whitelists = response.data;
        });
      axios.get('/api/workflows')
        .then(response => {
          this.workflows = response.data;
        });
    },
    editItem(item) {
      this.editedItem = {
        ...item,
        workflow: this.workflows.find(w => w.id === item.workflowid)
      };
      this.dialog = true;
    },
    saveChanges() {
      axios.put(`/api/whitelists/${this.editedItem.id}`, {
        workflowid: this.editedItem.workflow.id,
        url: this.editedItem.url,
        system: this.editedItem.system,
        layout: this.editedItem.layout,
        updated_date: new Date()
      }).then(() => {
        this.fetchData();
        this.closeDialog();
      });
    },
    closeDialog() {
      this.dialog = false;
      this.editedItem = {
        id: null,
        workflow: null,
        url: '',
        system: '',
        layout: ''
      };
    }
  }
}
</script>
```

### Backend Adjustments

Ensure that the backend properly updates the whitelist table based on the `workflowid`. The whitelist table should contain the `workflowid` as a foreign key that references the `workflows` table.

#### `app.py`

```python
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://username:password@servername/databasename?driver=ODBC+Driver+17+for+SQL+Server'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Workflow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workflowname = db.Column(db.String(50), nullable=False)
    system = db.Column(db.String(50), nullable=False)

class Whitelist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workflowid = db.Column(db.Integer, db.ForeignKey('workflow.id'), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    system = db.Column(db.String(50), nullable=False)
    layout = db.Column(db.String(50), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@app.route('/api/workflows', methods=['GET', 'POST'])
def handle_workflows():
    if request.method == 'GET':
        workflows = Workflow.query.all()
        return jsonify([{'id': w.id, 'workflowname': w.workflowname, 'system': w.system} for w in workflows])
    elif request.method == 'POST':
        data = request.json
        new_workflow = Workflow(workflowname=data['workflowname'], system=data['system'])
        db.session.add(new_workflow)
        db.session.commit()
        return jsonify({'message': 'Workflow added successfully'}), 201

@app.route('/api/whitelists', methods=['GET', 'POST'])
def handle_whitelists():
    if request.method == 'GET':
        whitelists = Whitelist.query.all()
        return jsonify([{
            'id': w.id,
            'workflowid': w.workflowid,
            'workflowname': Workflow.query.get(w.workflowid).workflowname,
            'url': w.url,
            'system': w.system,
            'layout': w.layout,
            'created_date': w.created_date,
            'updated_date': w.updated_date
        } for w in whitelists])
    elif request.method == 'POST':
        data = request.json
        new_whitelist = Whitelist(
            workflowid=data['workflowid'],
            url=data['url'],
            system=data['system'],
            layout=data['layout'],
            created_date=data.get('created_date', datetime.utcnow()),
            updated_date=data.get('updated_date', datetime.utcnow())
        )
        db.session.add(new_whitelist)
        db.session.commit()
        return jsonify({'message': 'Whitelist entry added successfully'}), 201

@app.route('/api/whitelists/<int:id>', methods=['PUT'])
def update_whitelist(id):
    data = request.json
    whitelist = Whitelist.query.get(id)
    if whitelist is None:
        return jsonify({'message': 'Whitelist entry not found'}), 404

    whitelist.workflowid = data.get('workflowid', whitelist.workflowid)
    whitelist.url = data.get('url', whitelist.url)
    whitelist.system = data.get('system', whitelist.system)
    whitelist.layout = data.get('layout', whitelist.layout)
    whitelist.updated_date = data.get('updated_date', datetime.utcnow())

    db.session.commit()
    return jsonify({'message': 'Whitelist entry updated successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)
```

### Explanation

1. **Frontend (`FormComponent.vue` and `AppStore.vue`):**
   - The `v-autocomplete` component uses the `workflowname` to display the options to the user.
   - When a new whitelist entry is created or edited, the selected workflow's ID (`workflow.id`) is sent to the backend.
   - The `saveChanges` method in `AppStore.vue` sends the `workflowid` along with other form data to the backend for updating the whitelist entry.

2. **Backend (`app.py`):**
   - The `Whitelist` model includes `workflowid` as a foreign key referencing the `Workflow` model.
   - The `/api/whitelists` route handles `GET` and `POST` requests for retrieving and adding whitelist entries, respectively.
   - The `/api/whitelists/<int:id>` route handles `PUT` requests for updating existing whitelist entries.
   - When updating a whitelist entry, the `workflowid` is updated based on the `workflow.id` received from the frontend.

By following this structure, the whitelist table is correctly updated in the database whenever an item is edited in the app store. The frontend uses `workflowname` for display purposes and `workflowid` for backend operations, ensuring the relationship between `workflows` and `whitelist` tables is maintained correctly.
