from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from .user import User
from .company import Company, CompanyProfile
from .business_profile import BusinessProfile
from .financial_opportunity import FinancialOpportunity
from .conversation_starter import ConversationStarter
from .industry_report import IndustryReport
from .audit_log import AuditLog
from .subscription import Subscription

__all__ = [
    'db',
    'User',
    'Company',
    'CompanyProfile', 
    'BusinessProfile',
    'FinancialOpportunity',
    'ConversationStarter',
    'IndustryReport',
    'AuditLog',
    'Subscription'
] 