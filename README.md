
from concurrent.futures import ThreadPoolExecutor, as_completed

@cross_origin()
@jwt_required()
def post(self):
    data = request.get_json()
    created_By = request.headers.get('Createdby')
    
    if not created_By:
        return {'message': "Missing CreatedBy header"}, 400

    workflow_id = data['workflowId']
    process_name = data['processName']
    fields = data['fields']

    # Step 1: Check for unique keyNames within the provided fields
    seen_keynames = set()
    for field in fields:
        key_name = field['keyName']
        if key_name in seen_keynames:
            return {"message": f"Duplicate keyName '{key_name}' in the provided fields"}, 400
        seen_keynames.add(key_name)

    entries_to_check = [
        (workflow_id, process_name, field['keyName'], field['layout'])
        for field in fields
    ]

    def check_existing_entries_in_mapping():
        with session_scope('DESIGNER') as session:
            return session.query(
                KeyNameMapping.workflow_id, KeyNameMapping.process_name, KeyNameMapping.activity_key_name, KeyNameMapping.activity_key_layout
            ).filter(
                or_(*[
                    and_(
                        KeyNameMapping.workflow_id == entry[0],
                        KeyNameMapping.process_name == entry[1],
                        KeyNameMapping.activity_key_name == entry[2],
                        KeyNameMapping.activity_key_layout == entry[3]
                    )
                    for entry in entries_to_check
                ])
            ).all()

    def check_existing_entries_in_config_request():
        with session_scope('DESIGNER') as session:
            return session.query(
                KeyNameStoreConfigRequest.workflow_id, KeyNameStoreConfigRequest.process_name, KeyNameStoreConfigRequest.activity_key_name, KeyNameStoreConfigRequest.activity_key_layout
            ).filter(
                or_(*[
                    and_(
                        KeyNameStoreConfigRequest.workflow_id == entry[0],
                        KeyNameStoreConfigRequest.process_name == entry[1],
                        KeyNameStoreConfigRequest.activity_key_name == entry[2],
                        KeyNameStoreConfigRequest.activity_key_layout == entry[3]
                    )
                    for entry in entries_to_check
                ])
            ).all()

    with ThreadPoolExecutor(max_workers=2) as executor:
        # Step 2: Execute both database queries concurrently
        futures = {
            executor.submit(check_existing_entries_in_mapping): "mapping",
            executor.submit(check_existing_entries_in_config_request): "config_request"
        }

        results = {
            "mapping": [],
            "config_request": []
        }

        for future in as_completed(futures):
            result_key = futures[future]
            try:
                results[result_key] = future.result()
            except Exception as e:
                return {"message": f"Error during database query: {str(e)}"}, 500

    # Convert results to sets for quick lookup
    existing_set = set(results["mapping"])
    config_request_set = set(results["config_request"])

    # Prepare new entries
    new_entries = [
        KeyNameMapping(
            workflow_id=workflow_id,
            process_name=process_name,
            activity_key_name=field['keyName'],
            activity_key_layout=field['layout'],
            remarks=field['remarks'],
            created_by=created_By,
            created_date=datetime.utcnow()
        )
        for field in fields
    ]

    # Step 3: Filter out entries that already exist in either table
    filtered_new_entries = [
        entry for entry in new_entries
        if (entry.workflow_id, entry.process_name, entry.activity_key_name, entry.activity_key_layout) not in existing_set
        and (entry.workflow_id, entry.process_name, entry.activity_key_name, entry.activity_key_layout) not in config_request_set
    ]

    # Step 4: Handle duplicates or conflicts
    if len(filtered_new_entries) < len(new_entries):
        return {"message": "One or more key name mappings already exist in the database or pending approval"}, 400

    with session_scope('DESIGNER') as session:
        # Step 5: Bulk save all valid new entries
        if filtered_new_entries:
            session.bulk_save_objects(filtered_new_entries)

    return {"message": "Key name mappings added successfully"}, 201





It looks like you want to create a similar set of resources for managing `KeyStoreRequests` and `KeyStoreConfigRequests` based on the logic from the `WhitelistMaker` resource. To move forward, I’ll help you adapt the structure and methods, while ensuring the checks and table references align with the `KeyNameMapping` requirements. 

I'll guide you through the key steps:

### 1. **Set Up the KeyStore Resources**

Start by creating the `KeyStoreMakerResource`, `KeyStoreMakerStatusResource`, `KeyStoreMakerRequestIdResource`, and `KeyStoreMakerIdResource` classes, similar to how they are structured in `WhitelistMaker`. Each class will perform operations on `KeyStoreRequests` and `KeyStoreConfigRequests`.

### 2. **Modify the `KeyStoreMakerResource`**

This will handle `GET`, `POST`, and `PUT` requests for creating, retrieving, and updating key store entries.

#### `get` Method:
This method should retrieve `KeyStoreRequests` based on the `created_by` header.

```python
class KeyStoreMakerResource(Resource):
    @jwt_required()
    def get(self):
        try:
            created_By = request.headers.get('Createdby')
            if not created_By:
                return {'message': "Missing CreatedBy header"}, 400

            with session_scope('DESIGNER') as session:
                key_requests = session.query(KeyStoreRequests).filter_by(
                        created_by=created_By,
                        is_active=True
                        ).all()
                
                data = [{
                    'requestId': k.request_id,
                    'count': k.count,
                    'approver1': k.approver_1,
                    'approver1Email': k.approver_1_email,
                    'requestCreatedDate': k.req_created_date,
                    'requestSentDate': k.req_sent_date,
                    'approverActionDate': k.approver_action_date,
                    'modifiedDate': k.modified_date,
                    'status': k.status 
                    } for k in key_requests]
                
            return jsonify(data)
        except Exception as e:
            logging.error(f"Error Occurred: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
```

#### `post` Method:
This method will handle the creation of a new key store entry, ensuring no duplicates and validating the inputs.

```python
@cross_origin()
@jwt_required()
def post(self):
    try:
        data = request.get_json()
        created_By = request.headers.get('Createdby')

        if not created_By:
            return {'message': "Missing CreatedBy header"}, 400

        # Validate URL (if needed for KeyStore)
        if data['url']:
            if not validators.url(data['url']):
                return jsonify({'message': 'Invalid URL'}), 400

        # Ensure at least two keys
        keys = [key.strip() for key in data['keys'].split(',')]
        if len(keys) < 2:
            return jsonify({'message': 'At least two keys are required'}), 400

        with session_scope('DESIGNER') as session:
            # Step 1: Fetch or create the workflow ID
            workflow_name = data.get('workflow_name')
            workflow = session.query(Workflow).filter_by(workflow_name=workflow_name).first()

            if not workflow:
                new_workflow = Workflow(
                    workflow_name=workflow_name,
                    system_name=workflow_name,
                    created_date=datetime.utcnow()
                )
                session.add(new_workflow)
                session.flush()  # Commit to get the new workflow ID
                workflow_id = new_workflow.id
            else:
                workflow_id = workflow.id

            # Step 2: Define the overlap check functions
            def check_key_store_entry(session, workflow_id):
                return session.query(KeyStoreRequests).filter_by(
                    workflow_url=data['url'],
                    environment=data['environment'],
                    workflow_id=workflow_id,
                    window_keys=data['keys']
                ).first()

            def check_key_config_requests_entry(session, workflow_id):
                return session.query(KeyStoreConfigRequests).filter_by(
                    workflow_url=data['url'],
                    environment=data['environment'],
                    workflow_id=workflow_id,
                    window_keys=data['keys']
                ).first()

            def check_key_store_overlap(session, keys):
                existing_keystores = session.query(KeyStoreRequests).filter(KeyStoreRequests.is_active == True).all()
                existing_keys = set()

                for ks in existing_keystores:
                    ex_keys = set(key.strip() for key in ks.window_keys.split(','))
                    existing_keys.update(ex_keys)

                overlap = existing_keys & set(keys)
                return overlap

            def check_key_config_requests_overlap(session, keys):
                existing_requests = session.query(KeyStoreConfigRequests).filter(KeyStoreConfigRequests.is_active == True).all()
                existing_keys = set()

                for ks in existing_requests:
                    ex_keys = set(key.strip() for key in ks.window_keys.split(','))
                    existing_keys.update(ex_keys)

                overlap = existing_keys & set(keys)
                return overlap

            # Step 3: Execute the overlap checks concurrently
            with ThreadPoolExecutor() as executor:
                # Run all checks concurrently
                future_keystore = executor.submit(check_key_store_entry, session, workflow_id)
                future_config_requests = executor.submit(check_key_config_requests_entry, session, workflow_id)
                future_keystore_overlap = executor.submit(check_key_store_overlap, session, keys)
                future_config_requests_overlap = executor.submit(check_key_config_requests_overlap, session, keys)

                # Get results
                keystore_result = future_keystore.result()
                config_requests_result = future_config_requests.result()
                keystore_overlap = future_keystore_overlap.result()
                config_requests_overlap = future_config_requests_overlap.result()

                # Check for existence
                if keystore_result:
                    return jsonify({'message': 'KeyStore Entry Already Exists in App Store'}), 400

                if config_requests_result:
                    return jsonify({
                        'message': f'Entry already exists with Request ID: {config_requests_result.request_id}',
                    }), 400

                # Check for overlap
                if keystore_overlap or config_requests_overlap:
                    overlap_keys = keystore_overlap | config_requests_overlap
                    return jsonify({
                        'message': f'One or more keys already exist with another workflow: {", ".join(overlap_keys)}'
                    }), 400

                # No conflicts, proceed with creating the request
                new_request = KeyStoreRequests(
                    count=1,
                    req_created_date=datetime.utcnow(),
                    modified_date=datetime.utcnow(),
                    created_by=created_By,
                    is_active=True,
                    status="OPEN",
                )
                session.add(new_request)
                session.flush()  # Commit to get the new RequestId

                new_keystore_config = KeyStoreConfigRequests(
                    request_id=new_request.request_id,
                    workflow_id=workflow_id,
                    serial_number=1,
                    workflow_name=workflow_name,
                    workflow_url=data['url'],
                    environment=data['environment'],
                    is_active=True,
                    status_ar="OPEN",
                    modified_date=datetime.utcnow(),
                    window_keys=data['keys'],
                    is_full_image_capture=data.get('screenCapture', 'no') == 'yes',
                )
                session.add(new_keystore_config)

                return jsonify({'message': 'KeyStore request created successfully', 'request_id': new_request.request_id}), 201
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
```

