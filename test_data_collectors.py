import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_collectors.sec_data import SECDataCollector
from data_collectors.linkedin_data import LinkedInDataCollector
from data_collectors.news_data import NewsDataCollector
from data_collectors.industry_research import IndustryResearchCollector

class TestSECDataCollector(unittest.TestCase):
    """Test SEC data collector compliance and functionality"""
    
    def setUp(self):
        self.collector = SECDataCollector()
    
    def test_compliance_info(self):
        """Test that SEC collector provides compliance information"""
        compliance_info = self.collector.get_compliance_info()
        
        self.assertIn('data_source', compliance_info)
        self.assertIn('access_method', compliance_info)
        self.assertIn('rate_limiting', compliance_info)
        self.assertIn('privacy_impact', compliance_info)
        self.assertIn('compliance_status', compliance_info)
        
        self.assertEqual(compliance_info['data_source'], 'SEC EDGAR Database')
        self.assertEqual(compliance_info['access_method'], 'Public API')
        self.assertEqual(compliance_info['rate_limiting'], '10 requests per second')
        self.assertEqual(compliance_info['privacy_impact'], 'Low - All data is public')
        self.assertEqual(compliance_info['compliance_status'], 'Fully compliant with SEC terms of use')
    
    def test_rate_limiting(self):
        """Test that rate limiting is respected"""
        import time
        start_time = time.time()
        
        # Call rate limiting method multiple times
        for _ in range(5):
            self.collector._respect_sec_rate_limits()
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Should take at least 0.5 seconds (5 * 0.1)
        self.assertGreaterEqual(elapsed_time, 0.4)
    
    def test_company_data_collection(self):
        """Test company data collection returns expected structure"""
        with patch.object(self.collector, '_find_company_cik', return_value='0000320193'):
            with patch.object(self.collector, '_get_company_info', return_value={'name': 'Test Company'}):
                with patch.object(self.collector, '_get_recent_filings', return_value=[]):
                    with patch.object(self.collector, '_get_financial_data', return_value={}):
                        result = self.collector.collect_company_data('Test Company')
        
        self.assertIsNotNone(result)
        self.assertIn('cik', result)
        self.assertIn('company_info', result)
        self.assertIn('recent_filings', result)
        self.assertIn('financial_data', result)
        self.assertIn('last_updated', result)
    
    def test_no_private_data_collected(self):
        """Test that no private data is collected"""
        with patch.object(self.collector, '_find_company_cik', return_value='0000320193'):
            with patch.object(self.collector, '_get_company_info', return_value={'name': 'Test Company'}):
                with patch.object(self.collector, '_get_recent_filings', return_value=[]):
                    with patch.object(self.collector, '_get_financial_data', return_value={}):
                        result = self.collector.collect_company_data('Test Company')
        
        # Check that no private data fields are present
        result_str = str(result).lower()
        private_fields = ['ssn', 'credit_card', 'bank_account', 'password', 'private_key']
        
        for field in private_fields:
            self.assertNotIn(field, result_str)

