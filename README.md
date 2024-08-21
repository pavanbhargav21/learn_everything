To include the `process_name` as part of the uniqueness check along with the `workflow_id`, `keyname`, and `layout`, we need to incorporate it into both the in-memory checks and the database query. This ensures that each `(workflow_id, process_name, keyname, layout)` combination is unique.

Here’s the updated version of the code with the `process_name` included:

### Updated `KeynameMappingResource` Class

```python
from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from flask_cors import cross_origin
from app.models import KeyNameMapping
from app import session_scope
from datetime import datetime
from sqlalchemy import tuple_

bp = Blueprint('keynamemapping', __name__, url_prefix='/api/keynamemapping')
api = Api(bp)

class KeynameMappingResource(Resource):
    @cross_origin()
    def post(self):
        with session_scope() as session:
            data = request.get_json()

            # Prepare data for checking and new entry creation
            entries_to_check = [(item['workflowId'], item['processName'], item['keyname'], item['layout']) for item in data]

            # In-memory check for duplicates in the current request
            if len(entries_to_check) != len(set(entries_to_check)):
                return {"message": "Duplicate key name mappings found in the request data"}, 400

            # Perform a single query to find existing entries
            existing_entries = session.query(
                tuple_(KeyNameMapping.workflow_id, KeyNameMapping.process_name, KeyNameMapping.activity_key_name, KeyNameMapping.activity_key_layout)
            ).filter(
                tuple_(KeyNameMapping.workflow_id, KeyNameMapping.process_name, KeyNameMapping.activity_key_name, KeyNameMapping.activity_key_layout).in_(entries_to_check)
            ).all()

            # Convert existing entries to a set for quick lookup
            existing_set = set(existing_entries)

            # Check if any of the entries already exist in the database
            for entry in entries_to_check:
                if entry in existing_set:
                    return {"message": f"Key name mapping {entry[2]} with layout {entry[3]} for workflow ID {entry[0]} and process name {entry[1]} already exists"}, 400

            # If all checks pass, prepare the new entries for insertion
            new_entries = [
                KeyNameMapping(
                    workflow_id=item['workflowId'],
                    process_name=item['processName'],
                    activity_key_name=item['keyname'],
                    activity_key_layout=item['layout'],
                    remarks=item['remarks'],
                    created_date=datetime.utcnow()
                ) for item in data
            ]

            # Bulk save all new entries at once
            if new_entries:
                session.bulk_save_objects(new_entries)

        return {"message": "Key name mappings added successfully"}, 201

api.add_resource(KeynameMappingResource, '/')
```

### Key Changes:

1. **Include `process_name` in Uniqueness Checks**:
   - The `entries_to_check` list now includes `process_name` as part of the tuple, making the uniqueness check based on `(workflow_id, process_name, keyname, layout)`.

2. **Database Query**:
   - The query now checks for existing entries based on all four fields: `workflow_id`, `process_name`, `activity_key_name`, and `activity_key_layout`.

3. **Error Message**:
   - The error message specifies the `process_name` along with the other fields to give more detailed feedback on what caused the duplication.

### Order of Checks:

- **In-Memory Duplicate Check**: Verifies that the combination of `(workflow_id, process_name, keyname, layout)` is unique within the current request.
- **Database Query**: Ensures that this combination does not already exist in the database.
- **Insert New Entries**: Only inserts the entries if they pass both the in-memory and database checks.

This ensures that the combination of `workflow_id`, `process_name`, `keyname`, and `layout` is unique both within the current request and in the database, providing accurate validation and optimized performance.









Got it! If the primary focus of your uniqueness check is on the combination of `workflow_id`, `process_name`, `activity_key_name`, `activity_key_layout`, and `activity_key_type`, then we can optimize the check accordingly. Instead of comparing entire patterns, we will check for the existence of a pattern based on these specific fields. This way, we avoid unnecessary comparisons and focus on what's critical.

### Revised Implementation

Here's how the code can be updated:

1. **Check 4**: Ensure that the combination of `workflow_id`, `process_name`, `activity_key_name`, `activity_key_layout`, and `activity_key_type` does not already exist in the database.
   
2. **Check 1**: Ensure at least one "Button" type per pattern.
   
3. **Check 2**: Ensure unique `activity_key_name` within the pattern.
   
4. **Check 3**: Ensure no duplicate sets of keys across patterns.

### Updated Code:

```python
@cross_origin()
@jwt_required()
def post(self):
    with session_scope('DESIGNER') as session:
        data = request.get_json()
        
        workflow_id = data['workflowId']
        process_name = data['processName']
        
        # Determine max pattern value only once per workflow and process
        max_pattern = session.query(func.max(VolumeMatrix.pattern)).filter(
            VolumeMatrix.workflow_id == workflow_id,
            VolumeMatrix.process_name == process_name
        ).scalar() or 0
        
        # A set to track combinations of keys across patterns
        all_key_sets = set()
        
        # Iterate through each pattern and perform checks in optimized order
        for pattern in data['pattern']:
            # Check 4: Ensure the combination of key fields does not already exist in the database
            for field in pattern['fields']:
                existing_entry = session.query(VolumeMatrix).filter(
                    VolumeMatrix.workflow_id == workflow_id,
                    VolumeMatrix.process_name == process_name,
                    VolumeMatrix.activity_key_name == field['keyName'],
                    VolumeMatrix.activity_key_layout == field['layout'],
                    VolumeMatrix.activity_key_type == field['type'],
                    VolumeMatrix.is_active == True
                ).first()
                
                if existing_entry:
                    return {"message": f"An entry with the same key combination already exists in the database for pattern {pattern['name']}."}, 400
            
            # Check 1: Ensure at least one "Button" type per pattern
            if not any(field['type'] == 'Button' for field in pattern['fields']):
                return {"message": f"Pattern {pattern['name']} must contain at least one 'Button' type field."}, 400
            
            # Check 2: Ensure unique activity_key_name within the pattern
            key_names = [field['keyName'] for field in pattern['fields']]
            if len(key_names) != len(set(key_names)):
                return {"message": f"Duplicate keys found within pattern {pattern['name']}."}, 400
            
            # Check 3: Ensure no duplicate sets of keys across patterns
            key_set = frozenset(key_names)
            if key_set in all_key_sets:
                return {"message": f"Duplicate key set found across patterns in {pattern['name']}."}, 400
            all_key_sets.add(key_set)
            
            # Update pattern number for new entries
            max_pattern += 1
            pattern_value = f"Pattern{max_pattern}"
            
            # Insert the new pattern after checks
            for field in pattern['fields']:
                new_entry = VolumeMatrix(
                    workflow_id=workflow_id,
                    process_name=process_name,
                    pattern=pattern_value,
                    activity_key_name=field['keyName'],
                    activity_key_layout=field['layout'],
                    activity_key_type=field['type'],
                    volume_type=field.get('volumeType'),
                    is_value=field.get('selectedValue'),
                    field_name=field.get('fieldName'),
                    field_layout=field.get('fieldLayout'),
                    status=field.get('status'),
                    created_date=datetime.utcnow(),
                    is_active=True,
                )
                session.add(new_entry)
        
    return {"message": "Volume Matrix added successfully"}, 201
```

### Key Changes and Reasoning:
- **Check 4 (First Check):** We now focus only on the relevant fields (`workflow_id`, `process_name`, `activity_key_name`, `activity_key_layout`, and `activity_key_type`). This ensures that we do not unnecessarily compare other fields and quickly eliminate any duplicates based on the critical combination.
  
- **Remaining Checks:** The order of the remaining checks is preserved as previously optimized, ensuring that invalid patterns are filtered out before moving to more complex operations.

This approach ensures that the most critical and potentially time-consuming check is done first, reducing unnecessary processing and improving performance.




from flask import Blueprint, jsonify
from flask_restful import Resource, Api
from app.models import ProcessDetailsView  # Import your SQLAlchemy model
from app import session_scope

# Create a Blueprint
process_bp = Blueprint('process', __name__)
api = Api(process_bp)

