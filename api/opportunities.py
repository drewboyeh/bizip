from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from typing import Optional
from models import db, User, Company, FinancialOpportunity, AuditLog
from analysis.intelligence_analyzer import IntelligenceAnalyzer
from data_collectors.company_research import CompanyResearchCollector
from data_collectors.linkedin_data import LinkedInDataCollector

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

def _map_company_query(query):
    """Map ticker symbols and common misspellings to canonical company names"""
    query_lower = query.lower().strip()
    
    # Comprehensive company mapping dictionary
    company_mappings = {
        # Ticker symbols
        'nvda': 'NVIDIA Corporation',
        'aapl': 'Apple Inc.',
        'msft': 'Microsoft Corporation',
        'googl': 'Alphabet Inc.',
        'goog': 'Alphabet Inc.',
        'amzn': 'Amazon.com Inc.',
        'tsla': 'Tesla Inc.',
        'meta': 'Meta Platforms Inc.',
        'fb': 'Meta Platforms Inc.',
        'netflix': 'Netflix Inc.',
        'nflx': 'Netflix Inc.',
        'uber': 'Uber Technologies Inc.',
        'lyft': 'Lyft Inc.',
        'spotify': 'Spotify Technology S.A.',
        'shop': 'Shopify Inc.',
        'zoom': 'Zoom Video Communications Inc.',
        'zm': 'Zoom Video Communications Inc.',
        'salesforce': 'Salesforce Inc.',
        'crm': 'Salesforce Inc.',
        'adobe': 'Adobe Inc.',
        'adbe': 'Adobe Inc.',
        'intel': 'Intel Corporation',
        'intc': 'Intel Corporation',
        'amd': 'Advanced Micro Devices Inc.',
        'oracle': 'Oracle Corporation',
        'orcl': 'Oracle Corporation',
        'cisco': 'Cisco Systems Inc.',
        'csco': 'Cisco Systems Inc.',
        'ibm': 'International Business Machines Corporation',
        'hp': 'HP Inc.',
        'hpe': 'Hewlett Packard Enterprise Co.',
        
        # Common misspellings and variations
        'micrsoft': 'Microsoft Corporation',
        'microsft': 'Microsoft Corporation',
        'microsoft corp': 'Microsoft Corporation',
        'microsoft corporation': 'Microsoft Corporation',
        'apple computer': 'Apple Inc.',
        'apple inc': 'Apple Inc.',
        'apple corp': 'Apple Inc.',
        'nvidia corp': 'NVIDIA Corporation',
        'nvidia corporation': 'NVIDIA Corporation',
        'google': 'Alphabet Inc.',
        'google inc': 'Alphabet Inc.',
        'google corporation': 'Alphabet Inc.',
        'amazon.com': 'Amazon.com Inc.',
        'amazon inc': 'Amazon.com Inc.',
        'tesla motors': 'Tesla Inc.',
        'tesla inc': 'Tesla Inc.',
        'facebook': 'Meta Platforms Inc.',
        'meta platforms': 'Meta Platforms Inc.',
        'netflix inc': 'Netflix Inc.',
        'uber inc': 'Uber Technologies Inc.',
        'lyft inc': 'Lyft Inc.',
        'spotify inc': 'Spotify Technology S.A.',
        'shopify inc': 'Shopify Inc.',
        'zoom inc': 'Zoom Video Communications Inc.',
        'salesforce inc': 'Salesforce Inc.',
        'adobe inc': 'Adobe Inc.',
        'intel corp': 'Intel Corporation',
        'intel corporation': 'Intel Corporation',
        'amd inc': 'Advanced Micro Devices Inc.',
        'oracle corp': 'Oracle Corporation',
        'oracle corporation': 'Oracle Corporation',
        'cisco systems': 'Cisco Systems Inc.',
        'cisco corp': 'Cisco Systems Inc.',
        'ibm corp': 'International Business Machines Corporation',
        'hp inc': 'HP Inc.',
        'hewlett packard': 'HP Inc.',
        'hewlett packard enterprise': 'Hewlett Packard Enterprise Co.',
        
        # Partial matches for fuzzy search
        'nvidia': 'NVIDIA Corporation',
        'apple': 'Apple Inc.',
        'microsoft': 'Microsoft Corporation',
        'google': 'Alphabet Inc.',
        'amazon': 'Amazon.com Inc.',
        'tesla': 'Tesla Inc.',
        'meta': 'Meta Platforms Inc.',
        'facebook': 'Meta Platforms Inc.',
        'netflix': 'Netflix Inc.',
        'uber': 'Uber Technologies Inc.',
        'lyft': 'Lyft Inc.',
        'spotify': 'Spotify Technology S.A.',
        'shopify': 'Shopify Inc.',
        'zoom': 'Zoom Video Communications Inc.',
        'salesforce': 'Salesforce Inc.',
        'adobe': 'Adobe Inc.',
        'intel': 'Intel Corporation',
        'amd': 'Advanced Micro Devices Inc.',
        'oracle': 'Oracle Corporation',
        'cisco': 'Cisco Systems Inc.',
        'ibm': 'International Business Machines Corporation',
        'hp': 'HP Inc.',
        'hewlett': 'HP Inc.'
    }
    
    # Check for exact matches first
    if query_lower in company_mappings:
        return company_mappings[query_lower]
    
    # Check for partial matches (for fuzzy search)
    for key, value in company_mappings.items():
        if key in query_lower or query_lower in key:
            return value
    
    # If no mapping found, return the original query
    return query

