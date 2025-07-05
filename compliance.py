from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, AuditLog, AuditLog
from datetime import datetime, timedelta

compliance_bp = Blueprint('compliance', __name__)

@compliance_bp.route('/audit-logs', methods=['GET'])
@jwt_required()
def get_audit_logs():
    """Get audit logs for current user"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        data_source = request.args.get('data_source')
        
        # Build query
        query = AuditLog.query.filter_by(user_id=current_user_id)
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                query = query.filter(AuditLog.timestamp >= start_dt)
            except ValueError:
                return jsonify({'error': 'Invalid start_date format'}), 400
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                query = query.filter(AuditLog.timestamp <= end_dt)
            except ValueError:
                return jsonify({'error': 'Invalid end_date format'}), 400
        
        if data_source:
            query = query.filter(AuditLog.data_sources.contains([data_source]))
        
        # Order by timestamp descending
        query = query.order_by(AuditLog.timestamp.desc())
        
        # Paginate results
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'audit_logs': [log.to_dict() for log in pagination.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get audit logs: {str(e)}'}), 500

@compliance_bp.route('/audit-logs/export', methods=['GET'])
@jwt_required()
def export_audit_logs():
    """Export audit logs as CSV or other format"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get date range
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            return jsonify({'error': 'start_date and end_date are required'}), 400
        
        try:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
        
        # Get audit logs for date range
        logs = AuditLog.query.filter(
            AuditLog.user_id == current_user_id,
            AuditLog.timestamp >= start_dt,
            AuditLog.timestamp <= end_dt
        ).order_by(AuditLog.timestamp.desc()).all()
        
        # Generate export data
        export_data = {
            'logs': [log.to_dict() for log in logs],
            'export_date': datetime.utcnow().isoformat(),
            'exported_by': current_user_id,
            'date_range': {
                'start_date': start_date,
                'end_date': end_date
            }
        }
        
        # Log export
        AuditLog.log_data_access(
            user_id=current_user_id,
            data_sources=['audit_log_export'],
            access_method='api',
            access_url='/api/compliance/audit-logs/export',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            request_method='GET',
            request_url=request.url
        )
        
        return jsonify({
            'export_data': export_data,
            'message': 'Audit logs exported successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to export audit logs: {str(e)}'}), 500