#### `put` Method:
This should allow for bulk updates, similar to the `WhitelistMakerResource` but adapted for `KeyStoreRequests`.

```python
@cross_origin()
@jwt_required()
def put(self):
    with session_scope('DESIGNER') as session:
        data = request.get_json()
        request_ids = data.get('requestIds', [])

        if not request_ids:
            return jsonify({"error": "No Request ID's provided"}), 400

        # Perform a bulk update to set Status to Sent for all given request_ids
        updated_count = session.query(KeyStoreRequests).filter(
            KeyStoreRequests.request_id.in_(request_ids)
        ).update(
            {KeyStoreRequests.status: 'SENT'},
            synchronize_session=False
        )
        return {'message': f"{updated_count} record's have been Sent for Approval"}, 200
```

### 3. **Status and ID-Based Resources**

Implement the other resources like `KeyStoreMakerStatusResource`, `KeyStoreMakerRequestIdResource`, and `KeyStoreMakerIdResource` following a similar structure. These should align with how status, request ID, and individual record updates are managed.

### 4. **Register Resources with API**

Finally, don't forget to register these resources with your Flask API instance:

```python
api.add_resource(KeyStoreMakerResource, '/keystore/')
api.add_resource(KeyStoreMakerStatusResource, '/keystore/status/<str:status>')
api.add_resource(KeyStoreMakerRequestIdResource, '/keystore/request-id/<int:request_id>')
api.add_resource(KeyStoreMakerIdResource, '/keystore/request-id/id/<int:id>')
```

### Conclusion
This should give you a strong foundation for your `KeyStoreMaker` resources, modeled after your existing `WhitelistMaker` structure but adapted for the new tables and logic you need. You can further adjust and expand as necessary.








Thank you for clarifying. I now understand that the statuses you're concerned with are already provided in the payload. Based on these statuses, you need to update the status of the `request_id` in another table. Here's how to properly handle this:

### Revised Implementation

Given that you have the statuses in the payload, you can directly determine the overall status without querying the database again. You'll only query the database to update the request's status based on the statuses provided.

Here’s how you can implement it:

```python
from sqlalchemy import update

class WhitelistMakerResource(Resource):
    @cross_origin()
    @jwt_required()
    def put(self):
        try:
            # Step 1: Parse the Incoming Payload
            data = request.get_json()
            request_id = data.get('request_id')
            updates = data.get('data', [])

            if not request_id:
                return jsonify({'message': 'Missing request_id'}), 400

            if not updates or not isinstance(updates, list):
                return jsonify({'message': 'Invalid or missing data'}), 400

            with session_scope('DESIGNER') as session:
                # Step 2: Extract the statuses from the payload
                statuses = [item['status'] for item in updates if 'id' in item and 'status' in item]

                if not statuses:
                    return jsonify({'message': 'No valid updates found in the payload'}), 400

                # Step 3: Determine the overall request status based on the payload statuses
                if all(status == 'approved' for status in statuses):
                    overall_status = 'approved'
                elif all(status == 'rejected' for status in statuses):
                    overall_status = 'rejected'
                else:
                    # If there's a mix of 'approved' and 'rejected'
                    approved_count = statuses.count('approved')
                    rejected_count = statuses.count('rejected')

                    if approved_count > 0 and rejected_count > 0:
                        overall_status = 'partially approved/rejected'
                    elif approved_count > rejected_count:
                        overall_status = 'partially approved'
                    else:
                        overall_status = 'partially rejected'

                # Step 4: Update the individual records
                stmt = (
                    update(WhitelistStoreConfigRequests)
                    .where(WhitelistStoreConfigRequests.id.in_([item['id'] for item in updates]))
                    .values(
                        status=case(
                            [
                                (WhitelistStoreConfigRequests.id == item['id'], item['status'])
                                for item in updates
                            ],
                            else_=WhitelistStoreConfigRequests.status
                        ),
                        modified_date=datetime.utcnow()
                    )
                )
                session.execute(stmt)

                # Step 5: Update the request status in WhitelistStoreRequests table
                request_update_stmt = (
                    update(WhitelistStoreRequests)
                    .where(WhitelistStoreRequests.id == request_id)
                    .values(
                        status=overall_status,
                        modified_date=datetime.utcnow()
                    )
                )
                session.execute(request_update_stmt)

                # Step 6: Commit the Transaction
                session.commit()

            return jsonify({'message': 'Records updated successfully'}), 200

        except Exception as e:
            logging.error(f"Error Occurred: {str(e)}")
            return jsonify({'status': 'error', 'message': 'An internal server error occurred'}), 500
```

### Explanation:

1. **Extract Statuses from Payload**: The statuses are directly extracted from the payload. You do not need to query the database for these, as they are provided by the frontend.

2. **Determine Overall Status**:
   - If all statuses in the payload are "approved," set the overall status to "approved."
   - If all are "rejected," set the status to "rejected."
   - If there's a mix of "approved" and "rejected," determine the appropriate overall status (e.g., "partially approved/rejected").

3. **Update Individual Records**: The individual records in the `WhitelistStoreConfigRequests` table are updated in bulk using the `update()` statement. 

4. **Update the Request's Status**: After determining the overall status, you update the status of the `request_id









from sqlalchemy import update

class WhitelistMakerResource(Resource):
    # Existing GET and POST methods...

    @cross_origin()
    @jwt_required()
    def put(self):
        try:
            # Step 1: Parse the Incoming Payload
            data = request.get_json()
            request_id = data.get('request_id')
            updates = data.get('data', [])

            if not request_id:
                return jsonify({'message': 'Missing request_id'}), 400

            if not updates or not isinstance(updates, list):
                return jsonify({'message': 'Invalid or missing data'}), 400

            with session_scope('DESIGNER') as session:
                # Step 2: Prepare the Update Statements
                # Extract the IDs and corresponding statuses from the payload
                id_status_map = {item['id']: item['status'] for item in updates if 'id' in item and 'status' in item}

                if not id_status_map:
                    return jsonify({'message': 'No valid updates found in the payload'}), 400

                # Step 3: Perform the Bulk Update in a Single Query
                stmt = (
                    update(WhitelistStoreConfigRequests)
                    .where(WhitelistStoreConfigRequests.id.in_(id_status_map.keys()))
                    .values(
                        status=func.coalesce(id_status_map[WhitelistStoreConfigRequests.id], WhitelistStoreConfigRequests.status),
                        modified_date=datetime.utcnow()
                    )
                )

                session.execute(stmt)

                # Step 4: Commit the Transaction
                session.commit()

            return jsonify({'message': 'Records updated successfully'}), 200
        except Exception as e:
            logging.error(f"Error Occurred: {str(e)}")
            return jsonify({'status': 'error', 'message': 'An internal server error occurred'}), 500






