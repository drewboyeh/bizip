import React, { useState } from 'react';
import './FinancialStatements.css';

const FinancialStatements = ({ company, onClose }) => {
  const [activeTab, setActiveTab] = useState('income');
  
  if (!company || !company.edgar_data) {
    return (
      <div className="financial-statements-overlay">
        <div className="financial-statements-modal">
          <div className="modal-header">
            <h2>Financial Statements - {company?.name || 'Company'}</h2>
            <button className="close-button" onClick={onClose}>×</button>
          </div>
          <div className="no-financial-data">
            <p>No financial data available for this company.</p>
            <p>Financial statements are only available for publicly traded companies with SEC filings.</p>
          </div>
        </div>
      </div>
    );
  }

  const financialData = company.edgar_data.financial_statements;
  
  // Income Statement Data
  const incomeStatementData = [
    { item: 'Revenue', value: financialData.revenue || 'N/A' },
    { item: 'Cost of Revenue', value: 'N/A' },
    { item: 'Gross Profit', value: 'N/A' },
    { item: 'Operating Expenses', value: 'N/A' },
    { item: 'Operating Income', value: 'N/A' },
    { item: 'Interest Expense', value: 'N/A' },
    { item: 'Income Tax Expense', value: 'N/A' },
    { item: 'Net Income', value: financialData.net_income || 'N/A' }
  ];

  // Balance Sheet Data
  const balanceSheetData = [
    { item: 'Cash and Cash Equivalents', value: financialData.cash_and_equivalents || 'N/A' },
    { item: 'Short-term Investments', value: 'N/A' },
    { item: 'Accounts Receivable', value: 'N/A' },
    { item: 'Inventory', value: 'N/A' },
    { item: 'Total Current Assets', value: 'N/A' },
    { item: 'Property, Plant & Equipment', value: 'N/A' },
    { item: 'Intangible Assets', value: 'N/A' },
    { item: 'Total Assets', value: financialData.total_assets || 'N/A' },
    { item: 'Accounts Payable', value: 'N/A' },
    { item: 'Short-term Debt', value: 'N/A' },
    { item: 'Total Current Liabilities', value: 'N/A' },
    { item: 'Long-term Debt', value: financialData.debt || 'N/A' },
    { item: 'Total Liabilities', value: financialData.total_liabilities || 'N/A' },
    { item: 'Total Shareholders\' Equity', value: 'N/A' }
  ];

  // Cash Flow Statement Data
  const cashFlowData = [
    { item: 'Net Income', value: financialData.net_income || 'N/A' },
    { item: 'Depreciation & Amortization', value: 'N/A' },
    { item: 'Changes in Working Capital', value: 'N/A' },
    { item: 'Operating Cash Flow', value: 'N/A' },
    { item: 'Capital Expenditures', value: 'N/A' },
    { item: 'Investing Cash Flow', value: 'N/A' },
    { item: 'Debt Issuance/Repayment', value: 'N/A' },
    { item: 'Dividends Paid', value: 'N/A' },
    { item: 'Financing Cash Flow', value: 'N/A' },
    { item: 'Net Change in Cash', value: 'N/A' }
  ];

  // Shareholders' Equity Data
  const equityData = [
    { item: 'Common Stock', value: 'N/A' },
    { item: 'Additional Paid-in Capital', value: 'N/A' },
    { item: 'Retained Earnings', value: 'N/A' },
    { item: 'Treasury Stock', value: 'N/A' },
    { item: 'Accumulated Other Comprehensive Income', value: 'N/A' },
    { item: 'Total Shareholders\' Equity', value: 'N/A' }
  ];

  const renderTable = (data, title) => (
    <div className="financial-table-container">
      <h3>{title}</h3>
      <table className="financial-table">
        <thead>
          <tr>
            <th>Item</th>
            <th>Amount</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <tr key={index} className={index % 2 === 0 ? 'even-row' : 'odd-row'}>
              <td className="item-cell">{row.item}</td>
              <td className="value-cell">{row.value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  return (
    <div className="financial-statements-overlay">
      <div className="financial-statements-modal">
        <div className="modal-header">
          <h2>Financial Statements - {company.name}</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <div className="financial-statements">
          <div className="financial-header">
            <p className="filing-date">Filing Date: {financialData.filing_date || 'N/A'}</p>
          </div>

          <div className="tab-container">
            <div className="tab-buttons">
              <button
                className={`tab-button ${activeTab === 'income' ? 'active' : ''}`}
                onClick={() => setActiveTab('income')}
              >
                Income Statement
              </button>
              <button
                className={`tab-button ${activeTab === 'balance' ? 'active' : ''}`}
                onClick={() => setActiveTab('balance')}
              >
                Balance Sheet
              </button>
              <button
                className={`tab-button ${activeTab === 'cashflow' ? 'active' : ''}`}
                onClick={() => setActiveTab('cashflow')}
              >
                Cash Flow Statement
              </button>
              <button
                className={`tab-button ${activeTab === 'equity' ? 'active' : ''}`}
                onClick={() => setActiveTab('equity')}
              >
                Shareholders' Equity
              </button>
            </div>

            <div className="tab-content">
              {activeTab === 'income' && renderTable(incomeStatementData, 'Income Statement')}
              {activeTab === 'balance' && renderTable(balanceSheetData, 'Balance Sheet')}
              {activeTab === 'cashflow' && renderTable(cashFlowData, 'Cash Flow Statement')}
              {activeTab === 'equity' && renderTable(equityData, 'Statement of Shareholders\' Equity')}
            </div>
          </div>

          <div className="financial-summary">
            <h3>Key Financial Metrics</h3>
            <div className="metrics-grid">
              <div className="metric">
                <span className="metric-label">Revenue:</span>
                <span className="metric-value">{financialData.revenue || 'N/A'}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Net Income:</span>
                <span className="metric-value">{financialData.net_income || 'N/A'}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Total Assets:</span>
                <span className="metric-value">{financialData.total_assets || 'N/A'}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Total Debt:</span>
                <span className="metric-value">{financialData.debt || 'N/A'}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Cash & Equivalents:</span>
                <span className="metric-value">{financialData.cash_and_equivalents || 'N/A'}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FinancialStatements; 