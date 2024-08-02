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