# Define the ProcessDetail resource
class ProcessDetail(Resource):
    def get(self):
        # Fetch all process names from the view
        with session_scope('DESIGNER') as session:
            processes = session.query(ProcessDetailsView.cpm_process_name).all()
            process_names = [process.cpm_process_name for process in processes]
        
        return jsonify({"process_names": process_names})

# Add the resource to the API
api.add_resource(ProcessDetail, '/process-names')

# To register this Blueprint in your main application
# from app.process import process_bp
# app.register_blueprint(process_bp, url_prefix='/api')






To access the view `Process_Details_View` in your SQLAlchemy models, you'll define it just like a regular table model, but without any primary key since views typically don't have one. Here's how you can define this view in your SQLAlchemy models:

### SQLAlchemy Model for the View

```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

# Assuming you're using the declarative base from SQLAlchemy
Base = declarative_base()

class ProcessDetailsView(Base):
    __tablename__ = 'Process_Details_View'  # Name of the view

    # Define the columns that correspond to the view
    gp_aid = Column('GP_AID', String(20), primary_key=True)
    spm_process_id = Column('SPM_PROCESS_ID', Integer)
    cpm_process_name = Column('CPM_PROCESS_NAME', String(500))

    def __repr__(self):
        return f"<ProcessDetailsView(gp_aid={self.gp_aid}, spm_process_id={self.spm_process_id}, cpm_process_name={self.cpm_process_name})>"
```

### Key Points:
1. **Primary Key:** While views typically don't have a primary key, SQLAlchemy expects one for ORM mappings. Here, I've used `gp_aid` as a primary key to satisfy SQLAlchemy's requirement. This may not be strictly necessary depending on how you plan to use this view, but it ensures compatibility with the ORM.

2. **Model Definition:** The model is defined just like any other SQLAlchemy model. The columns correspond to the fields in the view, with appropriate data types.

3. **Usage:** You can now query `ProcessDetailsView` like any other table in SQLAlchemy. For example:
   ```python
   session.query(ProcessDetailsView).filter(ProcessDetailsView.gp_aid == 'some_value').all()
   ```

### Usage Example

Suppose you want to fetch all records from the view:

```python
# Example of querying the view
with session_scope('DESIGNER') as session:
    records = session.query(ProcessDetailsView).all()
    for record in records:
        print(record)
```

This approach lets you seamlessly integrate SQL views into your SQLAlchemy ORM, making it easy to work with views as if they were tables.











from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from flask_cors import cross_origin
from app.models import KeyNameMapping
from app import session_scope
from datetime import datetime
from sqlalchemy import tuple_

bp = Blueprint('keynamemapping', __name__, url_prefix='/api/keynamemapping')
api = Api(bp)

class KeynameMappingResource(Resource):
    @cross_origin()
    def post(self):
        with session_scope() as session:
            data = request.get_json()

            # Prepare data for checking and new entry creation
            entries_to_check = []
            new_entries = []

            for item in data:
                entry_tuple = (item['workflowId'], item['keyname'], item['layout'])
                entries_to_check.append(entry_tuple)

                new_entries.append(KeyNameMapping(
                    workflow_id=item['workflowId'],
                    activity_key_name=item['keyname'],
                    activity_key_layout=item['layout'],
                    remarks=item['remarks'],
                    created_date=datetime.utcnow()
                ))

            # Perform a single query to find existing entries
            existing_entries = session.query(
                tuple_(KeyNameMapping.workflow_id, KeyNameMapping.activity_key_name, KeyNameMapping.activity_key_layout)
            ).filter(
                tuple_(KeyNameMapping.workflow_id, KeyNameMapping.activity_key_name, KeyNameMapping.activity_key_layout).in_(entries_to_check)
            ).all()

            # Convert existing entries to a set for quick lookup
            existing_set = set(existing_entries)

            # Filter out new entries that already exist
            filtered_new_entries = [
                entry for entry in new_entries
                if (entry.workflow_id, entry.activity_key_name, entry.activity_key_layout) not in existing_set
            ]

            # Check if there are duplicates
            if len(filtered_new_entries) < len(new_entries):
                return {"message": "One or more key name mappings already exist"}, 400

            # Bulk save all new entries at once
            if filtered_new_entries:
                session.bulk_save_objects(filtered_new_entries)

        return {"message": "Key name mappings added successfully"}, 201

api.add_resource(KeynameMappingResource, '/')




from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from flask_cors import cross_origin
from app.models import KeyNameMapping
from app import session_scope
from datetime import datetime
from sqlalchemy import tuple_

bp = Blueprint('keynamemapping', __name__, url_prefix='/api/keynamemapping')
api = Api(bp)

class KeynameMappingResource(Resource):
    @cross_origin()
    def post(self):
        with session_scope() as session:
            data = request.get_json()

            # Prepare the data to check for existing entries
            entries_to_check = [
                (item['workflowId'], item['keyname'], item['layout']) for item in data
            ]

            # Perform a single query to find existing entries
            existing_entries = session.query(
                KeyNameMapping.workflow_id,
                KeyNameMapping.activity_key_name,
                KeyNameMapping.activity_key_layout
            ).filter(
                tuple_(KeyNameMapping.workflow_id, KeyNameMapping.activity_key_name, KeyNameMapping.activity_key_layout).in_(entries_to_check)
            ).all()

            # Convert existing entries to a set for quick lookup
            existing_set = set(existing_entries)

            # Filter out new entries that already exist
            new_entries = [
                KeyNameMapping(
                    workflow_id=item['workflowId'],
                    activity_key_name=item['keyname'],
                    activity_key_layout=item['layout'],
                    remarks=item['remarks'],
                    created_date=datetime.utcnow()
                )
                for item in data
                if (item['workflowId'], item['keyname'], item['layout']) not in existing_set
            ]

            # Bulk save all new entries at once
            if new_entries:
                session.bulk_save_objects(new_entries)

        return {"message": "Key name mappings processed successfully"}, 201

api.add_resource(KeynameMappingResource, '/')






To reflect the changes you made to your database schema in your `models.py` file, you'll need to update your SQLAlchemy models to include the new tables, columns, and relationships. Here's how you can adjust your `models.py` to match the changes:

### 1. **Update the `AAD_QID_Mapping` Table**

```python
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class AAD_QID_Mapping(Base):
    __tablename__ = 'AAD_QID_MAPPING'
    id = Column(Integer, primary_key=True, autoincrement=True)
    aad = Column(String(100), nullable=False)
    qid = Column(String(100), nullable=False)
    employee_id = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)

    # Define relationships if needed
    # For example, if you have Employee and other related tables:
    # employee = relationship("Employee", back_populates="aad_qid_mappings")
```

### 2. **Update the `KeyNameMapping` Table**

```python
class KeyNameMapping(Base):
    __tablename__ = 'PLUGIN_KEY_VALUE_MAPPING'
    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(Integer, ForeignKey('PLUGIN_MASTER.id'), nullable=False)
    activity_key_name = Column(String, nullable=False)
    activity_key_layout = Column(String, nullable=False)
    ac_order = Column(Integer, nullable=False)
    remarks = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)
    created_date = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100), nullable=False)
    modified_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = Column(String(100), nullable=False)

    # Add foreign key relationships
    aad = Column(String(100), ForeignKey('AAD_QID_MAPPING.aad'), nullable=False)
    qid = Column(String(100), ForeignKey('AAD_QID_MAPPING.qid'), nullable=False)
    
    # Define relationship to AAD_QID_Mapping
    aad_qid_mapping = relationship("AAD_QID_Mapping")
```

### 3. **Update the `VolumeMatrix` Table**

```python
class VolumeMatrix(Base):
    __tablename__ = 'VOLUME_MATRIX'
    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(Integer, ForeignKey('PLUGIN_MASTER.id'), nullable=False)
    pattern = Column(String(50), nullable=True)
    activity_key_name = Column(String(1000), nullable=True)
    activity_key_type = Column(String(1000), nullable=True)
    activity_key_layout = Column(String(500), nullable=True)
    volume_type = Column(String(100), nullable=True)  # New column
    piece_value = Column(String(100), nullable=True)  # New column
    field_name = Column(String(100), nullable=True)  # New column
    field_layout = Column(String(100), nullable=True)  # New column
    status = Column(String(50), nullable=True)  # New column
    is_active = Column(Boolean, default=False)
    created_date = Column(DateTime, default=datetime.utcnow, nullable=True)
    created_by = Column(String(50), nullable=True)
    modified_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    modified_by = Column(String(50), nullable=True)

    # Define relationships if needed
```

