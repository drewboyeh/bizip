import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import feedparser
from urllib.parse import urljoin

class NewsDataCollector:
    """Collects business news and developments from legitimate news sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BusinessIntelligencePlatform/1.0 (Compliant Research Tool)'
        })
        self.logger = logging.getLogger(__name__)
        
        # Legitimate news sources
        self.news_sources = {
            'reuters': 'https://feeds.reuters.com/reuters/businessNews',
            'bloomberg': 'https://feeds.bloomberg.com/markets/news.rss',
            'cnbc': 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
            'wsj': 'https://feeds.wsj.com/public/rss/2_0/wsj.xml',
            'ft': 'https://www.ft.com/rss/home'
        }
        
    def collect_company_news(self, company_name: str, days_back: int = 30) -> List[Dict]:
        """Collect recent news about a specific company"""
        try:
            self.logger.info(f"Collecting news for company: {company_name}")
            
            all_news = []
            
            # Collect from multiple news sources
            for source_name, rss_url in self.news_sources.items():
                try:
                    source_news = self._collect_from_source(company_name, source_name, rss_url, days_back)
                    all_news.extend(source_news)
                    
                    # Respect rate limits
                    time.sleep(1)
                    
                except Exception as e:
                    self.logger.warning(f"Error collecting from {source_name}: {str(e)}")
                    continue
            
            # Sort by date and remove duplicates
            all_news = self._deduplicate_news(all_news)
            all_news.sort(key=lambda x: x.get('date', ''), reverse=True)
            
            self.logger.info(f"Collected {len(all_news)} news items for {company_name}")
            return all_news
            
        except Exception as e:
            self.logger.error(f"Error collecting news for {company_name}: {str(e)}")
            return []
    
    def collect_industry_news(self, industry: str, days_back: int = 30) -> List[Dict]:
        """Collect recent news about a specific industry"""
        try:
            self.logger.info(f"Collecting industry news for: {industry}")
            
            all_news = []
            
            # Collect from multiple news sources
            for source_name, rss_url in self.news_sources.items():
                try:
                    source_news = self._collect_industry_from_source(industry, source_name, rss_url, days_back)
                    all_news.extend(source_news)
                    
                    # Respect rate limits
                    time.sleep(1)
                    
                except Exception as e:
                    self.logger.warning(f"Error collecting industry news from {source_name}: {str(e)}")
                    continue
            
            # Sort by date and remove duplicates
            all_news = self._deduplicate_news(all_news)
            all_news.sort(key=lambda x: x.get('date', ''), reverse=True)
            
            self.logger.info(f"Collected {len(all_news)} industry news items for {industry}")
            return all_news
            
        except Exception as e:
            self.logger.error(f"Error collecting industry news for {industry}: {str(e)}")
            return []
    
    def _collect_from_source(self, company_name: str, source_name: str, rss_url: str, days_back: int) -> List[Dict]:
        """Collect news from a specific RSS source"""
        try:
            # Parse RSS feed
            feed = feedparser.parse(rss_url)
            
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            relevant_news = []
            
            for entry in feed.entries:
                try:
                    # Check if news is relevant to the company
                    if self._is_relevant_to_company(entry, company_name):
                        news_item = self._parse_news_entry(entry, source_name)
                        if news_item and news_item.get('date'):
                            news_date = datetime.fromisoformat(news_item['date'].replace('Z', '+00:00'))
                            if news_date >= cutoff_date:
                                relevant_news.append(news_item)
                                
                except Exception as e:
                    self.logger.warning(f"Error parsing news entry: {str(e)}")
                    continue
            
            return relevant_news
            
        except Exception as e:
            self.logger.warning(f"Error collecting from {source_name}: {str(e)}")
            return []
    
    def _collect_industry_from_source(self, industry: str, source_name: str, rss_url: str, days_back: int) -> List[Dict]:
        """Collect industry news from a specific RSS source"""
        try:
            # Parse RSS feed
            feed = feedparser.parse(rss_url)
            
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            relevant_news = []
            
            for entry in feed.entries:
                try:
                    # Check if news is relevant to the industry
                    if self._is_relevant_to_industry(entry, industry):
                        news_item = self._parse_news_entry(entry, source_name)
                        if news_item and news_item.get('date'):
                            news_date = datetime.fromisoformat(news_item['date'].replace('Z', '+00:00'))
                            if news_date >= cutoff_date:
                                relevant_news.append(news_item)
                                
                except Exception as e:
                    self.logger.warning(f"Error parsing industry news entry: {str(e)}")
                    continue
            
            return relevant_news
            
        except Exception as e:
            self.logger.warning(f"Error collecting industry news from {source_name}: {str(e)}")
            return []
    
    def _is_relevant_to_company(self, entry, company_name: str) -> bool:
        """Check if news entry is relevant to the company"""
        try:
            title = entry.get('title', '').lower()
            summary = entry.get('summary', '').lower()
            
            # Check for company name variations
            company_variations = [
                company_name.lower(),
                company_name.lower().replace(' ', ''),
                company_name.lower().replace(' ', '-'),
                company_name.lower().replace(' ', '_')
            ]
            
            for variation in company_variations:
                if variation in title or variation in summary:
                    return True
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Error checking company relevance: {str(e)}")
            return False
    
    def _is_relevant_to_industry(self, entry, industry: str) -> bool:
        """Check if news entry is relevant to the industry"""
        try:
            title = entry.get('title', '').lower()
            summary = entry.get('summary', '').lower()
            
            # Industry keywords
            industry_keywords = {
                'technology': ['tech', 'software', 'ai', 'artificial intelligence', 'cloud', 'digital'],
                'healthcare': ['health', 'medical', 'pharma', 'biotech', 'hospital', 'doctor'],
                'real estate': ['real estate', 'property', 'construction', 'housing', 'commercial'],
                'financial services': ['finance', 'banking', 'insurance', 'investment', 'wealth'],
                'manufacturing': ['manufacturing', 'factory', 'production', 'industrial'],
                'retail': ['retail', 'e-commerce', 'shopping', 'consumer', 'sales']
            }
            
            keywords = industry_keywords.get(industry.lower(), [industry.lower()])
            
            for keyword in keywords:
                if keyword in title or keyword in summary:
                    return True
            
            return False
            
        except Exception as e:
            self.logger.warning(f"Error checking industry relevance: {str(e)}")
            return False
    
    def _parse_news_entry(self, entry, source_name: str) -> Optional[Dict]:
        """Parse a news entry from RSS feed"""
        try:
            # Extract date
            date_str = entry.get('published', '')
            if date_str:
                # Parse various date formats
                try:
                    parsed_date = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
                    date_iso = parsed_date.isoformat()
                except:
                    date_iso = datetime.utcnow().isoformat()
            else:
                date_iso = datetime.utcnow().isoformat()
            
            # Extract content
            title = entry.get('title', '')
            summary = entry.get('summary', '')
            link = entry.get('link', '')
            
            # Clean summary (remove HTML tags)
            if summary:
                summary = self._clean_html(summary)
            
            news_item = {
                'title': title,
                'summary': summary,
                'url': link,
                'source': source_name,
                'date': date_iso,
                'sentiment': self._analyze_sentiment(title + ' ' + summary)
            }
            
            return news_item
            
        except Exception as e:
            self.logger.warning(f"Error parsing news entry: {str(e)}")
            return None
    
    def _clean_html(self, html_text: str) -> str:
        """Remove HTML tags from text"""
        try:
            import re
            clean = re.compile('<.*?>')
            return re.sub(clean, '', html_text)
        except Exception as e:
            self.logger.warning(f"Error cleaning HTML: {str(e)}")
            return html_text
    
    def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of news text"""
        try:
            text_lower = text.lower()
            
            # Simple sentiment analysis
            positive_words = ['growth', 'profit', 'success', 'increase', 'positive', 'strong', 'up', 'gain']
            negative_words = ['loss', 'decline', 'fall', 'negative', 'weak', 'down', 'drop', 'risk']
            
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count:
                return 'positive'
            elif negative_count > positive_count:
                return 'negative'
            else:
                return 'neutral'
                
        except Exception as e:
            self.logger.warning(f"Error analyzing sentiment: {str(e)}")
            return 'neutral'
    
    def _deduplicate_news(self, news_list: List[Dict]) -> List[Dict]:
        """Remove duplicate news items"""
        try:
            seen_titles = set()
            unique_news = []
            
            for news in news_list:
                title = news.get('title', '').lower()
                if title not in seen_titles:
                    seen_titles.add(title)
                    unique_news.append(news)
            
            return unique_news
            
        except Exception as e:
            self.logger.warning(f"Error deduplicating news: {str(e)}")
            return news_list
    
    def get_market_sentiment(self, company_name: str) -> Dict:
        """Get overall market sentiment for a company based on recent news"""
        try:
            news_items = self.collect_company_news(company_name, days_back=7)
            
            if not news_items:
                return {'sentiment': 'neutral', 'confidence': 'low', 'news_count': 0}
            
            sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
            
            for news in news_items:
                sentiment = news.get('sentiment', 'neutral')
                sentiment_counts[sentiment] += 1
            
            # Determine overall sentiment
            total_news = len(news_items)
            positive_ratio = sentiment_counts['positive'] / total_news
            negative_ratio = sentiment_counts['negative'] / total_news
            
            if positive_ratio > 0.6:
                overall_sentiment = 'positive'
            elif negative_ratio > 0.6:
                overall_sentiment = 'negative'
            else:
                overall_sentiment = 'neutral'
            
            confidence = 'high' if total_news >= 5 else 'medium' if total_news >= 2 else 'low'
            
            return {
                'sentiment': overall_sentiment,
                'confidence': confidence,
                'news_count': total_news,
                'sentiment_breakdown': sentiment_counts
            }
            
        except Exception as e:
            self.logger.warning(f"Error getting market sentiment: {str(e)}")
            return {'sentiment': 'neutral', 'confidence': 'low', 'news_count': 0}
    
    def get_industry_trends(self, industry: str) -> List[Dict]:
        """Get industry trends based on recent news"""
        try:
            news_items = self.collect_industry_news(industry, days_back=30)
            
            trends = []
            
            # Analyze common themes
            themes = {}
            for news in news_items:
                title = news.get('title', '').lower()
                summary = news.get('summary', '').lower()
                
                # Extract key themes
                key_phrases = self._extract_key_phrases(title + ' ' + summary)
                
                for phrase in key_phrases:
                    if phrase not in themes:
                        themes[phrase] = {'count': 0, 'sentiment': 'neutral'}
                    
                    themes[phrase]['count'] += 1
                    
                    # Update sentiment
                    if news.get('sentiment') == 'positive':
                        themes[phrase]['sentiment'] = 'positive'
                    elif news.get('sentiment') == 'negative':
                        themes[phrase]['sentiment'] = 'negative'
            
            # Convert to trend list
            for theme, data in themes.items():
                if data['count'] >= 2:  # Only include themes mentioned multiple times
                    trends.append({
                        'theme': theme,
                        'frequency': data['count'],
                        'sentiment': data['sentiment'],
                        'trend_strength': 'strong' if data['count'] >= 5 else 'moderate'
                    })
            
            # Sort by frequency
            trends.sort(key=lambda x: x['frequency'], reverse=True)
            
            return trends[:10]  # Return top 10 trends
            
        except Exception as e:
            self.logger.warning(f"Error getting industry trends: {str(e)}")
            return []
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from text"""
        try:
            # Simple key phrase extraction
            # In a real implementation, this would use NLP libraries
            
            # Common business terms
            business_terms = [
                'acquisition', 'merger', 'partnership', 'investment', 'funding',
                'expansion', 'growth', 'innovation', 'technology', 'digital',
                'regulation', 'compliance', 'market', 'competition', 'strategy'
            ]
            
            found_phrases = []
            text_lower = text.lower()
            
            for term in business_terms:
                if term in text_lower:
                    found_phrases.append(term)
            
            return found_phrases
            
        except Exception as e:
            self.logger.warning(f"Error extracting key phrases: {str(e)}")
            return []
    
    def get_compliance_info(self) -> Dict:
        """Get compliance information about news data collection"""
        return {
            'data_sources': 'Legitimate news RSS feeds',
            'access_method': 'Public RSS feeds',
            'rate_limiting': 'Respects source rate limits',
            'data_retention': 'News content only, no personal data',
            'privacy_impact': 'Low - Only public news content',
            'compliance_status': 'Compliant with news source terms of use'
        } 