from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from datetime import timedelta
import re
from models import db, User, AuditLog

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'username', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate email format
        email = data['email']
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 409
        
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already taken'}), 409
        
        # Validate password strength
        password = data['password']
        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400
        
        # Create new user
        user = User(
            email=email,
            username=data['username'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            company_name=data.get('company_name'),
            job_title=data.get('job_title'),
            phone=data.get('phone'),
            preferred_industries=data.get('preferred_industries', [])
        )
        
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Log registration
        AuditLog.log_data_access(
            user_id=user.id,
            data_sources=['user_registration'],
            access_method='api',
            access_url='/api/auth/register',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            request_method='POST',
            request_url=request.url
        )
        
        # Create access token
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(hours=24)
        )
        
        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return access token"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user by email
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Update last login
        user.last_login = db.func.now()
        db.session.commit()
        
        # Log login
        AuditLog.log_data_access(
            user_id=user.id,
            data_sources=['user_login'],
            access_method='api',
            access_url='/api/auth/login',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            request_method='POST',
            request_url=request.url
        )
        
        # Create access token
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(hours=24)
        )
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get profile: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        allowed_fields = ['first_name', 'last_name', 'company_name', 'job_title', 'phone', 'preferred_industries']
        
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        db.session.commit()
        
        # Log profile update
        AuditLog.log_data_access(
            user_id=user.id,
            data_sources=['profile_update'],
            access_method='api',
            access_url='/api/auth/profile',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            request_method='PUT',
            request_url=request.url
        )
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update profile: {str(e)}'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        # Verify current password
        if not user.check_password(data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Validate new password
        new_password = data['new_password']
        if len(new_password) < 8:
            return jsonify({'error': 'New password must be at least 8 characters long'}), 400
        
        # Update password
        user.set_password(new_password)
        db.session.commit()
        
        # Log password change
        AuditLog.log_data_access(
            user_id=user.id,
            data_sources=['password_change'],
            access_method='api',
            access_url='/api/auth/change-password',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            request_method='POST',
            request_url=request.url
        )
        
        return jsonify({
            'message': 'Password changed successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to change password: {str(e)}'}), 500

@auth_bp.route('/subscription', methods=['GET'])
@jwt_required()
def get_subscription():
    """Get current user subscription information"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        subscription_info = user.get_subscription_info()
        
        return jsonify({
            'subscription': subscription_info
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get subscription: {str(e)}'}), 500

@auth_bp.route('/subscription/upgrade', methods=['POST'])
@jwt_required()
def upgrade_subscription():
    """Upgrade user subscription"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        new_tier = data.get('tier')
        
        if not new_tier:
            return jsonify({'error': 'Subscription tier is required'}), 400
        
        # Validate tier
        valid_tiers = ['basic', 'professional', 'enterprise']
        if new_tier not in valid_tiers:
            return jsonify({'error': 'Invalid subscription tier'}), 400
        
        # Update subscription
        user.subscription_tier = new_tier
        db.session.commit()
        
        # Log subscription upgrade
        AuditLog.log_data_access(
            user_id=user.id,
            data_sources=['subscription_upgrade'],
            access_method='api',
            access_url='/api/auth/subscription/upgrade',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            request_method='POST',
            request_url=request.url
        )
        
        return jsonify({
            'message': 'Subscription upgraded successfully',
            'subscription': user.get_subscription_info()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to upgrade subscription: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (client should discard token)"""
    try:
        current_user_id = get_jwt_identity()
        
        # Log logout
        AuditLog.log_data_access(
            user_id=current_user_id,
            data_sources=['user_logout'],
            access_method='api',
            access_url='/api/auth/logout',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            request_method='POST',
            request_url=request.url
        )
        
        return jsonify({
            'message': 'Logout successful'
        })
        
    except Exception as e:
        return jsonify({'error': f'Logout failed: {str(e)}'}), 500 