You're correct that the `workflow_id` check should be performed before launching the `ThreadPoolExecutor`. This allows us to confirm that the `workflow_id` exists (or create it if necessary) before running the parallel overlap checks. Once we have the `workflow_id`, it can be passed to the functions within the `ThreadPoolExecutor` to ensure the checks are conducted properly.

Here's how you can modify the code:

1. **Retrieve or Create `workflow_id`**: Before launching the `ThreadPoolExecutor`, the `workflow_id` should be fetched from the database. If it doesn't exist, a new `workflow_id` should be created.

2. **Pass `workflow_id`**: Once the `workflow_id` is confirmed, pass it into the functions that are executed in parallel using `ThreadPoolExecutor`.

3. **Integrate with the Session Scope**: Ensure that the session is properly managed by the context manager and passed to the functions executed by the threads.

### Updated Code

```python
from flask import request, jsonify
from flask_jwt_extended import jwt_required
from concurrent.futures import ThreadPoolExecutor
from models import Whitelist, WhiteListStoreConfigRequests, Workflow, WhiteListAppStoreRequest
from app import session_scope
import validators
from datetime import datetime

@cross_origin()
@jwt_required()
def post(self):
    data = request.get_json()
    created_By = request.headers.get('Createdby')

    if not created_By:
        return {'message': "Missing CreatedBy header"}, 400

    if not validators.url(data['url']):
        return jsonify({'message': 'Invalid URL'}), 400

    titles = [title.strip() for title in data['titles'].split(',')]
    if len(titles) < 2:
        return jsonify({'message': 'At least two page titles are required'}), 400

    with session_scope('DESIGNER') as session:
        # Step 1: Fetch or create the workflow ID
        workflow_name = data.get('workflow_name')
        workflow = session.query(Workflow).filter_by(name=workflow_name).first()

        if not workflow:
            # If workflow doesn't exist, create a new one
            workflow = Workflow(name=workflow_name)
            session.add(workflow)
            session.flush()  # Flush to get the new workflow ID

        workflow_id = workflow.id  # Now we have the workflow ID

        # Step 2: Define the overlap check functions
        def check_whitelist_entry(session, workflow_id):
            return session.query(Whitelist).filter_by(
                workflow_url=data['url'],
                environment=data['environment'],
                workflow_id=workflow_id,
                window_titles=data['titles']
            ).first()

        def check_config_requests_entry(session, workflow_id):
            return session.query(WhiteListStoreConfigRequests).filter_by(
                WorkflowURL=data['url'],
                Environment=data['environment'],
                WorkflowID=workflow_id,
                WindowTitle=data['titles']
            ).first()

        def check_whitelist_overlap(session):
            existing_whitelists = session.query(Whitelist).filter(Whitelist.is_active == True).all()
            existing_titles = set()

            for wl in existing_whitelists:
                ex_titles = set(title.strip() for title in wl.window_titles.split(','))
                existing_titles.update(ex_titles)

            overlap = existing_titles & set(titles)
            return overlap

        def check_config_requests_overlap(session):
            existing_requests = session.query(WhiteListStoreConfigRequests).filter(WhiteListStoreConfigRequests.IsActive == True).all()
            existing_titles = set()

            for wl in existing_requests:
                ex_titles = set(title.strip() for title in wl.WindowTitle.split(','))
                existing_titles.update(ex_titles)

            overlap = existing_titles & set(titles)
            return overlap

        # Step 3: Execute the overlap checks concurrently
        with ThreadPoolExecutor() as executor:
            # Run all checks concurrently
            future_whitelist = executor.submit(check_whitelist_entry, session, workflow_id)
            future_config_requests = executor.submit(check_config_requests_entry, session, workflow_id)
            future_whitelist_overlap = executor.submit(check_whitelist_overlap, session)
            future_config_requests_overlap = executor.submit(check_config_requests_overlap, session)

            # Get results
            whitelist_result = future_whitelist.result()
            config_requests_result = future_config_requests.result()
            whitelist_overlap = future_whitelist_overlap.result()
            config_requests_overlap = future_config_requests_overlap.result()

            # Check for existence
            if whitelist_result:
                return jsonify({'message': 'Whitelist Entry Already Exists in main app store'}), 400

            if config_requests_result:
                return jsonify({
                    'message': f'Entry exists in WhiteListStoreConfigRequests with Request ID: {config_requests_result.RequestId}',
                }), 400

            # Check for overlap
            if whitelist_overlap or config_requests_overlap:
                overlap_titles = whitelist_overlap | config_requests_overlap
                return jsonify({
                    'message': f'One or more window titles already exist with another workflow: {", ".join(overlap_titles)}'
                }), 400

            # No conflicts, proceed with creating the request
            new_request = WhiteListAppStoreRequest(
                Count=1,
                Approver1=None,
                Approver2=None,
                Approver1Email=None,
                Approver2Email=None,
                RequestCreatedDate=datetime.utcnow(),
                RequestSendDate=None,
                ApproverActionDate=None,
                ModifiedDate=datetime.utcnow(),
                StatusCreatedBy=created_By,
                IsActive=True
            )
            session.add(new_request)
            session.flush()  # Commit to get the new RequestId

            new_whitelist_config = WhiteListStoreConfigRequests(
                RequestId=new_request.RequestId,
                WorkflowID=workflow_id,
                SerialNumber=None,
                WorkflowName=workflow_name,
                WorkflowURL=data['url'],
                Environment=data['environment'],
                IsActive=True,
                Status_AR='Open',
                ModifiedDate=datetime.utcnow(),
                WindowTitle=data['titles'],
                IsFullImageCapture=data.get('screenCapture', 'no') == 'yes',
                IsMaxTab=data.get('maxTab', 'no') == 'yes'
            )
            session.add(new_whitelist_config)

            return jsonify({'message': 'Whitelist request created successfully', 'request_id': new_request.RequestId}), 201
```

### Key Changes:

1. **Workflow ID Retrieval or Creation**:
    - We first check if the `workflow_name` exists. If not, we create it and retrieve the `workflow_id`.

2. **Passing `workflow_id`**:
    - The `workflow_id` is then passed into the `ThreadPoolExecutor` tasks that check for existing entries and overlaps.

3. **Session Scope Management**:
    - The session is opened at the start, the `ThreadPoolExecutor` tasks are executed within that context, and results are aggregated accordingly.

### Workflow and Overlap Validation Flow:

- **Workflow Validation**: Ensures that a valid `workflow_id` exists before any parallel checks.
- **Parallel Overlap Checks**: These checks ensure that window titles don't overlap across both the `Whitelist` and `WhiteListStoreConfigRequests` tables.
- **Decision Making**: Based on the results of the parallel checks, the process either continues to create a new request or returns an appropriate error message.

This approach maintains concurrency for checking the overlap, thus optimizing the process while ensuring the correctness of operations by handling workflow validation upfront.











The solution provided is generally efficient for the concurrent checking of two tables. However, depending on your specific use case and the scale of your data, there are a few additional optimizations and considerations you might explore:

### 1. **Indexing**

Ensure that the columns you are querying against (e.g., `workflow_url`, `environment`, `window_titles`) are properly indexed. Indexing these columns will speed up the search operations and reduce latency.

### 2. **Database Connection Pooling**

