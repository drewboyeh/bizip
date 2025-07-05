from datetime import datetime
from .user import db

class Company(db.Model):
    """Company model for business entities"""
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    legal_name = db.Column(db.String(200))
    duns_number = db.Column(db.String(20), unique=True)
    ein = db.Column(db.String(20), unique=True)
    
    # Business information
    industry = db.Column(db.String(100), index=True)
    sector = db.Column(db.String(100))
    business_type = db.Column(db.String(50))  # LLC, Corp, Partnership, etc.
    founded_year = db.Column(db.Integer)
    
    # Contact information
    website = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    
    # Address
    address_line1 = db.Column(db.String(200))
    address_line2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    zip_code = db.Column(db.String(20))
    country = db.Column(db.String(50))
    
    # Financial information
    estimated_revenue = db.Column(db.Numeric(15, 2))
    revenue_range = db.Column(db.String(50))  # $1M-$5M, $5M-$10M, etc.
    employee_count = db.Column(db.Integer)
    employee_range = db.Column(db.String(50))  # 1-10, 11-50, etc.
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_public = db.Column(db.Boolean, default=False)
    ticker_symbol = db.Column(db.String(10))
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_data_refresh = db.Column(db.DateTime)
    
    # Relationships
    profiles = db.relationship('CompanyProfile', backref='company', lazy='dynamic')
    executives = db.relationship('CompanyExecutive', backref='company', lazy='dynamic')
    
    def __repr__(self):
        return f'<Company {self.name}>'
    
    def to_dict(self):
        """Convert company to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'legal_name': self.legal_name,
            'duns_number': self.duns_number,
            'ein': self.ein,
            'industry': self.industry,
            'sector': self.sector,
            'business_type': self.business_type,
            'founded_year': self.founded_year,
            'website': self.website,
            'phone': self.phone,
            'email': self.email,
            'address': {
                'line1': self.address_line1,
                'line2': self.address_line2,
                'city': self.city,
                'state': self.state,
                'zip_code': self.zip_code,
                'country': self.country
            },
            'financial': {
                'estimated_revenue': float(self.estimated_revenue) if self.estimated_revenue else None,
                'revenue_range': self.revenue_range,
                'employee_count': self.employee_count,
                'employee_range': self.employee_range
            },
            'status': {
                'is_active': self.is_active,
                'is_public': self.is_public,
                'ticker_symbol': self.ticker_symbol
            },
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_data_refresh': self.last_data_refresh.isoformat() if self.last_data_refresh else None
        }

class CompanyProfile(db.Model):
    """Detailed company profile with analysis"""
    __tablename__ = 'company_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Business analysis
    business_model = db.Column(db.Text)
    value_proposition = db.Column(db.Text)
    target_market = db.Column(db.Text)
    competitive_advantages = db.Column(db.Text)
    growth_strategy = db.Column(db.Text)
    
    # Financial analysis
    revenue_growth_rate = db.Column(db.Float)
    profit_margins = db.Column(db.Float)
    cash_flow_analysis = db.Column(db.Text)
    debt_levels = db.Column(db.Text)
    investment_needs = db.Column(db.Text)
    
    # Risk assessment
    business_risks = db.Column(db.JSON)
    market_risks = db.Column(db.JSON)
    regulatory_risks = db.Column(db.JSON)
    financial_risks = db.Column(db.JSON)
    
    # Opportunities
    expansion_opportunities = db.Column(db.Text)
    efficiency_opportunities = db.Column(db.Text)
    partnership_opportunities = db.Column(db.Text)
    
    # Recent developments
    recent_news = db.Column(db.JSON)
    recent_milestones = db.Column(db.JSON)
    upcoming_events = db.Column(db.JSON)
    
    # Industry context
    industry_trends = db.Column(db.Text)
    market_position = db.Column(db.Text)
    competitive_landscape = db.Column(db.Text)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    analysis_date = db.Column(db.DateTime, default=datetime.utcnow)
    data_sources = db.Column(db.JSON)  # Track data sources used
    
    def __repr__(self):
        return f'<CompanyProfile {self.company_id}>'
    
    def to_dict(self):
        """Convert profile to dictionary"""
        return {
            'id': self.id,
            'company_id': self.company_id,
            'user_id': self.user_id,
            'business_analysis': {
                'business_model': self.business_model,
                'value_proposition': self.value_proposition,
                'target_market': self.target_market,
                'competitive_advantages': self.competitive_advantages,
                'growth_strategy': self.growth_strategy
            },
            'financial_analysis': {
                'revenue_growth_rate': self.revenue_growth_rate,
                'profit_margins': self.profit_margins,
                'cash_flow_analysis': self.cash_flow_analysis,
                'debt_levels': self.debt_levels,
                'investment_needs': self.investment_needs
            },
            'risk_assessment': {
                'business_risks': self.business_risks,
                'market_risks': self.market_risks,
                'regulatory_risks': self.regulatory_risks,
                'financial_risks': self.financial_risks
            },
            'opportunities': {
                'expansion_opportunities': self.expansion_opportunities,
                'efficiency_opportunities': self.efficiency_opportunities,
                'partnership_opportunities': self.partnership_opportunities
            },
            'recent_developments': {
                'recent_news': self.recent_news,
                'recent_milestones': self.recent_milestones,
                'upcoming_events': self.upcoming_events
            },
            'industry_context': {
                'industry_trends': self.industry_trends,
                'market_position': self.market_position,
                'competitive_landscape': self.competitive_landscape
            },
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'analysis_date': self.analysis_date.isoformat(),
            'data_sources': self.data_sources
        }

class CompanyExecutive(db.Model):
    """Company executive information"""
    __tablename__ = 'company_executives'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    
    # Executive information
    name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    linkedin_url = db.Column(db.String(200))
    
    # Background
    bio = db.Column(db.Text)
    experience = db.Column(db.JSON)
    education = db.Column(db.JSON)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<CompanyExecutive {self.name} at {self.company_id}>'
    
    def to_dict(self):
        """Convert executive to dictionary"""
        return {
            'id': self.id,
            'company_id': self.company_id,
            'name': self.name,
            'title': self.title,
            'email': self.email,
            'phone': self.phone,
            'linkedin_url': self.linkedin_url,
            'bio': self.bio,
            'experience': self.experience,
            'education': self.education,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 