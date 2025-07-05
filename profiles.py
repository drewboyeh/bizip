from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Company, CompanyProfile, AuditLog
from data_collectors.company_research import CompanyResearchCollector
from data_collectors.sec_data import SECDataCollector
from data_collectors.linkedin_data import LinkedInDataCollector
from data_collectors.news_data import NewsDataCollector
from analysis.intelligence_analyzer import IntelligenceAnalyzer
from datetime import datetime

profiles_bp = Blueprint('profiles', __name__)

@profiles_bp.route('/companies', methods=['GET'])
@jwt_required()
def get_companies():
    """Get list of companies for current user"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get companies associated with user
        companies = Company.query.filter_by(user_id=current_user_id).all()
        
        return jsonify({
            'companies': [company.to_dict() for company in companies]
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get companies: {str(e)}'}), 500

@profiles_bp.route('/companies', methods=['POST'])
@jwt_required()
def create_company():
    """Create a new company profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'error': 'Company name is required'}), 400
        
        # Check if company already exists for user
        existing_company = Company.query.filter_by(
            user_id=current_user_id,
            name=data['name']
        ).first()
        
        if existing_company:
            return jsonify({'error': 'Company already exists'}), 409
        
        # Create new company
        company = Company(
            user_id=current_user_id,
            name=data['name'],
            industry=data.get('industry'),
            website=data.get('website'),
            description=data.get('description')
        )
        
        db.session.add(company)
        db.session.commit()
        
        # Log company creation
        AuditLog.log_data_access(
            user_id=current_user_id,
            data_sources=['company_creation'],
            access_method='api',
            access_url='/api/profiles/companies',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            request_method='POST',
            request_url=request.url
        )
        
        return jsonify({
            'message': 'Company created successfully',
            'company': company.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create company: {str(e)}'}), 500

@profiles_bp.route('/companies/<int:company_id>', methods=['GET'])
@jwt_required()
def get_company(company_id):
    """Get detailed company profile"""
    try:
        current_user_id = get_jwt_identity()
        
        company = Company.query.filter_by(
            id=company_id,
            user_id=current_user_id
        ).first()
        
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        # Get company profile if exists
        profile = CompanyProfile.query.filter_by(company_id=company_id).first()
        
        company_data = company.to_dict()
        if profile:
            company_data['profile'] = profile.to_dict()
        
        return jsonify({
            'company': company_data
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get company: {str(e)}'}), 500

@profiles_bp.route('/companies/<int:company_id>/research', methods=['POST'])
@jwt_required()
def research_company(company_id):
    """Conduct comprehensive company research"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        company = Company.query.filter_by(
            id=company_id,
            user_id=current_user_id
        ).first()
        
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        # Check user's research limits
        if not user.can_perform_research():
            return jsonify({'error': 'Research limit exceeded for current subscription'}), 429
        
        # Initialize data collectors
        company_collector = CompanyResearchCollector()
        sec_collector = SECDataCollector()
        linkedin_collector = LinkedInDataCollector()
        news_collector = NewsDataCollector()
        
        # Collect data from multiple sources
        research_data = {}
        
        # Basic company research
        company_data = company_collector.collect_company_data(company.name)
        if company_data:
            research_data['company_data'] = company_data
        
        # SEC data (for public companies)
        sec_data = sec_collector.collect_company_data(company.name)
        if sec_data:
            research_data['sec_data'] = sec_data
        
        # LinkedIn data
        linkedin_data = linkedin_collector.collect_company_data(company.name)
        if linkedin_data:
            research_data['linkedin_data'] = linkedin_data
        
        # News data
        news_data = news_collector.collect_company_news(company.name, days_back=30)
        if news_data:
            research_data['news_data'] = news_data
        
        # Analyze data and generate insights
        analyzer = IntelligenceAnalyzer()
        insights = analyzer.analyze_company_data(research_data)
        
        # Create or update company profile
        profile = CompanyProfile.query.filter_by(company_id=company_id).first()
        if not profile:
            profile = CompanyProfile(company_id=company_id)
            db.session.add(profile)
        
        # Update profile with research data
        profile.update_with_research_data(research_data, insights)
        db.session.commit()
        
        # Update user's research usage
        user.increment_research_usage()
        db.session.commit()
        
        # Log research activity
        AuditLog.log_data_access(
            user_id=current_user_id,
            data_sources=list(research_data.keys()),
            access_method='api',
            access_url=f'/api/profiles/companies/{company_id}/research',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            request_method='POST',
            request_url=request.url
        )
        
        return jsonify({
            'message': 'Company research completed successfully',
            'profile': profile.to_dict(),
            'insights': insights
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to research company: {str(e)}'}), 500

@profiles_bp.route('/companies/<int:company_id>/profile', methods=['PUT'])
@jwt_required()
def update_company_profile(company_id):
    """Update company profile manually"""
    try:
        current_user_id = get_jwt_identity()
        
        company = Company.query.filter_by(
            id=company_id,
            user_id=current_user_id
        ).first()
        
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        data = request.get_json()
        
        # Update company basic info
        allowed_company_fields = ['name', 'industry', 'website', 'description']
        for field in allowed_company_fields:
            if field in data:
                setattr(company, field, data[field])
        
        # Update or create profile
        profile = CompanyProfile.query.filter_by(company_id=company_id).first()
        if not profile:
            profile = CompanyProfile(company_id=company_id)
            db.session.add(profile)
        
        # Update profile fields
        allowed_profile_fields = [
            'business_model', 'target_market', 'competitive_advantages',
            'financial_summary', 'key_metrics', 'growth_opportunities',
            'risk_factors', 'management_team'
        ]
        
        for field in allowed_profile_fields:
            if field in data:
                setattr(profile, field, data[field])
        
        db.session.commit()
        
        # Log profile update
        AuditLog.log_data_access(
            user_id=current_user_id,
            data_sources=['profile_update'],
            access_method='api',
            access_url=f'/api/profiles/companies/{company_id}/profile',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            request_method='PUT',
            request_url=request.url
        )
        
        return jsonify({
            'message': 'Company profile updated successfully',
            'company': company.to_dict(),
            'profile': profile.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update company profile: {str(e)}'}), 500

@profiles_bp.route('/companies/<int:company_id>', methods=['DELETE'])
@jwt_required()
def delete_company(company_id):
    """Delete company and associated profile"""
    try:
        current_user_id = get_jwt_identity()
        
        company = Company.query.filter_by(
            id=company_id,
            user_id=current_user_id
        ).first()
        
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        # Delete associated profile
        profile = CompanyProfile.query.filter_by(company_id=company_id).first()
        if profile:
            db.session.delete(profile)
        
        # Delete company
        db.session.delete(company)
        db.session.commit()
        
        # Log deletion
        AuditLog.log_data_access(
            user_id=current_user_id,
            data_sources=['company_deletion'],
            access_method='api',
            access_url=f'/api/profiles/companies/{company_id}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            request_method='DELETE',
            request_url=request.url
        )
        
        return jsonify({
            'message': 'Company deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete company: {str(e)}'}), 500

@profiles_bp.route('/companies/<int:company_id>/export', methods=['GET'])
@jwt_required()
def export_company_profile(company_id):
    """Export company profile as PDF or other format"""
    try:
        current_user_id = get_jwt_identity()
        
        company = Company.query.filter_by(
            id=company_id,
            user_id=current_user_id
        ).first()
        
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        profile = CompanyProfile.query.filter_by(company_id=company_id).first()
        
        # Generate export data
        export_data = {
            'company': company.to_dict(),
            'profile': profile.to_dict() if profile else None,
            'export_date': datetime.utcnow().isoformat(),
            'exported_by': current_user_id
        }
        
        # Log export
        AuditLog.log_data_access(
            user_id=current_user_id,
            data_sources=['profile_export'],
            access_method='api',
            access_url=f'/api/profiles/companies/{company_id}/export',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            request_method='GET',
            request_url=request.url
        )
        
        return jsonify({
            'export_data': export_data,
            'message': 'Profile exported successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to export profile: {str(e)}'}), 500 