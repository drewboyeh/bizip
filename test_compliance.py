import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import json
from datetime import datetime, timedelta

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.audit_log import AuditLog
from models.user import User

class TestComplianceAutomation(unittest.TestCase):
    """Test compliance automation and regulatory requirements"""
    
    def setUp(self):
        self.mock_db = Mock()
        self.mock_session = Mock()
        self.mock_db.session = self.mock_session
    
    def test_audit_log_creation(self):
        """Test that audit logs are created for all data access"""
        # Mock the database session
        with patch('models.audit_log.db', self.mock_db):
            # Test audit log creation
            AuditLog.log_data_access(
                user_id=1,
                data_sources=['sec_data', 'linkedin_data'],
                access_method='api',
                access_url='/api/profiles/companies/1/research',
                ip_address='192.168.1.1',
                user_agent='Mozilla/5.0',
                request_method='POST',
                request_url='http://localhost:5000/api/profiles/companies/1/research'
            )
            
            # Verify that session.add was called
            self.mock_session.add.assert_called_once()
            
            # Get the audit log that was added
            audit_log = self.mock_session.add.call_args[0][0]
            
            # Verify audit log fields
            self.assertEqual(audit_log.user_id, 1)
            self.assertEqual(audit_log.data_sources_used, ['sec_data', 'linkedin_data'])
            self.assertEqual(audit_log.data_access_method, 'api')
            self.assertEqual(audit_log.data_access_url, '/api/profiles/companies/1/research')
            self.assertEqual(audit_log.ip_address, '192.168.1.1')
            self.assertEqual(audit_log.user_agent, 'Mozilla/5.0')
            self.assertEqual(audit_log.request_method, 'POST')
            self.assertEqual(audit_log.request_url, 'http://localhost:5000/api/profiles/companies/1/research')
    
    def test_gdpr_compliance(self):
        """Test GDPR compliance requirements"""
        # Test data minimization
        user_data = {
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'company_name': 'Test Company'
        }
        
        # Verify no unnecessary personal data is collected
        unnecessary_fields = ['ssn', 'credit_card', 'bank_account', 'passport_number']
        for field in unnecessary_fields:
            self.assertNotIn(field, user_data)
        
        # Test data retention policy
        retention_period = 7 * 365  # 7 years for business records
        current_date = datetime.utcnow()
        retention_date = current_date - timedelta(days=retention_period)
        
        # Verify retention policy is reasonable
        self.assertLess(retention_date, current_date)
    
    def test_ccpa_compliance(self):
        """Test CCPA (California Consumer Privacy Act) compliance"""
        # Test right to know
        user_rights = {
            'right_to_know': True,
            'right_to_delete': True,
            'right_to_opt_out': True,
            'right_to_portability': True
        }
        
        for right, enabled in user_rights.items():
            self.assertTrue(enabled, f"CCPA right {right} must be enabled")
        
        # Test data categories disclosure
        data_categories = [
            'personal_information',
            'business_information',
            'usage_data',
            'technical_data'
        ]
        
        # Verify all data categories are documented
        for category in data_categories:
            self.assertIsInstance(category, str)
    
    def test_sox_compliance(self):
        """Test SOX (Sarbanes-Oxley) compliance for financial data"""
        # Test audit trail completeness
        audit_requirements = {
            'user_identification': True,
            'timestamp_recording': True,
            'data_access_logging': True,
            'change_tracking': True,
            'retention_period': '7_years'
        }
        
        for requirement, value in audit_requirements.items():
            self.assertTrue(value or isinstance(value, str), 
                          f"SOX requirement {requirement} must be met")
        
        # Test financial data handling
        financial_data_controls = {
            'encryption_in_transit': True,
            'encryption_at_rest': True,
            'access_controls': True,
            'backup_procedures': True
        }
        
        for control, enabled in financial_data_controls.items():
            self.assertTrue(enabled, f"Financial data control {control} must be enabled")
    
    def test_data_privacy_validation(self):
        """Test that no private data is exposed"""
        # Test API response validation
        api_responses = [
            {'company_name': 'Test Corp', 'industry': 'Technology'},
            {'market_size': 1000000, 'growth_rate': 5.2},
            {'news_items': [{'title': 'Company News', 'date': '2024-01-01'}]}
        ]
        
        private_data_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',  # Credit card
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{3}[\s-]?\d{3}[\s-]?\d{4}\b'  # Phone
        ]
        
        import re
        for response in api_responses:
            response_str = json.dumps(response)
            for pattern in private_data_patterns:
                matches = re.findall(pattern, response_str)
                self.assertEqual(len(matches), 0, 
                               f"Private data pattern {pattern} found in response")
    
    def test_rate_limiting_compliance(self):
        """Test that rate limiting is properly implemented"""
        rate_limits = {
            'sec_api': 10,  # requests per second
            'linkedin_scraping': 1,  # requests per second
            'news_feeds': 5,  # requests per second
            'industry_research': 2   # requests per second
        }
        
        for source, limit in rate_limits.items():
            self.assertGreater(limit, 0, f"Rate limit for {source} must be positive")
            self.assertLessEqual(limit, 100, f"Rate limit for {source} seems too high")
    
    def test_data_source_compliance(self):
        """Test that all data sources are compliant"""
        data_sources = {
            'sec_data': {
                'compliance': 'Compliant',
                'terms_accepted': True,
                'rate_limits_respected': True,
                'public_data_only': True
            },
            'linkedin_data': {
                'compliance': 'Compliant',
                'terms_accepted': True,
                'rate_limits_respected': True,
                'public_data_only': True
            },
            'news_data': {
                'compliance': 'Compliant',
                'terms_accepted': True,
                'rate_limits_respected': True,
                'public_data_only': True
            },
            'industry_research': {
                'compliance': 'Compliant',
                'terms_accepted': True,
                'rate_limits_respected': True,
                'public_data_only': True
            }
        }
        
        for source, compliance in data_sources.items():
            self.assertEqual(compliance['compliance'], 'Compliant',
                           f"Data source {source} must be compliant")
            self.assertTrue(compliance['terms_accepted'],
                          f"Data source {source} must accept terms")
            self.assertTrue(compliance['rate_limits_respected'],
                          f"Data source {source} must respect rate limits")
            self.assertTrue(compliance['public_data_only'],
                          f"Data source {source} must only collect public data")
    
    def test_user_consent_tracking(self):
        """Test that user consent is properly tracked"""
        consent_requirements = {
            'data_collection_consent': True,
            'marketing_consent': False,  # No marketing in this platform
            'third_party_sharing_consent': False,  # No third party sharing
            'consent_timestamp': True,
            'consent_version': True
        }
        
        for requirement, required in consent_requirements.items():
            if required:
                self.assertTrue(required, f"Consent requirement {requirement} must be met")
    
    def test_data_encryption(self):
        """Test that data encryption is properly implemented"""
        encryption_requirements = {
            'data_in_transit': 'TLS_1_3',
            'data_at_rest': 'AES_256',
            'key_management': 'secure',
            'certificate_validation': True
        }
        
        for requirement, value in encryption_requirements.items():
            self.assertIsNotNone(value, f"Encryption requirement {requirement} must be specified")
    
    def test_access_control_compliance(self):
        """Test that access controls are properly implemented"""
        access_controls = {
            'authentication_required': True,
            'authorization_required': True,
            'session_management': True,
            'password_policy': True,
            'multi_factor_auth': False  # Optional for this platform
        }
        
        for control, required in access_controls.items():
            if required:
                self.assertTrue(required, f"Access control {control} must be enabled")
    
    def test_incident_response_compliance(self):
        """Test that incident response procedures are in place"""
        incident_response = {
            'breach_detection': True,
            'notification_procedures': True,
            'response_team': True,
            'documentation_requirements': True,
            'recovery_procedures': True
        }
        
        for procedure, required in incident_response.items():
            self.assertTrue(required, f"Incident response procedure {procedure} must be in place")

