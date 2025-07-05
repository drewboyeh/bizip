import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///business_intelligence.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis configuration
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # API rate limiting
    RATELIMIT_DEFAULT = "200 per day;50 per hour"
    RATELIMIT_STORAGE_URL = REDIS_URL
    
    # Data collection settings
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    DELAY_BETWEEN_REQUESTS = 1  # seconds
    
    # Compliance settings
    AUDIT_LOG_ENABLED = True
    DATA_RETENTION_DAYS = 365
    PRIVACY_POLICY_URL = os.environ.get('PRIVACY_POLICY_URL')
    
    # External API keys
    ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY')
    SEC_API_KEY = os.environ.get('SEC_API_KEY')
    LINKEDIN_API_KEY = os.environ.get('LINKEDIN_API_KEY')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
    
    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = 'business_intelligence.log'
    
    # Celery configuration
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    
    # Pricing tiers
    PRICING_TIERS = {
        'basic': {
            'price': 199,
            'profiles_per_month': 50,
            'features': ['business_profiles', 'basic_analysis']
        },
        'professional': {
            'price': 399,
            'profiles_per_month': 200,
            'features': ['business_profiles', 'advanced_analysis', 'industry_reports']
        },
        'enterprise': {
            'price': 799,
            'profiles_per_month': -1,  # unlimited
            'features': ['business_profiles', 'advanced_analysis', 'industry_reports', 'custom_research']
        }
    }
    
    # Industry categories
    INDUSTRY_CATEGORIES = [
        'Healthcare',
        'Technology',
        'Real Estate',
        'Manufacturing',
        'Professional Services',
        'Financial Services',
        'Retail',
        'Construction',
        'Transportation',
        'Energy',
        'Education',
        'Entertainment',
        'Food & Beverage',
        'Automotive',
        'Aerospace',
        'Biotechnology',
        'Pharmaceuticals',
        'Telecommunications',
        'Utilities',
        'Other'
    ]
    
    # Financial planning opportunities
    PLANNING_OPPORTUNITIES = [
        'Business Succession Planning',
        'Tax Optimization',
        'Employee Benefit Plans',
        'Risk Management',
        'Investment Policy',
        'Estate Planning',
        'Retirement Planning',
        'Insurance Planning',
        'Debt Management',
        'Cash Flow Optimization'
    ]

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Production-specific settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
    }

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 