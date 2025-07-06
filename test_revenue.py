#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_collectors.company_research import CompanyResearchCollector

def test_company_data():
    """Test company data collection with updated financial data"""
    print("Testing company data collection with 2024 financial data...")
    
    collector = CompanyResearchCollector()
    
    # Test with different companies
    test_companies = [
        ('NVIDIA Corporation', 'NVIDIA'),
        ('Apple Inc.', 'AAPL'),
        ('Microsoft Corporation', 'MSFT'),
        ('Alphabet Inc.', 'GOOGL'),
        ('Amazon.com Inc.', 'AMZN'),
        ('Tesla Inc.', 'TSLA'),
        ('Meta Platforms Inc.', 'META'),
        ('Netflix Inc.', 'NFLX'),
        ('Salesforce Inc.', 'CRM'),
        ('Oracle Corporation', 'ORCL')
    ]
    
    for company_name, ticker in test_companies:
        print(f"\n{'='*50}")
        print(f"Testing: {company_name} ({ticker})")
        print(f"{'='*50}")
        
        try:
            data = collector.collect_company_data(company_name)
            if data:
                print(f"✅ Success")
                print(f"   Revenue: {data.get('estimated_revenue', 'NOT FOUND')}")
                print(f"   Market Cap: {data.get('market_cap', 'NOT FOUND')}")
                print(f"   Revenue Growth: {data.get('revenue_growth', 'NOT FOUND')}")
                print(f"   Profit Margin: {data.get('profit_margin', 'NOT FOUND')}")
                print(f"   P/E Ratio: {data.get('pe_ratio', 'NOT FOUND')}")
                print(f"   CEO: {data.get('ceo', 'Unknown')}")
                print(f"   Industry: {data.get('industry', 'Unknown')}")
            else:
                print(f"❌ No data returned")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_company_data() 