### Summary of Changes

- **`AAD_QID_Mapping` Table**: Added model with columns `id`, `aad`, `qid`, `employee_id`, and `is_active`.
- **`KeyNameMapping` Table**: Added `aad` and `qid` columns as foreign keys referencing `AAD_QID_Mapping`. Added relationships if necessary.
- **`VolumeMatrix` Table**: Added new columns `volume_type`, `piece_value`, `field_name`, `field_layout`, and `status`.

These modifications align your SQLAlchemy models with the updated database schema. Ensure to test these changes and run migrations if you're using Alembic for database migrations.




-- Create AID_QID_MAPPING table
CREATE TABLE AID_QID_MAPPING (
    id INT AUTO_INCREMENT PRIMARY KEY,
    aid VARCHAR(255) NOT NULL,
    qid VARCHAR(255) NOT NULL,
    description TEXT,
    UNIQUE (aid, qid)
);

-- Alter PLUGIN_KEY_VALUE_MAPPING table to add aid and qid columns
ALTER TABLE PLUGIN_KEY_VALUE_MAPPING
ADD COLUMN aid VARCHAR(255) NOT NULL,
ADD COLUMN qid VARCHAR(255) NOT NULL;

-- Add foreign key constraints on aid and qid columns
ALTER TABLE PLUGIN_KEY_VALUE_MAPPING
ADD CONSTRAINT fk_aid_qid
FOREIGN KEY (aid, qid)
REFERENCES AID_QID_MAPPING (aid, qid);




You can add a normal `id` column as the primary key in the `AIDQIDMapping` table, and still use `AID` and `QID` as foreign keys in the `KeyNameMapping` table. Here’s how you can structure your tables:

### Updated `AIDQIDMapping` Table with an `id` Column
```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class AIDQIDMapping(Base):
    __tablename__ = 'AID_QID_MAPPING'
    id = Column(Integer, primary_key=True, autoincrement=True)
    aid = Column(String, nullable=False)
    qid = Column(String, nullable=False)
    description = Column(String)

    # Unique constraint to ensure unique combinations of AID and QID
    __table_args__ = (
        UniqueConstraint('aid', 'qid'),
    )

    # Relationship to KeyNameMapping (if you want to use relationships)
    key_name_mappings = relationship("KeyNameMapping", back_populates="aid_qid_mapping")
```

### Updated `KeyNameMapping` Table with Foreign Keys
```python
class KeyNameMapping(Base):
    __tablename__ = 'PLUGIN_KEY_VALUE_MAPPING'
    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(Integer, ForeignKey('PLUGIN_MASTER.id'), nullable=False)

    # AID and QID as foreign keys
    aid = Column(String, nullable=False)
    qid = Column(String, nullable=False)

    activity_key_name = Column(String, nullable=False)
    activity_key_layout = Column(String, nullable=False)
    ac_order = Column(Integer, nullable=False)
    remarks = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)
    created_date = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100), nullable=False)
    modified_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modified_by = Column(String(100), nullable=False)

    # Enforcing foreign key relationship
    __table_args__ = (
        ForeignKeyConstraint(['aid', 'qid'], ['AID_QID_MAPPING.aid', 'AID_QID_MAPPING.qid']),
    )

    # Relationship to AIDQIDMapping (if you want to use relationships)
    aid_qid_mapping = relationship("AIDQIDMapping", back_populates="key_name_mappings")
```

### Key Points

1. **Primary Key (`id`) in `AIDQIDMapping`**:
   - The `AIDQIDMapping` table now includes an `id` column that serves as the primary key. This is an auto-incrementing integer that uniquely identifies each row.

2. **Unique Constraint**:
   - A unique constraint on the combination of `aid` and `qid` ensures that each pair of `aid` and `qid` values is unique.

3. **Foreign Keys in `KeyNameMapping`**:
   - The `aid` and `qid` columns in the `KeyNameMapping` table are defined as foreign keys that reference the `aid` and `qid` columns in the `AIDQIDMapping` table.
   - The `ForeignKeyConstraint` ensures that any combination of `aid` and `qid` in `KeyNameMapping` must exist in the `AIDQIDMapping` table.

4. **Relationships (Optional)**:
   - If you want to use relationships for easier querying, you can define them using SQLAlchemy's `relationship` function. This is optional but can simplify complex queries.

### Example Usage

Here’s how you might use these tables in practice:

```python
# Inserting a new entry into AIDQIDMapping
new_aid_qid_mapping = AIDQIDMapping(
    aid="A123",
    qid="Q456",
    description="Mapping for A123 and Q456"
)
session.add(new_aid_qid_mapping)
session.commit()

# Inserting a new entry into KeyNameMapping with foreign key constraints
new_key_name_mapping = KeyNameMapping(
    workflow_id=1,
    aid="A123",
    qid="Q456",
    activity_key_name="Key Name Example",
    activity_key_layout="Layout Example",
    ac_order=1,
    remarks="Some remarks",
    created_by="admin"
)
session.add(new_key_name_mapping)
session.commit()

# Querying KeyNameMapping entries related to a specific AID and QID
key_mappings = session.query(KeyNameMapping).filter_by(aid="A123", qid="Q456").all()
```

This setup allows you to maintain a regular `id` primary key in the `AIDQIDMapping` table while still enforcing the foreign key relationship between `AID`/`QID` pairs and `KeyNameMapping` records. The `id` column can be used for other references or indexing, while the `aid` and `qid` columns are used for data integrity checks in the `KeyNameMapping` table.





I understand. If you need to handle JWT operations and user session management separately, you can create a dedicated function to handle the creation of user sessions. This function will accept parameters like the JWT ID, user email, and other details, and then it will save this information to the database. This approach will help you avoid issues with decorators and make the code cleaner.

Here's how you can refactor your code to include a separate function for handling user sessions:

### **1. Create a Separate Function for User Session Management**

Define a function in a utility module (e.g., `app/utils.py`) to handle session creation:

```python
# app/utils.py

from app.database import session_scope
from app.models import UserSession
from sqlalchemy.exc import SQLAlchemyError

def create_user_session(jwt_id, user_email, user_name, login_time, psid):
    try:
        with session_scope() as session:
            session_record = UserSession(
                employee_id=psid,
                email=user_email,
                name=user_name,
                login_time=login_time,
                token=jwt_id,  # Store the JWT ID
                is_active=True
            )
            session.add(session_record)
            session.commit()
    except SQLAlchemyError as e:
        # Handle the database error as needed
        raise Exception("Database error")
```

### **2. Update `GetTokenFromAzure` to Use the New Function**

Update your `GetTokenFromAzure` class to call this function instead of directly handling the database operations:

