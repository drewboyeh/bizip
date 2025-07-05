"""
Conversation Analysis Module

Provides analysis capabilities for generating conversation starters and
engagement strategies for financial advisors working with business owners.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ConversationAnalyzer:
    """Analyzes business data to generate conversation starters and engagement strategies"""
    
    def __init__(self):
        """Initialize the conversation analyzer"""
        self.conversation_cache = {}
        self.compliance_log = []
    
    def analyze_conversation_starters(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze business data to generate conversation starters
        
        Args:
            business_data: Business profile and financial data
            
        Returns:
            Dictionary containing conversation analysis results
        """
        try:
            company_name = business_data.get('company_name', 'Unknown Company')
            
            # Log analysis start for compliance
            self._log_analysis_start(company_name)
            
            # Perform comprehensive conversation analysis
            analysis_result = {
                'summary': self._generate_conversation_summary(business_data),
                'high_priority_starters': self._identify_high_priority_starters(business_data),
                'industry_specific': self._generate_industry_specific_starters(business_data),
                'financial_planning': self._generate_financial_planning_starters(business_data),
                'business_growth': self._generate_business_growth_starters(business_data),
                'risk_management': self._generate_risk_management_starters(business_data),
                'personal_financial': self._generate_personal_financial_starters(business_data),
                'engagement_strategies': self._create_engagement_strategies(business_data),
                'follow_up_questions': self._generate_follow_up_questions(business_data),
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
            # Log analysis completion
            self._log_analysis_completion(company_name, analysis_result)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing conversation starters: {str(e)}")
            self._log_analysis_error(company_name, str(e))
            return {
                'error': f'Conversation analysis failed: {str(e)}',
                'summary': 'Unable to complete conversation analysis'
            }
    
    def _generate_conversation_summary(self, business_data: Dict[str, Any]) -> str:
        """Generate executive summary of conversation analysis"""
        company_name = business_data.get('company_name', 'this business')
        industry = business_data.get('industry', '')
        revenue = business_data.get('revenue', 0)
        
        summary = f"Analysis of {company_name} reveals several conversation opportunities. "
        
        if industry:
            summary += f"As a {industry} business, there are industry-specific challenges and opportunities to discuss. "
        
        if revenue > 10000000:  # $10M+
            summary += "As a high-revenue business, there are significant financial planning and wealth management topics to explore. "
        elif revenue > 1000000:  # $1M+
            summary += "As a growing business, there are opportunities to discuss expansion and optimization strategies. "
        
        # Add key conversation areas
        conversation_areas = business_data.get('conversation_areas', [])
        if conversation_areas:
            summary += f"Key conversation areas include {', '.join(conversation_areas[:3])}. "
        
        return summary
    
    def _identify_high_priority_starters(self, business_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify high-priority conversation starters"""
        starters = []
        
        # Industry-specific starters
        industry_starters = self._generate_industry_specific_starters(business_data)
        if industry_starters.get('high_priority'):
            starters.extend(industry_starters['high_priority'])
        
        # Financial planning starters
        financial_starters = self._generate_financial_planning_starters(business_data)
        if financial_starters.get('high_priority'):
            starters.extend(financial_starters['high_priority'])
        
        # Business growth starters
        growth_starters = self._generate_business_growth_starters(business_data)
        if growth_starters.get('high_priority'):
            starters.extend(growth_starters['high_priority'])
        
        # Sort by priority
        starters.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
        
        return starters[:5]  # Return top 5 starters
    
    def _generate_industry_specific_starters(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate industry-specific conversation starters"""
        starters = {
            'high_priority': [],
            'medium_priority': [],
            'low_priority': []
        }
        
        industry = business_data.get('industry', '').lower()
        company_name = business_data.get('company_name', 'your business')
        
        # Technology industry
        if 'technology' in industry or 'software' in industry or 'tech' in industry:
            starters['high_priority'].append({
                'topic': 'Technology Trends',
                'question': f"How are you adapting to the rapid changes in technology affecting {industry}?",
                'context': 'Technology is rapidly evolving and impacting business models',
                'follow_up': 'What technology investments are you considering for the next 12 months?',
                'priority_score': 9,
                'category': 'industry_specific'
            })
            
            starters['high_priority'].append({
                'topic': 'Talent Acquisition',
                'question': "How are you addressing the talent shortage in the technology sector?",
                'context': 'Technology talent is in high demand and short supply',
                'follow_up': 'What strategies are you using to attract and retain top talent?',
                'priority_score': 8,
                'category': 'industry_specific'
            })
        
        # Healthcare industry
        elif 'healthcare' in industry or 'medical' in industry or 'health' in industry:
            starters['high_priority'].append({
                'topic': 'Regulatory Compliance',
                'question': "How are you managing the increasing regulatory requirements in healthcare?",
                'context': 'Healthcare regulations are becoming more complex and costly',
                'follow_up': 'What compliance challenges are you facing this year?',
                'priority_score': 9,
                'category': 'industry_specific'
            })
            
            starters['high_priority'].append({
                'topic': 'Technology Integration',
                'question': "How are you integrating new technologies like telemedicine into your practice?",
                'context': 'Healthcare technology is rapidly evolving',
                'follow_up': 'What technology investments are you planning?',
                'priority_score': 8,
                'category': 'industry_specific'
            })
        
        # Manufacturing industry
        elif 'manufacturing' in industry or 'industrial' in industry:
            starters['high_priority'].append({
                'topic': 'Supply Chain Management',
                'question': "How are you managing supply chain disruptions and costs?",
                'context': 'Supply chain issues are affecting manufacturing businesses',
                'follow_up': 'What strategies are you using to mitigate supply chain risks?',
                'priority_score': 9,
                'category': 'industry_specific'
            })
            
            starters['high_priority'].append({
                'topic': 'Automation and Efficiency',
                'question': "How are you implementing automation to improve efficiency?",
                'context': 'Automation is key to staying competitive in manufacturing',
                'follow_up': 'What automation projects are you considering?',
                'priority_score': 8,
                'category': 'industry_specific'
            })
        
        # Financial services
        elif 'financial' in industry or 'banking' in industry or 'insurance' in industry:
            starters['high_priority'].append({
                'topic': 'Regulatory Changes',
                'question': "How are you adapting to the changing regulatory landscape in financial services?",
                'context': 'Financial regulations are constantly evolving',
                'follow_up': 'What compliance challenges are you facing?',
                'priority_score': 9,
                'category': 'industry_specific'
            })
            
            starters['high_priority'].append({
                'topic': 'Digital Transformation',
                'question': "How are you implementing digital solutions to meet customer expectations?",
                'context': 'Digital transformation is essential in financial services',
                'follow_up': 'What digital initiatives are you planning?',
                'priority_score': 8,
                'category': 'industry_specific'
            })
        
        # Retail industry
        elif 'retail' in industry or 'ecommerce' in industry:
            starters['high_priority'].append({
                'topic': 'E-commerce Strategy',
                'question': "How are you balancing online and offline sales channels?",
                'context': 'E-commerce is transforming retail business models',
                'follow_up': 'What percentage of your sales are online vs. in-store?',
                'priority_score': 9,
                'category': 'industry_specific'
            })
            
            starters['high_priority'].append({
                'topic': 'Customer Experience',
                'question': "How are you enhancing the customer experience across all touchpoints?",
                'context': 'Customer experience is critical for retail success',
                'follow_up': 'What customer experience initiatives are you implementing?',
                'priority_score': 8,
                'category': 'industry_specific'
            })
        
        return starters
    
    def _generate_financial_planning_starters(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate financial planning conversation starters"""
        starters = {
            'high_priority': [],
            'medium_priority': [],
            'low_priority': []
        }
        
        revenue = business_data.get('revenue', 0)
        business_type = business_data.get('business_type', '')
        
        # Tax planning
        starters['high_priority'].append({
            'topic': 'Tax Planning',
            'question': "How are you optimizing your tax strategy for the current year?",
            'context': 'Tax planning can significantly impact business profitability',
            'follow_up': 'What tax-saving strategies are you currently using?',
            'priority_score': 9,
            'category': 'financial_planning'
        })
        
        # Cash flow management
        if revenue > 1000000:
            starters['high_priority'].append({
                'topic': 'Cash Flow Management',
                'question': "How are you managing cash flow during periods of growth?",
                'context': 'Cash flow management is critical for business growth',
                'follow_up': 'What cash flow challenges are you experiencing?',
                'priority_score': 8,
                'category': 'financial_planning'
            })
        
        # Retirement planning
        if business_type in ['LLC', 'S-Corp', 'Partnership']:
            starters['high_priority'].append({
                'topic': 'Retirement Planning',
                'question': "How are you planning for retirement as a business owner?",
                'context': 'Business owners need specialized retirement planning',
                'follow_up': 'What retirement vehicles are you currently using?',
                'priority_score': 8,
                'category': 'financial_planning'
            })
        
        # Investment strategy
        if revenue > 5000000:
            starters['medium_priority'].append({
                'topic': 'Investment Strategy',
                'question': "How are you investing business profits for long-term growth?",
                'context': 'Investment strategy can enhance business value',
                'follow_up': 'What investment opportunities are you considering?',
                'priority_score': 7,
                'category': 'financial_planning'
            })
        
        return starters
    
    def _generate_business_growth_starters(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate business growth conversation starters"""
        starters = {
            'high_priority': [],
            'medium_priority': [],
            'low_priority': []
        }
        
        revenue = business_data.get('revenue', 0)
        employee_count = business_data.get('employee_count', 0)
        
        # Market expansion
        if revenue > 2000000:
            starters['high_priority'].append({
                'topic': 'Market Expansion',
                'question': "Have you considered expanding into new markets or customer segments?",
                'context': 'Market expansion can drive significant growth',
                'follow_up': 'What new markets are you evaluating?',
                'priority_score': 8,
                'category': 'business_growth'
            })
        
        # Product development
        if revenue > 1000000:
            starters['high_priority'].append({
                'topic': 'Product Development',
                'question': "How are you developing new products or services to meet customer needs?",
                'context': 'Product development is key to business growth',
                'follow_up': 'What new products or services are you planning?',
                'priority_score': 8,
                'category': 'business_growth'
            })
        
        # Operational efficiency
        if employee_count > 20:
            starters['medium_priority'].append({
                'topic': 'Operational Efficiency',
                'question': "How are you improving operational efficiency to support growth?",
                'context': 'Operational efficiency is critical for scaling',
                'follow_up': 'What efficiency initiatives are you implementing?',
                'priority_score': 7,
                'category': 'business_growth'
            })
        
        # Strategic partnerships
        starters['medium_priority'].append({
            'topic': 'Strategic Partnerships',
            'question': "Have you considered strategic partnerships to accelerate growth?",
            'context': 'Partnerships can provide access to new markets and capabilities',
            'follow_up': 'What types of partnerships would be most valuable?',
            'priority_score': 7,
            'category': 'business_growth'
        })
        
        return starters
    
    def _generate_risk_management_starters(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate risk management conversation starters"""
        starters = {
            'high_priority': [],
            'medium_priority': [],
            'low_priority': []
        }
        
        industry = business_data.get('industry', '').lower()
        revenue = business_data.get('revenue', 0)
        
        # Insurance review
        starters['high_priority'].append({
            'topic': 'Insurance Review',
            'question': "When was the last time you reviewed your business insurance coverage?",
            'context': 'Insurance needs change as businesses grow and evolve',
            'follow_up': 'What types of insurance coverage do you currently have?',
            'priority_score': 8,
            'category': 'risk_management'
        })
        
        # Cybersecurity
        if industry in ['technology', 'healthcare', 'financial'] or revenue > 5000000:
            starters['high_priority'].append({
                'topic': 'Cybersecurity',
                'question': "How are you protecting your business from cybersecurity threats?",
                'context': 'Cybersecurity threats are increasing for all businesses',
                'follow_up': 'What cybersecurity measures do you have in place?',
                'priority_score': 9,
                'category': 'risk_management'
            })
        
        # Succession planning
        if business_data.get('business_age', 0) > 10:
            starters['medium_priority'].append({
                'topic': 'Succession Planning',
                'question': "Have you developed a succession plan for your business?",
                'context': 'Succession planning is critical for business continuity',
                'follow_up': 'What are your plans for business transition?',
                'priority_score': 7,
                'category': 'risk_management'
            })
        
        # Compliance management
        if industry in ['healthcare', 'financial', 'manufacturing']:
            starters['medium_priority'].append({
                'topic': 'Compliance Management',
                'question': "How are you managing regulatory compliance requirements?",
                'context': 'Compliance requirements are becoming more complex',
                'follow_up': 'What compliance challenges are you facing?',
                'priority_score': 7,
                'category': 'risk_management'
            })
        
        return starters
    
    def _generate_personal_financial_starters(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personal financial planning conversation starters"""
        starters = {
            'high_priority': [],
            'medium_priority': [],
            'low_priority': []
        }
        
        revenue = business_data.get('revenue', 0)
        business_type = business_data.get('business_type', '')
        
        # Personal wealth management
        if revenue > 5000000:
            starters['high_priority'].append({
                'topic': 'Personal Wealth Management',
                'question': "How are you managing your personal wealth outside of the business?",
                'context': 'Personal wealth management is important for business owners',
                'follow_up': 'What investment strategies are you using for personal wealth?',
                'priority_score': 8,
                'category': 'personal_financial'
            })
        
        # Estate planning
        if business_type in ['LLC', 'S-Corp', 'Partnership']:
            starters['high_priority'].append({
                'topic': 'Estate Planning',
                'question': "Have you developed an estate plan that includes your business interests?",
                'context': 'Estate planning is critical for business owners',
                'follow_up': 'What estate planning strategies are you considering?',
                'priority_score': 8,
                'category': 'personal_financial'
            })
        
        # Life insurance
        starters['medium_priority'].append({
            'topic': 'Life Insurance',
            'question': "How does life insurance fit into your overall financial plan?",
            'context': 'Life insurance can provide protection and tax benefits',
            'follow_up': 'What types of life insurance do you currently have?',
            'priority_score': 7,
            'category': 'personal_financial'
        })
        
        # Disability insurance
        starters['medium_priority'].append({
            'topic': 'Disability Insurance',
            'question': "How are you protecting your income if you become disabled?",
            'context': 'Disability insurance is important for business owners',
            'follow_up': 'Do you have disability insurance coverage?',
            'priority_score': 7,
            'category': 'personal_financial'
        })
        
        return starters
    
    def _create_engagement_strategies(self, business_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create engagement strategies for financial advisors"""
        strategies = {
            'initial_approach': [],
            'ongoing_engagement': [],
            'relationship_building': [],
            'value_proposition': []
        }
        
        industry = business_data.get('industry', '')
        revenue = business_data.get('revenue', 0)
        
        # Initial approach strategies
        strategies['initial_approach'].append({
            'strategy': 'Industry Expertise',
            'description': f'Demonstrate deep understanding of {industry} challenges and opportunities',
            'implementation': 'Research industry trends and prepare relevant insights',
            'timing': 'Initial meeting'
        })
        
        strategies['initial_approach'].append({
            'strategy': 'Value-First Approach',
            'description': 'Provide immediate value through insights and analysis',
            'implementation': 'Share relevant industry data and financial insights',
            'timing': 'Initial meeting'
        })
        
        # Ongoing engagement strategies
        strategies['ongoing_engagement'].append({
            'strategy': 'Regular Check-ins',
            'description': 'Schedule regular meetings to discuss business developments',
            'implementation': 'Monthly or quarterly business review meetings',
            'timing': 'Ongoing'
        })
        
        strategies['ongoing_engagement'].append({
            'strategy': 'Educational Content',
            'description': 'Provide educational content relevant to their business',
            'implementation': 'Share articles, reports, and insights',
            'timing': 'Weekly/Monthly'
        })
        
        # Relationship building strategies
        strategies['relationship_building'].append({
            'strategy': 'Networking Opportunities',
            'description': 'Connect them with other business owners and professionals',
            'implementation': 'Introduce to relevant contacts and networking groups',
            'timing': 'As opportunities arise'
        })
        
        strategies['relationship_building'].append({
            'strategy': 'Personal Touch',
            'description': 'Remember personal details and business milestones',
            'implementation': 'Send personalized notes and congratulations',
            'timing': 'Regularly'
        })
        
        # Value proposition strategies
        if revenue > 10000000:
            strategies['value_proposition'].append({
                'strategy': 'Comprehensive Planning',
                'description': 'Offer comprehensive business and personal financial planning',
                'implementation': 'Develop integrated planning approach',
                'timing': 'Ongoing'
            })
        else:
            strategies['value_proposition'].append({
                'strategy': 'Growth-Focused Planning',
                'description': 'Focus on strategies to support business growth',
                'implementation': 'Develop growth-oriented financial strategies',
                'timing': 'Ongoing'
            })
        
        return strategies
    
    def _generate_follow_up_questions(self, business_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate follow-up questions for deeper engagement"""
        follow_ups = []
        
        # Business challenges
        follow_ups.append({
            'category': 'Business Challenges',
            'questions': [
                "What's the biggest challenge you're facing in your business right now?",
                "How do you see your industry changing over the next 3-5 years?",
                "What keeps you up at night regarding your business?"
            ]
        })
        
        # Financial goals
        follow_ups.append({
            'category': 'Financial Goals',
            'questions': [
                "What are your primary financial goals for the next 12 months?",
                "How do you measure success in your business?",
                "What would you like to accomplish financially in the next 3-5 years?"
            ]
        })
        
        # Personal goals
        follow_ups.append({
            'category': 'Personal Goals',
            'questions': [
                "How do you balance business and personal financial goals?",
                "What's most important to you personally when it comes to financial planning?",
                "How do you want to use your wealth to make an impact?"
            ]
        })
        
        return follow_ups
    
    def _log_analysis_start(self, company_name: str):
        """Log analysis start for compliance"""
        self.compliance_log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'action': 'conversation_analysis_start',
            'company': company_name,
            'status': 'started'
        })
    
    def _log_analysis_completion(self, company_name: str, result: Dict[str, Any]):
        """Log analysis completion for compliance"""
        self.compliance_log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'action': 'conversation_analysis_completion',
            'company': company_name,
            'status': 'completed',
            'starters_generated': len(result.get('high_priority_starters', [])),
            'categories_covered': len([k for k in result.keys() if 'starters' in k])
        })
    
    def _log_analysis_error(self, company_name: str, error: str):
        """Log analysis error for compliance"""
        self.compliance_log.append({
            'timestamp': datetime.utcnow().isoformat(),
            'action': 'conversation_analysis_error',
            'company': company_name,
            'status': 'failed',
            'error': error
        })
    
    def get_compliance_log(self) -> List[Dict[str, Any]]:
        """Get compliance log for audit purposes"""
        return self.compliance_log.copy()
    
    def clear_compliance_log(self):
        """Clear compliance log"""
        self.compliance_log.clear()
