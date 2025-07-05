from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Company, FinancialOpportunity, AuditLog
from analysis.intelligence_analyzer import IntelligenceAnalyzer

opportunities_bp = Blueprint('opportunities', __name__)

@opportunities_bp.route('/opportunities', methods=['GET'])
@jwt_required()
def get_opportunities():
    """Get financial planning opportunities for current user"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get opportunities for user's companies
        companies = Company.query.filter_by(user_id=current_user_id).all()
        company_ids = [company.id for company in companies]
        
        opportunities = FinancialOpportunity.query.filter(
            FinancialOpportunity.company_id.in_(company_ids)
        ).order_by(FinancialOpportunity.created_at.desc()).all()
        
        return jsonify({
            'opportunities': [opp.to_dict() for opp in opportunities]
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get opportunities: {str(e)}'}), 500

@opportunities_bp.route('/opportunities/<int:company_id>', methods=['GET'])
@jwt_required()
def get_company_opportunities(company_id):
    """Get opportunities for a specific company"""
    try:
        current_user_id = get_jwt_identity()
        
        # Verify company belongs to user
        company = Company.query.filter_by(
            id=company_id,
            user_id=current_user_id
        ).first()
        
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        opportunities = FinancialOpportunity.query.filter_by(
            company_id=company_id
        ).order_by(FinancialOpportunity.priority.desc(), FinancialOpportunity.created_at.desc()).all()
        
        return jsonify({
            'opportunities': [opp.to_dict() for opp in opportunities]
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get company opportunities: {str(e)}'}), 500

@opportunities_bp.route('/opportunities/generate/<int:company_id>', methods=['POST'])
@jwt_required()
def generate_opportunities(company_id):
    """Generate new financial planning opportunities for a company"""
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
        
        # Check if user can generate opportunities
        if not user.can_generate_opportunities():
            return jsonify({'error': 'Opportunity generation limit exceeded for current subscription'}), 429
        
        # Get company profile data
        from models import CompanyProfile
        profile = CompanyProfile.query.filter_by(company_id=company_id).first()
        
        if not profile:
            return jsonify({'error': 'Company profile not found. Please research the company first.'}), 400
        
        # Generate opportunities using AI analyzer
        analyzer = IntelligenceAnalyzer()
        opportunities_data = analyzer.identify_financial_opportunities(profile.to_dict())
        
        # Create opportunity records
        new_opportunities = []
        for opp_data in opportunities_data:
            opportunity = FinancialOpportunity(
                company_id=company_id,
                opportunity_type=opp_data['type'],
                title=opp_data['title'],
                description=opp_data['description'],
                priority=opp_data['priority'],
                estimated_value=opp_data.get('estimated_value'),
                implementation_timeline=opp_data.get('timeline'),
                risk_level=opp_data.get('risk_level', 'medium'),
                required_resources=opp_data.get('required_resources', []),
                success_metrics=opp_data.get('success_metrics', [])
            )
            
            db.session.add(opportunity)
            new_opportunities.append(opportunity)
        
        db.session.commit()
        
        # Update user's opportunity generation usage
        user.increment_opportunity_usage()
        db.session.commit()
        
        # Log opportunity generation
        AuditLog.log_data_access(
            user_id=current_user_id,
            data_sources=['opportunity_generation'],
            access_method='api',
            access_url=f'/api/opportunities/generate/{company_id}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            request_method='POST',
            request_url=request.url
        )
        
        return jsonify({
            'message': f'Generated {len(new_opportunities)} opportunities successfully',
            'opportunities': [opp.to_dict() for opp in new_opportunities]
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to generate opportunities: {str(e)}'}), 500

@opportunities_bp.route('/opportunities/<int:opportunity_id>', methods=['GET'])
@jwt_required()
def get_opportunity(opportunity_id):
    """Get detailed information about a specific opportunity"""
    try:
        current_user_id = get_jwt_identity()
        
        opportunity = FinancialOpportunity.query.get(opportunity_id)
        
        if not opportunity:
            return jsonify({'error': 'Opportunity not found'}), 404
        
        # Verify user owns the company
        company = Company.query.filter_by(
            id=opportunity.company_id,
            user_id=current_user_id
        ).first()
        
        if not company:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({
            'opportunity': opportunity.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get opportunity: {str(e)}'}), 500

@opportunities_bp.route('/opportunities/<int:opportunity_id>', methods=['PUT'])
@jwt_required()
def update_opportunity(opportunity_id):
    """Update opportunity details"""
    try:
        current_user_id = get_jwt_identity()
        
        opportunity = FinancialOpportunity.query.get(opportunity_id)
        
        if not opportunity:
            return jsonify({'error': 'Opportunity not found'}), 404
        
        # Verify user owns the company
        company = Company.query.filter_by(
            id=opportunity.company_id,
            user_id=current_user_id
        ).first()
        
        if not company:
            return jsonify({'error': 'Access denied'}), 403
        
        data = request.get_json()
        
        # Update allowed fields
        allowed_fields = [
            'title', 'description', 'priority', 'estimated_value',
            'implementation_timeline', 'risk_level', 'required_resources',
            'success_metrics', 'status', 'notes'
        ]
        
        for field in allowed_fields:
            if field in data:
                setattr(opportunity, field, data[field])
        
        db.session.commit()
        
        # Log opportunity update
        AuditLog.log_data_access(
            user_id=current_user_id,
            data_sources=['opportunity_update'],
            access_method='api',
            access_url=f'/api/opportunities/{opportunity_id}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            request_method='PUT',
            request_url=request.url
        )
        
        return jsonify({
            'message': 'Opportunity updated successfully',
            'opportunity': opportunity.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update opportunity: {str(e)}'}), 500

@opportunities_bp.route('/opportunities/<int:opportunity_id>', methods=['DELETE'])
@jwt_required()
def delete_opportunity(opportunity_id):
    """Delete an opportunity"""
    try:
        current_user_id = get_jwt_identity()
        
        opportunity = FinancialOpportunity.query.get(opportunity_id)
        
        if not opportunity:
            return jsonify({'error': 'Opportunity not found'}), 404
        
        # Verify user owns the company
        company = Company.query.filter_by(
            id=opportunity.company_id,
            user_id=current_user_id
        ).first()
        
        if not company:
            return jsonify({'error': 'Access denied'}), 403
        
        db.session.delete(opportunity)
        db.session.commit()
        
        # Log opportunity deletion
        AuditLog.log_data_access(
            user_id=current_user_id,
            data_sources=['opportunity_deletion'],
            access_method='api',
            access_url=f'/api/opportunities/{opportunity_id}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            request_method='DELETE',
            request_url=request.url
        )
        
        return jsonify({
            'message': 'Opportunity deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete opportunity: {str(e)}'}), 500

@opportunities_bp.route('/opportunities/prioritize', methods=['POST'])
@jwt_required()
def prioritize_opportunities():
    """Prioritize opportunities based on business impact and feasibility"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        company_id = data.get('company_id')
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        # Verify company belongs to user
        company = Company.query.filter_by(
            id=company_id,
            user_id=current_user_id
        ).first()
        
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        # Get opportunities for the company
        opportunities = FinancialOpportunity.query.filter_by(
            company_id=company_id
        ).all()
        
        if not opportunities:
            return jsonify({'error': 'No opportunities found for this company'}), 404
        
        # Use AI analyzer to prioritize opportunities
        analyzer = IntelligenceAnalyzer()
        prioritized_opportunities = analyzer.prioritize_opportunities(
            [opp.to_dict() for opp in opportunities]
        )
        
        # Update opportunity priorities
        for opp_data in prioritized_opportunities:
            opportunity = FinancialOpportunity.query.get(opp_data['id'])
            if opportunity:
                opportunity.priority = opp_data['priority']
                opportunity.priority_reason = opp_data.get('priority_reason')
        
        db.session.commit()
        
        # Log prioritization
        AuditLog.log_data_access(
            user_id=current_user_id,
            data_sources=['opportunity_prioritization'],
            access_method='api',
            access_url='/api/opportunities/prioritize',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            request_method='POST',
            request_url=request.url
        )
        
        return jsonify({
            'message': 'Opportunities prioritized successfully',
            'opportunities': [opp.to_dict() for opp in opportunities]
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to prioritize opportunities: {str(e)}'}), 500

@opportunities_bp.route('/opportunities/analytics', methods=['GET'])
@jwt_required()
def get_opportunity_analytics():
    """Get analytics and insights about opportunities"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get all user's companies
        companies = Company.query.filter_by(user_id=current_user_id).all()
        company_ids = [company.id for company in companies]
        
        # Get all opportunities
        opportunities = FinancialOpportunity.query.filter(
            FinancialOpportunity.company_id.in_(company_ids)
        ).all()
        
        # Calculate analytics
        total_opportunities = len(opportunities)
        high_priority = len([opp for opp in opportunities if opp.priority == 'high'])
        medium_priority = len([opp for opp in opportunities if opp.priority == 'medium'])
        low_priority = len([opp for opp in opportunities if opp.priority == 'low'])
        
        # Calculate total estimated value
        total_value = sum(opp.estimated_value or 0 for opp in opportunities)
        
        # Group by opportunity type
        type_distribution = {}
        for opp in opportunities:
            opp_type = opp.opportunity_type
            if opp_type not in type_distribution:
                type_distribution[opp_type] = 0
            type_distribution[opp_type] += 1
        
        analytics = {
            'total_opportunities': total_opportunities,
            'priority_distribution': {
                'high': high_priority,
                'medium': medium_priority,
                'low': low_priority
            },
            'total_estimated_value': total_value,
            'type_distribution': type_distribution,
            'average_value_per_opportunity': total_value / total_opportunities if total_opportunities > 0 else 0
        }
        
        return jsonify({
            'analytics': analytics
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get analytics: {str(e)}'}), 500 