```python
from flask import Blueprint, request, jsonify, redirect
from flask_restful import Api, Resource
from flask_jwt_extended import create_access_token, get_jwt
from app.utils import create_user_session  # Import the utility function
from app.azure_authentication import get_me, save_user_information, get_token_from_code  # Import required functions
from datetime import datetime
from urllib.parse import urlencode
from app import jwt, BACKEND_API_URL, FROENTEND_API_URL

api_login = Api(Blueprint('login', __name__, url_prefix='/login'))

class GetTokenFromAzure(Resource):
    @cross_origin()
    def get(self):
        auth_code = request.args.get('code')
        redirect_uri = f'{BACKEND_API_URL}/get_token'
        token = get_token_from_code(auth_code, redirect_uri)
        
        if token.get('access_token'):
            access_token = token.get('access_token')
            get_user = get_me(access_token, '/me')
            user_email = get_user.get('userPrincipalName')
            user_id = get_user.get('id')
            get_user_details = get_me(access_token, f'/users/{user_id}?$select=streetAddress,employeeID,department,companyName,mobilePhone,country')
            get_manager = get_me(access_token, f'/users/{user_id}/manager?$select=mailNickname,mail')

            user_info = save_user_information({
                'u_first_name': get_user.get('givenName', ''),
                'u_last_name': get_user.get('surname', ''),
                'is_active': 'Y',
                'u_email': get_user.get('mail', ''),
                'u_psid': get_user_details.get('employeeId', ''),
                'u_lm_psid': get_manager.get('mailNickname'),
                'u_lm_email': get_manager.get('mail'),
            })

            user_id = user_info.id  # Adjust this according to your actual attribute

            # Create JWT access token
            jwt_access_token = create_access_token(identity=user_email, additional_claims={'user_id': user_id})
            jwt_id = get_jwt()['jti']  # Get the unique JWT ID
            
            # Call the function to create user session
            try:
                create_user_session(jwt_id, user_email, f"{get_user.get('givenName', '')} {get_user.get('surname', '')}", datetime.utcnow(), user_info.psid)
            except Exception as e:
                return jsonify({"msg": "Database error"}), 500

            user = {
                'user_name': get_user.get('displayName', ''),
                'user_email': get_user.get('userPrincipalName', ''),
                'access_token': jwt_access_token,
                'user_phone_number': get_user_details.get('mobilePhone', ''),
                'user_office_location': get_user_details.get('streetAddress', ''),
                'user_language': get_user.get('preferredLanguage', ''),
                'user_job_title': get_user.get('jobTitle', ''),
                'user_employee_id': get_user_details.get('employeeId', ''),
                'user_department': get_user_details.get('department', ''),
                'user_company_name': get_user_details.get('companyName', ''),
                'u_id': user_id
            }
            return redirect(f'{FROENTEND_API_URL}/oauth/login/redirect/?{urlencode(user)}')
```

### **3. Update `Logout` to Use the New Function**

The `Logout` function does not need changes related to session management directly since it's handled by the `create_user_session` function. Just ensure that the token ID is correctly used:

```python
class Logout(Resource):
    @jwt_required()
    @cross_origin()
    def post(self):
        token_id = get_jwt()['jti']  # Get JWT ID from the current token
        blacklist_token(token_id)

        with session_scope() as session:
            user_session = session.query(UserSession).filter_by(token=token_id).first()
            if user_session:
                user_session.logout_time = datetime.utcnow()
                user_session.is_active = False
                # Commit is automatically handled by session_scope()
        
        return jsonify({"msg": "Logout successful"}), 200
```

### Summary

- **Utility Function**: Created a utility function `create_user_session` to handle user session creation.
- **`GetTokenFromAzure` Update**: Refactored to call `create_user_session`.
- **`Logout`**: Ensure it uses the token ID properly.

This approach separates concerns, making your code cleaner and more maintainable. It also ensures that your session management and token operations are handled correctly.







Sure, let's provide the full code for `azure_authentication.py`, `login.py`, and ensure everything aligns with your project structure and requirements.

### `azure_authentication.py`

This module handles interactions with Azure AD to get user information and manage authentication.

```python
import requests
from flask import current_app as app

def get_token_from_code(auth_code, redirect_uri):
    """
    Exchange authorization code for access token.
    """
    token_url = 'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': redirect_uri,
        'client_id': app.config['AZURE_CLIENT_ID'],
        'client_secret': app.config['AZURE_CLIENT_SECRET'],
    }
    response = requests.post(token_url, data=data)
    return response.json()

def get_me(access_token, endpoint):
    """
    Get user information from Microsoft Graph API.
    """
    headers = {'Authorization': f'Bearer {access_token}'}
    graph_url = f'https://graph.microsoft.com/v1.0{endpoint}'
    response = requests.get(graph_url, headers=headers)
    return response.json()

def save_user_information(user_info):
    """
    Save user information and return the saved user details.
    """
    # Assuming you have a function or ORM to save user details to the database
    from app.models import User  # Adjust the import based on actual structure
    from app.database import session_scope
    
    with session_scope() as session:
        user = session.query(User).filter_by(email=user_info.get('u_email')).first()
        if user:
            # Update existing user
            user.first_name = user_info.get('u_first_name')
            user.last_name = user_info.get('u_last_name')
            user.is_active = user_info.get('is_active')
            user.psid = user_info.get('u_psid')
            user.manager_psid = user_info.get('u_lm_psid')
            user.manager_email = user_info.get('u_lm_email')
        else:
            # Create new user
            user = User(
                first_name=user_info.get('u_first_name'),
                last_name=user_info.get('u_last_name'),
                email=user_info.get('u_email'),
                is_active=user_info.get('is_active'),
                psid=user_info.get('u_psid'),
                manager_psid=user_info.get('u_lm_psid'),
                manager_email=user_info.get('u_lm_email')
            )
            session.add(user)
        session.commit()
        return user
```

### `login.py`

Ensure this file is updated with correct imports and functionality based on your requirements.

```python
from flask import Blueprint, request, jsonify, redirect
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, create_access_token
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from urllib.parse import urlencode
from app.models import UserSession  # Import UserSession from app.models
from app.database import session_scope  # Import session_scope from app.database
from app.azure_authentication import get_me, save_user_information, get_token_from_code  # Import required functions from azure_authentication
from app import jwt, BACKEND_API_URL, FROENTEND_API_URL  # Import jwt and other settings from app

api_login = Api(Blueprint('login', __name__, url_prefix='/login'))

@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    token = jwt_payload["jti"]
    with session_scope() as session:
        return session.query(UserSession).filter_by(token=token, is_blacklisted=True).scalar() is not None

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"msg": "The token has expired"}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"msg": "Invalid token"}), 401

def blacklist_token(token):
    with session_scope() as session:
        user_session = session.query(UserSession).filter_by(token=token).first()
        if user_session:
            user_session.is_blacklisted = True
            session.commit()

class GetTokenFromAzure(Resource):
    @cross_origin()
    def get(self):
        auth_code = request.args.get('code')
        redirect_uri = f'{BACKEND_API_URL}/get_token'
        token = get_token_from_code(auth_code, redirect_uri)
        
        if token.get('access_token'):
            access_token = token.get('access_token')
            get_user = get_me(access_token, '/me')
            user_email = get_user.get('userPrincipalName')
            user_id = get_user.get('id')
            get_user_details = get_me(access_token, f'/users/{user_id}?$select=streetAddress,employeeID,department,companyName,mobilePhone,country')
            get_manager = get_me(access_token, f'/users/{user_id}/manager?$select=mailNickname,mail')

            user_info = save_user_information({
                'u_first_name': get_user.get('givenName', ''),
                'u_last_name': get_user.get('surname', ''),
                'is_active': 'Y',
                'u_email': get_user.get('mail', ''),
                'u_psid': get_user_details.get('employeeId', ''),
                'u_lm_psid': get_manager.get('mailNickname'),
                'u_lm_email': get_manager.get('mail'),
            })

            # Ensure user_info has the required attribute
            user_id = user_info.id  # Adjust this according to your actual attribute

            # Create JWT access token
            jwt_access_token = create_access_token(identity=user_email, additional_claims={'user_id': user_id})
            
            # Save session information
            try:
                with session_scope() as session:
                    session_record = UserSession(
                        employee_id=user_info.psid,  # Adjust attribute based on your model
                        email=user_email,
                        name=f"{get_user.get('givenName', '')} {get_user.get('surname', '')}",
                        login_time=datetime.utcnow(),
                        token=jwt_access_token,
                        is_active=True
                    )
                    session.add(session_record)
                    # Commit is automatically handled by session_scope()
                    
            except SQLAlchemyError as e:
                return jsonify({"msg": "Database error"}), 500

            user = {
                'user_name': get_user.get('displayName', ''),
                'user_email': get_user.get('userPrincipalName', ''),
                'access_token': jwt_access_token,
                'user_phone_number': get_user_details.get('mobilePhone', ''),
                'user_office_location': get_user_details.get('streetAddress', ''),
                'user_language': get_user.get('preferredLanguage', ''),
                'user_job_title': get_user.get('jobTitle', ''),
                'user_employee_id': get_user_details.get('employeeId', ''),
                'user_department': get_user_details.get('department', ''),
                'user_company_name': get_user_details.get('companyName', ''),
                'u_id': user_id
            }
            return redirect(f'{FROENTEND_API_URL}/oauth/login/redirect/?{urlencode(user)}')

class Logout(Resource):
    @jwt_required()
    @cross_origin()
    def post(self):
        identity = get_jwt_identity()
        token = get_jwt()['jti']  # Get JWT ID
        blacklist_token(token)

        with session_scope() as session:
            user_session = session.query(UserSession).filter_by(token=token).first()
            if user_session:
                user_session.logout_time = datetime.utcnow()
                user_session.is_active = False
                # Commit is automatically handled by session_scope()
        
        return jsonify({"msg": "Logout successful"}), 200

api_login.add_resource(GetTokenFromAzure, '/get_token_from_azure')
api_login.add_resource(Logout, '/logout')
```