Ensure that your SQLAlchemy setup is using connection pooling. Connection pooling reduces the overhead of establishing database connections by reusing existing ones.

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Example engine with connection pooling
engine = create_engine('your_database_url', pool_size=10, max_overflow=20)
Session = sessionmaker(bind=engine)
```

### 3. **Optimize Database Queries**

- **Filter Columns**: Only retrieve the columns you need. If you’re querying just to check existence, avoid loading unnecessary data.
  
- **Reduce Overlap Checks**: If you’re checking for existence across tables, make sure the checks are minimal and focused.

### 4. **Asynchronous Processing**

If your Flask application is running in an environment that supports asynchronous processing, consider using asynchronous frameworks or libraries. Flask itself is synchronous, but you can use extensions or deploy with an ASGI server like `uvicorn` for asynchronous support.

### 5. **Batch Processing**

If your application might receive multiple concurrent requests that need similar checks, consider batching these operations or aggregating requests to optimize database interactions.

### 6. **Caching**

If the data you are querying does not change frequently, consider implementing caching for your queries to reduce the load on the database and speed up response times.

### 7. **Error Handling**

Ensure robust error handling around database operations to catch and manage potential exceptions that could affect performance.

### Updated Code Snippet with Indexing and Optimizations

Here’s how you can implement indexing and connection pooling in the provided code snippet:

```python
from flask import request, jsonify
from flask_jwt_extended import jwt_required
from concurrent.futures import ThreadPoolExecutor
from models import Whitelist, WhiteListStoreConfigRequests, Workflow
from app import Session, session_scope
import validators
from datetime import datetime

@cross_origin()
@jwt_required()
def post(self):
    data = request.get_json()
    created_By = request.headers.get('Createdby')

    if not created_By:
        return {'message': "Missing CreatedBy header"}, 400

    if not validators.url(data['url']):
        return jsonify({'message': 'Invalid URL'}), 400

    titles = [title.strip() for title in data['titles'].split(',')]
    if len(titles) < 2:
        return jsonify({'message': 'At least two page titles are required'}), 400

    def check_whitelist_entry(session):
        return session.query(Whitelist).filter_by(
            workflow_url=data['url'],
            environment=data['environment'],
            window_titles=data['titles']
        ).first()

    def check_config_requests_entry(session):
        return session.query(WhiteListStoreConfigRequests).filter_by(
            WorkflowURL=data['url'],
            Environment=data['environment'],
            WindowTitle=data['titles']
        ).first()

    with ThreadPoolExecutor() as executor:
        with session_scope('DESIGNER') as session:
            future_whitelist = executor.submit(check_whitelist_entry, session)
            future_config_requests = executor.submit(check_config_requests_entry, session)

            whitelist_result = future_whitelist.result()
            config_requests_result = future_config_requests.result()

            if whitelist_result:
                return jsonify({'message': 'Whitelist Entry Already Exists in main app store'}), 400

            if config_requests_result:
                return jsonify({
                    'message': 'Entry exists in WhiteListStoreConfigRequests',
                    'request_id': config_requests_result.RequestId
                }), 400

            new_request = WhiteListAppStoreRequest(
                Count=1,
                Approver1=None,
                Approver2=None,
                Approver1Email=None,
                Approver2Email=None,
                RequestCreatedDate=datetime.utcnow(),
                RequestSendDate=None,
                ApproverActionDate=None,
                ModifiedDate=datetime.utcnow(),
                StatusCreatedBy=created_By,
                IsActive=True
            )
            session.add(new_request)
            session.flush()  # Commit to get the new RequestId

            new_whitelist_config = WhiteListStoreConfigRequests(
                RequestId=new_request.RequestId,
                WorkflowID=None,
                SerialNumber=None,
                WorkflowName=data.get('workflow_name'),
                WorkflowURL=data['url'],
                Environment=data['environment'],
                IsActive=True,
                Status_AR='Open',
                ModifiedDate=datetime.utcnow(),
                WindowTitle=data['titles'],
                IsFullImageCapture=data.get('screenCapture', 'no') == 'yes',
                IsMaxTab=data.get('maxTab', 'no') == 'yes'
            )
            session.add(new_whitelist_config)

            return jsonify({'message': 'Whitelist request created successfully', 'request_id': new_request.RequestId}), 201
