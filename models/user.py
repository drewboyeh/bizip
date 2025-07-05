from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """User model for financial advisors"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    company_name = db.Column(db.String(100))
    job_title = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    
    # Subscription and billing
    subscription_tier = db.Column(db.String(20), default='basic')  # basic, professional, enterprise
    subscription_status = db.Column(db.String(20), default='active')  # active, suspended, cancelled
    subscription_start_date = db.Column(db.DateTime)
    subscription_end_date = db.Column(db.DateTime)
    profiles_used_this_month = db.Column(db.Integer, default=0)
    
    # Account settings
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Preferences
    preferred_industries = db.Column(db.JSON)  # List of industry preferences
    notification_settings = db.Column(db.JSON)  # Email, SMS preferences
    
    # Relationships
    business_profiles = db.relationship('BusinessProfile', backref='user', lazy='dynamic')
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def can_create_profile(self):
        """Check if user can create a new business profile based on subscription"""
        from config import Config
        
        tier_config = Config.PRICING_TIERS.get(self.subscription_tier, {})
        max_profiles = tier_config.get('profiles_per_month', 0)
        
        if max_profiles == -1:  # Unlimited
            return True
        
        return self.profiles_used_this_month < max_profiles
    
    def increment_profile_usage(self):
        """Increment the profile usage counter"""
        self.profiles_used_this_month += 1
        db.session.commit()
    
    def reset_monthly_usage(self):
        """Reset monthly usage counter (called by scheduler)"""
        self.profiles_used_this_month = 0
        db.session.commit()
    
    def get_subscription_info(self):
        """Get current subscription information"""
        from config import Config
        
        tier_config = Config.PRICING_TIERS.get(self.subscription_tier, {})
        return {
            'tier': self.subscription_tier,
            'status': self.subscription_status,
            'price': tier_config.get('price', 0),
            'max_profiles': tier_config.get('profiles_per_month', 0),
            'features': tier_config.get('features', []),
            'profiles_used': self.profiles_used_this_month,
            'start_date': self.subscription_start_date,
            'end_date': self.subscription_end_date
        }
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'company_name': self.company_name,
            'job_title': self.job_title,
            'phone': self.phone,
            'subscription_tier': self.subscription_tier,
            'subscription_status': self.subscription_status,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat(),
            'preferred_industries': self.preferred_industries,
            'subscription_info': self.get_subscription_info()
        } 