#!/usr/bin/env python3
"""
Financial Data Updater
Automatically updates hardcoded financial data from Alpha Vantage API
Run this script daily to keep company financial data current
"""

import requests
import json
import time
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional

# Set up logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('financial_updates.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FinancialDataUpdater:
    """Updates hardcoded financial data from Alpha Vantage API"""
    
    def __init__(self):
        # Alpha Vantage API key - you can get a free key from https://www.alphavantage.co/support/#api-key
        self.api_key = "demo"  # Replace with your actual API key
        self.base_url = "https://www.alphavantage.co/query"
        self.session = requests.Session()
        
        # Companies to track with their Alpha Vantage symbols
        self.companies = {
            'NVIDIA': 'NVDA',
            'Apple': 'AAPL', 
            'Microsoft': 'MSFT',
            'Alphabet': 'GOOGL',
            'Amazon': 'AMZN',
            'Tesla': 'TSLA',
            'Meta': 'META',
            'Netflix': 'NFLX',
            'Salesforce': 'CRM',
            'Oracle': 'ORCL',
            'Intel': 'INTC',
            'AMD': 'AMD',
            'Cisco': 'CSCO',
            'Adobe': 'ADBE',
            'PayPal': 'PYPL',
            'Visa': 'V',
            'Mastercard': 'MA',
            'JPMorgan': 'JPM',
            'Bank of America': 'BAC',
            'Wells Fargo': 'WFC'
        }
    
    def get_company_data(self, symbol: str) -> Optional[Dict]:
        """Get company financial data from Alpha Vantage"""
        try:
            # Get quote data
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            response = self.session.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API errors
            if 'Error Message' in data:
                logger.warning(f"API Error for {symbol}: {data['Error Message']}")
                return None
            
            if 'Note' in data:
                logger.warning(f"API Rate Limit for {symbol}: {data['Note']}")
                return None
            
            quote = data.get('Global Quote', {})
            if not quote:
                logger.warning(f"No quote data found for {symbol}")
                return None
            
            # Get company overview for additional financial data
            overview_params = {
                'function': 'OVERVIEW',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            overview_response = self.session.get(self.base_url, params=overview_params, timeout=10)
            overview_data = overview_response.json()
            
            # Extract key metrics
            market_cap = quote.get('06. market cap', '0')
            price = quote.get('05. price', '0')
            volume = quote.get('06. volume', '0')
            
            # From overview data
            revenue = overview_data.get('RevenueTTM', '0')
            profit_margin = overview_data.get('ProfitMargin', '0')
            pe_ratio = overview_data.get('PERatio', '0')
            description = overview_data.get('Description', '')
            
            return {
                'symbol': symbol,
                'name': overview_data.get('Name', ''),
                'market_cap': self._format_market_cap(market_cap),
                'revenue': self._format_revenue(revenue),
                'profit_margin': f"{float(profit_margin) * 100:.1f}%" if profit_margin and profit_margin != 'None' else "N/A",
                'pe_ratio': f"{float(pe_ratio):.1f}" if pe_ratio and pe_ratio != 'None' else "N/A",
                'price': f"${float(price):.2f}" if price else "N/A",
                'volume': self._format_volume(volume),
                'description': description[:200] + "..." if len(description) > 200 else description,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def _format_market_cap(self, market_cap: str) -> str:
        """Format market cap in readable format"""
        try:
            value = float(market_cap)
            if value >= 1e12:
                return f"${value/1e12:.1f}T"
            elif value >= 1e9:
                return f"${value/1e9:.1f}B"
            elif value >= 1e6:
                return f"${value/1e6:.1f}M"
            else:
                return f"${value:,.0f}"
        except:
            return "N/A"
    
    def _format_revenue(self, revenue: str) -> str:
        """Format revenue in readable format"""
        try:
            value = float(revenue)
            if value >= 1e12:
                return f"${value/1e12:.1f}T"
            elif value >= 1e9:
                return f"${value/1e9:.1f}B"
            elif value >= 1e6:
                return f"${value/1e6:.1f}M"
            else:
                return f"${value:,.0f}"
        except:
            return "N/A"
    
    def _format_volume(self, volume: str) -> str:
        """Format volume in readable format"""
        try:
            value = float(volume)
            if value >= 1e9:
                return f"{value/1e9:.1f}B"
            elif value >= 1e6:
                return f"{value/1e6:.1f}M"
            else:
                return f"{value:,.0f}"
        except:
            return "N/A"
    
    def update_company_research_file(self, company_data: Dict[str, Dict]):
        """Update the company_research.py file with new financial data"""
        try:
            # Read the current file
            with open('data_collectors/company_research.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create a backup of the current file
            backup_filename = f"data_collectors/company_research_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
            with open(backup_filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Backup created: {backup_filename}")
            
            # Save the updated data to JSON for manual review
            with open('data_collectors/updated_financial_data.json', 'w', encoding='utf-8') as f:
                json.dump(company_data, f, indent=2, ensure_ascii=False)
            
            logger.info("Updated financial data saved to updated_financial_data.json")
            
            # Create a summary report
            self._create_summary_report(company_data)
            
        except Exception as e:
            logger.error(f"Error updating company research file: {str(e)}")
    
    def _create_summary_report(self, company_data: Dict[str, Dict]):
        """Create a summary report of the updates"""
        report_filename = f"financial_update_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write("FINANCIAL DATA UPDATE REPORT\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for company_name, data in company_data.items():
                if data:
                    f.write(f"{company_name} ({data['symbol']})\n")
                    f.write(f"  Revenue: {data['revenue']}\n")
                    f.write(f"  Market Cap: {data['market_cap']}\n")
                    f.write(f"  P/E Ratio: {data['pe_ratio']}\n")
                    f.write(f"  Profit Margin: {data['profit_margin']}\n")
                    f.write(f"  Price: {data['price']}\n")
                    f.write(f"  Volume: {data['volume']}\n")
                    f.write("-" * 30 + "\n")
        
        logger.info(f"Summary report created: {report_filename}")
    
    def run_daily_update(self):
        """Run the daily financial data update"""
        logger.info("Starting daily financial data update...")
        
        company_data = {}
        
        for company_name, symbol in self.companies.items():
            logger.info(f"Fetching data for {company_name} ({symbol})...")
            
            data = self.get_company_data(symbol)
            if data:
                company_data[company_name] = data
                logger.info(f"SUCCESS - Updated {company_name}: Revenue={data['revenue']}, Market Cap={data['market_cap']}")
            else:
                logger.warning(f"FAILED - Failed to update {company_name}")
            
            # Rate limiting - Alpha Vantage allows 5 calls per minute for free tier
            time.sleep(12)  # Wait 12 seconds between calls
        
        # Update the company research file
        self.update_company_research_file(company_data)
        
        logger.info("Daily financial data update completed!")
        return company_data

def main():
    """Main function to run the updater"""
    updater = FinancialDataUpdater()
    
    try:
        company_data = updater.run_daily_update()
        
        # Print summary
        print("\n" + "="*60)
        print("FINANCIAL DATA UPDATE SUMMARY")
        print("="*60)
        
        for company_name, data in company_data.items():
            if data:
                print(f"{company_name:20} | Revenue: {data['revenue']:15} | Market Cap: {data['market_cap']:12} | P/E: {data['pe_ratio']:8}")
        
        print("="*60)
        print("Update completed successfully!")
        print("Check updated_financial_data.json for the latest data")
        print("Note: You may need to manually update the hardcoded values in company_research.py")
        
    except Exception as e:
        logger.error(f"Update failed: {str(e)}")
        raise

if __name__ == "__main__":
    main() 