```

### Summary

These optimizations ensure that the application scales well and performs efficiently. The threading model you've used will help with parallel checks, and indexing, connection pooling, and caching will further enhance performance. Adjustments can be made based on your application's specific needs and behavior.







In your case, where roles and permissions are driven by Azure Active Directory (AAD) groups and there's no admin interface for manual changes, you need a system where roles and permissions are dynamically assigned based on AAD groups and managed through existing AAD mechanisms. Here’s how you can set it up:

### **1. Database Schema Design**

Even without an admin interface, you need tables to store roles, permissions, and their mappings. These tables should be designed to accommodate the automatic assignment of roles and permissions based on AAD groups.

#### **Tables and Example Data**

1. **`Roles` Table**:
   - Stores different application roles.
   ```plaintext
   Roles
   -----
   RoleID (PK) | RoleName
   ----------- | ----------
   1           | Admin
   2           | User
   3           | Reviewer
   ```

2. **`Permissions` Table**:
   - Stores various permissions that can be assigned to roles.
   ```plaintext
   Permissions
   -----------
   PermissionID (PK) | PermissionName
   ----------------- | ----------------
   1                 | view_dashboard
   2                 | edit_user
   3                 | approve_request
   ```

3. **`RolePermissions` Table**:
   - Maps roles to permissions.
   ```plaintext
   RolePermissions
   ---------------
   RoleID (FK) | PermissionID (FK)
   ----------  | -----------------
   1           | 1
   1           | 2
   2           | 1
   3           | 3
   ```

4. **`RoleADGroupMapping` Table**:
   - Maps AAD groups to application roles. This helps in automatically assigning roles based on group membership.
   ```plaintext
   RoleADGroupMapping
   -------------------
   RoleID (FK) | ADGroupID
   ----------  | ----------
   1           | AADGroup1
   2           | AADGroup2
   3           | AADGroup3
   ```

5. **`UserRoles` Table**:
   - Stores user roles assigned based on their AAD group memberships.
   ```plaintext
   UserRoles
   ---------
   UserID (PK) | RoleID (FK)
   ----------  | ----------
   user1       | 1
   user2       | 2
   user3       | 3
   ```

### **2. Data Flow and Automatic Role Assignment**

Here’s how you can handle roles and permissions assignment based on AAD groups:

1. **User Login and Group Retrieval**:
   - When a user logs in, retrieve their AAD group memberships using Microsoft Graph API.

2. **Determine User Roles**:
   - For each AAD group the user belongs to, find the corresponding role using the `RoleADGroupMapping` table.
   - Assign these roles to the user in the `UserRoles` table.

3. **Check Permissions**:
   - When checking permissions for a user, retrieve their roles from the `UserRoles` table.
   - Fetch the associated permissions using the `RolePermissions` table.

### **3. Example Workflow**

**User Logs In**:
   1. **Retrieve AAD Groups**: Fetch the groups the user belongs to via Microsoft Graph API.
   2. **Map AAD Groups to Roles**: Use `RoleADGroupMapping` to find roles associated with the user's AAD groups.
   3. **Assign Roles to User**: Store the user's roles in the `UserRoles` table.

**Permission Check**:
   1. **Retrieve User Roles**: From `UserRoles`, find the roles assigned to the user.
   2. **Fetch Permissions**: Use `RolePermissions` to get permissions for those roles.
   3. **Authorize Action**: Check if the user has the required permissions.

### **4. Maintenance and Updates**

- **Roles and Permissions Management**: Maintain roles and permissions in the database. Any changes to roles or permissions will require updates to the `Roles`, `Permissions`, and `RolePermissions` tables.
- **AAD Group Management**: Update `RoleADGroupMapping` as new AAD groups and roles are added.

### **Summary**

1. **Database Tables**:
   - `Roles`: Defines roles in your application.
   - `Permissions`: Defines what each role can do.
   - `RolePermissions`: Maps roles to permissions.
   - `RoleADGroupMapping`: Maps AAD groups to roles.
   - `UserRoles`: Stores user-role mappings.

2. **Flow**:
   - Retrieve user AAD groups and map them to roles.
   - Assign roles to users and check their permissions dynamically.

By using this approach, you can manage roles and permissions effectively without a manual admin interface, leveraging AAD for dynamic user management and role assignment.










You're right; the AD group's names weren't explicitly defined in the example tables provided. To properly map AD groups to roles, we should introduce an additional table to explicitly manage the AD groups and their relationships with roles. Let me correct this and show you how AD groups can be incorporated.

### Revised Table Structure with AD Groups

### 1. **ADGroups Table**
**Table Name**: `ad_groups`
| id  | name         | description               | created_at          | updated_at          |
|-----|--------------|---------------------------|---------------------|---------------------|
| 1   | AdminGroup   | Admins with full access    | 2024-01-01 10:00:00 | 2024-01-01 10:00:00 |
| 2   | UserGroup    | Regular users             | 2024-01-01 10:00:00 | 2024-01-01 10:00:00 |
| 3   | CheckerGroup | Users who approve requests | 2024-01-01 10:00:00 | 2024-01-01 10:00:00 |
| 4   | MakerGroup   | Users who submit forms     | 2024-01-01 10:00:00 | 2024-01-01 10:00:00 |

### 2. **Users Table**
**Table Name**: `users`
| id  | user_id       | name          | email              | country | created_at          | updated_at          |
|-----|---------------|---------------|--------------------|---------|---------------------|---------------------|
| 1   | jdoe          | John Doe      | jdoe@example.com   | USA     | 2024-01-01 10:00:00 | 2024-01-01 10:00:00 |
| 2   | asmith        | Alice Smith   | asmith@example.com | UK      | 2024-01-02 11:00:00 | 2024-01-02 11:00:00 |
| 3   | bwhite        | Bob White     | bwhite@example.com | India   | 2024-01-03 12:00:00 | 2024-01-03 12:00:00 |

### 3. **Roles Table**
**Table Name**: `roles`
| id  | name       | description                  | created_at          | updated_at          |
|-----|------------|------------------------------|---------------------|---------------------|
| 1   | Admin      | Full access to all features   | 2024-01-01 10:00:00 | 2024-01-01 10:00:00 |
| 2   | Maker      | Can submit forms and requests | 2024-01-01 10:00:00 | 2024-01-01 10:00:00 |
| 3   | Checker    | Can approve requests          | 2024-01-01 10:00:00 | 2024-01-01 10:00:00 |
| 4   | Viewer     | Read-only access              | 2024-01-01 10:00:00 | 2024-01-01 10:00:00 |

### 4. **Permissions Table**
**Table Name**: `permissions`
| id  | name              | description                             | created_at          | updated_at          |
|-----|-------------------|-----------------------------------------|---------------------|---------------------|
| 1   | view_dashboard    | Can view the dashboard                  | 2024-01-01 10:00:00 | 2024-01-01 10:00:00 |
| 2   | submit_form       | Can submit forms                        | 2024-01-01 10:00:00 | 2024-01-01 10:00:00 |
| 3   | approve_request   | Can approve submitted requests          | 2024-01-01 10:00:00 | 2024-01-01 10:00:00 |
| 4   | edit_settings     | Can modify application settings         | 2024-01-01 10:00:00 | 2024-01-01 10:00:00 |
| 5   | view_reports      | Can view generated reports              | 2024-01-01 10:00:00 | 2024-01-01 10:00:00 |

### 5. **RolePermissions Table**
**Table Name**: `role_permissions`
| id  | role_id | permission_id | 
|-----|---------|---------------|
| 1   | 1       | 1             | 
| 2   | 1       | 2             | 
| 3   | 1       | 3             | 
| 4   | 1       | 4             | 
| 5   | 2       | 2             | 
| 6   | 3       | 3             | 
| 7   | 4       | 1             | 
| 8   | 4       | 5             | 

### 6. **UserRoles Table**
**Table Name**: `user_roles`
| id  | user_id | role_id | assigned_via_ad_group | 
|-----|---------|---------|-----------------------|
| 1   | 1       | 1       | True                  | 
| 2   | 2       | 3       | True                  | 
| 3   | 3       | 2       | True                  | 
| 4   | 1       | 4       | False                 | 

### 7. **ADGroupRoles Table**
**Table Name**: `ad_group_roles`
| id  | ad_group_id | role_id |
|-----|-------------|---------|
| 1   | 1           | 1       |
| 2   | 2           | 4       |
| 3   | 3           | 3       |
| 4   | 4           | 2       |

### 8. **UserSession Table**
**Table Name**: `user_sessions`
| id  | user_id | login_time          | logout_time         | is_active | is_blacklisted | session_token                      |
|-----|---------|---------------------|---------------------|-----------|----------------|------------------------------------|
| 1   | 1       | 2024-01-05 09:00:00 | 2024-01-05 17:00:00 | False     | False          | abc123xyz                           |
| 2   | 2       | 2024-01-05 09:30:00 | NULL                | True      | False          | def456uvw                           |
| 3   | 3       | 2024-01-05 10:00:00 | NULL                | True      | False          | ghi789rst                           |

### Mapping Example

- **ADGroups Table**: Defines the names and descriptions of AD groups.
  - `AdminGroup`: Admins with full access.
  - `UserGroup`: Regular users.
  - `CheckerGroup`: Users who approve requests.
  - `MakerGroup`: Users who submit forms.

- **ADGroupRoles Table**: Maps AD groups to roles.
  - `AdminGroup` (ID: 1) is mapped to the `Admin` role (ID: 1).
  - `UserGroup` (ID: 2) is mapped to the `Viewer` role (ID: 4).
  - `CheckerGroup` (ID: 3) is mapped to the `Checker` role (ID: 3).
  - `MakerGroup` (ID: 4) is mapped to the `Maker` role (ID: 2).

- **UserRoles Table**: Maps users to roles based on their AD group memberships.
  - **John Doe** (`user_id: 1`) belongs to `AdminGroup`, so he is assigned the `Admin` role via `ad_group_roles`. He is also assigned the `Viewer` role directly (manually).

This structure ensures that:
- Users are assigned roles based on their AD group memberships.
- AD groups can be easily updated without having to modify user-specific data.
- Permissions are linked to roles, which are linked to AD groups, simplifying the management of user access across different countries or organizational units.












Based on your requirements, I’ll outline the database tables needed for handling user roles, permissions, and session management, including the necessary columns and how they map together. Here's how you can structure your database:

### 1. **Users Table**
   - **Purpose**: Store basic user information along with their associated AD groups.
   - **Table Name**: `users`
   - **Columns**:
     - `id` (Primary Key, Auto-increment)
     - `user_id` (VARCHAR, Unique): The user's ID (e.g., email or username).
     - `name` (VARCHAR): The user's full name.
     - `email` (VARCHAR): The user's email address.
     - `country` (VARCHAR): The user's country (optional, for country-based roles).
     - `ad_groups` (VARCHAR): A comma-separated list of AD groups the user belongs to.
     - `created_at` (TIMESTAMP): When the user was added to the system.
     - `updated_at` (TIMESTAMP): When the user’s record was last updated.

### 2. **Roles Table**
   - **Purpose**: Define roles that can be assigned to users, either directly or through AD groups.
   - **Table Name**: `roles`
   - **Columns**:
     - `id` (Primary Key, Auto-increment)
     - `name` (VARCHAR, Unique): The name of the role (e.g., "Admin", "Maker", "Checker").
     - `description` (TEXT): A brief description of the role.
     - `created_at` (TIMESTAMP): When the role was created.
     - `updated_at` (TIMESTAMP): When the role was last updated.

### 3. **Permissions Table**
   - **Purpose**: Define the permissions that can be granted to roles, allowing fine-grained control over what each role can do.
   - **Table Name**: `permissions`
   - **Columns**:
     - `id` (Primary Key, Auto-increment)
     - `name` (VARCHAR, Unique): The name of the permission (e.g., "view_dashboard", "submit_form").
     - `description` (TEXT): A brief description of the permission.
     - `created_at` (TIMESTAMP): When the permission was created.
     - `updated_at` (TIMESTAMP): When the permission was last updated.

### 4. **RolePermissions Table**
   - **Purpose**: Map roles to permissions, defining what actions each role is allowed to perform.
   - **Table Name**: `role_permissions`
   - **Columns**:
     - `id` (Primary Key, Auto-increment)
     - `role_id` (Foreign Key to `roles.id`)
     - `permission_id` (Foreign Key to `permissions.id`)

### 5. **UserRoles Table**
   - **Purpose**: Assign roles to users. This can be done either directly or through their AD group memberships.
   - **Table Name**: `user_roles`
   - **Columns**:
     - `id` (Primary Key, Auto-increment)
     - `user_id` (Foreign Key to `users.id`)
     - `role_id` (Foreign Key to `roles.id`)
     - `assigned_via_ad_group` (BOOLEAN): Indicates if the role was assigned via an AD group.

### 6. **UserSession Table**
   - **Purpose**: Track user sessions, including when they log in and out, and whether they are currently active or blacklisted.
   - **Table Name**: `user_sessions`
   - **Columns**:
     - `id` (Primary Key, Auto-increment)
     - `user_id` (Foreign Key to `users.id`)
     - `login_time` (TIMESTAMP): When the user logged in.
     - `logout_time` (TIMESTAMP, Nullable): When the user logged out.
     - `is_active` (BOOLEAN): Whether the session is currently active.
     - `is_blacklisted` (BOOLEAN): Whether the user is blacklisted from logging in.
     - `session_token` (VARCHAR, Unique): The session token for the current login session.

### Mapping and Implementation

- **User and Roles Mapping**: When a user logs in, their AD groups are checked, and roles are assigned based on those groups. These roles are mapped in the `user_roles` table. You can also assign roles directly to users if necessary.

- **Role and Permissions Mapping**: The `role_permissions` table maps each role to specific permissions, defining what actions each role can perform in the application.

- **Authorization Logic**:
  - When a user attempts to access a feature or API, check the user’s roles (from `user_roles`) and their associated permissions (from `role_permissions`).
  - If the user has the required permission, they are allowed access; otherwise, they are denied.

- **Handling Country-Specific Roles**: You can add logic that assigns roles based on the `country` field in the `users` table. For instance, users from a specific country can be assigned additional roles automatically.

- **Session Management**: The `user_sessions` table tracks login and logout times. You can use this to manage active sessions and enforce session timeouts or blacklist users if necessary.

### Workflow:

1. **User Login**: 
   - Retrieve or create the user in the `users` table.
   - Fetch the user's AD groups.
   - Map these groups to roles using the `user_roles` table.
   - Start a session and record it in the `user_sessions` table.

2. **Role Assignment**:
   - Assign roles directly or via AD groups, then map these roles to specific permissions.

3. **Authorization Check**:
   - For each action (e.g., API call or page access), check if the user’s roles grant them the necessary permissions.
   - Deny access if the user lacks the required permissions.

### Example Flow:

- A user logs in, and their AD groups are checked.
- Based on the groups, roles are assigned (e.g., "Maker", "Checker").
- These roles are mapped to permissions like "submit_form" or "approve_workflow".
- When the user tries to submit a form, the application checks if they have the "submit_form" permission via their roles.
- If yes, the action proceeds; otherwise, access is denied.

This approach gives you flexibility in managing user permissions, handling different AD group structures, and supporting country-specific roles or permissions.







from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required
from datetime import datetime
import pandas as pd
import os
from werkzeug.utils import secure_filename
from app.models.model_designer import Workflow, KeyNameMapping, VolumeMatrix
from app.database import session_scope
from sqlalchemy import func

bp = Blueprint('upload', __name__, url_prefix='/api/upload')
api = Api(bp)

ALLOWED_EXTENSIONS = {'xls', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class UploadResource(Resource):
    @cross_origin()
    @jwt_required()
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

            missing_workflows = set()
            key_store_workflows = set()
            volume_store_workflows = set()

            try:
                with session_scope('DESIGNER') as session:
                    results = {
                        'AppStore': [],
                        'KeyStore': [],
                        'VolumeStore': [],
                        'MissingWorkflows': []
                    }
                    workflow_names_from_appstore = set()

                    # Process AppStore sheet
                    app_store_data = pd.read_excel(file_path, sheet_name='AppStore', header=1)
                    if 'WorkflowName' in app_store_data.columns:
                        new_workflows = []
                        for _, row in app_store_data.iterrows():
                            workflow_name = str(row['WorkflowName'])
                            workflow_names_from_appstore.add(workflow_name)

                            existing_workflow = session.query(Workflow).filter_by(workflow_name=workflow_name, is_active=True).first()
                            if not existing_workflow:
                                new_workflows.append(Workflow(
                                    workflow_name=workflow_name,
                                    workflow_url=row.get('WorkflowURL'),
                                    environment=row.get('Environment'),
                                    window_titles=row.get('WindowTitles'),
                                    each_image_capture=row.get('EachImageCapture'),
                                    is_active=True,
                                    created_date=datetime.utcnow()
                                ))
                                results['AppStore'].append(f"Created: {workflow_name}")
                            else:
                                results['AppStore'].append(f"Exists: {workflow_name}")

                        if new_workflows:
                            session.bulk_save_objects(new_workflows)

                    # Process KeyStore sheet
                    key_store_data = pd.read_excel(file_path, sheet_name='KeyStore', header=1)
                    if 'WorkflowName' in key_store_data.columns:
                        keyname_entries = []
                        for _, row in key_store_data.iterrows():
                            workflow_name = str(row['WorkflowName'])
                            if workflow_name not in workflow_names_from_appstore:
                                key_store_workflows.add(workflow_name)
                                continue

                            if 'Keyname' in row and 'Layout' in row and 'Remarks' in row:
                                workflow = session.query(Workflow).filter_by(workflow_name=workflow_name).first()
                                if workflow:
                                    existing_key_mapping = session.query(KeyNameMapping).filter_by(
                                        workflow_id=workflow.id,
                                        activity_key_name=row['Keyname'],
                                        activity_key_layout=row['Layout'],
                                        remarks=row['Remarks'],
                                        is_active=True
                                    ).first()
                                    
                                    if existing_key_mapping:
                                        results['KeyStore'].append(f"Duplicate: {workflow_name} - {row['Keyname']}")
                                        continue
                                    
                                    keyname_entries.append(KeyNameMapping(
                                        workflow_id=workflow.id,
                                        activity_key_name=row['Keyname'],
                                        activity_key_layout=row['Layout'],
                                        remarks=row['Remarks'],
                                        is_active=True,
                                        created_date=datetime.utcnow()
                                    ))
                                    results['KeyStore'].append(f"Inserted: {workflow_name} - {row['Keyname']}")
                                else:
                                    results['KeyStore'].append(f"Missing Workflow: {workflow_name}")

                        if keyname_entries:
                            session.bulk_save_objects(keyname_entries)

                    # Process VolumeStore sheet
                    volume_store_data = pd.read_excel(file_path, sheet_name='VolumeStore', header=1)
                    if 'WorkflowName' in volume_store_data.columns:
                        volume_entries = []
                        pattern_key_sets = {}  # For tracking unique key sets within a pattern
                        button_types_per_pattern = {}  # For tracking button types within patterns

                        for _, row in volume_store_data.iterrows():
                            workflow_name = str(row['WorkflowName'])
                            if workflow_name not in workflow_names_from_appstore:
                                volume_store_workflows.add(workflow_name)
                                continue

                            if 'ProcessName' in row and 'Pattern' in row and 'KeyName' in row:
                                workflow = session.query(Workflow).filter_by(workflow_name=workflow_name).first()
                                if workflow:
                                    process_name = str(row['ProcessName'])
                                    pattern = row['Pattern']
                                    key_name = row['KeyName']
                                    layout = row['Layout']
                                    key_type = row['Type']

                                    # Ensure combination of keys doesn't already exist
                                    existing_entry = session.query(VolumeMatrix).filter(
                                        VolumeMatrix.workflow_id == workflow.id,
                                        VolumeMatrix.process_name == process_name,
                                        VolumeMatrix.activity_key_name == key_name,
                                        VolumeMatrix.activity_key_layout == layout,
                                        VolumeMatrix.activity_key_type == key_type,
                                        VolumeMatrix.pattern == pattern,
                                        VolumeMatrix.is_active == True
                                    ).first()
                                    
                                    if existing_entry:
                                        results['VolumeStore'].append(f"Duplicate: {workflow_name} - {process_name} - {key_name} - {layout} - {key_type}")
                                        continue

                                    # Ensure unique activity key name within the pattern
                                    if (pattern, key_name) in pattern_key_sets:
                                        results['VolumeStore'].append(f"Duplicate KeyName: {workflow_name} - {process_name} - {key_name} within Pattern {pattern}")
                                        continue
                                    pattern_key_sets[(pattern, key_name)] = True

                                    # Ensure at least one button type per pattern
                                    if pattern not in button_types_per_pattern:
                                        button_types_per_pattern[pattern] = False
                                    if key_type == "button":  # Assuming "button" is the type for buttons
                                        button_types_per_pattern[pattern] = True

                                    # Track the set of keys per pattern for duplicate set validation
                                    key_set = frozenset((key_name, layout, key_type))
                                    if pattern in pattern_key_sets and key_set in pattern_key_sets[pattern]:
                                        results['VolumeStore'].append(f"Duplicate Key Set: {workflow_name} - {process_name} - {key_name} within Pattern {pattern}")
                                        continue
                                    pattern_key_sets.setdefault(pattern, []).append(key_set)

                                    # Insert the valid entry
                                    volume_entries.append(VolumeMatrix(
                                        workflow_id=workflow.id,
                                        process_name=process_name,
                                        pattern=pattern,
                                        activity_key_name=key_name,
                                        activity_key_layout=layout,
                                        activity_key_type=key_type,
                                        # Other fields here...
                                        created_date=datetime.utcnow(),
                                        created_by=request.headers.get('Createdby', 'unknown'),
                                        is_active=True,
                                    ))

                        # Ensure at least one button type per pattern validation
                        for pattern, has_button in button_types_per_pattern.items():
                            if not has_button:
                                results['VolumeStore'].append(f"Missing Button Type in Pattern {pattern}")
                                return jsonify(results), 400

                        if volume_entries:
                            session.bulk_save_objects(volume_entries)

                    if key_store_workflows or volume_store_workflows:
                        missing_workflows_info = {
                            'KeyStore': list(key_store_workflows),
                            'VolumeStore': list(volume_store_workflows)
                        }
                        results['MissingWorkflows'] = missing_workflows_info
                        return jsonify(results), 400

                    session.commit()
                    return jsonify(results), 201

            except Exception as e:
                return jsonify({'message': str(e)}), 500
        else:
            return jsonify({'message': 'Invalid file type'}), 400

api.add_resource(UploadResource, '/')








from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required
from datetime import datetime
import pandas as pd
import os
from werkzeug.utils import secure_filename
from app.models.model_designer import Workflow, KeyNameMapping, VolumeMatrix
from app.database import session_scope
from sqlalchemy import func

bp = Blueprint('upload', __name__, url_prefix='/api/upload')
api = Api(bp)

ALLOWED_EXTENSIONS = {'xls', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class UploadResource(Resource):
    @cross_origin()
    @jwt_required()
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

            missing_workflows = set()
            key_store_workflows = set()
            volume_store_workflows = set()

            try:
                with session_scope('DESIGNER') as session:
                    results = {
                        'AppStore': [],
                        'KeyStore': [],
                        'VolumeStore': [],
                        'MissingWorkflows': []
                    }
                    workflow_names_from_appstore = set()

                    # Process AppStore sheet
                    app_store_data = pd.read_excel(file_path, sheet_name='AppStore', header=1)
                    if 'WorkflowName' in app_store_data.columns:
                        new_workflows = []
                        for _, row in app_store_data.iterrows():
                            workflow_name = str(row['WorkflowName'])
                            workflow_names_from_appstore.add(workflow_name)

                            existing_workflow = session.query(Workflow).filter_by(workflow_name=workflow_name, is_active=True).first()
                            if not existing_workflow:
                                new_workflows.append(Workflow(
                                    workflow_name=workflow_name,
                                    workflow_url=row.get('WorkflowURL'),
                                    environment=row.get('Environment'),
                                    window_titles=row.get('WindowTitles'),
                                    each_image_capture=row.get('EachImageCapture'),
                                    is_active=True,
                                    created_date=datetime.utcnow()
                                ))
                                results['AppStore'].append(f"Created: {workflow_name}")
                            else:
                                results['AppStore'].append(f"Exists: {workflow_name}")

                        if new_workflows:
                            session.bulk_save_objects(new_workflows)

                    # Process KeyStore sheet
                    key_store_data = pd.read_excel(file_path, sheet_name='KeyStore', header=1)
                    if 'WorkflowName' in key_store_data.columns:
                        keyname_entries = []
                        for _, row in key_store_data.iterrows():
                            workflow_name = str(row['WorkflowName'])
                            if workflow_name not in workflow_names_from_appstore:
                                key_store_workflows.add(workflow_name)
                                continue

                            if 'Keyname' in row and 'Layout' in row and 'Remarks' in row:
                                workflow = session.query(Workflow).filter_by(workflow_name=workflow_name).first()
                                if workflow:
                                    existing_key_mapping = session.query(KeyNameMapping).filter_by(
                                        workflow_id=workflow.id,
                                        activity_key_name=row['Keyname'],
                                        activity_key_layout=row['Layout'],
                                        remarks=row['Remarks'],
                                        is_active=True
                                    ).first()
                                    
                                    if existing_key_mapping:
                                        results['KeyStore'].append(f"Duplicate: {workflow_name} - {row['Keyname']}")
                                        continue
                                    
                                    keyname_entries.append(KeyNameMapping(
                                        workflow_id=workflow.id,
                                        activity_key_name=row['Keyname'],
                                        activity_key_layout=row['Layout'],
                                        remarks=row['Remarks'],
                                        is_active=True,
                                        created_date=datetime.utcnow()
                                    ))
                                    results['KeyStore'].append(f"Inserted: {workflow_name} - {row['Keyname']}")
                                else:
                                    results['KeyStore'].append(f"Missing Workflow: {workflow_name}")

                        if keyname_entries:
                            session.bulk_save_objects(keyname_entries)

                    # Process VolumeStore sheet
                    volume_store_data = pd.read_excel(file_path, sheet_name='VolumeStore', header=1)
                    if 'WorkflowName' in volume_store_data.columns:
                        volume_entries = []
                        for _, row in volume_store_data.iterrows():
                            workflow_name = str(row['WorkflowName'])
                            if workflow_name not in workflow_names_from_appstore:
                                volume_store_workflows.add(workflow_name)
                                continue

                            if 'ProcessName' in row and 'Pattern' in row and 'KeyName' in row:
                                workflow = session.query(Workflow).filter_by(workflow_name=workflow_name).first()
                                if workflow:
                                    process_name = str(row['ProcessName'])
                                    
                                    max_pattern = session.query(func.max(VolumeMatrix.pattern)).filter(
                                        VolumeMatrix.workflow_id == workflow.id,
                                        VolumeMatrix.process_name == process_name,
                                        VolumeMatrix.is_active == True
                                    ).scalar() or 0
                                    
                                    pattern = row['Pattern']
                                    key_name = row['KeyName']
                                    layout = row['Layout']
                                    key_type = row['Type']
                                    volume_type = row.get('VolumeType')
                                    field_name = row.get('FieldName')
                                    field_layout = row.get('FieldLayout')
                                    status = row.get('Status')
                                    selected_value = row.get('SelectedValue', 'no') == 'yes'

                                    existing_entry = session.query(VolumeMatrix).filter(
                                        VolumeMatrix.workflow_id == workflow.id,
                                        VolumeMatrix.process_name == process_name,
                                        VolumeMatrix.activity_key_name == key_name,
                                        VolumeMatrix.activity_key_layout == layout,
                                        VolumeMatrix.activity_key_type == key_type,
                                        VolumeMatrix.is_active == True
                                    ).first()
                                    
                                    if existing_entry:
                                        results['VolumeStore'].append(f"Duplicate: {workflow_name} - {key_name} - {layout} - {key_type}")
                                        continue

                                    if not pattern or not key_name or not layout:
                                        results['VolumeStore'].append(f"Invalid data: {workflow_name} - {key_name} - {layout} - {key_type}")
                                        continue

                                    volume_entries.append(VolumeMatrix(
                                        workflow_id=workflow.id,
                                        process_name=process_name,
                                        pattern=max_pattern + 1,
                                        activity_key_name=key_name,
                                        activity_key_layout=layout,
                                        activity_key_type=key_type,
                                        volume_type=volume_type,
                                        is_value=selected_value,
                                        field_name=field_name,
                                        field_layout=field_layout,
                                        status=status,
                                        created_date=datetime.utcnow(),
                                        created_by=request.headers.get('Createdby', 'unknown'),
                                        is_active=True,
                                    ))
                                    results['VolumeStore'].append(f"Inserted: {workflow_name} - {key_name} - {layout} - {key_type}")
                                else:
                                    results['VolumeStore'].append(f"Missing Workflow: {workflow_name}")

                        if volume_entries:
                            session.bulk_save_objects(volume_entries)

                    if key_store_workflows or volume_store_workflows:
                        missing_workflows_info = {
                            'KeyStore': list(key_store_workflows),
                            'VolumeStore': list(volume_store_workflows)
                        }
                        results['MissingWorkflows'] = missing_workflows_info
                        return jsonify(results), 400

                    session.commit()
                    return jsonify(results), 201

            except Exception as e:
                return jsonify({'message': str(e)}), 500
        else:
            return jsonify({'message': 'Invalid file type'}), 400

api.add_resource(UploadResource, '/')













-----------
------------------
--------------------------





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
        data = request.get_json()

        workflow_id = data['workflowId']
        process_name = data['processName']
        fields = data['fields']

        # Step 1: Check for unique keyNames within the provided fields
        seen_keynames = set()
        for field in fields:
            key_name = field['keyName']
            if key_name in seen_keynames:
                return {"message": f"Duplicate keyName '{key_name}' in the provided fields"}, 400
            seen_keynames.add(key_name)

        with session_scope() as session:
            # Step 2: Prepare data for checking existing records and creating new entries
            entries_to_check = []
            new_entries = []

            for field in fields:
                entry_tuple = (workflow_id, process_name, field['keyName'], field['layout'])
                entries_to_check.append(entry_tuple)

                new_entries.append(KeyNameMapping(
                    workflow_id=workflow_id,
                    process_name=process_name,
                    activity_key_name=field['keyName'],
                    activity_key_layout=field['layout'],
                    remarks=field['remarks'],
                    created_date=datetime.utcnow()
                ))

            # Step 3: Check for existing entries in the database
            existing_entries = session.query(
                tuple_(KeyNameMapping.workflow_id, KeyNameMapping.process_name, KeyNameMapping.activity_key_name, KeyNameMapping.activity_key_layout)
            ).filter(
                tuple_(KeyNameMapping.workflow_id, KeyNameMapping.process_name, KeyNameMapping.activity_key_name, KeyNameMapping.activity_key_layout).in_(entries_to_check)
            ).all()

            # Convert existing entries to a set for quick lookup
            existing_set = set(existing_entries)

            # Step 4: Filter out new entries that already exist in the database
            filtered_new_entries = [
                entry for entry in new_entries
                if (entry.workflow_id, entry.process_name, entry.activity_key_name, entry.activity_key_layout) not in existing_set
            ]

            # Step 5: Handle duplicates
            if len(filtered_new_entries) < len(new_entries):
                return {"message": "One or more key name mappings already exist in the database"}, 400

            # Step 6: Bulk save all valid new entries
            if filtered_new_entries:
                session.bulk_save_objects(filtered_new_entries)

        return {"message": "Key name mappings added successfully"}, 201

api.add_resource(KeynameMappingResource, '/')





Yes, there are several optimizations you can make to improve performance and reduce latency in the `post` method. Here are some suggestions:

1. **Batch Queries**: Minimize the number of queries to the database. For example, you can retrieve all existing whitelist entries and their titles in a single query rather than querying in a loop.

2. **Use Set Operations**: To check for title overlaps more efficiently, you can use set operations directly instead of processing them in a loop.

3. **Optimize Workflow Lookup**: Use a single query to check for the existence of the workflow and get its ID if it exists.

Here's an optimized version of your `post` method:

```python
from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required
from flask_cors import cross_origin
from sqlalchemy.orm import aliased
from sqlalchemy import func
from app.models.model_designer import Workflow, Whitelist
from app.database import session_scope
from datetime import datetime
import validators