class TestLinkedInDataCollector(unittest.TestCase):
    """Test LinkedIn data collector compliance and functionality"""
    
    def setUp(self):
        self.collector = LinkedInDataCollector()
    
    def test_compliance_info(self):
        """Test that LinkedIn collector provides compliance information"""
        compliance_info = self.collector.get_compliance_info()
        
        self.assertIn('data_source', compliance_info)
        self.assertIn('access_method', compliance_info)
        self.assertIn('data_types', compliance_info)
        self.assertIn('privacy_compliance', compliance_info)
        self.assertIn('rate_limiting', compliance_info)
        self.assertIn('terms_compliance', compliance_info)
        
        self.assertEqual(compliance_info['data_source'], 'LinkedIn Public Company Pages')
        self.assertEqual(compliance_info['access_method'], 'Public Web Scraping')
        self.assertEqual(compliance_info['data_types'], 'Public business information only')
        self.assertEqual(compliance_info['privacy_compliance'], 'No personal data collected')
    
    def test_public_data_only(self):
        """Test that only public business data is collected"""
        data_collection_scope = self.collector.get_data_collection_scope()
        excluded_data_types = self.collector.get_excluded_data_types()
        
        # Check that excluded data types are not in collection scope
        for excluded_type in excluded_data_types:
            self.assertNotIn(excluded_type.lower(), [scope.lower() for scope in data_collection_scope])
    
    def test_validate_public_data_only(self):
        """Test validation of public data only"""
        # Test with valid public data
        valid_data = {
            'company_name': 'Test Company',
            'industry': 'Technology',
            'employee_count': 100
        }
        self.assertTrue(self.collector._validate_public_data_only(valid_data))
        
        # Test with potentially private data
        invalid_data = {
            'company_name': 'Test Company',
            'employee_email': 'test@company.com'
        }
        self.assertFalse(self.collector._validate_public_data_only(invalid_data))
    
    def test_rate_limiting(self):
        """Test that rate limiting is respected"""
        import time
        start_time = time.time()
        
        # Call rate limiting method multiple times
        for _ in range(3):
            self.collector._respect_linkedin_rate_limits()
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Should take at least 2.5 seconds (3 * 1 - some tolerance)
        self.assertGreaterEqual(elapsed_time, 2.0)

class TestNewsDataCollector(unittest.TestCase):
    """Test news data collector compliance and functionality"""
    
    def setUp(self):
        self.collector = NewsDataCollector()
    
    def test_compliance_info(self):
        """Test that news collector provides compliance information"""
        compliance_info = self.collector.get_compliance_info()
        
        self.assertIn('data_sources', compliance_info)
        self.assertIn('access_method', compliance_info)
        self.assertIn('rate_limiting', compliance_info)
        self.assertIn('data_retention', compliance_info)
        self.assertIn('privacy_impact', compliance_info)
        self.assertIn('compliance_status', compliance_info)
        
        self.assertEqual(compliance_info['data_sources'], 'Legitimate news RSS feeds')
        self.assertEqual(compliance_info['access_method'], 'Public RSS feeds')
        self.assertEqual(compliance_info['privacy_impact'], 'Low - Only public news content')
    
    def test_news_sources_legitimate(self):
        """Test that only legitimate news sources are used"""
        legitimate_sources = ['reuters', 'bloomberg', 'cnbc', 'wsj', 'ft']
        
        for source in legitimate_sources:
            self.assertIn(source, self.collector.news_sources)
    
    def test_sentiment_analysis(self):
        """Test sentiment analysis functionality"""
        # Test positive sentiment
        positive_text = "Company shows strong growth and positive results"
        sentiment = self.collector._analyze_sentiment(positive_text)
        self.assertEqual(sentiment, 'positive')
        
        # Test negative sentiment
        negative_text = "Company faces decline and losses"
        sentiment = self.collector._analyze_sentiment(negative_text)
        self.assertEqual(sentiment, 'negative')
        
        # Test neutral sentiment
        neutral_text = "Company reports quarterly earnings"
        sentiment = self.collector._analyze_sentiment(neutral_text)
        self.assertEqual(sentiment, 'neutral')
    
    def test_html_cleaning(self):
        """Test HTML tag removal"""
        html_text = "<p>This is <strong>bold</strong> text with <a href='#'>links</a></p>"
        cleaned_text = self.collector._clean_html(html_text)
        
        self.assertNotIn('<p>', cleaned_text)
        self.assertNotIn('<strong>', cleaned_text)
        self.assertNotIn('<a', cleaned_text)
        self.assertIn('This is bold text with links', cleaned_text)

