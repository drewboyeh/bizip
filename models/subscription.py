from datetime import datetime, timedelta
from .user import db

class Subscription(db.Model):
    """Subscription and billing management"""
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Subscription details
    tier = db.Column(db.String(20), nullable=False)  # basic, professional, enterprise
    status = db.Column(db.String(20), default='active')  # active, suspended, cancelled, expired
    billing_cycle = db.Column(db.String(20), default='monthly')  # monthly, annual
    
    # Billing information
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD')
    next_billing_date = db.Column(db.DateTime, nullable=False)
    last_billing_date = db.Column(db.DateTime)
    
    # Usage tracking
    profiles_used_this_period = db.Column(db.Integer, default=0)
    profiles_limit = db.Column(db.Integer)
    reports_used_this_period = db.Column(db.Integer, default=0)
    reports_limit = db.Column(db.Integer)
    
    # Payment information
    payment_method = db.Column(db.String(50))  # credit_card, bank_transfer, etc.
    payment_status = db.Column(db.String(20), default='paid')  # paid, pending, failed
    last_payment_amount = db.Column(db.Numeric(10, 2))
    last_payment_date = db.Column(db.DateTime)
    
    # Trial information
    is_trial = db.Column(db.Boolean, default=False)
    trial_start_date = db.Column(db.DateTime)
    trial_end_date = db.Column(db.DateTime)
    trial_days_remaining = db.Column(db.Integer)
    
    # Cancellation
    cancellation_date = db.Column(db.DateTime)
    cancellation_reason = db.Column(db.Text)
    auto_renew = db.Column(db.Boolean, default=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Subscription {self.tier} for {self.user_id}>'
    
    def to_dict(self):
        """Convert subscription to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'tier': self.tier,
            'status': self.status,
            'billing_cycle': self.billing_cycle,
            'billing': {
                'amount': float(self.amount),
                'currency': self.currency,
                'next_billing_date': self.next_billing_date.isoformat(),
                'last_billing_date': self.last_billing_date.isoformat() if self.last_billing_date else None
            },
            'usage': {
                'profiles_used': self.profiles_used_this_period,
                'profiles_limit': self.profiles_limit,
                'reports_used': self.reports_used_this_period,
                'reports_limit': self.reports_limit
            },
            'payment': {
                'method': self.payment_method,
                'status': self.payment_status,
                'last_amount': float(self.last_payment_amount) if self.last_payment_amount else None,
                'last_date': self.last_payment_date.isoformat() if self.last_payment_date else None
            },
            'trial': {
                'is_trial': self.is_trial,
                'start_date': self.trial_start_date.isoformat() if self.trial_start_date else None,
                'end_date': self.trial_end_date.isoformat() if self.trial_end_date else None,
                'days_remaining': self.trial_days_remaining
            },
            'cancellation': {
                'date': self.cancellation_date.isoformat() if self.cancellation_date else None,
                'reason': self.cancellation_reason,
                'auto_renew': self.auto_renew
            },
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def can_create_profile(self):
        """Check if user can create a new business profile"""
        if self.profiles_limit is None:  # Unlimited
            return True
        
        return self.profiles_used_this_period < self.profiles_limit
    
    def can_generate_report(self):
        """Check if user can generate a new industry report"""
        if self.reports_limit is None:  # Unlimited
            return True
        
        return self.reports_used_this_period < self.reports_limit
    
    def increment_profile_usage(self):
        """Increment profile usage counter"""
        if self.can_create_profile():
            self.profiles_used_this_period += 1
            self.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        return False
    
    def increment_report_usage(self):
        """Increment report usage counter"""
        if self.can_generate_report():
            self.reports_used_this_period += 1
            self.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        return False
    
    def reset_usage_counters(self):
        """Reset usage counters for new billing period"""
        self.profiles_used_this_period = 0
        self.reports_used_this_period = 0
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def is_trial_active(self):
        """Check if trial is still active"""
        if not self.is_trial:
            return False
        
        if not self.trial_end_date:
            return False
        
        return datetime.utcnow() < self.trial_end_date
    
    def get_trial_days_remaining(self):
        """Get number of trial days remaining"""
        if not self.is_trial_active():
            return 0
        
        remaining = self.trial_end_date - datetime.utcnow()
        return max(0, remaining.days)
    
    def upgrade_tier(self, new_tier, new_amount):
        """Upgrade subscription tier"""
        from config import Config
        
        tier_config = Config.PRICING_TIERS.get(new_tier, {})
        
        self.tier = new_tier
        self.amount = new_amount
        self.profiles_limit = tier_config.get('profiles_per_month')
        self.updated_at = datetime.utcnow()
        
        db.session.commit()
    
    def cancel_subscription(self, reason=None, immediate=False):
        """Cancel subscription"""
        self.status = 'cancelled'
        self.cancellation_date = datetime.utcnow()
        self.cancellation_reason = reason
        self.auto_renew = False
        
        if immediate:
            self.status = 'expired'
        
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def suspend_subscription(self, reason=None):
        """Suspend subscription"""
        self.status = 'suspended'
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def reactivate_subscription(self):
        """Reactivate suspended subscription"""
        if self.status == 'suspended':
            self.status = 'active'
            self.updated_at = datetime.utcnow()
            db.session.commit()
    
    def process_billing(self):
        """Process billing for the subscription"""
        if self.status != 'active':
            return False
        
        if self.is_trial_active():
            return True
        
        # Update billing dates
        if self.billing_cycle == 'monthly':
            self.next_billing_date = self.next_billing_date + timedelta(days=30)
        elif self.billing_cycle == 'annual':
            self.next_billing_date = self.next_billing_date + timedelta(days=365)
        
        self.last_billing_date = datetime.utcnow()
        self.reset_usage_counters()
        
        self.updated_at = datetime.utcnow()
        db.session.commit()
        
        return True
    
    def get_usage_percentage(self):
        """Get usage percentage for profiles and reports"""
        profile_percentage = 0
        report_percentage = 0
        
        if self.profiles_limit:
            profile_percentage = (self.profiles_used_this_period / self.profiles_limit) * 100
        
        if self.reports_limit:
            report_percentage = (self.reports_used_this_period / self.reports_limit) * 100
        
        return {
            'profiles': min(profile_percentage, 100),
            'reports': min(report_percentage, 100)
        }
    
    def get_next_billing_info(self):
        """Get information about next billing"""
        days_until_billing = (self.next_billing_date - datetime.utcnow()).days
        
        return {
            'next_billing_date': self.next_billing_date.isoformat(),
            'days_until_billing': max(0, days_until_billing),
            'amount': float(self.amount),
            'currency': self.currency,
            'auto_renew': self.auto_renew
        }
    
    @classmethod
    def create_trial_subscription(cls, user_id, tier='professional', trial_days=14):
        """Create a trial subscription"""
        from config import Config
        
        tier_config = Config.PRICING_TIERS.get(tier, {})
        trial_start = datetime.utcnow()
        trial_end = trial_start + timedelta(days=trial_days)
        
        subscription = cls(
            user_id=user_id,
            tier=tier,
            status='active',
            billing_cycle='monthly',
            amount=tier_config.get('price', 0),
            next_billing_date=trial_end,
            profiles_limit=tier_config.get('profiles_per_month'),
            reports_limit=tier_config.get('reports_per_month'),
            is_trial=True,
            trial_start_date=trial_start,
            trial_end_date=trial_end,
            trial_days_remaining=trial_days
        )
        
        db.session.add(subscription)
        db.session.commit()
        return subscription
    
    @classmethod
    def get_expiring_trials(cls, days=3):
        """Get trials expiring within specified days"""
        cutoff_date = datetime.utcnow() + timedelta(days=days)
        
        return cls.query.filter(
            cls.is_trial == True,
            cls.trial_end_date <= cutoff_date,
            cls.status == 'active'
        ).all()
    
    @classmethod
    def get_upcoming_billings(cls, days=7):
        """Get subscriptions with upcoming billing dates"""
        cutoff_date = datetime.utcnow() + timedelta(days=days)
        
        return cls.query.filter(
            cls.next_billing_date <= cutoff_date,
            cls.status == 'active',
            cls.auto_renew == True
        ).all() 