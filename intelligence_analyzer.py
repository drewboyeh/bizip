from typing import Dict, List, Optional
import logging
from datetime import datetime

class IntelligenceAnalyzer:
    """Analyzes company data to identify financial planning opportunities"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def analyze_company(self, company_data: Dict) -> Dict:
        """Analyze company data and identify financial planning opportunities"""
        try:
            self.logger.info(f"Starting analysis for company: {company_data.get('name', 'Unknown')}")
            
            analysis_result = {
                'summary': {},
                'planning_needs': [],
                'opportunities': [],
                'conversation_starters': [],
                'recent_developments': [],
                'risk_factors': [],
                'industry_insights': []
            }
            
            # Analyze business model and structure
            business_analysis = self._analyze_business_model(company_data)
            analysis_result['summary'].update(business_analysis)
            
            # Identify financial planning opportunities
            opportunities = self._identify_planning_opportunities(company_data)
            analysis_result['opportunities'] = opportunities
            
            # Generate conversation starters
            conversation_starters = self._generate_conversation_starters(company_data, opportunities)
            analysis_result['conversation_starters'] = conversation_starters
            
            # Analyze recent developments
            recent_developments = self._analyze_recent_developments(company_data)
            analysis_result['recent_developments'] = recent_developments
            
            # Identify risk factors
            risk_factors = self._identify_risk_factors(company_data)
            analysis_result['risk_factors'] = risk_factors
            
            # Generate industry insights
            industry_insights = self._generate_industry_insights(company_data)
            analysis_result['industry_insights'] = industry_insights
            
            # Determine primary planning needs
            planning_needs = self._determine_planning_needs(opportunities, company_data)
            analysis_result['planning_needs'] = planning_needs
            
            self.logger.info(f"Analysis completed for {company_data.get('name', 'Unknown')}")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Error analyzing company: {str(e)}")
            return {}
    
    def _analyze_business_model(self, company_data: Dict) -> Dict:
        """Analyze company's business model and structure"""
        try:
            analysis = {
                'business_type': company_data.get('business_type', 'Unknown'),
                'industry': company_data.get('industry', 'Unknown'),
                'estimated_revenue': company_data.get('estimated_revenue'),
                'employee_count': company_data.get('employee_count'),
                'is_public': company_data.get('is_public', False)
            }
            
            # Determine business maturity
            if company_data.get('founded_year'):
                years_in_business = datetime.now().year - company_data['founded_year']
                if years_in_business < 3:
                    analysis['maturity'] = 'Startup'
                elif years_in_business < 10:
                    analysis['maturity'] = 'Growth'
                else:
                    analysis['maturity'] = 'Established'
            
            # Determine company size category
            revenue = company_data.get('estimated_revenue')
            if revenue:
                if revenue < 1000000:
                    analysis['size_category'] = 'Small Business'
                elif revenue < 10000000:
                    analysis['size_category'] = 'Medium Business'
                elif revenue < 100000000:
                    analysis['size_category'] = 'Large Business'
                else:
                    analysis['size_category'] = 'Enterprise'
            
            return analysis
            
        except Exception as e:
            self.logger.warning(f"Error analyzing business model: {str(e)}")
            return {}
    
    def _identify_planning_opportunities(self, company_data: Dict) -> List[Dict]:
        """Identify financial planning opportunities based on company data"""
        opportunities = []
        
        try:
            # Business succession planning
            if self._needs_succession_planning(company_data):
                opportunities.append({
                    'type': 'Business Succession Planning',
                    'priority': 'high',
                    'description': 'Company appears to be owner-operated and may benefit from succession planning',
                    'estimated_value': 50000,
                    'urgency': 'medium'
                })
            
            # Tax optimization
            if self._needs_tax_optimization(company_data):
                opportunities.append({
                    'type': 'Tax Optimization',
                    'priority': 'medium',
                    'description': 'Opportunities for tax-efficient business structure and deductions',
                    'estimated_value': 25000,
                    'urgency': 'normal'
                })
            
            # Employee benefit plans
            if self._needs_employee_benefits(company_data):
                opportunities.append({
                    'type': 'Employee Benefit Plans',
                    'priority': 'medium',
                    'description': 'Company may benefit from structured employee benefit programs',
                    'estimated_value': 15000,
                    'urgency': 'normal'
                })
            
            # Risk management
            if self._needs_risk_management(company_data):
                opportunities.append({
                    'type': 'Risk Management',
                    'priority': 'high',
                    'description': 'Gaps identified in business risk management and insurance coverage',
                    'estimated_value': 30000,
                    'urgency': 'high'
                })
            
            # Investment policy
            if self._needs_investment_policy(company_data):
                opportunities.append({
                    'type': 'Investment Policy',
                    'priority': 'medium',
                    'description': 'Company may benefit from formalized investment policy and cash management',
                    'estimated_value': 20000,
                    'urgency': 'normal'
                })
            
            # Estate planning
            if self._needs_estate_planning(company_data):
                opportunities.append({
                    'type': 'Estate Planning',
                    'priority': 'high',
                    'description': 'Business owner may need estate planning for business assets',
                    'estimated_value': 40000,
                    'urgency': 'medium'
                })
            
        except Exception as e:
            self.logger.warning(f"Error identifying opportunities: {str(e)}")
        
        return opportunities
    
    def _needs_succession_planning(self, company_data: Dict) -> bool:
        """Determine if company needs succession planning"""
        # Private companies with significant value
        if not company_data.get('is_public') and company_data.get('estimated_revenue', 0) > 5000000:
            return True
        return False
    
    def _needs_tax_optimization(self, company_data: Dict) -> bool:
        """Determine if company needs tax optimization"""
        # Companies with significant revenue
        if company_data.get('estimated_revenue', 0) > 1000000:
            return True
        return False
    
    def _needs_employee_benefits(self, company_data: Dict) -> bool:
        """Determine if company needs employee benefit plans"""
        # Companies with employees
        if company_data.get('employee_count', 0) > 5:
            return True
        return False
    
    def _needs_risk_management(self, company_data: Dict) -> bool:
        """Determine if company needs risk management"""
        # All companies need risk management
        return True
    
    def _needs_investment_policy(self, company_data: Dict) -> bool:
        """Determine if company needs investment policy"""
        # Companies with significant cash reserves
        if company_data.get('estimated_revenue', 0) > 2000000:
            return True
        return False
    
    def _needs_estate_planning(self, company_data: Dict) -> bool:
        """Determine if company needs estate planning"""
        # Private companies with significant value
        if not company_data.get('is_public') and company_data.get('estimated_revenue', 0) > 3000000:
            return True
        return False
    
    def _generate_conversation_starters(self, company_data: Dict, opportunities: List[Dict]) -> List[Dict]:
        """Generate conversation starters based on company data and opportunities"""
        starters = []
        
        try:
            company_name = company_data.get('name', 'your company')
            industry = company_data.get('industry', 'your industry')
            
            # Industry-specific starters
            if industry == 'Technology':
                starters.append({
                    'topic': 'Technology Industry Trends',
                    'context': f'I noticed {company_name} is in the technology sector. The industry is experiencing rapid growth with AI and cloud computing driving significant changes.',
                    'suggested_approach': 'Discuss how these trends might impact your business planning and what opportunities they present for financial optimization.'
                })
            
            elif industry == 'Healthcare':
                starters.append({
                    'topic': 'Healthcare Regulatory Changes',
                    'context': f'Healthcare practices like {company_name} are facing evolving regulatory requirements and reimbursement changes.',
                    'suggested_approach': 'Explore how these changes might affect your practice valuation and what planning strategies could help mitigate risks.'
                })
            
            elif industry == 'Real Estate':
                starters.append({
                    'topic': 'Real Estate Market Cycles',
                    'context': f'Real estate businesses like {company_name} operate in cyclical markets that can significantly impact cash flow and valuations.',
                    'suggested_approach': 'Discuss strategies for managing market volatility and optimizing your real estate portfolio for long-term success.'
                })
            
            # Opportunity-based starters
            for opportunity in opportunities:
                if opportunity['type'] == 'Business Succession Planning':
                    starters.append({
                        'topic': 'Business Succession Planning',
                        'context': f'Many successful businesses like {company_name} reach a point where succession planning becomes critical for long-term sustainability.',
                        'suggested_approach': 'Share insights about succession planning strategies that have worked well for similar companies in your industry.'
                    })
                
                elif opportunity['type'] == 'Tax Optimization':
                    starters.append({
                        'topic': 'Tax Efficiency Strategies',
                        'context': f'Companies at {company_name}\'s stage often have opportunities to optimize their tax structure and reduce their overall tax burden.',
                        'suggested_approach': 'Discuss current tax planning strategies that could benefit your business structure and operations.'
                    })
            
            # Recent developments
            if company_data.get('recent_news'):
                starters.append({
                    'topic': 'Recent Business Developments',
                    'context': f'I saw that {company_name} recently made some significant business moves. These developments often create new planning opportunities.',
                    'suggested_approach': 'Explore how these recent changes might impact your financial planning needs and what new opportunities they might present.'
                })
            
        except Exception as e:
            self.logger.warning(f"Error generating conversation starters: {str(e)}")
        
        return starters
    
    def _analyze_recent_developments(self, company_data: Dict) -> List[Dict]:
        """Analyze recent developments and their implications"""
        developments = []
        
        try:
            news_items = company_data.get('recent_news', [])
            
            for news in news_items:
                development = {
                    'title': news.get('title'),
                    'date': news.get('date'),
                    'source': news.get('source'),
                    'summary': news.get('summary'),
                    'planning_implications': self._analyze_news_implications(news)
                }
                developments.append(development)
                
        except Exception as e:
            self.logger.warning(f"Error analyzing recent developments: {str(e)}")
        
        return developments
    
    def _analyze_news_implications(self, news_item: Dict) -> List[str]:
        """Analyze planning implications of news items"""
        implications = []
        
        title = news_item.get('title', '').lower()
        summary = news_item.get('summary', '').lower()
        
        if any(word in title or word in summary for word in ['partnership', 'acquisition', 'merger']):
            implications.append('May need business structure review')
            implications.append('Potential for tax optimization opportunities')
        
        if any(word in title or word in summary for word in ['funding', 'investment', 'capital']):
            implications.append('Cash flow management planning needed')
            implications.append('Investment policy development opportunity')
        
        if any(word in title or word in summary for word in ['expansion', 'growth', 'new market']):
            implications.append('Risk management review recommended')
            implications.append('Employee benefit plan expansion opportunity')
        
        return implications
    
    def _identify_risk_factors(self, company_data: Dict) -> List[Dict]:
        """Identify potential risk factors for the business"""
        risks = []
        
        try:
            # Industry-specific risks
            industry = company_data.get('industry')
            if industry == 'Technology':
                risks.append({
                    'category': 'Technology Risk',
                    'description': 'Rapid technological changes may impact business model',
                    'severity': 'medium'
                })
            
            elif industry == 'Healthcare':
                risks.append({
                    'category': 'Regulatory Risk',
                    'description': 'Changing healthcare regulations may affect operations',
                    'severity': 'high'
                })
            
            # Size-based risks
            revenue = company_data.get('estimated_revenue', 0)
            if revenue < 1000000:
                risks.append({
                    'category': 'Cash Flow Risk',
                    'description': 'Small businesses often face cash flow challenges',
                    'severity': 'high'
                })
            
            # General business risks
            risks.extend([
                {
                    'category': 'Market Risk',
                    'description': 'Economic conditions may impact business performance',
                    'severity': 'medium'
                },
                {
                    'category': 'Operational Risk',
                    'description': 'Key person dependency and operational continuity',
                    'severity': 'medium'
                }
            ])
            
        except Exception as e:
            self.logger.warning(f"Error identifying risk factors: {str(e)}")
        
        return risks
    
    def _generate_industry_insights(self, company_data: Dict) -> List[Dict]:
        """Generate industry-specific insights"""
        insights = []
        
        try:
            industry = company_data.get('industry')
            
            if industry == 'Technology':
                insights.extend([
                    {
                        'topic': 'AI Integration',
                        'insight': 'Technology companies are increasingly integrating AI into their operations, creating new planning opportunities.',
                        'relevance': 'high'
                    },
                    {
                        'topic': 'Remote Work Trends',
                        'insight': 'The shift to remote work is changing how technology companies structure their operations and benefits.',
                        'relevance': 'medium'
                    }
                ])
            
            elif industry == 'Healthcare':
                insights.extend([
                    {
                        'topic': 'Value-Based Care',
                        'insight': 'The shift to value-based care is changing how healthcare practices are valued and structured.',
                        'relevance': 'high'
                    },
                    {
                        'topic': 'Telemedicine Growth',
                        'insight': 'Telemedicine adoption is creating new opportunities for practice expansion and revenue diversification.',
                        'relevance': 'medium'
                    }
                ])
            
        except Exception as e:
            self.logger.warning(f"Error generating industry insights: {str(e)}")
        
        return insights
    
    def _determine_planning_needs(self, opportunities: List[Dict], company_data: Dict) -> List[str]:
        """Determine primary planning needs based on opportunities and company data"""
        needs = []
        
        try:
            # Sort opportunities by priority
            high_priority = [opp for opp in opportunities if opp.get('priority') == 'high']
            medium_priority = [opp for opp in opportunities if opp.get('priority') == 'medium']
            
            # Add high priority needs first
            for opp in high_priority:
                needs.append(opp['type'])
            
            # Add medium priority needs (up to 3 total)
            for opp in medium_priority:
                if len(needs) < 3:
                    needs.append(opp['type'])
            
            # Ensure we have at least one need
            if not needs and opportunities:
                needs.append(opportunities[0]['type'])
            
        except Exception as e:
            self.logger.warning(f"Error determining planning needs: {str(e)}")
        
        return needs 