### Notes:
- **Imports:** Adjusted for your project structure.
- **`save_user_information`:** Assumed to be in `azure_authentication.py`, returning a user object with attributes used.
- **UID Handling:** Ensure the correct attribute is used based on your model's definition.
- **Session Handling:** Managed by `session_scope()`, which handles commits and rollbacks.

Make sure to adjust paths and model attributes according to your actual setup. If you have further details or corrections, feel free to provide them!









If you want to avoid raw queries and keep things simple, you can work with SQLAlchemy and Python to handle comma-separated values in a more straightforward way. Here’s a simplified approach:

### Simplified Approach

1. **Fetch All Whitelists**: Retrieve all existing `Whitelist` entries, including their `window_titles`. This will be done once and kept in memory for checking against new entries.

2. **Check for Duplicates**: Convert the comma-separated `window_titles` to sets for easy comparison and check if any titles already exist with other workflows.

3. **Add New Entries**: If there are no duplicates, proceed to add new entries to the database.

Here’s how you can implement this approach:

```python
class WhitelistResource(Resource):
    @cross_origin()
    def post(self):
        with session_scope() as session:
            data = request.get_json()
            workflow_name = data['workflow_name']
            new_titles = {title.strip() for title in data['titles'].split(',')}  # New titles as a set

            # Fetch all existing whitelists and their window_titles
            existing_whitelists = session.query(Whitelist).filter(Whitelist.is_active == True).all()

            existing_titles = set()
            for wl in existing_whitelists:
                # Split existing titles and add to the set
                titles = {title.strip() for title in wl.window_titles.split(',')}
                existing_titles.update(titles)

            # Check for overlap
            overlap = new_titles & existing_titles  # Intersection of sets
            if overlap:
                return jsonify({'message': f'One or more window titles already exist with another workflow: {", ".join(overlap)}'}), 400

            # Create or get the workflow
            workflow = session.query(Workflow).filter_by(workflow_name=workflow_name).first()
            if not workflow:
                new_workflow = Workflow(
                    workflow_name=workflow_name,
                    system_name=workflow_name,
                    created_date=datetime.utcnow()
                )
                session.add(new_workflow)
                session.commit()  # Commit to get the new workflow ID

                workflow = session.query(Workflow).filter_by(workflow_name=workflow_name).first()

            # Create new whitelist entry
            new_whitelist = Whitelist(
                workflow_id=workflow.id,
                workflow_name=workflow_name,
                workflow_url=data['url'],
                environment=data['environment'],
                is_active=True,
                window_titles=data['titles'],
                created_date=datetime.utcnow()
            )
            session.add(new_whitelist)

        return jsonify({'message': 'Whitelist entry created successfully', 'workflow_id': workflow.id}), 201
```

### **Explanation:**

1. **Fetching Existing Whitelists**: Retrieve all active `Whitelist` entries. This avoids querying individual titles and handles them in bulk.

2. **Set Operations**: Convert existing `window_titles` and new `titles` to sets for efficient comparison. Use set intersection to find any overlaps.

3. **Adding New Entries**: If no overlap is found, proceed to create and add new entries. Commit changes to get the new workflow ID if a new workflow is created.

This approach keeps the logic simple, avoids raw SQL queries, and uses SQLAlchemy efficiently for checking duplicates.







class WhitelistResource(Resource):
    #@jwt_required()
    @cross_origin()
    def get(self):
        with session_scope() as session:
            workflow_alias = aliased(Workflow)
            whitelist_alias = aliased(Whitelist)
            query = session.query(
                whitelist_alias.id,
                whitelist_alias.workflow_name,
                whitelist_alias.workflow_url,
                whitelist_alias.environment,
                whitelist_alias.is_active,
                workflow_alias.system_name,
                whitelist_alias.window_titles
            ).join(workflow_alias, whitelist_alias.workflow_id == workflow_alias.id).filter(whitelist_alias.is_active == True)
            whitelists = query.all()
            data = [{
                'id': w.id,
                'workflow_name': w.workflow_name,
                'system': w.system_name,
                'url': w.workflow_url,
                'environment': w.environment,
                'is_active': w.is_active,
                'titles': w.window_titles
            } for w in whitelists]
        return jsonify(data)

    #@jwt_required()
    @cross_origin()
    def post(self):
        with session_scope() as session:
            data = request.get_json()
            workflow_name = data['workflow_name']
            titles = {title.strip() for title in data['titles'].split(',')}  # Use a set for unique titles

            # Check if any of the window_titles already exist with another workflow
            existing_titles_query = session.query(Whitelist.window_titles).filter(
                Whitelist.window_titles.in_(titles),
                Whitelist.workflow_name != workflow_name
            ).distinct().all()

            existing_titles = {title for (title,) in existing_titles_query}  # Convert to set for quick lookup

            if existing_titles:
                return jsonify({'message': 'One or more window titles already exist with another workflow'}), 400

            # Create or get the workflow
            workflow = session.query(Workflow).filter_by(workflow_name=workflow_name).first()
            if not workflow:
                new_workflow = Workflow(
                    workflow_name=workflow_name,
                    system_name=workflow_name,
                    created_date=datetime.utcnow()
                )
                session.add(new_workflow)
                session.commit()  # Commit to get the new workflow ID

                workflow = session.query(Workflow).filter_by(workflow_name=workflow_name).first()

            # Create new whitelist entry
            new_whitelist = Whitelist(
                workflow_id=workflow.id,
                workflow_name=workflow_name,
                workflow_url=data['url'],
                environment=data['environment'],
                is_active=True,
                window_titles=data['titles'],
                created_date=datetime.utcnow()
            )
            session.add(new_whitelist)
        
        return jsonify({'message': 'Whitelist entry created successfully'}), 201

    #@jwt_required()
    @cross_origin()
    def put(self, id):
        with session_scope() as session:
            data = request.get_json()
            whitelist = session.query(Whitelist).get(id)
            if not whitelist:
                return {'message': 'Whitelist entry not found'}, 404

            whitelist.workflow_name = data['workflow_name']
            whitelist.workflow_url = data['url']
            whitelist.environment = data['environment']
            whitelist.is_active = data['isActive']
            whitelist.window_titles = data['title']
            whitelist.modified_date = datetime.utcnow()

        return {'message': 'Whitelist entry updated successfully'}, 200

    #@jwt_required()
    @cross_origin()
    def delete(self, id):
        with session_scope() as session:
            whitelist = session.query(Whitelist).get(id)
            if not whitelist:
                return {'message': 'Whitelist entry not found'}, 404
            whitelist.is_active = False
        return {'message': 'Whitelist entry deleted successfully'}, 200

api.add_resource(WhitelistResource, '/')
api.add_resource(WhitelistDetailResource, '/<int:id>')










