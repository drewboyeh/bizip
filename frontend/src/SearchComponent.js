import React, { useState } from 'react';
import './SearchComponent.css';
import FinancialStatements from './FinancialStatements';

const SearchComponent = () => {
  const [companyQuery, setCompanyQuery] = useState('');
  const [personQuery, setPersonQuery] = useState('');
  const [companyResults, setCompanyResults] = useState([]);
  const [personResults, setPersonResults] = useState([]);
  const [companyLoading, setCompanyLoading] = useState(false);
  const [personLoading, setPersonLoading] = useState(false);
  const [companyError, setCompanyError] = useState('');
  const [personError, setPersonError] = useState('');
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [showFinancialStatements, setShowFinancialStatements] = useState(false);
  const [expandedCompanyIndex, setExpandedCompanyIndex] = useState(null);
  
  // Report generation state
  const [reportData, setReportData] = useState(null);
  const [reportLoading, setReportLoading] = useState(false);
  const [reportError, setReportError] = useState('');
  const [showReport, setShowReport] = useState(false);

  const handleCompanySearch = async () => {
    if (!companyQuery.trim()) {
      setCompanyError('Please enter a company name');
      return;
    }

    setCompanyLoading(true);
    setCompanyError('');

    try {
      const url = 'http://127.0.0.1:5000/api/opportunities/search';
      const body = {
        query: companyQuery,
        search_type: 'company'
      };

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body)
      });

      const data = await response.json();

      if (response.ok) {
        const transformedResults = [];
        
        if (data.companies && data.companies.length > 0) {
          data.companies.forEach(company => {
            transformedResults.push({
              name: company.name,
              title: 'Company',
              company: company.name,
              estimated_net_worth: 'Company Data Available',
              linkedin_url: company.linkedin_url || '#',
              company_info: {
                industry: company.industry || 'Unknown',
                revenue: company.estimated_revenue || 'Unknown',
                employees: company.employee_count || 'Unknown'
              },
              financial_opportunities: [
                'Business Succession Planning',
                'Tax Optimization',
                'Employee Benefit Plans'
              ],
              conversation_starters: [
                'Recent company developments',
                'Industry trends and market position',
                'Technology investments and innovation'
              ],
              planning_needs: [
                'Estate Planning',
                'Retirement Planning',
                'Risk Management'
              ],
              recent_news: company.recent_news || [],
              data_sources: company.data_sources || [],
              edgar_data: company.edgar_data || null,
              edgar_status: company.edgar_status || null,
              linkedin_status: company.linkedin_status || null,
              companyresearch_status: company.companyresearch_status || null,
              ceo_name: company.ceo || null,
              ticker: company.ticker || null
            });
          });
        }
        
        setCompanyResults(transformedResults);
      } else {
        setCompanyError(data.error || 'Company search failed');
      }
    } catch (err) {
      setCompanyError('Failed to connect to server. Make sure the backend is running.');
    } finally {
      setCompanyLoading(false);
    }
  };

  const handlePersonSearch = async () => {
    if (!personQuery.trim()) {
      setPersonError('Please enter a person name');
      return;
    }

    setPersonLoading(true);
    setPersonError('');

    try {
      const url = 'http://127.0.0.1:5000/api/opportunities/search';
      const body = {
        query: personQuery,
        search_type: 'person'
      };

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body)
      });

      const data = await response.json();

      if (response.ok) {
        const transformedResults = [];
        
        if (data.individuals && data.individuals.length > 0) {
          data.individuals.forEach(individual => {
            transformedResults.push({
              name: individual.name,
              title: individual.title || 'Business Executive',
              company: individual.company || 'Various',
              estimated_net_worth: individual.estimated_net_worth || 'Confidential',
              linkedin_url: individual.linkedin_url || '#',
              company_info: {
                industry: 'Technology',
                revenue: 'Confidential',
                employees: 'N/A'
              },
              financial_opportunities: [
                'Personal Wealth Management',
                'Tax Planning',
                'Investment Advisory'
              ],
              conversation_starters: [
                'Recent business developments',
                'Industry leadership insights',
                'Strategic planning opportunities'
              ],
              planning_needs: [
                'Estate Planning',
                'Retirement Planning',
                'Risk Management'
              ],
              recent_news: [],
              data_sources: individual.data_sources || []
            });
          });
        }
        
        setPersonResults(transformedResults);
      } else {
        setPersonError(data.error || 'Person search failed');
      }
    } catch (err) {
      setPersonError('Failed to connect to server. Make sure the backend is running.');
    } finally {
      setPersonLoading(false);
    }
  };

  const handleKeyDown = (event, searchType) => {
    if (event.key === 'Enter') {
      if (searchType === 'company') {
        handleCompanySearch();
      } else {
        handlePersonSearch();
      }
    }
  };

  // Helper to get CEO name from executives or data_sources
  const getCEOName = (result) => {
    if (result.ceo_name) return result.ceo_name;
    
    if (result.executives && Array.isArray(result.executives)) {
      const ceo = result.executives.find(e => e.title && e.title.toLowerCase().includes('ceo'));
      if (ceo) return ceo.name;
    }
    if (result.ceo_name) return result.ceo_name;
    return 'Unknown';
  };

  // Helper to render status/error messages
  const renderStatusMessage = (status, type) => {
    if (!status) return null;
    
    const isError = status.toLowerCase().includes('error') || 
                   status.toLowerCase().includes('failed') ||
                   status.toLowerCase().includes('not found') ||
                   status.toLowerCase().includes('forbidden');
    
    return (
      <div className={`status-message ${isError ? 'error' : 'warning'}`}>
        <span className="status-icon">{isError ? '⚠️' : 'ℹ️'}</span>
        <span className="status-text">
          <strong>{type}:</strong> {status}
        </span>
      </div>
    );
  };

  // Compact company row with expand/collapse
  const renderCompanyRows = () => {
    return companyResults
      .filter(result => result.title === 'Company')
      .map((result, index) => {
        const isExpanded = expandedCompanyIndex === index;
        const hasErrors = result.edgar_status || result.linkedin_status || result.companyresearch_status;
        
        return (
          <div key={index}>
            <div
              className={`company-row${isExpanded ? ' expanded' : ''}${hasErrors ? ' has-errors' : ''}`}
              onClick={() => setExpandedCompanyIndex(isExpanded ? null : index)}
            >
              <span className="company-row-name">
                {result.name}
                {result.ticker && <span className="ticker-symbol"> ({result.ticker})</span>}
              </span>
              <span className="company-row-label">Company</span>
              <span className="company-row-ceo">{getCEOName(result)}</span>
              {hasErrors && <span className="error-indicator">⚠️</span>}
            </div>
            {isExpanded && (
              <div className="company-profile-expanded">
                <div className="result-header">
                  <h3>
                    {result.name}
                    {result.ticker && <span className="ticker-symbol"> ({result.ticker})</span>}
                  </h3>
                  <span className="title">{result.title}</span>
                </div>
                
                {/* Display status/error messages */}
                <div className="status-messages">
                  {renderStatusMessage(result.edgar_status, 'SEC EDGAR')}
                  {renderStatusMessage(result.linkedin_status, 'LinkedIn')}
                  {renderStatusMessage(result.companyresearch_status, 'Company Research')}
                </div>
                
                <div className="result-details">
                  <p><strong>Company:</strong> {result.company}</p>
                  <p><strong>Estimated Net Worth:</strong> {result.estimated_net_worth}</p>
                  <p><strong>LinkedIn:</strong> <a href={result.linkedin_url} target="_blank" rel="noopener noreferrer">View Profile</a></p>
                </div>
                {result.company_info && (
                  <div className="company-info">
                    <h4>Company Information</h4>
                    <p><strong>Industry:</strong> {result.company_info.industry}</p>
                    <p><strong>Revenue:</strong> {result.company_info.revenue}</p>
                    <p><strong>Employees:</strong> {result.company_info.employees}</p>
                  </div>
                )}
                {result.company && result.company !== 'Various' && (
                  <div className="company-actions">
                    <button
                      className="view-financials-btn"
                      onClick={e => {
                        e.stopPropagation();
                        setSelectedCompany(result);
                        setShowFinancialStatements(true);
                      }}
                    >
                      View Company Financial Statements
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        );
      });
  };

  const renderIndividualResults = () => {
    return personResults.map((result, index) => (
      <div key={index} className="result-card">
        <div className="result-header">
          <h3>{result.name}</h3>
          <span className="title">{result.title}</span>
        </div>
        <div className="result-details">
          <p><strong>Company:</strong> {result.company}</p>
          <p><strong>Estimated Net Worth:</strong> {result.estimated_net_worth}</p>
          <p><strong>LinkedIn:</strong> <a href={result.linkedin_url} target="_blank" rel="noopener noreferrer">View Profile</a>
            {result.linkedin_note && <span className="linkedin-note"> ({result.linkedin_note})</span>}
          </p>
        </div>
        
        {result.company_info && (
          <div className="company-info">
            <h4>Company Information</h4>
            <p><strong>Industry:</strong> {result.company_info.industry}</p>
            <p><strong>Revenue:</strong> {result.company_info.revenue}</p>
            <p><strong>Employees:</strong> {result.company_info.employees}</p>
          </div>
        )}

        <div className="opportunities">
          <h4>Financial Opportunities</h4>
          <ul>
            {result.financial_opportunities.map((opp, i) => (
              <li key={i}>{opp}</li>
            ))}
          </ul>
        </div>

        <div className="conversation-starters">
          <h4>Conversation Starters</h4>
          <ul>
            {result.conversation_starters.map((starter, i) => (
              <li key={i}>{starter}</li>
            ))}
          </ul>
        </div>

        <div className="planning-needs">
          <h4>Planning Needs</h4>
          <ul>
            {result.planning_needs.map((need, i) => (
              <li key={i}>{need}</li>
            ))}
          </ul>
        </div>

        {result.recent_news && result.recent_news.length > 0 && (
          <div className="recent-news">
            <h4>Recent News</h4>
            <ul>
              {result.recent_news.map((news, i) => (
                <li key={i}>
                  <strong>{news.title}</strong> - {news.date} ({news.source})
                </li>
              ))}
            </ul>
          </div>
        )}
        
        {/* Add buttons for actions */}
        <div className="profile-actions">
          {/* Generate Report Button */}
          <button
            className="generate-report-btn"
            onClick={() => generateReport(result.name, result.company)}
            disabled={reportLoading}
          >
            {reportLoading ? 'Generating Report...' : '📊 Generate Detailed Report'}
          </button>
          
          {/* View Company Financial Statements Button */}
          {result.company && result.company !== 'Various' && (
            <button
              className="view-financials-btn"
              onClick={() => {
                setSelectedCompany(result);
                setShowFinancialStatements(true);
              }}
            >
              View Company Financial Statements
            </button>
          )}
        </div>
      </div>
    ));
  };

  const renderCompanyResults = () => {
    return companyResults.map((result, index) => (
      <div key={index} className="result-card">
        <div className="result-header">
          <h3>{result.company_name}</h3>
        </div>
        <div className="result-details">
          <p><strong>Industry:</strong> {result.industry}</p>
          <p><strong>Revenue:</strong> {result.revenue}</p>
          <p><strong>Employees:</strong> {result.employees}</p>
        </div>

        <div className="executives">
          <h4>Key Executives</h4>
          <ul>
            {result.executives.map((exec, i) => (
              <li key={i}>
                <strong>{exec.name}</strong> - {exec.title}
                <br />
                <a href={exec.linkedin_url} target="_blank" rel="noopener noreferrer">LinkedIn Profile</a>
              </li>
            ))}
          </ul>
        </div>

        <div className="opportunities">
          <h4>Financial Opportunities</h4>
          <ul>
            {result.financial_opportunities.map((opp, i) => (
              <li key={i}>{opp}</li>
            ))}
          </ul>
        </div>

        <div className="conversation-starters">
          <h4>Conversation Starters</h4>
          <ul>
            {result.conversation_starters.map((starter, i) => (
              <li key={i}>{starter}</li>
            ))}
          </ul>
        </div>

        <div className="planning-needs">
          <h4>Planning Needs</h4>
          <ul>
            {result.planning_needs.map((need, i) => (
              <li key={i}>{need}</li>
            ))}
          </ul>
        </div>
      </div>
    ));
  };

  const generateReport = async (personName, companyName) => {
    setReportLoading(true);
    setReportError('');

    try {
      const url = 'http://127.0.0.1:5000/api/opportunities/generate-report';
      const body = {
        person_name: personName,
        company_name: companyName
      };

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body)
      });

      const data = await response.json();

      if (response.ok) {
        setReportData(data);
        setShowReport(true);
      } else {
        setReportError(data.error || 'Report generation failed');
      }
    } catch (err) {
      setReportError('Failed to connect to server. Make sure the backend is running.');
    } finally {
      setReportLoading(false);
    }
  };

  const renderReport = () => {
    if (!reportData) return null;

    return (
      <div className="report-overlay">
        <div className="report-modal">
          <div className="report-header">
            <h2>🤖 AI Analysis Report</h2>
            <button 
              className="close-btn"
              onClick={() => {
                setShowReport(false);
                setReportData(null);
              }}
            >
              ×
            </button>
          </div>
          
          <div className="report-content">
            <div className="llm-response">
              <div className="ai-avatar">
                <span className="ai-icon">🤖</span>
              </div>
              <div className="response-text">
                {reportData.llm_response ? (
                  <div className="llm-message">
                    {reportData.llm_response.split('\n').map((paragraph, index) => {
                      if (paragraph.trim() === '') return null;
                      if (paragraph.startsWith('•')) {
                        return <li key={index} className="bullet-point">{paragraph}</li>;
                      }
                      return <p key={index} className="paragraph">{paragraph}</p>;
                    })}
                  </div>
                ) : (
                  <div className="loading-message">
                    <p>Generating AI analysis...</p>
                  </div>
                )}
              </div>
            </div>
            
            <div className="report-footer">
              <div className="report-meta">
                <p><strong>Report Generated:</strong> {new Date(reportData.report_generated).toLocaleString()}</p>
                <p><strong>Data Sources:</strong> {reportData.data_sources.join(', ')}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="search-component">
      <div className="search-header">
        <h2>Business Intelligence Platform</h2>
        <p>Search for companies and high-net-worth individuals</p>
      </div>

      <div className="search-form">
        <div className="search-section company-search-section">
          <div className="search-section-title">🔍 Company Search</div>
          <div className="search-input-group">
            <input
              type="text"
              value={companyQuery}
              onChange={(e) => setCompanyQuery(e.target.value)}
              onKeyDown={(e) => handleKeyDown(e, 'company')}
              placeholder="Enter company name..."
              className="search-input"
            />
          </div>
          <div className="search-buttons">
            <button
              onClick={handleCompanySearch}
              disabled={companyLoading}
              className="search-btn company-search-btn"
            >
              {companyLoading ? 'Searching...' : 'Search Companies'}
            </button>
          </div>
        </div>

        <div className="search-section person-search-section">
          <div className="search-section-title">👤 Person Search</div>
          <div className="search-input-group">
            <input
              type="text"
              value={personQuery}
              onChange={(e) => setPersonQuery(e.target.value)}
              onKeyDown={(e) => handleKeyDown(e, 'person')}
              placeholder="Enter person name..."
              className="search-input"
            />
          </div>
          <div className="search-buttons">
            <button
              onClick={handlePersonSearch}
              disabled={personLoading}
              className="search-btn person-search-btn"
            >
              {personLoading ? 'Searching...' : 'Search People'}
            </button>
          </div>
        </div>
      </div>

      {companyError && (
        <div className="error-message">
          {companyError}
        </div>
      )}

      {personError && (
        <div className="error-message">
          {personError}
        </div>
      )}

      {reportError && (
        <div className="error-message">
          {reportError}
        </div>
      )}

      {companyResults.length > 0 && (
        <div className="search-results company-results">
          <h3>Company Search Results ({companyResults.length} found)</h3>
          <div className="results-container">
            {renderCompanyRows()}
          </div>
        </div>
      )}

      {personResults.length > 0 && (
        <div className="search-results person-results">
          <h3>Person Search Results ({personResults.length} found)</h3>
          <div className="results-container">
            {renderIndividualResults()}
          </div>
        </div>
      )}

      {selectedCompany && showFinancialStatements && (
        <FinancialStatements
          company={selectedCompany}
          onClose={() => {
            setShowFinancialStatements(false);
            setSelectedCompany(null);
          }}
        />
      )}

      {showReport && renderReport()}
    </div>
  );
};

export default SearchComponent; 