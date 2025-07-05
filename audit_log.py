from datetime import datetime
from .user import db

class AuditLog(db.Model):
    """Audit log for compliance and data tracking"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Action details
    action_type = db.Column(db.String(50), nullable=False)  # data_access, profile_created, report_generated, etc.
    action_description = db.Column(db.Text, nullable=False)
    resource_type = db.Column(db.String(50))  # company, profile, report, opportunity
    resource_id = db.Column(db.Integer)
    
    # Data source tracking
    data_sources_used = db.Column(db.JSON)  # List of data sources accessed
    data_access_method = db.Column(db.String(50))  # api, web_scraping, manual_research
    data_access_url = db.Column(db.String(500))
    
    # Compliance information
    compliance_status = db.Column(db.String(20), default='compliant')  # compliant, review_needed, violation
    privacy_impact = db.Column(db.String(20))  # low, medium, high
    data_retention_required = db.Column(db.Boolean, default=True)
    
    # Request details
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    request_method = db.Column(db.String(10))
    request_url = db.Column(db.String(500))
    
    # Results and outcomes
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)
    processing_time = db.Column(db.Float)  # seconds
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    session_id = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<AuditLog {self.action_type} by {self.user_id}>'
    
    def to_dict(self):
        """Convert audit log to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': {
                'type': self.action_type,
                'description': self.action_description,
                'resource_type': self.resource_type,
                'resource_id': self.resource_id
            },
            'data_sources': {
                'sources_used': self.data_sources_used,
                'access_method': self.data_access_method,
                'access_url': self.data_access_url
            },
            'compliance': {
                'status': self.compliance_status,
                'privacy_impact': self.privacy_impact,
                'data_retention_required': self.data_retention_required
            },
            'request': {
                'ip_address': self.ip_address,
                'user_agent': self.user_agent,
                'method': self.request_method,
                'url': self.request_url
            },
            'results': {
                'success': self.success,
                'error_message': self.error_message,
                'processing_time': self.processing_time
            },
            'created_at': self.created_at.isoformat(),
            'session_id': self.session_id
        }
    
    @classmethod
    def log_data_access(cls, user_id, data_sources, access_method, access_url, 
                       resource_type=None, resource_id=None, ip_address=None, 
                       user_agent=None, request_method=None, request_url=None):
        """Log data access for compliance"""
        log_entry = cls(
            user_id=user_id,
            action_type='data_access',
            action_description=f'Accessed data from {len(data_sources)} sources',
            resource_type=resource_type,
            resource_id=resource_id,
            data_sources_used=data_sources,
            data_access_method=access_method,
            data_access_url=access_url,
            ip_address=ip_address,
            user_agent=user_agent,
            request_method=request_method,
            request_url=request_url
        )
        
        db.session.add(log_entry)
        db.session.commit()
        return log_entry
    
    @classmethod
    def log_profile_creation(cls, user_id, company_name, data_sources_used, 
                           ip_address=None, user_agent=None):
        """Log business profile creation"""
        log_entry = cls(
            user_id=user_id,
            action_type='profile_created',
            action_description=f'Created business profile for {company_name}',
            resource_type='business_profile',
            data_sources_used=data_sources_used,
            data_access_method='api',
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.add(log_entry)
        db.session.commit()
        return log_entry
    
    @classmethod
    def log_report_generation(cls, user_id, report_type, industry, 
                            data_sources_used, processing_time=None):
        """Log report generation"""
        log_entry = cls(
            user_id=user_id,
            action_type='report_generated',
            action_description=f'Generated {report_type} report for {industry}',
            resource_type='industry_report',
            data_sources_used=data_sources_used,
            data_access_method='api',
            processing_time=processing_time
        )
        
        db.session.add(log_entry)
        db.session.commit()
        return log_entry
    
    @classmethod
    def log_opportunity_identification(cls, user_id, opportunity_type, company_name,
                                     data_sources_used, estimated_value=None):
        """Log financial opportunity identification"""
        description = f'Identified {opportunity_type} opportunity for {company_name}'
        if estimated_value:
            description += f' (estimated value: ${estimated_value:,.2f})'
        
        log_entry = cls(
            user_id=user_id,
            action_type='opportunity_identified',
            action_description=description,
            resource_type='financial_opportunity',
            data_sources_used=data_sources_used,
            data_access_method='analysis'
        )
        
        db.session.add(log_entry)
        db.session.commit()
        return log_entry
    
    @classmethod
    def log_compliance_violation(cls, user_id, violation_type, description,
                               resource_type=None, resource_id=None):
        """Log compliance violations"""
        log_entry = cls(
            user_id=user_id,
            action_type='compliance_violation',
            action_description=description,
            resource_type=resource_type,
            resource_id=resource_id,
            compliance_status='violation',
            privacy_impact='high',
            success=False
        )
        
        db.session.add(log_entry)
        db.session.commit()
        return log_entry
    
    @classmethod
    def get_user_activity_summary(cls, user_id, days=30):
        """Get summary of user activity"""
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        activities = cls.query.filter(
            cls.user_id == user_id,
            cls.created_at >= cutoff_date
        ).all()
        
        summary = {
            'total_actions': len(activities),
            'data_access_count': 0,
            'profiles_created': 0,
            'reports_generated': 0,
            'opportunities_identified': 0,
            'compliance_violations': 0,
            'data_sources_accessed': set(),
            'last_activity': None
        }
        
        for activity in activities:
            if activity.action_type == 'data_access':
                summary['data_access_count'] += 1
            elif activity.action_type == 'profile_created':
                summary['profiles_created'] += 1
            elif activity.action_type == 'report_generated':
                summary['reports_generated'] += 1
            elif activity.action_type == 'opportunity_identified':
                summary['opportunities_identified'] += 1
            elif activity.action_type == 'compliance_violation':
                summary['compliance_violations'] += 1
            
            if activity.data_sources_used:
                summary['data_sources_accessed'].update(activity.data_sources_used)
            
            if not summary['last_activity'] or activity.created_at > summary['last_activity']:
                summary['last_activity'] = activity.created_at
        
        summary['data_sources_accessed'] = list(summary['data_sources_accessed'])
        return summary
    
    @classmethod
    def get_compliance_report(cls, start_date=None, end_date=None):
        """Generate compliance report"""
        query = cls.query
        
        if start_date:
            query = query.filter(cls.created_at >= start_date)
        
        if end_date:
            query = query.filter(cls.created_at <= end_date)
        
        logs = query.all()
        
        report = {
            'total_actions': len(logs),
            'compliant_actions': 0,
            'violations': 0,
            'review_needed': 0,
            'data_sources_used': set(),
            'privacy_impact_summary': {'low': 0, 'medium': 0, 'high': 0},
            'action_type_summary': {}
        }
        
        for log in logs:
            if log.compliance_status == 'compliant':
                report['compliant_actions'] += 1
            elif log.compliance_status == 'violation':
                report['violations'] += 1
            elif log.compliance_status == 'review_needed':
                report['review_needed'] += 1
            
            if log.data_sources_used:
                report['data_sources_used'].update(log.data_sources_used)
            
            if log.privacy_impact:
                report['privacy_impact_summary'][log.privacy_impact] += 1
            
            action_type = log.action_type
            report['action_type_summary'][action_type] = report['action_type_summary'].get(action_type, 0) + 1
        
        report['data_sources_used'] = list(report['data_sources_used'])
        return report
    
    def mark_for_review(self, reason):
        """Mark log entry for compliance review"""
        self.compliance_status = 'review_needed'
        self.action_description += f' [REVIEW NEEDED: {reason}]'
        db.session.commit()
    
    def is_retention_required(self):
        """Check if log entry should be retained based on compliance requirements"""
        if not self.data_retention_required:
            return False
        
        # Keep high privacy impact logs longer
        if self.privacy_impact == 'high':
            return True
        
        # Keep violation logs
        if self.compliance_status == 'violation':
            return True
        
        # Keep data access logs for audit trail
        if self.action_type == 'data_access':
            return True
        
        return False 