from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, IndustryReport, AuditLog
from data_collectors.industry_research import IndustryResearchCollector
from data_collectors.news_data import NewsDataCollector
from analysis.intelligence_analyzer import IntelligenceAnalyzer
from datetime import datetime

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports', methods=['GET'])
@jwt_required()
def get_reports():
    """Get industry reports for current user"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get reports for user's preferred industries
        reports = IndustryReport.query.filter_by(user_id=current_user_id).order_by(
            IndustryReport.created_at.desc()
        ).all()
        
        return jsonify({
            'reports': [report.to_dict() for report in reports]
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get reports: {str(e)}'}), 500

@reports_bp.route('/reports/<int:report_id>', methods=['GET'])
@jwt_required()
def get_report(report_id):
    """Get detailed industry report"""
    try:
        current_user_id = get_jwt_identity()
        
        report = IndustryReport.query.filter_by(
            id=report_id,
            user_id=current_user_id
        ).first()
        
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        return jsonify({
            'report': report.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get report: {str(e)}'}), 500

@reports_bp.route('/reports/generate', methods=['POST'])
@jwt_required()
def generate_report():
    """Generate new industry report"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        industry = data.get('industry')
        
        if not industry:
            return jsonify({'error': 'Industry is required'}), 400
        
        # Check if user can generate reports
        if not user.can_generate_reports():
            return jsonify({'error': 'Report generation limit exceeded for current subscription'}), 429
        
        # Initialize data collectors
        industry_collector = IndustryResearchCollector()
        news_collector = NewsDataCollector()
        
        # Collect industry data
        industry_data = industry_collector.collect_industry_data(industry)
        if not industry_data:
            return jsonify({'error': 'Failed to collect industry data'}), 500
        
        # Collect industry news
        news_data = news_collector.collect_industry_news(industry, days_back=90)
        
        # Get industry trends
        trends = news_collector.get_industry_trends(industry)
        
        # Get industry outlook
        outlook = industry_collector.get_industry_outlook(industry)
        
        # Get competitive analysis
        competitive_analysis = industry_collector.get_competitive_analysis(industry)
        
        # Analyze data and generate insights
        analyzer = IntelligenceAnalyzer()
        insights = analyzer.analyze_industry_data(industry_data, news_data, trends)
        
        # Create industry report
        report = IndustryReport(
            user_id=current_user_id,
            industry=industry,
            market_data=industry_data.get('market_data', {}),
            regulatory_data=industry_data.get('regulatory', {}),
            technology_trends=industry_data.get('technology_trends', {}),
            workforce_data=industry_data.get('workforce', {}),
            financial_benchmarks=industry_data.get('financial_benchmarks', {}),
            news_summary=news_data[:10] if news_data else [],  # Top 10 news items
            key_trends=trends,
            outlook=outlook,
            competitive_analysis=competitive_analysis,
            insights=insights
        )
        
        db.session.add(report)
        db.session.commit()
        
        # Update user's report generation usage
        user.increment_report_usage()
        db.session.commit()
        
        # Log report generation
        AuditLog.log_data_access(
            user_id=current_user_id,
            data_sources=['industry_research', 'news_data'],
            access_method='api',
            access_url='/api/reports/generate',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            request_method='POST',
            request_url=request.url
        )
        
        return jsonify({
            'message': 'Industry report generated successfully',
            'report': report.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to generate report: {str(e)}'}), 500

@reports_bp.route('/reports/<int:report_id>', methods=['DELETE'])
@jwt_required()
def delete_report(report_id):
    """Delete an industry report"""
    try:
        current_user_id = get_jwt_identity()
        
        report = IndustryReport.query.filter_by(
            id=report_id,
            user_id=current_user_id
        ).first()
        
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        db.session.delete(report)
        db.session.commit()
        
        # Log report deletion
        AuditLog.log_data_access(
            user_id=current_user_id,
            data_sources=['report_deletion'],
            access_method='api',
            access_url=f'/api/reports/{report_id}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            request_method='DELETE',
            request_url=request.url
        )
        
        return jsonify({
            'message': 'Report deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete report: {str(e)}'}), 500

@reports_bp.route('/reports/industries', methods=['GET'])
@jwt_required()
def get_available_industries():
    """Get list of available industries for reports"""
    try:
        # This would typically come from a configuration or database
        # For now, return a predefined list
        industries = [
            'Technology',
            'Healthcare',
            'Financial Services',
            'Real Estate',
            'Manufacturing',
            'Retail',
            'Energy',
            'Transportation',
            'Education',
            'Media and Entertainment',
            'Telecommunications',
            'Aerospace and Defense',
            'Biotechnology',
            'Pharmaceuticals',
            'Automotive',
            'Food and Beverage',
            'Construction',
            'Mining and Metals',
            'Chemicals',
            'Textiles and Apparel'
        ]
        
        return jsonify({
            'industries': industries
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get industries: {str(e)}'}), 500

@reports_bp.route('/reports/analytics', methods=['GET'])
@jwt_required()
def get_report_analytics():
    """Get analytics about industry reports"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get all user's reports
        reports = IndustryReport.query.filter_by(user_id=current_user_id).all()
        
        # Calculate analytics
        total_reports = len(reports)
        
        # Group by industry
        industry_distribution = {}
        for report in reports:
            industry = report.industry
            if industry not in industry_distribution:
                industry_distribution[industry] = 0
            industry_distribution[industry] += 1
        
        # Get most recent reports
        recent_reports = reports[:5] if len(reports) >= 5 else reports
        
        analytics = {
            'total_reports': total_reports,
            'industry_distribution': industry_distribution,
            'recent_reports': [report.to_dict() for report in recent_reports],
            'most_researched_industry': max(industry_distribution.items(), key=lambda x: x[1])[0] if industry_distribution else None
        }
        
        return jsonify({
            'analytics': analytics
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get analytics: {str(e)}'}), 500

@reports_bp.route('/reports/compare', methods=['POST'])
@jwt_required()
def compare_industries():
    """Compare multiple industries"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        industries = data.get('industries', [])
        if len(industries) < 2:
            return jsonify({'error': 'At least 2 industries are required for comparison'}), 400
        
        if len(industries) > 5:
            return jsonify({'error': 'Maximum 5 industries can be compared at once'}), 400
        
        # Get existing reports for these industries
        reports = IndustryReport.query.filter(
            IndustryReport.user_id == current_user_id,
            IndustryReport.industry.in_(industries)
        ).all()
        
        # Generate missing reports
        existing_industries = [report.industry for report in reports]
        missing_industries = [ind for ind in industries if ind not in existing_industries]
        
        new_reports = []
        for industry in missing_industries:
            # Generate report for missing industry
            industry_collector = IndustryResearchCollector()
            industry_data = industry_collector.collect_industry_data(industry)
            
            if industry_data:
                report = IndustryReport(
                    user_id=current_user_id,
                    industry=industry,
                    market_data=industry_data.get('market_data', {}),
                    regulatory_data=industry_data.get('regulatory', {}),
                    technology_trends=industry_data.get('technology_trends', {}),
                    workforce_data=industry_data.get('workforce', {}),
                    financial_benchmarks=industry_data.get('financial_benchmarks', {})
                )
                db.session.add(report)
                new_reports.append(report)
        
        db.session.commit()
        
        # Get all reports for comparison
        all_reports = IndustryReport.query.filter(
            IndustryReport.user_id == current_user_id,
            IndustryReport.industry.in_(industries)
        ).all()
        
        # Create comparison data
        comparison_data = {}
        for report in all_reports:
            comparison_data[report.industry] = {
                'market_size': report.market_data.get('market_size', {}),
                'growth_rate': report.market_data.get('market_size', {}).get('growth_rate'),
                'financial_benchmarks': report.financial_benchmarks,
                'technology_trends': report.technology_trends,
                'workforce_data': report.workforce_data
            }
        
        # Log comparison
        AuditLog.log_data_access(
            user_id=current_user_id,
            data_sources=['industry_comparison'],
            access_method='api',
            access_url='/api/reports/compare',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            request_method='POST',
            request_url=request.url
        )
        
        return jsonify({
            'message': 'Industry comparison completed',
            'comparison': comparison_data,
            'reports': [report.to_dict() for report in all_reports]
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to compare industries: {str(e)}'}), 500

@reports_bp.route('/reports/export/<int:report_id>', methods=['GET'])
@jwt_required()
def export_report(report_id):
    """Export industry report as PDF or other format"""
    try:
        current_user_id = get_jwt_identity()
        
        report = IndustryReport.query.filter_by(
            id=report_id,
            user_id=current_user_id
        ).first()
        
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # Generate export data
        export_data = {
            'report': report.to_dict(),
            'export_date': datetime.utcnow().isoformat(),
            'exported_by': current_user_id
        }
        
        # Log export
        AuditLog.log_data_access(
            user_id=current_user_id,
            data_sources=['report_export'],
            access_method='api',
            access_url=f'/api/reports/export/{report_id}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            request_method='GET',
            request_url=request.url
        )
        
        return jsonify({
            'export_data': export_data,
            'message': 'Report exported successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to export report: {str(e)}'}), 500 