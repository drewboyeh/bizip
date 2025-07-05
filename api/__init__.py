from .auth import auth_bp
from .profiles import profiles_bp
from .opportunities import opportunities_bp
from .reports import reports_bp
from .compliance import compliance_bp

__all__ = [
    'auth_bp',
    'profiles_bp',
    'opportunities_bp',
    'reports_bp',
    'compliance_bp'
] 