class TestIndustryResearchCollector(unittest.TestCase):
    """Test industry research collector compliance and functionality"""
    
    def setUp(self):
        self.collector = IndustryResearchCollector()
    
    def test_compliance_info(self):
        """Test that industry research collector provides compliance information"""
        compliance_info = self.collector.get_compliance_info()
        
        self.assertIn('data_sources', compliance_info)
        self.assertIn('access_method', compliance_info)
        self.assertIn('data_types', compliance_info)
        self.assertIn('privacy_impact', compliance_info)
        self.assertIn('compliance_status', compliance_info)
        self.assertIn('data_retention', compliance_info)
        
        self.assertEqual(compliance_info['data_sources'], 'Public industry reports and research')
        self.assertEqual(compliance_info['data_types'], 'Aggregated industry statistics and trends')
        self.assertEqual(compliance_info['privacy_impact'], 'Low - No individual company data')
    
    def test_industry_data_structure(self):
        """Test that industry data has expected structure"""
        with patch.object(self.collector, '_collect_market_data', return_value={'market_size': {}}):
            with patch.object(self.collector, '_collect_regulatory_data', return_value={}):
                with patch.object(self.collector, '_collect_technology_trends', return_value={}):
                    with patch.object(self.collector, '_collect_workforce_data', return_value={}):
                        with patch.object(self.collector, '_collect_financial_benchmarks', return_value={}):
                            result = self.collector.collect_industry_data('Technology')
        
        self.assertIsNotNone(result)
        self.assertIn('industry', result)
        self.assertIn('sources', result)
        self.assertIn('last_updated', result)
        self.assertEqual(result['industry'], 'Technology')
    
    def test_no_individual_company_data(self):
        """Test that no individual company data is collected"""
        with patch.object(self.collector, '_collect_market_data', return_value={'market_size': {}}):
            with patch.object(self.collector, '_collect_regulatory_data', return_value={}):
                with patch.object(self.collector, '_collect_technology_trends', return_value={}):
                    with patch.object(self.collector, '_collect_workforce_data', return_value={}):
                        with patch.object(self.collector, '_collect_financial_benchmarks', return_value={}):
                            result = self.collector.collect_industry_data('Technology')
        
        # Check that no individual company identifiers are present
        result_str = str(result).lower()
        individual_identifiers = ['company_name', 'employee_name', 'personal', 'individual']
        
        for identifier in individual_identifiers:
            self.assertNotIn(identifier, result_str)

class TestDataCollectorIntegration(unittest.TestCase):
    """Integration tests for data collectors"""
    
    def test_all_collectors_compliant(self):
        """Test that all data collectors are compliant"""
        collectors = [
            SECDataCollector(),
            LinkedInDataCollector(),
            NewsDataCollector(),
            IndustryResearchCollector()
        ]
        
        for collector in collectors:
            compliance_info = collector.get_compliance_info()
            # Check for compliance information - different collectors may have different field names
            if 'compliance_status' in compliance_info:
                self.assertTrue(
                    'compliant' in compliance_info['compliance_status'].lower(),
                    f"Expected 'compliant' in status, got: {compliance_info['compliance_status']}"
                )
            elif 'terms_compliance' in compliance_info:
                self.assertTrue(
                    'compliant' in compliance_info['terms_compliance'].lower(),
                    f"Expected 'compliant' in terms_compliance, got: {compliance_info['terms_compliance']}"
                )
            else:
                # Check if any field contains 'compliant'
                has_compliance = any(
                    'compliant' in str(value).lower() 
                    for value in compliance_info.values()
                )
                self.assertTrue(
                    has_compliance,
                    f"No compliance information found in: {compliance_info}"
                )
    
    def test_no_cross_contamination(self):
        """Test that data collectors don't share private data"""
        # This test ensures that data collectors are isolated
        # and don't accidentally share private information
        
        sec_collector = SECDataCollector()
        linkedin_collector = LinkedInDataCollector()
        
        # Each collector should have its own session and configuration
        self.assertIsNot(sec_collector.session, linkedin_collector.session)
        self.assertIsNot(sec_collector.logger, linkedin_collector.logger)

if __name__ == '__main__':
    unittest.main() 