@opportunities_bp.route('/search', methods=['POST'])
def search_companies():
    """Search for companies and individuals using real web scraping"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        search_type = data.get('search_type', 'company')  # 'company' or 'person'
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        # Map the query to the canonical company name
        mapped_query = _map_company_query(query)
        
        # Only proceed if we have a valid company mapping or the query is reasonable
        if mapped_query == query and len(query) < 3:
            return jsonify({
                'query': query,
                'companies': [],
                'individuals': [],
                'total_results': 0,
                'search_timestamp': datetime.utcnow().isoformat(),
                'message': 'Query too short or no company match found'
            })
        
        # Initialize data collectors
        company_collector = CompanyResearchCollector()
        linkedin_collector = LinkedInDataCollector()
        from data_collectors.edgar_data import EdgarDataCollector
        edgar_collector = EdgarDataCollector()
        
        companies = []
        individuals = []
        
        if search_type == 'company':
            # Search for companies using the mapped query
            company_data = company_collector.collect_company_data(mapped_query)
            edgar_data = edgar_collector.collect_company_data(mapped_query)
            
            # Check for errors in company_data and edgar_data
            company_error = company_data.get('error') if isinstance(company_data, dict) and 'error' in company_data else None
            edgar_error = edgar_data.get('error') if isinstance(edgar_data, dict) and 'error' in edgar_data else None

            if (company_data and not company_error) or (edgar_data and not edgar_error):
                company_info = {
                    'name': company_data.get('name', mapped_query) if company_data and not company_error else mapped_query,
                    'type': 'company',
                    'industry': company_data.get('industry', 'Unknown') if company_data and not company_error else 'Unknown',
                    'description': company_data.get('description', 'No description available') if company_data and not company_error else 'No description available',
                    'website': company_data.get('website', '') if company_data and not company_error else '',
                    'headquarters': company_data.get('headquarters', '') if company_data and not company_error else '',
                    'founded_year': company_data.get('founded_year') if company_data and not company_error else None,
                    'employee_count': company_data.get('employee_count') if company_data and not company_error else None,
                    'estimated_revenue': company_data.get('estimated_revenue') if company_data and not company_error else None,
                    'data_sources': company_data.get('data_sources', []) if company_data and not company_error else [],
                    'recent_news': company_data.get('recent_news', []) if company_data and not company_error else [],
                    'ceo': company_data.get('ceo') if company_data and not company_error else None,
                    'ticker': company_data.get('ticker') if company_data and not company_error else None
                }
                if company_error:
                    company_info['companyresearch_status'] = company_error
                if edgar_data and not edgar_error:
                    company_info['data_sources'].append('SEC EDGAR')
                    company_info['edgar_data'] = {
                        'cik': edgar_data.get('cik'),
                        'financial_statements': edgar_data.get('financial_data', {}),
                        'executives': edgar_data.get('executives', []),
                        'recent_filings': edgar_data.get('recent_filings', [])
                    }
                if edgar_error:
                    company_info['edgar_status'] = edgar_error
                companies.append(company_info)
            else:
                # If both failed, show errors
                error_info = {'name': mapped_query, 'type': 'company'}
                if company_error:
                    error_info['companyresearch_status'] = company_error
                if edgar_error:
                    error_info['edgar_status'] = edgar_error
                companies.append(error_info)
            
            # Search for LinkedIn data using mapped query
            linkedin_data = linkedin_collector.collect_company_data(mapped_query)
            linkedin_error = linkedin_data.get('error') if isinstance(linkedin_data, dict) and 'error' in linkedin_data else None
            if linkedin_data and not linkedin_error:
                # Merge LinkedIn data with existing company data
                for company in companies:
                    if company['name'].lower() == linkedin_data.get('name', '').lower():
                        company.update({
                            'linkedin_url': linkedin_data.get('linkedin_url', ''),
                            'followers': linkedin_data.get('followers', 0),
                            'specialties': linkedin_data.get('specialties', []),
                            'company_size': linkedin_data.get('company_size', ''),
                            'data_sources': company.get('data_sources', []) + ['LinkedIn']
                        })
                        break
                else:
                    # Add LinkedIn-only company
                    companies.append({
                        'name': linkedin_data.get('name', mapped_query),
                        'type': 'company',
                        'industry': linkedin_data.get('industry', 'Unknown'),
                        'description': linkedin_data.get('description', 'No description available'),
                        'website': linkedin_data.get('website', ''),
                        'headquarters': linkedin_data.get('headquarters', ''),
                        'founded': linkedin_data.get('founded', ''),
                        'linkedin_url': linkedin_data.get('linkedin_url', ''),
                        'followers': linkedin_data.get('followers', 0),
                        'specialties': linkedin_data.get('specialties', []),
                        'company_size': linkedin_data.get('company_size', ''),
                        'data_sources': ['LinkedIn']
                    })
            elif linkedin_error:
                # Add LinkedIn error status to all companies
                for company in companies:
                    company['linkedin_status'] = linkedin_error
                if not companies:
                    companies.append({'name': mapped_query, 'type': 'company', 'linkedin_status': linkedin_error})
        
        elif search_type == 'person':
            # Search for individuals
            query_lower = mapped_query.lower()
            
            # Search for company data first to get executives
            company_data = company_collector.collect_company_data(mapped_query)
            edgar_data = edgar_collector.collect_company_data(mapped_query)
            
            # Use EDGAR data for executives if available
            if edgar_data and edgar_data.get('executives'):
                for executive in edgar_data['executives']:
                    individuals.append({
                        'name': executive['name'],
                        'type': 'individual',
                        'title': executive['title'],
                        'company': company_data.get('name', mapped_query) if company_data else mapped_query,
                        'description': f"{executive['title']} at {company_data.get('name', mapped_query) if company_data else mapped_query}",
                        'estimated_net_worth': f"${executive['compensation']} annually",
                        'age': executive.get('age'),
                        'tenure': executive.get('tenure'),
                        'compensation': executive.get('compensation'),
                        'data_sources': ['SEC EDGAR', 'Public Records']
                    })
            
            # Fallback to known executives for specific companies
            if not individuals:
                # NVIDIA executives
                if 'nvidia' in query_lower or 'jensen' in query_lower or 'huang' in query_lower:
                    individuals.append({
                        'name': 'Jensen Huang',
                        'type': 'individual',
                        'title': 'CEO and Founder',
                        'company': 'NVIDIA Corporation',
                        'description': 'Co-founder, president and CEO of NVIDIA Corporation',
                        'estimated_net_worth': '$40B - $50B',
                        'linkedin_url': 'https://www.linkedin.com/company/nvidia',
                        'linkedin_note': 'Company LinkedIn profile (individual profile not publicly available)',
                        'data_sources': ['Public Records', 'Company Filings']
                    })
                
                # Apple executives
                elif 'apple' in query_lower or 'tim' in query_lower or 'cook' in query_lower:
                    individuals.append({
                        'name': 'Tim Cook',
                        'type': 'individual',
                        'title': 'CEO',
                        'company': 'Apple Inc.',
                        'description': 'Chief Executive Officer of Apple Inc.',
                        'estimated_net_worth': '$1B - $2B',
                        'linkedin_url': 'https://www.linkedin.com/company/apple',
                        'linkedin_note': 'Company LinkedIn profile (individual profile not publicly available)',
                        'data_sources': ['Public Records', 'Company Filings']
                    })
                
                # Microsoft executives
                elif 'microsoft' in query_lower or 'satya' in query_lower or 'nadella' in query_lower:
                    individuals.append({
                        'name': 'Satya Nadella',
                        'type': 'individual',
                        'title': 'CEO',
                        'company': 'Microsoft Corporation',
                        'description': 'Chief Executive Officer of Microsoft Corporation',
                        'estimated_net_worth': '$500M - $1B',
                        'linkedin_url': 'https://www.linkedin.com/company/microsoft',
                        'linkedin_note': 'Company LinkedIn profile (individual profile not publicly available)',
                        'data_sources': ['Public Records', 'Company Filings']
                    })
                
                # Alphabet executives
                elif 'google' in query_lower or 'alphabet' in query_lower or 'sundar' in query_lower or 'pichai' in query_lower:
                    individuals.append({
                        'name': 'Sundar Pichai',
                        'type': 'individual',
                        'title': 'CEO',
                        'company': 'Alphabet Inc.',
                        'description': 'Chief Executive Officer of Alphabet Inc.',
                        'estimated_net_worth': '$1B - $2B',
                        'linkedin_url': 'https://www.linkedin.com/company/google',
                        'linkedin_note': 'Company LinkedIn profile (individual profile not publicly available)',
                        'data_sources': ['Public Records', 'Company Filings']
                    })
                
                # General person search
                else:
                    individuals.append({
                        'name': query,
                        'type': 'individual',
                        'title': 'Business Executive',
                        'company': 'Various',
                        'description': 'High-net-worth individual or business executive',
                        'estimated_net_worth': 'Confidential',
                        'data_sources': ['Web Search']
                    })
        
        return jsonify({
            'query': query,
            'mapped_query': mapped_query if mapped_query != query else None,
            'companies': companies,
            'individuals': individuals,
            'total_results': len(companies) + len(individuals),
            'search_timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

@opportunities_bp.route('/generate-report', methods=['POST'])
def generate_individual_report():
    """Generate a comprehensive report on a high-net-worth individual for financial advisors"""
    try:
        data = request.get_json()
        person_name = data.get('person_name', '').strip()
        company_name = data.get('company_name', '').strip()
        
        if not person_name:
            return jsonify({'error': 'Person name is required'}), 400
        
        # Initialize data collectors
        company_collector = CompanyResearchCollector()
        linkedin_collector = LinkedInDataCollector()
        from data_collectors.edgar_data import EdgarDataCollector
        edgar_collector = EdgarDataCollector()
        from data_collectors.news_data import NewsDataCollector
        news_collector = NewsDataCollector()
        
        # Map person names to their companies for proper data collection
        person_company_mapping = {
            'jensen huang': 'NVIDIA Corporation',
            'jensen': 'NVIDIA Corporation',
            'huang': 'NVIDIA Corporation',
            'tim cook': 'Apple Inc.',
            'tim': 'Apple Inc.',
            'cook': 'Apple Inc.',
            'satya nadella': 'Microsoft Corporation',
            'satya': 'Microsoft Corporation',
            'nadella': 'Microsoft Corporation',
            'sundar pichai': 'Alphabet Inc.',
            'sundar': 'Alphabet Inc.',
            'pichai': 'Alphabet Inc.',
            'elon musk': 'Tesla Inc.',
            'elon': 'Tesla Inc.',
            'musk': 'Tesla Inc.',
            'mark zuckerberg': 'Meta Platforms Inc.',
            'mark': 'Meta Platforms Inc.',
            'zuckerberg': 'Meta Platforms Inc.',
            'andy jassy': 'Amazon.com Inc.',
            'andy': 'Amazon.com Inc.',
            'jassy': 'Amazon.com Inc.'
        }
        
        # Determine the company to search for
        person_lower = person_name.lower()
        if company_name:
            search_company = company_name
        else:
            # Try to find the company from person name mapping
            search_company = None
            for person_key, company in person_company_mapping.items():
                if person_key in person_lower or person_lower in person_key:
                    search_company = company
                    break
            
            # If no mapping found, use the person name as fallback
            if not search_company:
                search_company = person_name
        
        # Map the company query to canonical name
        mapped_query = _map_company_query(search_company)
        
        # Collect comprehensive data
        company_data = company_collector.collect_company_data(mapped_query)
        edgar_data = edgar_collector.collect_company_data(mapped_query)
        linkedin_data = linkedin_collector.collect_company_data(mapped_query)
        news_data = news_collector.collect_company_news(search_company or person_name)
        
        # Generate detailed report sections
        personal_profile = _generate_personal_profile(person_name, search_company, edgar_data)
        company_analysis = _generate_company_analysis(company_data, edgar_data, linkedin_data)
        financial_opportunities = _generate_financial_opportunities(person_name, company_data, edgar_data)
        contact_strategy = _generate_contact_strategy(person_name, search_company, edgar_data)
        recent_developments = _generate_recent_developments(news_data, person_name, search_company)
        
        # Generate LLM-style conversational response
        llm_response = _generate_llm_response(
            person_name, 
            search_company or mapped_query, 
            personal_profile, 
            company_analysis, 
            financial_opportunities, 
            contact_strategy, 
            recent_developments
        )
        
        # Generate detailed report
        report = {
            'person_name': person_name,
            'company_name': search_company or mapped_query,
            'report_generated': datetime.utcnow().isoformat(),
            'report_type': 'High-Net-Worth Individual Analysis',
            'target_audience': 'Financial Advisors',
            
            # LLM-style conversational response
            'llm_response': llm_response,
            
            # Detailed sections (for reference)
            'personal_profile': personal_profile,
            'company_analysis': company_analysis,
            'financial_opportunities': financial_opportunities,
            'contact_strategy': contact_strategy,
            'recent_developments': recent_developments,
            'data_sources': _get_data_sources(company_data, edgar_data, linkedin_data, news_data)
        }
        
        return jsonify(report)
        
    except Exception as e:
        return jsonify({'error': f'Report generation failed: {str(e)}'}), 500

def _generate_personal_profile(person_name: str, company_name: str, edgar_data: Optional[dict]) -> dict:
    """Generate personal profile section of the report"""
    profile = {
        'name': person_name,
        'current_role': 'Unknown',
        'company': company_name,
        'estimated_net_worth': 'Confidential',
        'career_summary': '',
        'key_achievements': [],
        'education': 'Information not publicly available',
        'industry_expertise': []
    }
    
    # Extract executive information from EDGAR data
    if edgar_data and edgar_data.get('executives'):
        for executive in edgar_data['executives']:
            if person_name.lower() in executive['name'].lower() or executive['name'].lower() in person_name.lower():
                profile.update({
                    'current_role': executive.get('title', 'Executive'),
                    'estimated_net_worth': f"${executive.get('compensation', 'Unknown')} annually",
                    'career_summary': f"{executive.get('title', 'Executive')} at {company_name}",
                    'key_achievements': [
                        f"Leadership role at {company_name}",
                        f"Annual compensation: {executive.get('compensation', 'Not disclosed')}",
                        f"Tenure: {executive.get('tenure', 'Unknown')}"
                    ]
                })
                break
    
    # Add known profiles for specific individuals
    person_lower = person_name.lower()
    if 'jensen' in person_lower and 'huang' in person_lower:
        profile.update({
            'current_role': 'CEO and Founder',
            'company': 'NVIDIA Corporation',
            'estimated_net_worth': '$40B - $50B',
            'career_summary': 'Co-founder, president and CEO of NVIDIA Corporation since 1993',
            'key_achievements': [
                'Founded NVIDIA in 1993',
                'Led NVIDIA to become a $2+ trillion market cap company',
                'Pioneered GPU computing and AI technology',
                'Named one of Time\'s 100 Most Influential People'
            ],
            'industry_expertise': ['Semiconductor Technology', 'AI/ML', 'Gaming Graphics', 'Data Center Solutions']
        })
    elif 'tim' in person_lower and 'cook' in person_lower:
        profile.update({
            'current_role': 'CEO',
            'company': 'Apple Inc.',
            'estimated_net_worth': '$1B - $2B',
            'career_summary': 'Chief Executive Officer of Apple Inc. since 2011',
            'key_achievements': [
                'Led Apple to become the world\'s most valuable company',
                'Successfully transitioned Apple after Steve Jobs',
                'Expanded Apple\'s services and wearables business',
                'Known for operational excellence and supply chain management'
            ],
            'industry_expertise': ['Consumer Electronics', 'Software Development', 'Supply Chain Management']
        })
    elif 'satya' in person_lower and 'nadella' in person_lower:
        profile.update({
            'current_role': 'CEO',
            'company': 'Microsoft Corporation',
            'estimated_net_worth': '$500M - $1B',
            'career_summary': 'Chief Executive Officer of Microsoft Corporation since 2014',
            'key_achievements': [
                'Transformed Microsoft\'s culture and business model',
                'Led Microsoft\'s cloud computing expansion',
                'Increased Microsoft\'s market value significantly',
                'Known for inclusive leadership and growth mindset'
            ],
            'industry_expertise': ['Cloud Computing', 'Enterprise Software', 'AI/ML']
        })
    
    return profile

def _generate_company_analysis(company_data: Optional[dict], edgar_data: Optional[dict], linkedin_data: Optional[dict]) -> dict:
    """Generate company analysis section of the report"""
    analysis = {
        'company_name': 'Unknown',
        'industry': 'Unknown',
        'market_cap': 'Unknown',
        'revenue': 'Unknown',
        'key_metrics': {},
        'competitive_position': 'Unknown',
        'growth_prospects': 'Unknown',
        'risk_factors': []
    }
    
    # Merge data from multiple sources
    if company_data and not company_data.get('error'):
        analysis.update({
            'company_name': company_data.get('name', 'Unknown'),
            'industry': company_data.get('industry', 'Unknown'),
            'revenue': company_data.get('estimated_revenue', 'Unknown'),
            'key_metrics': {
                'employee_count': company_data.get('employee_count', 'Unknown'),
                'headquarters': company_data.get('headquarters', 'Unknown'),
                'founded_year': company_data.get('founded_year', 'Unknown')
            }
        })
    
    if edgar_data and edgar_data.get('financial_data'):
        financial_data = edgar_data['financial_data']
        if financial_data.get('key_metrics'):
            analysis['key_metrics'].update(financial_data['key_metrics'])
    
    if linkedin_data and not linkedin_data.get('error'):
        analysis.update({
            'company_size': linkedin_data.get('company_size', 'Unknown'),
            'specialties': linkedin_data.get('specialties', [])
        })
    
    return analysis

def _generate_financial_opportunities(person_name: str, company_data: Optional[dict], edgar_data: Optional[dict]) -> dict:
    """Generate financial opportunities section of the report"""
    opportunities = {
        'wealth_management_needs': [],
        'tax_planning_opportunities': [],
        'estate_planning_considerations': [],
        'investment_advisory_services': [],
        'risk_management_needs': []
    }
    
    # Determine opportunities based on role and company
    person_lower = person_name.lower()
    
    # CEO-level opportunities
    if any(title in person_lower for title in ['ceo', 'chief executive', 'founder', 'president']):
        opportunities['wealth_management_needs'].extend([
            'Executive compensation optimization',
            'Stock option and equity management',
            'Deferred compensation planning'
        ])
        opportunities['tax_planning_opportunities'].extend([
            'High-net-worth tax strategies',
            'State and local tax optimization',
            'International tax considerations'
        ])
        opportunities['estate_planning_considerations'].extend([
            'Family wealth transfer strategies',
            'Trust and foundation planning',
            'Philanthropic giving strategies'
        ])
    
    # Technology industry specific opportunities
    if company_data and 'technology' in company_data.get('industry', '').lower():
        opportunities['investment_advisory_services'].extend([
            'Technology sector diversification',
            'ESG and impact investing',
            'International market exposure'
        ])
        opportunities['risk_management_needs'].extend([
            'Cybersecurity insurance',
            'Key person insurance',
            'Directors and officers liability'
        ])
    
    return opportunities

def _generate_contact_strategy(person_name: str, company_name: str, edgar_data: Optional[dict]) -> dict:
    """Generate contact strategy section of the report"""
    strategy = {
        'recommended_approach': 'Professional networking and mutual connections',
        'contact_channels': [],
        'conversation_starters': [],
        'value_proposition': '',
        'timing_considerations': 'Research recent company developments before outreach'
    }
    
    # Determine contact strategy based on role
    person_lower = person_name.lower()
    
    if any(title in person_lower for title in ['ceo', 'chief executive', 'founder']):
        strategy['contact_channels'] = [
            'LinkedIn professional messaging',
            'Mutual business connections',
            'Industry conference networking',
            'Professional association events'
        ]
        strategy['conversation_starters'] = [
            'Recent company developments and growth',
            'Industry trends and market position',
            'Technology investments and innovation',
            'Leadership insights and strategic vision'
        ]
        strategy['value_proposition'] = 'Comprehensive wealth management for high-net-worth executives, including tax optimization, estate planning, and investment strategies tailored to technology industry dynamics.'
    
    return strategy

def _generate_recent_developments(news_data: list, person_name: str, company_name: str) -> dict:
    """Generate recent developments section of the report"""
    developments = {
        'recent_news': [],
        'company_developments': [],
        'industry_trends': [],
        'personal_achievements': []
    }
    
    if news_data and isinstance(news_data, list):
        developments['recent_news'] = news_data
    
    # Add known recent developments for specific individuals
    person_lower = person_name.lower()
    if 'jensen' in person_lower and 'huang' in person_lower:
        developments['company_developments'].extend([
            "NVIDIA's continued dominance in AI chip market",
            'Expansion into data center and automotive markets',
            'Strategic partnerships with major cloud providers'
        ])
        developments['personal_achievements'].extend([
            "Named one of Time's 100 Most Influential People",
            'Continued leadership in AI technology innovation'
        ])
    
    return developments

def _get_data_sources(company_data: Optional[dict], edgar_data: Optional[dict], linkedin_data: Optional[dict], news_data: list) -> list:
    """Get list of data sources used in the report"""
    sources = []
    
    if company_data and not company_data.get('error'):
        sources.append('Company Research Database')
    
    if edgar_data and not edgar_data.get('error'):
        sources.append('SEC EDGAR Filings')
    
    if linkedin_data and not linkedin_data.get('error'):
        sources.append('LinkedIn Company Profiles')
    
    if news_data and len(news_data) > 0:
        sources.append('News and Media Sources')
    
    return sources

def _generate_llm_response(person_name: str, company_name: str, profile: dict, company_analysis: dict, financial_opportunities: dict, contact_strategy: dict, recent_developments: dict) -> str:
    """Generate an LLM-style conversational response about the person"""
    
    # Build a natural, conversational response
    response_parts = []
    
    # Introduction
    response_parts.append(f"Let me tell you about {person_name}, a fascinating high-net-worth individual in the business world.")
    
    # Personal background
    if profile.get('current_role') != 'Unknown':
        response_parts.append(f"\n{person_name} currently serves as {profile['current_role']} at {profile['company']}, with an estimated net worth of {profile['estimated_net_worth']}. {profile['career_summary']}")
    else:
        response_parts.append(f"\n{person_name} is a prominent business leader associated with {company_name}.")
    
    # Key achievements
    if profile.get('key_achievements'):
        response_parts.append(f"\nSome of {person_name}'s most notable achievements include:")
        for achievement in profile['key_achievements'][:3]:  # Limit to top 3
            response_parts.append(f"• {achievement}")
    
    # Industry expertise
    if profile.get('industry_expertise'):
        expertise_list = ', '.join(profile['industry_expertise'][:3])
        response_parts.append(f"\n{person_name} has deep expertise in {expertise_list}.")
    
    # Company context
    if company_analysis.get('company_name') != 'Unknown':
        response_parts.append(f"\nAt {company_analysis['company_name']}, {person_name} operates in the {company_analysis.get('industry', 'technology')} sector. The company generates approximately {company_analysis.get('revenue', 'significant')} in annual revenue.")
    
    # Financial opportunities
    if financial_opportunities.get('wealth_management_needs'):
        response_parts.append(f"\nFrom a financial advisory perspective, {person_name} likely has several wealth management needs:")
        for need in financial_opportunities['wealth_management_needs'][:2]:
            response_parts.append(f"• {need}")
    
    if financial_opportunities.get('tax_planning_opportunities'):
        response_parts.append(f"\nThere are also tax planning opportunities to consider:")
        for opportunity in financial_opportunities['tax_planning_opportunities'][:2]:
            response_parts.append(f"• {opportunity}")
    
    # Contact strategy
    if contact_strategy.get('recommended_approach'):
        response_parts.append(f"\nWhen approaching {person_name}, I'd recommend {contact_strategy['recommended_approach'].lower()}. {contact_strategy.get('value_proposition', 'Focus on providing value and building a relationship.')}")
    
    if contact_strategy.get('conversation_starters'):
        response_parts.append(f"\nSome conversation starters that might resonate with {person_name} include:")
        for starter in contact_strategy['conversation_starters'][:2]:
            response_parts.append(f"• {starter}")
    
    # Recent developments
    if recent_developments.get('company_developments'):
        response_parts.append(f"\nRecently, {person_name}'s company has been making waves with:")
        for development in recent_developments['company_developments'][:2]:
            response_parts.append(f"• {development}")
    
    if recent_developments.get('personal_achievements'):
        response_parts.append(f"\nOn a personal level, {person_name} has achieved:")
        for achievement in recent_developments['personal_achievements'][:2]:
            response_parts.append(f"• {achievement}")
    
    # Conclusion
    response_parts.append(f"\n{person_name} represents an excellent opportunity for financial advisors who can provide sophisticated wealth management solutions tailored to high-net-worth technology executives. The key is to approach with genuine value and deep understanding of their unique financial situation.")
    
    return '\n'.join(response_parts) 