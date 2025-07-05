from datetime import datetime, timedelta
from .user import db

class BusinessProfile(db.Model):
    """Business profile for financial planning intelligence"""
    __tablename__ = 'business_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    
    # Profile metadata
    profile_name = db.Column(db.String(200))
    profile_type = db.Column(db.String(50))  # prospect, client, referral_source
    status = db.Column(db.String(20), default='active')  # active, archived, deleted
    
    # Financial planning focus areas
    primary_planning_needs = db.Column(db.JSON)  # List of planning areas
    secondary_planning_needs = db.Column(db.JSON)
    urgency_level = db.Column(db.String(20))  # low, medium, high, critical
    
    # Relationship information
    relationship_stage = db.Column(db.String(50))  # prospect, qualified, proposal, client
    relationship_notes = db.Column(db.Text)
    next_follow_up_date = db.Column(db.DateTime)
    last_contact_date = db.Column(db.DateTime)
    
    # Financial planning opportunities
    opportunities_identified = db.Column(db.JSON)
    opportunities_prioritized = db.Column(db.JSON)
    estimated_opportunity_value = db.Column(db.Numeric(15, 2))
    
    # Conversation starters and insights
    conversation_starters = db.Column(db.JSON)
    recent_developments = db.Column(db.JSON)
    industry_insights = db.Column(db.JSON)
    
    # Custom fields
    custom_fields = db.Column(db.JSON)  # User-defined fields
    tags = db.Column(db.JSON)  # User-defined tags
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_analysis_date = db.Column(db.DateTime)
    
    # Relationships
    financial_opportunities = db.relationship('FinancialOpportunity', backref='business_profile', lazy='dynamic')
    conversation_starters_rel = db.relationship('ConversationStarter', backref='business_profile', lazy='dynamic')
    
    def __repr__(self):
        return f'<BusinessProfile {self.id} for {self.company_id}>'
    
    def to_dict(self):
        """Convert business profile to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'company_id': self.company_id,
            'profile_name': self.profile_name,
            'profile_type': self.profile_type,
            'status': self.status,
            'planning_focus': {
                'primary_needs': self.primary_planning_needs,
                'secondary_needs': self.secondary_planning_needs,
                'urgency_level': self.urgency_level
            },
            'relationship': {
                'stage': self.relationship_stage,
                'notes': self.relationship_notes,
                'next_follow_up': self.next_follow_up_date.isoformat() if self.next_follow_up_date else None,
                'last_contact': self.last_contact_date.isoformat() if self.last_contact_date else None
            },
            'opportunities': {
                'identified': self.opportunities_identified,
                'prioritized': self.opportunities_prioritized,
                'estimated_value': float(self.estimated_opportunity_value) if self.estimated_opportunity_value else None
            },
            'insights': {
                'conversation_starters': self.conversation_starters,
                'recent_developments': self.recent_developments,
                'industry_insights': self.industry_insights
            },
            'custom': {
                'fields': self.custom_fields,
                'tags': self.tags
            },
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_analysis_date': self.last_analysis_date.isoformat() if self.last_analysis_date else None
        }
    
    def add_opportunity(self, opportunity_type, description, estimated_value=None, priority='medium'):
        """Add a financial planning opportunity"""
        if not self.opportunities_identified:
            self.opportunities_identified = []
        
        opportunity = {
            'type': opportunity_type,
            'description': description,
            'estimated_value': estimated_value,
            'priority': priority,
            'created_at': datetime.utcnow().isoformat()
        }
        
        self.opportunities_identified.append(opportunity)
        db.session.commit()
    
    def add_conversation_starter(self, topic, context, suggested_approach):
        """Add a conversation starter"""
        if not self.conversation_starters:
            self.conversation_starters = []
        
        starter = {
            'topic': topic,
            'context': context,
            'suggested_approach': suggested_approach,
            'created_at': datetime.utcnow().isoformat()
        }
        
        self.conversation_starters.append(starter)
        db.session.commit()
    
    def update_relationship_stage(self, new_stage, notes=None):
        """Update relationship stage"""
        self.relationship_stage = new_stage
        if notes:
            self.relationship_notes = notes
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def schedule_follow_up(self, follow_up_date, notes=None):
        """Schedule a follow-up"""
        self.next_follow_up_date = follow_up_date
        if notes:
            self.relationship_notes = notes
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def get_priority_opportunities(self):
        """Get high-priority opportunities"""
        if not self.opportunities_identified:
            return []
        
        return [opp for opp in self.opportunities_identified if opp.get('priority') in ['high', 'critical']]
    
    def get_recent_developments(self, days=30):
        """Get recent developments within specified days"""
        if not self.recent_developments:
            return []
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent = []
        
        for dev in self.recent_developments:
            dev_date = datetime.fromisoformat(dev.get('date', ''))
            if dev_date >= cutoff_date:
                recent.append(dev)
        
        return recent 