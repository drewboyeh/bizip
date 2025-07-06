from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from config import config
from models import db, User, Company, BusinessProfile, FinancialOpportunity, ConversationStarter, IndustryReport, AuditLog, Subscription
from data_collectors.company_research import CompanyResearchCollector
from analysis.intelligence_analyzer import IntelligenceAnalyzer
from api.auth import auth_bp
from api.profiles import profiles_bp
from api.opportunities import opportunities_bp
from api.reports import reports_bp
from api.compliance import compliance_bp
import os

def create_app(config_name='development'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    JWTManager(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(profiles_bp, url_prefix='/api/profiles')
    app.register_blueprint(opportunities_bp, url_prefix='/api/opportunities')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    app.register_blueprint(compliance_bp, url_prefix='/api/compliance')
    
    # Initialize database
    with app.app_context():
        db.create_all()
    
    @app.route('/api/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'version': '1.0.0',
            'environment': config_name
        })
    
    @app.route('/api/dashboard/stats', methods=['GET'])
    @jwt_required()
    def get_dashboard_stats():
        """Get dashboard statistics for authenticated user"""
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's business profiles
        profiles = BusinessProfile.query.filter_by(user_id=current_user_id).all()
        
        # Get opportunities
        opportunities = FinancialOpportunity.query.filter_by(user_id=current_user_id).all()
        
        # Get conversation starters
        conversation_starters = ConversationStarter.query.filter_by(user_id=current_user_id).all()
        
        # Calculate statistics
        stats = {
            'total_profiles': len(profiles),
            'active_profiles': len([p for p in profiles if p.status == 'active']),
            'total_opportunities': len(opportunities),
            'high_priority_opportunities': len([o for o in opportunities if o.priority in ['high', 'critical']]),
            'total_conversation_starters': len(conversation_starters),
            'recent_conversation_starters': len([c for c in conversation_starters if c.is_relevant()]),
            'subscription_info': user.get_subscription_info(),
            'usage_percentage': {
                'profiles': (user.profiles_used_this_month / user.get_subscription_info()['max_profiles'] * 100) if user.get_subscription_info()['max_profiles'] > 0 else 0
            }
        }
        
        return jsonify(stats)
    
    @app.route('/api/company/research', methods=['POST'])
    @jwt_required()
    def research_company():
        """Research a company and create business profile"""
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if user can create profile
        if not user.can_create_profile():
            return jsonify({'error': 'Profile limit reached for current subscription tier'}), 403
        
        data = request.get_json()
        company_name = data.get('company_name')
        
        if not company_name:
            return jsonify({'error': 'Company name is required'}), 400
        
        try:
            # Initialize collectors
            collector = CompanyResearchCollector()
            analyzer = IntelligenceAnalyzer()
            
            # Collect company data
            company_data = collector.collect_company_data(company_name)
            
            if not company_data:
                return jsonify({'error': 'Company not found or data unavailable'}), 404
            
            # Create or update company record
            company = Company.query.filter_by(name=company_name).first()
            if not company:
                company = Company(**company_data)
                db.session.add(company)
                db.session.commit()
            
            # Analyze company for financial planning opportunities
            analysis_result = analyzer.analyze_company(company_data)
            
            # Create business profile
            profile = BusinessProfile(
                user_id=current_user_id,
                company_id=company.id,
                profile_name=f"{company_name} - Business Profile",
                profile_type='prospect',
                primary_planning_needs=analysis_result.get('planning_needs', []),
                opportunities_identified=analysis_result.get('opportunities', []),
                conversation_starters=analysis_result.get('conversation_starters', []),
                recent_developments=analysis_result.get('recent_developments', [])
            )
            
            db.session.add(profile)
            
            # Increment user's profile usage
            user.increment_profile_usage()
            
            # Log the activity
            AuditLog.log_profile_creation(
                user_id=current_user_id,
                company_name=company_name,
                data_sources_used=company_data.get('data_sources', []),
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            db.session.commit()
            
            return jsonify({
                'message': 'Company profile created successfully',
                'profile_id': profile.id,
                'company_id': company.id,
                'analysis_summary': analysis_result.get('summary', {})
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Error creating profile: {str(e)}'}), 500
    
    @app.route('/api/industry/report/<industry>', methods=['GET'])
    @jwt_required()
    def get_industry_report(industry):
        """Get industry report for specified industry"""
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if user can access industry reports
        subscription = Subscription.query.filter_by(user_id=current_user_id).first()
        if not subscription or not subscription.can_generate_report():
            return jsonify({'error': 'Report limit reached for current subscription tier'}), 403
        
        try:
            # Get or create industry report
            report = IndustryReport.query.filter_by(industry=industry).first()
            
            if not report:
                # Generate new industry report
                from data_collectors.industry_research import IndustryResearchCollector
                from analysis.industry_analyzer import IndustryAnalyzer
                
                collector = IndustryResearchCollector()
                analyzer = IndustryAnalyzer()
                
                industry_data = collector.collect_industry_data(industry)
                if industry_data:
                    analysis_result = analyzer.analyze_industry(industry_data)
                    
                    report = IndustryReport(
                        industry=industry,
                        report_type='quarterly',
                        title=f"{industry} Industry Analysis",
                        summary=analysis_result.get('summary'),
                        key_findings=analysis_result.get('key_findings'),
                        market_trends=analysis_result.get('market_trends'),
                        planning_opportunities=analysis_result.get('planning_opportunities'),
                        risk_factors=analysis_result.get('risk_factors'),
                        data_sources=industry_data.get('sources', [])
                    )
                    
                    db.session.add(report)
            
            # Increment report usage
            subscription.increment_report_usage()
            
            # Log the activity
            AuditLog.log_report_generation(
                user_id=current_user_id,
                report_type='industry',
                industry=industry,
                data_sources_used=report.data_sources or []
            )
            
            db.session.commit()
            
            return jsonify(report.to_dict())
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Error generating report: {str(e)}'}), 500
    
    @app.route('/api/search/individuals', methods=['POST'])
    def search_high_net_worth_individuals():
        """Search for high-net-worth individuals and their business details"""
        data = request.get_json()
        search_query = data.get('search_query', '')
        search_type = data.get('search_type', 'company')  # 'company', 'industry', 'location'
        
        if not search_query:
            return jsonify({'error': 'Search query is required'}), 400
        
        try:
            # Mock data for demonstration (in production, this would use real data collectors)
            results = []
            
            if search_type == 'company':
                # Mock company executives
                executives = [
                    {
                        'name': 'John Smith',
                        'title': 'Chief Executive Officer',
                        'company': search_query,
                        'linkedin_url': 'https://linkedin.com/in/johnsmith',
                        'estimated_net_worth': '$50M - $100M'
                    },
                    {
                        'name': 'Jane Doe',
                        'title': 'Chief Financial Officer',
                        'company': search_query,
                        'linkedin_url': 'https://linkedin.com/in/janedoe',
                        'estimated_net_worth': '$20M - $50M'
                    },
                    {
                        'name': 'Mike Johnson',
                        'title': 'Chief Technology Officer',
                        'company': search_query,
                        'linkedin_url': 'https://linkedin.com/in/mikejohnson',
                        'estimated_net_worth': '$10M - $30M'
                    }
                ]
                
                for executive in executives:
                    results.append({
                        'name': executive['name'],
                        'title': executive['title'],
                        'company': search_query,
                        'linkedin_url': executive['linkedin_url'],
                        'estimated_net_worth': executive['estimated_net_worth'],
                        'company_info': {
                            'industry': 'Technology',
                            'revenue': '$500M - $1B',
                            'employees': '500-1000'
                        },
                        'recent_news': [
                            {
                                'title': f'{search_query} Announces New Product Launch',
                                'date': '2024-01-15',
                                'source': 'TechCrunch'
                            },
                            {
                                'title': f'{search_query} Reports Strong Q4 Earnings',
                                'date': '2024-01-10',
                                'source': 'Bloomberg'
                            }
                        ],
                        'financial_opportunities': [
                            'Business Succession Planning',
                            'Tax Optimization',
                            'Employee Benefit Plans'
                        ],
                        'conversation_starters': [
                            'Recent company expansion plans',
                            'Industry trends and market position',
                            'Technology investments and innovation'
                        ],
                        'planning_needs': [
                            'Estate Planning',
                            'Retirement Planning',
                            'Risk Management'
                        ]
                    })
            
            elif search_type == 'industry':
                # Mock industry leaders
                industry_leaders = [
                    {
                        'name': 'Sarah Wilson',
                        'title': 'CEO',
                        'company': f'Leading {search_query} Company',
                        'linkedin_url': 'https://linkedin.com/in/sarahwilson',
                        'estimated_net_worth': '$100M - $200M'
                    },
                    {
                        'name': 'David Brown',
                        'title': 'CFO',
                        'company': f'Top {search_query} Firm',
                        'linkedin_url': 'https://linkedin.com/in/davidbrown',
                        'estimated_net_worth': '$30M - $80M'
                    }
                ]
                
                for leader in industry_leaders:
                    results.append({
                        'name': leader['name'],
                        'title': leader['title'],
                        'company': leader['company'],
                        'industry': search_query,
                        'linkedin_url': leader['linkedin_url'],
                        'estimated_net_worth': leader['estimated_net_worth'],
                        'recent_news': [
                            {
                                'title': f'{search_query} Industry Growth Trends',
                                'date': '2024-01-12',
                                'source': 'Industry Report'
                            }
                        ],
                        'financial_opportunities': [
                            'Industry Consolidation Opportunities',
                            'Market Expansion Planning',
                            'Strategic Partnerships'
                        ],
                        'conversation_starters': [
                            'Industry growth projections',
                            'Market competition analysis',
                            'Regulatory changes impact'
                        ],
                        'planning_needs': [
                            'Strategic Planning',
                            'Investment Planning',
                            'Risk Management'
                        ]
                    })
            
            return jsonify({
                'success': True,
                'search_query': search_query,
                'search_type': search_type,
                'results_count': len(results),
                'results': results
            })
            
        except Exception as e:
            return jsonify({'error': f'Search failed: {str(e)}'}), 500
    
    @app.route('/api/search/companies', methods=['POST'])
    def search_companies():
        """Search for companies and their key executives"""
        data = request.get_json()
        search_query = data.get('search_query', '')
        
        if not search_query:
            return jsonify({'error': 'Search query is required'}), 400
        
        try:
            # Mock data for demonstration
            results = [{
                'company_name': search_query,
                'industry': 'Technology',
                'revenue': '$500M - $1B',
                'employees': '500-1000',
                'executives': [
                    {
                        'name': 'John Smith',
                        'title': 'Chief Executive Officer',
                        'linkedin_url': 'https://linkedin.com/in/johnsmith'
                    },
                    {
                        'name': 'Jane Doe',
                        'title': 'Chief Financial Officer',
                        'linkedin_url': 'https://linkedin.com/in/janedoe'
                    },
                    {
                        'name': 'Mike Johnson',
                        'title': 'Chief Technology Officer',
                        'linkedin_url': 'https://linkedin.com/in/mikejohnson'
                    }
                ],
                'financial_opportunities': [
                    'Business Succession Planning',
                    'Tax Optimization',
                    'Employee Benefit Plans'
                ],
                'conversation_starters': [
                    'Recent company expansion plans',
                    'Industry trends and market position',
                    'Technology investments and innovation'
                ],
                'planning_needs': [
                    'Estate Planning',
                    'Retirement Planning',
                    'Risk Management'
                ]
            }]
            
            return jsonify({
                'success': True,
                'search_query': search_query,
                'results_count': len(results),
                'results': results
            })
            
        except Exception as e:
            return jsonify({'error': f'Search failed: {str(e)}'}), 500
    
    @app.route('/api/summary')
    def summary():
        # Replace these with real data as needed
        return jsonify({
            "active_users": 1200,
            "opportunities": 34,
            "compliance_alerts": 2
        })
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app(os.environ.get('FLASK_ENV', 'development'))
    app.run(debug=True, host='0.0.0.0', port=5000) 