class WorkflowResource(Resource):
    #@jwt_required()
    @cross_origin()
    def get(self):
        with session_scope() as session:
            workflows = session.query(Workflow).all()
            data = [{
                'id': w.id,
                'workflow_name': w.workflow_name,
                'system_name': w.system_name,
                # Uncomment the following lines if you need more fields
                # 'system_version': w.system_version,
                # 'is_feed': w.is_feed,
                # 'is_extension_enabled': w.is_extension_enabled,
                # 'layout_type': w.layout_type,
                # 'is_active': w.is_active,
                # 'created_date': w.created_date,
                # 'created_by': w.created_by,
                # 'modified_date': w.modified_date,
                # 'modified_by': w.modified_by
            } for w in workflows]
        return jsonify(data)

    #@jwt_required()
    @cross_origin()
    def post(self):
        with session_scope() as session:
            data = request.get_json()
            new_workflow = Workflow(
                workflow_name=data['workflow_name'],
                system_name=data['system_name'],
                created_date=datetime.utcnow()
            )
            session.add(new_workflow)
            # No need to call session.commit() as session_scope handles it

            # Prepare the response with created workflow details
            response = {
                'id': new_workflow.id,
                'workflow_name': new_workflow.workflow_name,
                'system_name': new_workflow.system_name
            }
        return jsonify(response), 201

    #@jwt_required()
    @cross_origin()
    def put(self, id):
        with session_scope() as session:
            data = request.get_json()
            workflow = session.query(Workflow).get(id)
            if not workflow:
                return {'message': 'Workflow entry not found'}, 404

            workflow.workflow_name = data['workflow_name']
            workflow.system_name = data['system_name']
            # Uncomment the following lines if you need to update more fields
            # workflow.system_version = data['system_version']
            # workflow.is_feed = data['is_feed']
            # workflow.is_extension_enabled = data['is_extension_enabled']
            # workflow.layout_type = data['layout_type']
            # workflow.is_active = data['is_active']
            workflow.modified_by = data['modified_by']
            workflow.modified_date = datetime.utcnow()

            # No need to call session.commit() as session_scope handles it
        return {'message': 'Workflow entry updated successfully'}, 200

    #@jwt_required()
    @cross_origin()
    def delete(self, id):
        with session_scope() as session:
            workflow = session.query(Workflow).get(id)
            if not workflow:
                return {'message': 'Workflow entry not found'}, 404

            session.delete(workflow)
            # No need to call session.commit() as session_scope handles it
        return {'message': 'Workflow entry deleted successfully'}, 200

api.add_resource(WorkflowResource, '/')
api.add_resource(WorkflowDetailResource, '/<int:id>')






The error "name 'response' is not defined" usually indicates that there’s a problem with how the `response` object is being used or created in your code. In Flask-RESTful, you generally do not need to define an `OPTIONS` method manually unless you have specific needs. However, if you do need to define it, you should ensure you are correctly importing and using the necessary components.

Here's a step-by-step approach to handle CORS and define the `OPTIONS` method correctly in Flask-RESTful:

### **1. Import Necessary Components**

Make sure you have the necessary imports for handling responses and CORS:

```python
from flask import make_response
from flask_restful import Resource
```

### **2. Define the OPTIONS Method**

In your Flask-RESTful resource, you can define the `OPTIONS` method to handle CORS preflight requests. Here’s an example of how you might do this:

```python
from flask import make_response, request
from flask_restful import Resource

class MyResource(Resource):
    def get(self):
        # Your GET logic here
        return {'message': 'GET request successful'}

    def options(self):
        response = make_response()  # Create an empty response object
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
        return response
```

### **3. Ensure Correct Usage**

- **`make_response`**: This function creates a response object. Make sure it's imported from `flask` and used correctly.
- **`response`**: The variable name `response` should be defined before being used. In this case, `response` is created by `make_response()`.

### **4. Debugging**

If you still encounter the "name 'response' is not defined" error:

1. **Check Imports**: Ensure that `make_response` is imported from `flask`.

2. **Check Scope**: Verify that the `response` variable is defined in the scope where you are trying to use it. It should be defined in the `options` method where you are trying to set headers and return it.

3. **Correct Syntax**: Make sure there are no typos or syntax errors in your code.

### **Example with Flask-RESTful Blueprint**

If you are using Blueprints with Flask-RESTful, the approach remains similar:

```python
from flask import Blueprint, make_response
from flask_restful import Api, Resource

api_bp = Blueprint('api_bp', __name__)
api = Api(api_bp)

class MyResource(Resource):
    def get(self):
        return {'message': 'GET request successful'}

    def options(self):
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
        return response

api.add_resource(MyResource, '/my-resource')

# In your main app file
from flask import Flask
from your_module import api_bp  # Adjust the import according to your project structure

app = Flask(__name__)
app.register_blueprint(api_bp, url_prefix='/api')
```

In this example, the `options` method is correctly defined to handle preflight requests and set appropriate CORS headers.







If you anticipate connecting to different databases in the future and want to maintain separate connections and models, you can structure your application to support multiple database connections. Here’s how you can design it:

### Updated Project Structure

1. **`config/`**: Contains configuration for different databases.
2. **`app/__init__.py`**: Initializes the app and sets up database connections dynamically.
3. **`app/models/`**: Contains models for different databases.
4. **`app/routes/`**: Contains routes for the application.
5. **`app/database/`**: Manages database connections and sessions.

### Detailed Code Structure

#### `.env` File
Store connection details for different databases.

```env
# Default Database configurations
DEFAULT_DB_TYPE=sql_server
DEFAULT_DB_SERVER=pre.database.windows.net
DEFAULT_DB_DATABASE=predb
DEFAULT_DB_USERNAME=my_db_username
DEFAULT_DB_PASSWORD=my_db_password
DEFAULT_DB_DRIVER={ODBC Driver 18 for SQL Server}
DEFAULT_DB_USE_AD_AUTH=False  # Set to True for Active Directory MSI

# Another Database configurations (for example, PostgreSQL)
SECONDARY_DB_TYPE=postgresql
SECONDARY_DB_SERVER=secondary.database.server
SECONDARY_DB_DATABASE=secondary_db
SECONDARY_DB_USERNAME=secondary_db_user
SECONDARY_DB_PASSWORD=secondary_db_password
SECONDARY_DB_DRIVER=postgresql
SECONDARY_DB_USE_AD_AUTH=False
```

#### `app/database/connection_manager.py`
Manages connections to different databases based on the configuration.

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
import os
import urllib

Base = declarative_base()

def get_connection_string(db_name):
    db_type = os.getenv(f'{db_name}_DB_TYPE')
    server = os.getenv(f'{db_name}_DB_SERVER')
    database = os.getenv(f'{db_name}_DB_DATABASE')
    username = os.getenv(f'{db_name}_DB_USERNAME', '')
    password = os.getenv(f'{db_name}_DB_PASSWORD', '')
    driver = os.getenv(f'{db_name}_DB_DRIVER')
    use_ad_auth = os.getenv(f'{db_name}_DB_USE_AD_AUTH', 'False') == 'True'
    
    if use_ad_auth:
        params = urllib.parse.quote_plus(
            f'Driver={driver};'
            f'Server=tcp:{server},1433;'
            f'Database={database};'
            f'TrustServerCertificate=no;'
            f'Connection Timeout=30;'
            f'Authentication=ActiveDirectoryMsi'
        )
    else:
        if db_type == 'postgresql':
            params = f'postgresql://{username}:{password}@{server}/{database}'
        else:
            params = urllib.parse.quote_plus(
                f'Driver={driver};'
                f'Server=tcp:{server},1433;'
                f'Database={database};'
                f'TrustServerCertificate=no;'
                f'Connection Timeout=30;'
                f'Uid={username};'
                f'Pwd={password}'
            )
    
    connection_string = f'{db_type}+pyodbc:///?odbc_connect={params}'
    return connection_string

def create_engine_session(db_name):
    engine = create_engine(get_connection_string(db_name), fast_executemany=True, pool_size=10, max_overflow=20)
    Session = scoped_session(sessionmaker(bind=engine))
    Base.metadata.create_all(engine)
    return engine, Session

def get_session(db_name):
    _, session = create_engine_session(db_name)
    return session