bp = Blueprint('whitelists', __name__, url_prefix='/api/whitelists')
api = Api(bp)

class WhitelistResource(Resource):
    @jwt_required()
    def get(self):
        with session_scope('DESIGNER') as session:
            workflow_alias = aliased(Workflow)
            whitelist_alias = aliased(Whitelist)
            query = session.query(
                whitelist_alias.id,
                whitelist_alias.workflow_name,
                whitelist_alias.workflow_url,
                whitelist_alias.environment,
                whitelist_alias.is_active,
                workflow_alias.system_name,
                whitelist_alias.window_titles,
                whitelist_alias.full_image_capture
            ).join(workflow_alias, whitelist_alias.workflow_id == workflow_alias.id).filter(whitelist_alias.is_active == True)
            whitelists = query.all()
            data = [{
                'id': w.id,
                'workflow_name': w.workflow_name,
                'system': w.system_name,
                'url': w.workflow_url,
                'environment': w.environment,
                'is_active': w.is_active,
                'titles': w.window_titles,
                'full_image_capture': w.full_image_capture
            } for w in whitelists]
        return jsonify(data)

    @cross_origin()
    @jwt_required()
    def post(self):
        data = request.get_json()

        # Validate URL
        if not validators.url(data['url']):
            return jsonify({'message': 'Invalid URL'}), 400

        # Ensure at least two titles
        titles = [title.strip() for title in data['titles'].split(',')]
        if len(titles) < 2:
            return jsonify({'message': 'At least two page titles are required'}), 400

        with session_scope('DESIGNER') as session:
            workflow_name = data['workflow_name']

            # Retrieve or create the workflow and get its ID
            workflow = session.query(Workflow).filter_by(workflow_name=workflow_name).first()
            if not workflow:
                new_workflow = Workflow(
                    workflow_name=workflow_name,
                    system_name=workflow_name,
                    created_date=datetime.utcnow()
                )
                session.add(new_workflow)
                session.flush()  # Commit to get the new workflow ID
                work_id = new_workflow.id
            else:
                work_id = workflow.id

            # Check for existing whitelist entry
            existing_wlist = session.query(Whitelist).filter_by(
                workflow_id=work_id,
                workflow_url=data['url'],
                environment=data['environment'],
                window_titles=data['titles']
            ).first()

            if existing_wlist:
                return jsonify({'message': 'Whitelist Entry Already Exists'}), 409

            # Fetch all existing whitelists and their window_titles
            existing_whitelists = session.query(Whitelist).filter(Whitelist.is_active == True).all()
            existing_titles = set()

            for wl in existing_whitelists:
                titles = set(title.strip() for title in wl.window_titles.split(','))
                existing_titles.update(titles)

            # Convert new titles to a set
            new_titles = set(titles)

            # Check for overlap
            overlap = new_titles & existing_titles  # Intersection of sets
            if overlap:
                return jsonify({'message': f'One or more window titles already exist with another workflow: {", ".join(overlap)}'}), 400

            # Create new whitelist entry
            new_whitelist = Whitelist(
                workflow_id=work_id,
                workflow_name=workflow_name,
                workflow_url=data['url'],
                environment=data['environment'],
                is_active=True,
                window_titles=data['titles'],
                full_image_capture=data.get('screen_capture', 'no') == 'yes',  # Update based on screen_capture value
                created_date=datetime.utcnow()
            )
            session.add(new_whitelist)

        return jsonify({'message': 'Whitelist entry created successfully', 'workflow_id': work_id}), 201

