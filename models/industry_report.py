from datetime import datetime
from .user import db

class IndustryReport(db.Model):
    """Industry reports and analysis for financial planning"""
    __tablename__ = 'industry_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    industry = db.Column(db.String(100), nullable=False, index=True)
    report_type = db.Column(db.String(50))  # quarterly, annual, special, regulatory
    
    # Report content
    title = db.Column(db.String(200), nullable=False)
    summary = db.Column(db.Text)
    key_findings = db.Column(db.JSON)
    market_trends = db.Column(db.JSON)
    regulatory_updates = db.Column(db.JSON)
    
    # Financial planning insights
    planning_opportunities = db.Column(db.JSON)
    risk_factors = db.Column(db.JSON)
    tax_considerations = db.Column(db.JSON)
    succession_planning_insights = db.Column(db.JSON)
    
    # Market data
    market_size = db.Column(db.Numeric(15, 2))
    growth_rate = db.Column(db.Float)
    key_players = db.Column(db.JSON)
    competitive_landscape = db.Column(db.Text)
    
    # Regulatory and compliance
    regulatory_changes = db.Column(db.JSON)
    compliance_requirements = db.Column(db.JSON)
    upcoming_deadlines = db.Column(db.JSON)
    
    # Technology and innovation
    technology_trends = db.Column(db.JSON)
    innovation_opportunities = db.Column(db.JSON)
    digital_transformation = db.Column(db.Text)
    
    # Workforce and talent
    talent_trends = db.Column(db.JSON)
    compensation_trends = db.Column(db.JSON)
    benefit_trends = db.Column(db.JSON)
    
    # Financial metrics
    average_revenue = db.Column(db.Numeric(15, 2))
    average_profit_margins = db.Column(db.Float)
    financing_trends = db.Column(db.JSON)
    valuation_metrics = db.Column(db.JSON)
    
    # Sources and methodology
    data_sources = db.Column(db.JSON)
    methodology = db.Column(db.Text)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Access control
    is_public = db.Column(db.Boolean, default=False)
    subscription_tier_required = db.Column(db.String(20))  # basic, professional, enterprise
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version = db.Column(db.String(20), default='1.0')
    
    def __repr__(self):
        return f'<IndustryReport {self.industry} - {self.title}>'
    
    def to_dict(self):
        """Convert industry report to dictionary"""
        return {
            'id': self.id,
            'industry': self.industry,
            'report_type': self.report_type,
            'title': self.title,
            'summary': self.summary,
            'key_findings': self.key_findings,
            'market_trends': self.market_trends,
            'regulatory_updates': self.regulatory_updates,
            'planning_insights': {
                'opportunities': self.planning_opportunities,
                'risk_factors': self.risk_factors,
                'tax_considerations': self.tax_considerations,
                'succession_planning': self.succession_planning_insights
            },
            'market_data': {
                'market_size': float(self.market_size) if self.market_size else None,
                'growth_rate': self.growth_rate,
                'key_players': self.key_players,
                'competitive_landscape': self.competitive_landscape
            },
            'regulatory': {
                'changes': self.regulatory_changes,
                'compliance_requirements': self.compliance_requirements,
                'upcoming_deadlines': self.upcoming_deadlines
            },
            'technology': {
                'trends': self.technology_trends,
                'innovation_opportunities': self.innovation_opportunities,
                'digital_transformation': self.digital_transformation
            },
            'workforce': {
                'talent_trends': self.talent_trends,
                'compensation_trends': self.compensation_trends,
                'benefit_trends': self.benefit_trends
            },
            'financial_metrics': {
                'average_revenue': float(self.average_revenue) if self.average_revenue else None,
                'average_profit_margins': self.average_profit_margins,
                'financing_trends': self.financing_trends,
                'valuation_metrics': self.valuation_metrics
            },
            'sources': {
                'data_sources': self.data_sources,
                'methodology': self.methodology,
                'last_updated': self.last_updated.isoformat()
            },
            'access': {
                'is_public': self.is_public,
                'subscription_tier_required': self.subscription_tier_required
            },
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'version': self.version
        }
    
    def get_planning_opportunities_summary(self):
        """Get a summary of planning opportunities"""
        if not self.planning_opportunities:
            return []
        
        summary = []
        for opportunity in self.planning_opportunities:
            summary.append({
                'type': opportunity.get('type'),
                'description': opportunity.get('description'),
                'estimated_value': opportunity.get('estimated_value'),
                'urgency': opportunity.get('urgency')
            })
        
        return summary
    
    def get_urgent_regulatory_changes(self):
        """Get urgent regulatory changes"""
        if not self.regulatory_changes:
            return []
        
        urgent_changes = []
        for change in self.regulatory_changes:
            if change.get('urgency') in ['high', 'critical']:
                urgent_changes.append(change)
        
        return urgent_changes
    
    def get_upcoming_deadlines(self, days=90):
        """Get upcoming deadlines within specified days"""
        if not self.upcoming_deadlines:
            return []
        
        from datetime import timedelta
        cutoff_date = datetime.utcnow() + timedelta(days=days)
        upcoming = []
        
        for deadline in self.upcoming_deadlines:
            deadline_date = datetime.fromisoformat(deadline.get('date', ''))
            if deadline_date <= cutoff_date:
                upcoming.append(deadline)
        
        return upcoming
    
    def is_accessible_for_tier(self, user_tier):
        """Check if report is accessible for user's subscription tier"""
        if self.is_public:
            return True
        
        if not self.subscription_tier_required:
            return True
        
        tier_hierarchy = {
            'basic': 1,
            'professional': 2,
            'enterprise': 3
        }
        
        user_level = tier_hierarchy.get(user_tier, 0)
        required_level = tier_hierarchy.get(self.subscription_tier_required, 0)
        
        return user_level >= required_level
    
    def get_key_insights(self):
        """Get key insights for financial advisors"""
        insights = []
        
        if self.key_findings:
            insights.extend(self.key_findings)
        
        if self.planning_opportunities:
            for opp in self.planning_opportunities:
                insights.append(f"Planning Opportunity: {opp.get('description', '')}")
        
        if self.risk_factors:
            for risk in self.risk_factors:
                insights.append(f"Risk Factor: {risk.get('description', '')}")
        
        return insights[:10]  # Limit to top 10 insights
    
    def update_market_data(self, market_size=None, growth_rate=None, key_players=None):
        """Update market data"""
        if market_size is not None:
            self.market_size = market_size
        
        if growth_rate is not None:
            self.growth_rate = growth_rate
        
        if key_players is not None:
            self.key_players = key_players
        
        self.last_updated = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def add_regulatory_change(self, change_type, description, effective_date, urgency='medium'):
        """Add a regulatory change"""
        if not self.regulatory_changes:
            self.regulatory_changes = []
        
        change = {
            'type': change_type,
            'description': description,
            'effective_date': effective_date,
            'urgency': urgency,
            'added_date': datetime.utcnow().isoformat()
        }
        
        self.regulatory_changes.append(change)
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def get_industry_comparison_data(self):
        """Get data for industry comparison"""
        return {
            'industry': self.industry,
            'market_size': float(self.market_size) if self.market_size else None,
            'growth_rate': self.growth_rate,
            'average_revenue': float(self.average_revenue) if self.average_revenue else None,
            'average_profit_margins': self.average_profit_margins,
            'key_trends': self.market_trends[:5] if self.market_trends else []
        } 