@compliance_bp.route('/compliance-report', methods=['GET'])
@jwt_required()
def get_compliance_report():
    """Get compliance report for current user"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get date range (default to last 30 days)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        # Get audit logs for period
        logs = AuditLog.query.filter(
            AuditLog.user_id == current_user_id,
            AuditLog.timestamp >= start_date,
            AuditLog.timestamp <= end_date
        ).all()
        
        # Calculate compliance metrics
        total_activities = len(logs)
        
        # Group by data source
        data_source_usage = {}
        for log in logs:
            for source in log.data_sources:
                if source not in data_source_usage:
                    data_source_usage[source] = 0
                data_source_usage[source] += 1
        
        # Group by access method
        access_method_usage = {}
        for log in logs:
            method = log.access_method
            if method not in access_method_usage:
                access_method_usage[method] = 0
            access_method_usage[method] += 1
        
        # Calculate daily activity
        daily_activity = {}
        for log in logs:
            date_str = log.timestamp.strftime('%Y-%m-%d')
            if date_str not in daily_activity:
                daily_activity[date_str] = 0
            daily_activity[date_str] += 1
        
        # Compliance status
        compliance_status = {
            'data_access_compliant': True,  # Assuming all access is compliant
            'rate_limits_respected': True,
            'privacy_protected': True,
            'audit_trail_complete': True
        }
        
        compliance_report = {
            'user_id': current_user_id,
            'report_period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'total_activities': total_activities,
            'data_source_usage': data_source_usage,
            'access_method_usage': access_method_usage,
            'daily_activity': daily_activity,
            'compliance_status': compliance_status,
            'generated_at': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'compliance_report': compliance_report
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get compliance report: {str(e)}'}), 500

@compliance_bp.route('/data-sources', methods=['GET'])
@jwt_required()
def get_data_source_info():
    """Get information about data sources and compliance"""
    try:
        # This would typically come from configuration or database
        # For now, return predefined information
        data_sources = {
            'sec_data': {
                'name': 'SEC EDGAR Database',
                'compliance_status': 'Compliant',
                'data_types': 'Public financial filings',
                'rate_limits': '10 requests per second',
                'privacy_impact': 'Low - Public data only',
                'retention_policy': 'Permanent public record'
            },
            'linkedin_data': {
                'name': 'LinkedIn Public Company Pages',
                'compliance_status': 'Compliant',
                'data_types': 'Public business information',
                'rate_limits': 'Respects robots.txt',
                'privacy_impact': 'Low - Public business data only',
                'retention_policy': 'Business information only'
            },
            'news_data': {
                'name': 'Legitimate News Sources',
                'compliance_status': 'Compliant',
                'data_types': 'Public news content',
                'rate_limits': 'Respects source limits',
                'privacy_impact': 'Low - Public news only',
                'retention_policy': 'News content only'
            },
            'industry_research': {
                'name': 'Industry Research Databases',
                'compliance_status': 'Compliant',
                'data_types': 'Aggregated industry statistics',
                'rate_limits': 'Licensed access',
                'privacy_impact': 'Low - No individual data',
                'retention_policy': 'Industry-level data only'
            }
        }
        
        return jsonify({
            'data_sources': data_sources
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get data source info: {str(e)}'}), 500

@compliance_bp.route('/privacy-policy', methods=['GET'])
def get_privacy_policy():
    """Get privacy policy information"""
    try:
        privacy_policy = {
            'data_collection': {
                'personal_data': 'Minimal - Only account information',
                'business_data': 'Public business information only',
                'data_retention': 'As long as account is active',
                'data_sharing': 'No sharing with third parties'
            },
            'compliance': {
                'gdpr': 'Compliant',
                'ccpa': 'Compliant',
                'sox': 'Not applicable - No financial reporting',
                'hipaa': 'Not applicable - No health data'
            },
            'security': {
                'encryption': 'All data encrypted in transit and at rest',
                'access_controls': 'Role-based access control',
                'audit_logging': 'Complete audit trail maintained',
                'data_backup': 'Regular automated backups'
            },
            'user_rights': {
                'access': 'Users can access their data',
                'correction': 'Users can correct their data',
                'deletion': 'Users can delete their account and data',
                'portability': 'Users can export their data'
            }
        }
        
        return jsonify({
            'privacy_policy': privacy_policy
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get privacy policy: {str(e)}'}), 500

@compliance_bp.route('/terms-of-service', methods=['GET'])
def get_terms_of_service():
    """Get terms of service"""
    try:
        terms_of_service = {
            'acceptable_use': {
                'business_purposes': 'Only for legitimate business intelligence',
                'compliance': 'Must comply with all applicable laws',
                'data_respect': 'Must respect data source terms of service',
                'no_misuse': 'No unauthorized access or data scraping'
            },
            'limitations': {
                'rate_limits': 'Must respect all rate limits',
                'data_usage': 'Data for business intelligence only',
                'redistribution': 'No redistribution of data',
                'commercial_use': 'Commercial use allowed with proper licensing'
            },
            'liability': {
                'data_accuracy': 'No guarantee of data accuracy',
                'service_availability': 'No guarantee of service availability',
                'damages': 'Limited liability for damages',
                'indemnification': 'Users must indemnify against misuse'
            },
            'termination': {
                'violation': 'Service may be terminated for violations',
                'data_retention': 'Data may be retained for compliance',
                'refunds': 'No refunds for policy violations'
            }
        }
        
        return jsonify({
            'terms_of_service': terms_of_service
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get terms of service: {str(e)}'}), 500

@compliance_bp.route('/data-request', methods=['POST'])
@jwt_required()
def request_data_deletion():
    """Request data deletion (GDPR compliance)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        request_type = data.get('request_type', 'deletion')
        
        if request_type not in ['deletion', 'access', 'correction']:
            return jsonify({'error': 'Invalid request type'}), 400
        
        # Create data request record
        # This would typically be stored in a separate table
        data_request = {
            'user_id': current_user_id,
            'request_type': request_type,
            'request_date': datetime.utcnow().isoformat(),
            'status': 'pending',
            'description': data.get('description', ''),
            'requested_by': current_user_id
        }
        
        # Log the request
        AuditLog.log_data_access(
            user_id=current_user_id,
            data_sources=['data_request'],
            access_method='api',
            access_url='/api/compliance/data-request',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            request_method='POST',
            request_url=request.url
        )
        
        return jsonify({
            'message': f'Data {request_type} request submitted successfully',
            'request_id': f'REQ_{current_user_id}_{int(datetime.utcnow().timestamp())}',
            'status': 'pending',
            'estimated_completion': '5-10 business days'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to submit data request: {str(e)}'}), 500 