@contextmanager
def session_scope(db_name):
    session = get_session(db_name)
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.remove()
```

#### `app/__init__.py`
Initialize the app with dynamic database connections.

```python
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
    jwt = JWTManager(app)
    CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE"]}})
    
    # Initialize database connections
    from .database.connection_manager import create_engine_session
    default_engine, default_session = create_engine_session('DEFAULT')
    secondary_engine, secondary_session = create_engine_session('SECONDARY')
    
    # Register blueprints
    from .routes import workflows, whitelists, keynamemapping, volumematrix, upload, login
    app.register_blueprint(workflows.bp)
    app.register_blueprint(whitelists.bp)
    app.register_blueprint(keynamemapping.bp)
    app.register_blueprint(volumematrix.bp)
    app.register_blueprint(upload.bp)
    app.register_blueprint(login.bp)
    app.register_blueprint(login.token_bp)
    
    return app
```

#### `app/models/`
Create separate files for models specific to each database.

**Example for `app/models/default_models.py`:**

```python
from app.database.connection_manager import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime

class DefaultModel(Base):
    __tablename__ = 'default_table'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    is_active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.utcnow)
    modified_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Example for `app/models/secondary_models.py`:**

```python
from app.database.connection_manager import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime

class SecondaryModel(Base):
    __tablename__ = 'secondary_table'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    is_active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.utcnow)
    modified_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

#### `app/routes/`
Update routes to use models from the appropriate file based on the database connection.

**Example for `app/routes/default_routes.py`:**

```python
from flask import Blueprint, request, jsonify
from app.models.default_models import DefaultModel
from app.database.connection_manager import session_scope

bp = Blueprint('default_routes', __name__)

@bp.route('/default', methods=['GET'])
def get_default():
    with session_scope('DEFAULT') as session:
        data = session.query(DefaultModel).all()
        return jsonify([item.to_dict() for item in data])
```

**Example for `app/routes/secondary_routes.py`:**

```python
from flask import Blueprint, request, jsonify
from app.models.secondary_models import SecondaryModel
from app.database.connection_manager import session_scope

bp = Blueprint('secondary_routes', __name__)

@bp.route('/secondary', methods=['GET'])
def get_secondary():
    with session_scope('SECONDARY') as session:
        data = session.query(SecondaryModel).all()
        return jsonify([item.to_dict() for item in data])
```

### Summary
- **Environment Variables**: Store configurations for each database.
- **Connection Manager**: Dynamically create connections based on environment variables.
- **Models**: Keep separate models for different databases.
- **Routes**: Use the appropriate models and connections.

This setup will make it easier to manage multiple databases and switch connections as needed, without altering the core application logic.









------------------------

from app import create_app
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def main():
    """Run the Flask application."""
    app = create_app()

    # Determine if the environment is local
    is_local = os.environ.get('ENV') == 'local'

    if is_local:
        app.run(
            debug=True,  # Enable debug mode
            host='0.0.0.0',  # Allow access from all IP addresses
            port=int(os.environ.get('BACKEND_PORT', 5000))  # Use BACKEND_PORT from environment or default to 5000
        )
    else:
        app.run()  # Use default settings for non-local environments

if __name__ == '__main__':
    main()









def get_service_details(service_name):
    with Session() as session:
        # Fetch all related records where service_name is either a lender or a borrower
        services = session.query(SkillMatching).filter(
            or_(
                SkillMatching.hrl_5_lender == service_name,
                SkillMatching.hrl_5_borrower == service_name
            )
        ).all()
        
        if not services:
            return {'message': 'Service not found'}, 404

        # Extract all HR5 names related to the given service_name
        response = {'HR5_service_name': service_name, 'HR4_details': []}
        
        for service in services:
            if service.hrl_5_lender == service_name:
                opposite_service = service.hrl_5_borrower
                HR4_name = service.hrl_4_borrower
                HR3_name = service.hrl_3_borrower
            else:
                opposite_service = service.hrl_5_lender
                HR4_name = service.hrl_4_lender
                HR3_name = service.hrl_3_lender
            
            response['HR4_details'].append({
                'HR5_opposite_service': opposite_service,
                'HR4_name': HR4_name if HR4_name else "N/A",
                'HR3_name': HR3_name if HR3_name else "N/A",
                'matching_percentage': service.skill_match
            })
        
    return response




Understood. We need to address two main issues:

1. **Service Name as Lender or Borrower**: The service name could be either a lender or a borrower, so we need to handle both cases in our query.

2. **Fetching HR4 and HR3 Names**: Ensure that HR4 and HR3 names are correctly fetched regardless of whether the service name is a lender or borrower.

### Revised Approach

We'll use a single query to handle both scenarios where the service name could be either a lender or a borrower. We'll also ensure that HR4 and HR3 names are correctly fetched based on whether they are associated with the lender or borrower roles.

Here’s a revised function:

```python
def get_service_details(service_name):
    with Session() as session:
        # Create aliases for self-joins
        hrl_4_service_alias = aliased(SkillMatching, name='hrl_4_service')
        hrl_3_service_alias = aliased(SkillMatching, name='hrl_3_service')
        
        # Query to get HR-5 service and its corresponding HR-4 and HR-3 details
        query = session.query(
            SkillMatching.hrl_5_lender.label('HR5_service_name'),
            SkillMatching.hrl_5_borrower.label('HR5_opposite_service'),
            hrl_4_service_alias.hrl_4_lender.label('HR4_lender_name'),
            hrl_4_service_alias.hrl_4_borrower.label('HR4_borrower_name'),
            hrl_3_service_alias.hrl_3_lender.label('HR3_lender_name'),
            hrl_3_service_alias.hrl_3_borrower.label('HR3_borrower_name'),
            SkillMatching.skill_match.label('matching_percentage')
        ).outerjoin(
            hrl_4_service_alias,
            or_(
                SkillMatching.hrl_5_lender == hrl_4_service_alias.hrl_4_lender,
                SkillMatching.hrl_5_borrower == hrl_4_service_alias.hrl_4_borrower
            )
        ).outerjoin(
            hrl_3_service_alias,
            or_(
                SkillMatching.hrl_4_lender == hrl_3_service_alias.hrl_4_lender,
                SkillMatching.hrl_4_borrower == hrl_3_service_alias.hrl_4_borrower
            )
        ).filter(
            or_(
                SkillMatching.hrl_5_lender == service_name,
                SkillMatching.hrl_5_borrower == service_name
            )
        ).all()

        # Debug: Print raw results to check query output
        for result in query:
            print(result)

        # Process the results
        response = {'HR5_service_name': service_name, 'HR4_details': []}

        for result in query:
            # Check if HR5_service_name is lender or borrower and adjust accordingly
            if result.HR5_service_name == service_name:
                opposite_service = result.HR5_opposite_service
                HR4_name = result.HR4_lender_name if result.HR4_lender_name else result.HR4_borrower_name
                HR3_name = result.HR3_lender_name if result.HR3_lender_name else result.HR3_borrower_name
            else:
                opposite_service = result.HR5_service_name
                HR4_name = result.HR4_borrower_name if result.HR4_borrower_name else result.HR4_lender_name
                HR3_name = result.HR3_borrower_name if result.HR3_borrower_name else result.HR3_lender_name

            response['HR4_details'].append({
                'HR5_opposite_service': opposite_service,
                'HR4_name': HR4_name if HR4_name else "N/A",
                'HR3_name': HR3_name if HR3_name else "N/A",
                'matching_percentage': result.matching_percentage
            })

    return response
