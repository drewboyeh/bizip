import requests
import time
from datetime import datetime
from typing import Dict, List, Optional
import logging
import re

class SECDataCollector:
    """Collects data from SEC EDGAR database for public companies"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BusinessIntelligencePlatform/1.0 (Compliant Research Tool)'
        })
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://data.sec.gov"
        
    def collect_company_data(self, company_name: str) -> Optional[Dict]:
        """Collect SEC data for a company"""
        try:
            self.logger.info(f"Collecting SEC data for: {company_name}")
            
            # Search for company CIK
            cik = self._find_company_cik(company_name)
            if not cik:
                self.logger.warning(f"No CIK found for {company_name}")
                return None
            
            # Collect basic company information
            company_info = self._get_company_info(cik)
            if not company_info:
                return None
            
            # Collect recent filings
            recent_filings = self._get_recent_filings(cik)
            
            # Collect financial data
            financial_data = self._get_financial_data(cik)
            
            # Combine all data
            sec_data = {
                'cik': cik,
                'company_info': company_info,
                'recent_filings': recent_filings,
                'financial_data': financial_data,
                'last_updated': datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"SEC data collection completed for {company_name}")
            return sec_data
            
        except Exception as e:
            self.logger.error(f"Error collecting SEC data for {company_name}: {str(e)}")
            return None
    
    def _find_company_cik(self, company_name: str) -> Optional[str]:
        """Find company CIK (Central Index Key) from SEC database"""
        try:
            # This would use SEC's company search API
            # For demonstration, return a mock CIK
            search_url = f"{self.base_url}/submissions/CIK{company_name.replace(' ', '').upper()}.json"
            
            # Simulate API call with rate limiting
            time.sleep(0.1)  # Respect SEC rate limits
            
            # Mock response for demonstration
            if 'tech' in company_name.lower():
                return "0000320193"  # Apple CIK
            elif 'microsoft' in company_name.lower():
                return "0000789019"  # Microsoft CIK
            else:
                return "0001234567"  # Generic CIK
                
        except Exception as e:
            self.logger.warning(f"Error finding CIK for {company_name}: {str(e)}")
            return None
    
    def _get_company_info(self, cik: str) -> Optional[Dict]:
        """Get basic company information from SEC"""
        try:
            # This would fetch company information from SEC API
            # For demonstration, return mock data
            
            company_info = {
                'name': 'Sample Company Inc.',
                'ticker': 'SAMPLE',
                'sic_code': '7372',
                'sic_description': 'Prepackaged Software',
                'state': 'CA',
                'incorporated_state': 'DE',
                'fiscal_year_end': '12-31',
                'business_description': 'Technology company specializing in software solutions.',
                'officers': [
                    {
                        'name': 'John Smith',
                        'title': 'Chief Executive Officer',
                        'cik': '0001234567'
                    },
                    {
                        'name': 'Jane Doe',
                        'title': 'Chief Financial Officer',
                        'cik': '0001234568'
                    }
                ]
            }
            
            return company_info
            
        except Exception as e:
            self.logger.warning(f"Error getting company info for CIK {cik}: {str(e)}")
            return None
    
    def _get_recent_filings(self, cik: str) -> List[Dict]:
        """Get recent SEC filings for the company"""
        try:
            # This would fetch recent filings from SEC API
            # For demonstration, return mock data
            
            filings = [
                {
                    'accession_number': '0000320193-24-000001',
                    'filing_date': '2024-01-15',
                    'form': '10-K',
                    'description': 'Annual Report',
                    'url': f'https://www.sec.gov/Archives/edgar/data/{cik}/0000320193-24-000001.txt'
                },
                {
                    'accession_number': '0000320193-24-000002',
                    'filing_date': '2024-02-15',
                    'form': '10-Q',
                    'description': 'Quarterly Report',
                    'url': f'https://www.sec.gov/Archives/edgar/data/{cik}/0000320193-24-000002.txt'
                },
                {
                    'accession_number': '0000320193-24-000003',
                    'filing_date': '2024-03-01',
                    'form': '8-K',
                    'description': 'Current Report - Material Event',
                    'url': f'https://www.sec.gov/Archives/edgar/data/{cik}/0000320193-24-000003.txt'
                }
            ]
            
            return filings
            
        except Exception as e:
            self.logger.warning(f"Error getting recent filings for CIK {cik}: {str(e)}")
            return []
    
    def _get_financial_data(self, cik: str) -> Optional[Dict]:
        """Extract key financial data from recent filings"""
        try:
            # This would parse financial data from 10-K and 10-Q filings
            # For demonstration, return mock data
            
            financial_data = {
                'revenue': {
                    'latest': 394328000000,  # $394.3B
                    'previous_year': 365817000000,  # $365.8B
                    'growth_rate': 7.8
                },
                'net_income': {
                    'latest': 96995000000,  # $97.0B
                    'previous_year': 94680000000,  # $94.7B
                    'growth_rate': 2.4
                },
                'total_assets': {
                    'latest': 352755000000,  # $352.8B
                    'previous_year': 346747000000  # $346.7B
                },
                'total_liabilities': {
                    'latest': 287912000000,  # $287.9B
                    'previous_year': 287912000000  # $287.9B
                },
                'cash_and_equivalents': {
                    'latest': 48004000000,  # $48.0B
                    'previous_year': 48304000000  # $48.3B
                },
                'debt': {
                    'latest': 95984000000,  # $96.0B
                    'previous_year': 95984000000  # $96.0B
                },
                'key_ratios': {
                    'current_ratio': 1.07,
                    'debt_to_equity': 0.73,
                    'return_on_equity': 0.15,
                    'profit_margin': 0.25
                }
            }
            
            return financial_data
            
        except Exception as e:
            self.logger.warning(f"Error getting financial data for CIK {cik}: {str(e)}")
            return None
    
    def _parse_filing_content(self, filing_url: str) -> Optional[Dict]:
        """Parse content from SEC filing"""
        try:
            # This would download and parse the filing content
            # For demonstration, return mock parsed data
            
            parsed_data = {
                'risk_factors': [
                    'Competition in the technology industry',
                    'Dependence on key personnel',
                    'Regulatory changes affecting the business'
                ],
                'business_description': 'Technology company focused on software and services.',
                'management_discussion': 'Company experienced strong growth in key product areas.',
                'legal_proceedings': [],
                'executive_compensation': {
                    'ceo_total_compensation': 98700000,
                    'cfo_total_compensation': 25000000
                }
            }
            
            return parsed_data
            
        except Exception as e:
            self.logger.warning(f"Error parsing filing content: {str(e)}")
            return None
    
    def get_insider_trading_data(self, cik: str) -> List[Dict]:
        """Get insider trading data for the company"""
        try:
            # This would fetch insider trading data from SEC
            # For demonstration, return mock data
            
            insider_trades = [
                {
                    'filer_name': 'John Smith',
                    'filer_title': 'CEO',
                    'transaction_date': '2024-01-15',
                    'transaction_type': 'Sale',
                    'shares_traded': 10000,
                    'price_per_share': 150.00,
                    'total_value': 1500000.00
                },
                {
                    'filer_name': 'Jane Doe',
                    'filer_title': 'CFO',
                    'transaction_date': '2024-01-20',
                    'transaction_type': 'Purchase',
                    'shares_traded': 5000,
                    'price_per_share': 148.00,
                    'total_value': 740000.00
                }
            ]
            
            return insider_trades
            
        except Exception as e:
            self.logger.warning(f"Error getting insider trading data: {str(e)}")
            return []
    
    def get_executive_compensation(self, cik: str) -> Optional[Dict]:
        """Get executive compensation data"""
        try:
            # This would parse executive compensation from proxy statements
            # For demonstration, return mock data
            
            compensation_data = {
                'fiscal_year': '2023',
                'executives': [
                    {
                        'name': 'John Smith',
                        'title': 'Chief Executive Officer',
                        'salary': 3000000,
                        'bonus': 5000000,
                        'stock_awards': 80000000,
                        'option_awards': 0,
                        'total_compensation': 88000000
                    },
                    {
                        'name': 'Jane Doe',
                        'title': 'Chief Financial Officer',
                        'salary': 1000000,
                        'bonus': 2000000,
                        'stock_awards': 20000000,
                        'option_awards': 0,
                        'total_compensation': 23000000
                    }
                ]
            }
            
            return compensation_data
            
        except Exception as e:
            self.logger.warning(f"Error getting executive compensation: {str(e)}")
            return None
    
    def _respect_sec_rate_limits(self):
        """Respect SEC rate limits"""
        time.sleep(0.1)  # SEC allows 10 requests per second
    
    def get_compliance_info(self) -> Dict:
        """Get compliance information about SEC data collection"""
        return {
            'data_source': 'SEC EDGAR Database',
            'access_method': 'Public API',
            'rate_limiting': '10 requests per second',
            'data_retention': 'Permanent public record',
            'privacy_impact': 'Low - All data is public',
            'compliance_status': 'Fully compliant with SEC terms of use'
        } 