class WhitelistDetailResource(Resource):
    @cross_origin()
    @jwt_required()
    def put(self, id):
        with session_scope('DESIGNER') as session:
            data = request.get_json()
            whitelist = session.query(Whitelist).get(id)
            if not whitelist:
                return {'message': 'Whitelist entry not found'}, 404

            whitelist.workflow_name = data['workflow_name']
            whitelist.workflow_url = data['url']
            whitelist.environment = data['environment']
            whitelist.is_active = data['isActive']
            whitelist.window_titles = data['title']
            whitelist.full_image_capture = data.get('screen_capture', 'no') == 'yes'  # Update based on screen_capture value
            whitelist.modified_date = datetime.utcnow()

        return {'message': 'Whitelist entry updated successfully'}, 200

    @cross_origin()
    @jwt_required()
    def delete(self, id):
        with session_scope('DESIGNER') as session:
            whitelist = session.query(Whitelist).get(id)
            if not whitelist:
                return {'message': 'Whitelist entry not found'}, 404
            whitelist.is_active = False
        return {'message': 'Whitelist entry deleted successfully'}, 200

api.add_resource(WhitelistResource, '/')
api.add_resource(WhitelistDetailResource, '/<int:id>')
```

### Key Optimizations:

1. **Batch Queries**: Retrieve all necessary whitelist entries and their titles in one go. This reduces the number of database interactions compared to querying in a loop.

2. **Set Operations**: Use set operations to handle title overlap checks. This is efficient for large datasets.

3. **Single Workflow Lookup**: Retrieve or create the workflow and get its ID in one operation to minimize database calls.

4. **Error Handling and Validation**: Included validation for URL and page titles before processing, reducing unnecessary database interactions for invalid data.

By implementing these optimizations, you should see improved performance and reduced latency in your `post` method.






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