```

### Key Adjustments

1. **Aliases for HR4 and HR3**: Added aliases to join `SkillMatching` with itself for HR4 and HR3 details. This ensures that both HR4 and HR3 names are correctly fetched.

2. **Handling Lender and Borrower Roles**: Adjusted the logic to handle both cases where the service name could be a lender or borrower.

3. **Check for NULL Values**: Ensured that if the HR4 or HR3 names are `NULL`, they are set to `"N/A"`.

4. **Debugging Output**: Added debug prints to verify the results and ensure the query is capturing the expected data.

By using this revised approach, you should be able to accurately fetch the HR4 and HR3 names and ensure that the service name is correctly identified as either a lender or borrower.











from sqlalchemy.orm import aliased
from sqlalchemy.sql import or_

def get_service_details(service_name):
    with Session() as session:
        # Create aliases for self-joins
        hrl_5_service_alias = aliased(SkillMatching)
        hrl_4_service_alias = aliased(SkillMatching)
        
        # Query to get HR-5 service and its corresponding HR-4 details
        query = session.query(
            SkillMatching.hrl_5_lender.label('HR5_service_name'),
            SkillMatching.hrl_5_borrower.label('HR5_opposite_service'),
            hrl_4_service_alias.hrl_4_lender.label('HR4_name'),
            hrl_4_service_alias.hrl_4_borrower.label('HR4_name_opposite'),
            hrl_4_service_alias.hrl_3_lender.label('HR3_name'),
            hrl_4_service_alias.hrl_3_borrower.label('HR3_name_opposite'),
            SkillMatching.skill_match.label('matching_percentage')
        ).outerjoin(
            hrl_4_service_alias,
            or_(
                SkillMatching.hrl_5_lender == hrl_4_service_alias.hrl_4_borrower,
                SkillMatching.hrl_5_borrower == hrl_4_service_alias.hrl_4_lender
            )
        ).filter(
            or_(
                SkillMatching.hrl_5_lender == service_name,
                SkillMatching.hrl_5_borrower == service_name
            )
        ).all()

        # Process the results
        response = {'HR5_service_name': service_name, 'HR4_details': []}

        for result in query:
            response['HR4_details'].append({
                'HR5_opposite_service': result.HR5_opposite_service,
                'HR4_name': result.HR4_name or result.HR4_name_opposite,
                'HR3_name': result.HR3_name or result.HR3_name_opposite,
                'matching_percentage': result.matching_percentage
            })

    return response










from sqlalchemy.orm import aliased

def get_service_details(service_name):
    with Session() as session:
        # Alias for self-joins
        hrl_5_service_alias = aliased(SkillMatching)
        hrl_4_service_alias = aliased(SkillMatching)
        
        # Query to get HR-5 service and its corresponding HR-4 details
        query = session.query(
            SkillMatching.hrl_5_lender.label('HR5_service_name'),
            SkillMatching.hrl_5_borrower.label('HR5_opposite_service'),
            hrl_4_service_alias.hrl_4_lender.label('HR4_name'),
            hrl_4_service_alias.hrl_4_borrower.label('HR4_name_opposite'),
            hrl_4_service_alias.hrl_3_lender.label('HR3_name'),
            hrl_4_service_alias.hrl_3_borrower.label('HR3_name_opposite'),
            SkillMatching.skill_match.label('matching_percentage')
        ).join(
            hrl_4_service_alias,
            or_(
                SkillMatching.hrl_5_lender == hrl_4_service_alias.hrl_4_borrower,
                SkillMatching.hrl_5_borrower == hrl_4_service_alias.hrl_4_lender
            )
        ).filter(
            or_(
                SkillMatching.hrl_5_lender == service_name,
                SkillMatching.hrl_5_borrower == service_name
            )
        ).all()

        # Process the results
        response = {'HR5_service_name': service_name, 'HR4_details': []}

        for result in query:
            response['HR4_details'].append({
                'HR5_opposite_service': result.HR5_opposite_service,
                'HR4_name': result.HR4_name or result.HR4_name_opposite,
                'HR3_name': result.HR3_name or result.HR3_name_opposite,
                'matching_percentage': result.matching_percentage
            })

    return response













INSERT INTO SKILL_MATCHING (
    "HRL_3_LENDER", 
    "HRL_4_LENDER", 
    "HRL_5_LENDER", 
    "HRL_3_BORROWER", 
    "HRL_4_BORROWER", 
    "HRL_5_BORROWER", 
    "SKILL_MATCH"
) VALUES
('Wholesale Operations', 'Wholesale Client & Account Servicing', 'Closures - Wholesale', 'WPB Operations', 'Cards and Loans', 'Card Account Servicing and Closing', '43%'),
('Wholesale Operations', 'Wholesale Client & Account Servicing', 'Closures - Wholesale', 'WPB Operations', 'Cards and Loans', 'Third Party Vendor Mgmt/ Proc', '40%'),
('Wholesale Operations', 'Wholesale Client & Account Servicing', 'Closures - Wholesale', 'WPB Operations', 'Cards and Loans', 'Cards & Loans Glbl Mgmt & Sup', '36%'),
('Wholesale Operations', 'Wholesale Client & Account Servicing', 'Closures - Wholesale', 'WPB Operations', 'Cash', 'Vault Cash', '33%'),
('Wholesale Operations', 'Wholesale Client & Account Servicing', 'Closures - Wholesale', 'WPB Operations', 'Cash', 'Remote Self Service Terminal Cash Replenishment', '32%'),
('Wholesale Operations', 'Wholesale Client & Account Servicing', 'Closures - Wholesale', 'Wholesale Operations', 'Trade and Receivables Finance', 'Trade and Receivables Finance', '24%'),
('Wholesale Operations', 'Wholesale Client & Account Servicing', 'IVB WS Client & Acc Svcng', 'WPB Operations', 'Cards and Loans', 'Loan Account Onboarding', '65%'),
('Wholesale Operations', 'Wholesale Client & Account Servicing', 'IVB WS Client & Acc Svcng', 'WPB Operations', 'Cards and Loans', 'Loan Account Servicing', '57%'),
('Wholesale Operations', 'Wholesale Client & Account Servicing', 'IVB WS Client & Acc Svcng', 'WPB Operations', 'Cards and Loans', 'Acquiring', '55%'),
('Wholesale Operations', 'Wholesale Client & Account Servicing', 'IVB WS Client & Acc Svcng', 'WPB Operations', 'Cards and Loans', 'Card Account Onboarding', '51%'),
('Wholesale Operations', 'Wholesale Client & Account Servicing', 'IVB WS Client & Acc Svcng', 'WPB Operations', 'Cards and Loans', 'Third Party Vendor Mgmt/ Proc', '51%'),
('Wholesale Operations', 'Wholesale Client & Account Servicing', 'IVB WS Client & Acc Svcng', 'WPB Operations', 'Cards and Loans', 'Card Dispute Management', '49%'),
('Wholesale Operations', 'Wholesale Client & Account Servicing', 'IVB WS Client & Acc Svcng', 'WPB Operations', 'Cards and Loans', 'Cards & Loans Glbl Mgmt & Sup', '45%'),
('Wholesale Operations', 'Wholesale Client & Account Servicing', 'IVB WS Client & Acc Svcng', 'WPB Operations', 'Cards and Loans', 'Card Fraud Claims and Recovery', '43%'),
('Wholesale Operations', 'Wholesale Client & Account Servicing', 'IVB WS Client & Acc Svcng', 'WPB Operations', 'Cash', 'Vault Cash', '42%'),
('Wholesale Operations', 'Wholesale Client & Account Servicing', 'IVB WS Client & Acc Svcng', 'WPB Operations', 'Cards and Loans', 'Card Issuance', '41%'),
('Wholesale Operations', 'Wholesale Client & Account Servicing', 'IVB WS Client & Acc Svcng', 'WPB Operations', 'Cards and Loans', 'Card Account Servicing and Closing', '41%'),
('Wholesale Operations', 'Wholesale Client & Account Servicing', 'IVB WS Client & Acc Svcng', 'WPB Operations', 'Cash', 'Remote Self Service Terminal Cash Replenishment', '37%'),
('Wholesale Operations', 'Wholesale Client & Account Servicing', 'IVB WS Client & Acc Svcng', 'Wholesale Operations', 'Trade and Receivables Finance', 'Trade and Receivables Finance', '28%'),
('Wholesale Operations', 'Wholesale Client & Account Servicing', 'IVB WS Client & Acc Svcng', 'Wholesale Operations', 'Trade and Receivables Finance', 'Import Processing', '21%'),
('Wholesale Operations', 'Wholesale Client & Account Servicing', 'IVB WS Client & Acc Svcng', 'Wholesale Operations', 'Trade and Receivables Finance', 'Export Processing', '21%');