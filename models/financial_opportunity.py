from datetime import datetime, timedelta
from .user import db

class FinancialOpportunity(db.Model):
    """Financial planning opportunities identified for businesses"""
    __tablename__ = 'financial_opportunities'
    
    id = db.Column(db.Integer, primary_key=True)
    business_profile_id = db.Column(db.Integer, db.ForeignKey('business_profiles.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Opportunity details
    opportunity_type = db.Column(db.String(100), nullable=False)  # e.g., "Business Succession Planning"
    category = db.Column(db.String(50))  # tax, retirement, estate, business, insurance
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    # Financial impact
    estimated_value = db.Column(db.Numeric(15, 2))
    value_range = db.Column(db.String(50))  # e.g., "$50K-$100K"
    annual_savings = db.Column(db.Numeric(15, 2))
    one_time_benefit = db.Column(db.Numeric(15, 2))
    
    # Priority and urgency
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    urgency = db.Column(db.String(20), default='normal')  # normal, urgent, time-sensitive
    deadline = db.Column(db.DateTime)
    
    # Implementation details
    complexity = db.Column(db.String(20))  # simple, moderate, complex
    implementation_time = db.Column(db.String(50))  # e.g., "2-4 weeks"
    required_resources = db.Column(db.JSON)
    
    # Status tracking
    status = db.Column(db.String(20), default='identified')  # identified, proposed, in_progress, completed, declined
    progress_percentage = db.Column(db.Integer, default=0)
    
    # Notes and context
    business_context = db.Column(db.Text)  # Why this opportunity exists
    regulatory_context = db.Column(db.Text)  # Regulatory drivers
    market_context = db.Column(db.Text)  # Market conditions affecting this
    notes = db.Column(db.Text)
    
    # Related opportunities
    related_opportunities = db.Column(db.JSON)  # IDs of related opportunities
    prerequisites = db.Column(db.JSON)  # Opportunities that should be addressed first
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    identified_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_reviewed = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<FinancialOpportunity {self.title}>'
    
    def to_dict(self):
        """Convert opportunity to dictionary"""
        return {
            'id': self.id,
            'business_profile_id': self.business_profile_id,
            'user_id': self.user_id,
            'opportunity_type': self.opportunity_type,
            'category': self.category,
            'title': self.title,
            'description': self.description,
            'financial_impact': {
                'estimated_value': float(self.estimated_value) if self.estimated_value else None,
                'value_range': self.value_range,
                'annual_savings': float(self.annual_savings) if self.annual_savings else None,
                'one_time_benefit': float(self.one_time_benefit) if self.one_time_benefit else None
            },
            'priority': {
                'level': self.priority,
                'urgency': self.urgency,
                'deadline': self.deadline.isoformat() if self.deadline else None
            },
            'implementation': {
                'complexity': self.complexity,
                'time_required': self.implementation_time,
                'required_resources': self.required_resources
            },
            'status': {
                'current': self.status,
                'progress': self.progress_percentage
            },
            'context': {
                'business': self.business_context,
                'regulatory': self.regulatory_context,
                'market': self.market_context,
                'notes': self.notes
            },
            'relationships': {
                'related_opportunities': self.related_opportunities,
                'prerequisites': self.prerequisites
            },
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'identified_date': self.identified_date.isoformat(),
            'last_reviewed': self.last_reviewed.isoformat() if self.last_reviewed else None
        }
    
    def update_status(self, new_status, progress_percentage=None, notes=None):
        """Update opportunity status"""
        self.status = new_status
        if progress_percentage is not None:
            self.progress_percentage = progress_percentage
        if notes:
            self.notes = notes
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def mark_as_reviewed(self):
        """Mark opportunity as reviewed"""
        self.last_reviewed = datetime.utcnow()
        db.session.commit()
    
    def add_related_opportunity(self, opportunity_id):
        """Add a related opportunity"""
        if not self.related_opportunities:
            self.related_opportunities = []
        
        if opportunity_id not in self.related_opportunities:
            self.related_opportunities.append(opportunity_id)
            db.session.commit()
    
    def add_prerequisite(self, opportunity_id):
        """Add a prerequisite opportunity"""
        if not self.prerequisites:
            self.prerequisites = []
        
        if opportunity_id not in self.prerequisites:
            self.prerequisites.append(opportunity_id)
            db.session.commit()
    
    def is_urgent(self):
        """Check if opportunity is urgent"""
        if self.urgency in ['urgent', 'time-sensitive']:
            return True
        
        if self.deadline and self.deadline <= datetime.utcnow() + timedelta(days=30):
            return True
        
        return False
    
    def get_priority_score(self):
        """Calculate priority score for sorting"""
        priority_scores = {
            'low': 1,
            'medium': 2,
            'high': 3,
            'critical': 4
        }
        
        urgency_scores = {
            'normal': 0,
            'urgent': 1,
            'time-sensitive': 2
        }
        
        base_score = priority_scores.get(self.priority, 0)
        urgency_bonus = urgency_scores.get(self.urgency, 0)
        
        return base_score + urgency_bonus
    
    def get_estimated_total_value(self):
        """Get total estimated value including annual savings"""
        total = 0
        
        if self.estimated_value:
            total += float(self.estimated_value)
        
        if self.annual_savings:
            total += float(self.annual_savings)
        
        if self.one_time_benefit:
            total += float(self.one_time_benefit)
        
        return total 