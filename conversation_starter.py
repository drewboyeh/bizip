from datetime import datetime
from .user import db

class ConversationStarter(db.Model):
    """Conversation starters and insights for financial advisors"""
    __tablename__ = 'conversation_starters'
    
    id = db.Column(db.Integer, primary_key=True)
    business_profile_id = db.Column(db.Integer, db.ForeignKey('business_profiles.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Conversation starter details
    topic = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50))  # business_development, industry_trends, regulatory, personal
    context = db.Column(db.Text, nullable=False)
    suggested_approach = db.Column(db.Text)
    
    # Timing and relevance
    relevance_score = db.Column(db.Integer)  # 1-10 scale
    urgency = db.Column(db.String(20))  # low, medium, high
    best_timing = db.Column(db.String(50))  # next_meeting, follow_up, quarterly_review
    
    # Business context
    business_milestone = db.Column(db.String(200))  # e.g., "Recent funding round"
    industry_trend = db.Column(db.String(200))  # e.g., "AI integration in healthcare"
    regulatory_change = db.Column(db.String(200))  # e.g., "New tax law changes"
    
    # Financial planning connection
    planning_areas = db.Column(db.JSON)  # List of planning areas this relates to
    opportunity_value = db.Column(db.Numeric(15, 2))
    risk_mitigation = db.Column(db.Text)
    
    # Usage tracking
    used_count = db.Column(db.Integer, default=0)
    last_used = db.Column(db.DateTime)
    success_rating = db.Column(db.Integer)  # 1-5 scale after use
    feedback = db.Column(db.Text)
    
    # Customization
    custom_notes = db.Column(db.Text)
    tags = db.Column(db.JSON)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = db.Column(db.DateTime)  # When this becomes less relevant
    
    def __repr__(self):
        return f'<ConversationStarter {self.topic}>'
    
    def to_dict(self):
        """Convert conversation starter to dictionary"""
        return {
            'id': self.id,
            'business_profile_id': self.business_profile_id,
            'user_id': self.user_id,
            'topic': self.topic,
            'category': self.category,
            'context': self.context,
            'suggested_approach': self.suggested_approach,
            'timing': {
                'relevance_score': self.relevance_score,
                'urgency': self.urgency,
                'best_timing': self.best_timing
            },
            'business_context': {
                'milestone': self.business_milestone,
                'industry_trend': self.industry_trend,
                'regulatory_change': self.regulatory_change
            },
            'planning_connection': {
                'areas': self.planning_areas,
                'opportunity_value': float(self.opportunity_value) if self.opportunity_value else None,
                'risk_mitigation': self.risk_mitigation
            },
            'usage': {
                'used_count': self.used_count,
                'last_used': self.last_used.isoformat() if self.last_used else None,
                'success_rating': self.success_rating,
                'feedback': self.feedback
            },
            'custom': {
                'notes': self.custom_notes,
                'tags': self.tags
            },
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
    
    def mark_as_used(self, success_rating=None, feedback=None):
        """Mark conversation starter as used"""
        self.used_count += 1
        self.last_used = datetime.utcnow()
        
        if success_rating is not None:
            self.success_rating = success_rating
        
        if feedback:
            self.feedback = feedback
        
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def is_relevant(self):
        """Check if conversation starter is still relevant"""
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        
        # Check if it's been used too many times (might be stale)
        if self.used_count > 5:
            return False
        
        return True
    
    def get_effectiveness_score(self):
        """Calculate effectiveness score based on usage and ratings"""
        if self.used_count == 0:
            return 0
        
        # Base score from success rating
        base_score = self.success_rating or 3
        
        # Bonus for multiple successful uses
        if self.used_count > 1 and self.success_rating and self.success_rating >= 4:
            base_score += 1
        
        return min(base_score, 5)
    
    def get_priority_score(self):
        """Calculate priority score for sorting"""
        priority_scores = {
            'low': 1,
            'medium': 2,
            'high': 3
        }
        
        base_score = priority_scores.get(self.urgency, 1)
        
        # Add relevance score
        if self.relevance_score:
            base_score += self.relevance_score / 10
        
        # Add effectiveness bonus
        base_score += self.get_effectiveness_score() / 10
        
        return base_score
    
    def update_relevance(self, new_score, new_urgency=None):
        """Update relevance score and urgency"""
        self.relevance_score = new_score
        
        if new_urgency:
            self.urgency = new_urgency
        
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def add_tag(self, tag):
        """Add a tag to the conversation starter"""
        if not self.tags:
            self.tags = []
        
        if tag not in self.tags:
            self.tags.append(tag)
            db.session.commit()
    
    def remove_tag(self, tag):
        """Remove a tag from the conversation starter"""
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
            db.session.commit()
    
    def get_suggested_script(self):
        """Generate a suggested conversation script"""
        script_parts = []
        
        if self.context:
            script_parts.append(f"Context: {self.context}")
        
        if self.suggested_approach:
            script_parts.append(f"Approach: {self.suggested_approach}")
        
        if self.planning_areas:
            areas = ", ".join(self.planning_areas)
            script_parts.append(f"Planning areas: {areas}")
        
        if self.opportunity_value:
            script_parts.append(f"Potential value: ${self.opportunity_value:,.2f}")
        
        return "\n\n".join(script_parts) 