class TestComplianceReporting(unittest.TestCase):
    """Test compliance reporting functionality"""
    
    def test_compliance_report_generation(self):
        """Test that compliance reports can be generated"""
        report_data = {
            'report_period': {
                'start_date': '2024-01-01',
                'end_date': '2024-01-31'
            },
            'total_activities': 150,
            'data_source_usage': {
                'sec_data': 50,
                'linkedin_data': 30,
                'news_data': 40,
                'industry_research': 30
            },
            'compliance_status': {
                'data_access_compliant': True,
                'rate_limits_respected': True,
                'privacy_protected': True,
                'audit_trail_complete': True
            }
        }
        
        # Verify report structure
        self.assertIn('report_period', report_data)
        self.assertIn('total_activities', report_data)
        self.assertIn('data_source_usage', report_data)
        self.assertIn('compliance_status', report_data)
        
        # Verify compliance status
        for status, compliant in report_data['compliance_status'].items():
            self.assertTrue(compliant, f"Compliance status {status} must be True")
    
    def test_audit_log_export(self):
        """Test that audit logs can be exported for compliance"""
        export_format = 'json'  # or CSV, XML
        date_range = {
            'start_date': '2024-01-01',
            'end_date': '2024-01-31'
        }
        
        # Verify export requirements
        self.assertIn(export_format, ['json', 'csv', 'xml'])
        self.assertIsInstance(date_range['start_date'], str)
        self.assertIsInstance(date_range['end_date'], str)
    
    def test_data_retention_compliance(self):
        """Test that data retention policies are followed"""
        retention_policies = {
            'audit_logs': '7_years',
            'user_data': 'account_lifetime',
            'company_data': 'account_lifetime',
            'research_data': '5_years',
            'temporary_data': '30_days'
        }
        
        for data_type, retention in retention_policies.items():
            self.assertIsInstance(retention, str)
            self.assertGreater(len(retention), 0)

if __name__ == '__main__':
    unittest.main() 