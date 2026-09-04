import React, { useState, useEffect } from 'react';
import { financialApi, FinancialDashboardSummary, FinancialTransaction } from '../services/api/financial';

export const FinancialReportsPage: React.FC = () => {
  const [summary, setSummary] = useState<FinancialDashboardSummary | null>(null);
  const [transactions, setTransactions] = useState<FinancialTransaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [txLoading, setTxLoading] = useState(false);

  // Filters state
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [directionFilter, setDirectionFilter] = useState('');

  useEffect(() => {
    fetchDashboard();
  }, []);

  useEffect(() => {
    fetchTransactions();
  }, [search, typeFilter, directionFilter]);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      const sumRes = await financialApi.getDashboard();
      setSummary(sumRes.data);
    } catch (err) {
      console.error('Failed to load financial summary', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchTransactions = async () => {
    try {
      setTxLoading(true);
      const params: any = {};
      if (search.trim()) params.search = search.trim();
      if (typeFilter) params.transaction_type = typeFilter;
      if (directionFilter) params.direction = directionFilter;

      const txRes = await financialApi.getTransactions(params);
      setTransactions(txRes.data);
    } catch (err) {
      console.error('Failed to load transactions', err);
    } finally {
      setTxLoading(false);
    }
  };

  const formatINR = (val: number | string | undefined) => {
    if (val === undefined || val === null) return '₹ 0.00';
    const num = typeof val === 'string' ? parseFloat(val) : val;
    return '₹ ' + num.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  };

  const getTransactionLabel = (type: string) => {
    switch (type) {
      case 'EXPENSE_REIMBURSEMENT': return 'Expense Reimbursement';
      case 'LOAN_DISBURSEMENT': return 'Loan Disbursement';
      case 'LOAN_REPAYMENT': return 'Loan Repayment (EMI)';
      case 'SALARY_ADVANCE': return 'Salary Advance Payout';
      case 'SALARY_ADVANCE_RECOVERY': return 'Advance Recovery';
      case 'ADJUSTMENT': return 'Manual Adjustment';
      case 'REVERSAL': return 'Transaction Reversal';
      default: return type;
    }
  };

  return (
    <div style={{ padding: '28px', fontFamily: "'Inter', -apple-system, sans-serif", background: '#F9FAFB', minHeight: '100vh' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px' }}>
        <div>
          <h2 style={{ fontSize: '24px', fontWeight: '700', color: '#111827', margin: 0 }}>📊 Financial Ledger & Reports</h2>
          <p style={{ color: '#6B7280', fontSize: '14px', marginTop: '4px', margin: 0 }}>
            Audit-grade double-entry financial ledger and multi-tenant employee services control panel in Indian Rupees (₹).
          </p>
        </div>
        <button
          onClick={() => window.print()}
          style={{
            padding: '9px 16px',
            background: '#FFFFFF',
            border: '1px solid #D1D5DB',
            borderRadius: '6px',
            color: '#374151',
            fontWeight: '600',
            fontSize: '13px',
            cursor: 'pointer',
            boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}
        >
          🖨️ Export Ledger Report
        </button>
      </div>

      {loading || !summary ? (
        <div style={{ padding: '32px', textAlign: 'center', color: '#6B7280' }}>Loading financial dashboard metrics...</div>
      ) : (
        <>
          {/* Metric Cards Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '20px', marginBottom: '32px' }}>
            <div style={{ background: '#FFFFFF', padding: '20px', borderRadius: '12px', border: '1px solid #E5E7EB', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
              <div style={{ color: '#6B7280', fontSize: '13px', fontWeight: '500' }}>Total Submitted Claims</div>
              <div style={{ fontSize: '26px', fontWeight: '800', color: '#111827', marginTop: '8px' }}>{summary.total_claims_count}</div>
              <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '6px' }}>Pending Review: <strong style={{ color: '#D97706' }}>{formatINR(summary.pending_claims_amount)}</strong></div>
            </div>

            <div style={{ background: '#FFFFFF', padding: '20px', borderRadius: '12px', border: '1px solid #E5E7EB', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
              <div style={{ color: '#6B7280', fontSize: '13px', fontWeight: '500' }}>Approved Reimbursements</div>
              <div style={{ fontSize: '26px', fontWeight: '800', color: '#059669', marginTop: '8px' }}>{formatINR(summary.approved_reimbursements_amount)}</div>
              <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '6px' }}>Queued for Next Payroll Run</div>
            </div>

            <div style={{ background: '#FFFFFF', padding: '20px', borderRadius: '12px', border: '1px solid #E5E7EB', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
              <div style={{ color: '#6B7280', fontSize: '13px', fontWeight: '500' }}>Outstanding Loans Principal</div>
              <div style={{ fontSize: '26px', fontWeight: '800', color: '#2563EB', marginTop: '8px' }}>{formatINR(summary.outstanding_loans_principal)}</div>
              <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '6px' }}>Active Loans: <strong>{summary.total_active_loans_count}</strong> (Expected EMI: <strong>{formatINR(summary.monthly_loan_recovery_expected)}</strong>/mo)</div>
            </div>

            <div style={{ background: '#FFFFFF', padding: '20px', borderRadius: '12px', border: '1px solid #E5E7EB', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
              <div style={{ color: '#6B7280', fontSize: '13px', fontWeight: '500' }}>Outstanding Salary Advances</div>
              <div style={{ fontSize: '26px', fontWeight: '800', color: '#D97706', marginTop: '8px' }}>{formatINR(summary.outstanding_advances_amount)}</div>
              <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '6px' }}>Active Advances: <strong>{summary.total_active_advances_count} Accounts</strong></div>
            </div>
          </div>

          {/* Ledger Section Header & Search Filters */}
          <div style={{ background: '#FFFFFF', borderRadius: '12px', border: '1px solid #E5E7EB', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '16px' }}>
              <h3 style={{ fontSize: '18px', fontWeight: '700', color: '#111827', margin: 0 }}>
                📜 Immutable Financial Ledger Transactions
              </h3>
              <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                {/* Search Bar */}
                <input
                  type="text"
                  placeholder="Search ref ID, employee, cost center..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  style={{
                    padding: '8px 14px',
                    borderRadius: '6px',
                    border: '1px solid #D1D5DB',
                    fontSize: '13px',
                    width: '240px'
                  }}
                />

                {/* Transaction Type Filter */}
                <select
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value)}
                  style={{
                    padding: '8px 12px',
                    borderRadius: '6px',
                    border: '1px solid #D1D5DB',
                    fontSize: '13px',
                    background: '#FFF'
                  }}
                >
                  <option value="">All Transaction Types</option>
                  <option value="EXPENSE_REIMBURSEMENT">Expense Reimbursement</option>
                  <option value="LOAN_DISBURSEMENT">Loan Disbursement</option>
                  <option value="LOAN_REPAYMENT">Loan Repayment</option>
                  <option value="SALARY_ADVANCE">Salary Advance</option>
                  <option value="SALARY_ADVANCE_RECOVERY">Advance Recovery</option>
                  <option value="ADJUSTMENT">Adjustment</option>
                  <option value="REVERSAL">Reversal</option>
                </select>

                {/* Direction Filter */}
                <select
                  value={directionFilter}
                  onChange={(e) => setDirectionFilter(e.target.value)}
                  style={{
                    padding: '8px 12px',
                    borderRadius: '6px',
                    border: '1px solid #D1D5DB',
                    fontSize: '13px',
                    background: '#FFF'
                  }}
                >
                  <option value="">All Directions</option>
                  <option value="CREDIT">🟢 CREDIT (Payout / Disbursed)</option>
                  <option value="DEBIT">🔴 DEBIT (Recovery / Repayment)</option>
                </select>
              </div>
            </div>

            {/* Table */}
            {txLoading ? (
              <p style={{ color: '#6B7280', textAlign: 'center', padding: '24px' }}>Loading ledger transactions...</p>
            ) : transactions.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '40px 20px', color: '#9CA3AF' }}>
                <p style={{ fontSize: '15px', fontWeight: '500' }}>No financial transactions recorded matching selected criteria.</p>
              </div>
            ) : (
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
                <thead>
                  <tr style={{ background: '#F9FAFB', textAlign: 'left', borderBottom: '1px solid #E5E7EB', color: '#4B5563', fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    <th style={{ padding: '12px 16px' }}>Date & Time</th>
                    <th style={{ padding: '12px 16px' }}>Employee</th>
                    <th style={{ padding: '12px 16px' }}>Transaction Type</th>
                    <th style={{ padding: '12px 16px' }}>Reference ID</th>
                    <th style={{ padding: '12px 16px' }}>Direction</th>
                    <th style={{ padding: '12px 16px', textAlign: 'right' }}>Amount (₹)</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.map((tx) => (
                    <tr key={tx.id} style={{ borderBottom: '1px solid #F3F4F6' }}>
                      <td style={{ padding: '14px 16px', color: '#374151', fontSize: '13px' }}>
                        {new Date(tx.transaction_date).toLocaleString('en-IN', {
                          day: '2-digit',
                          month: 'short',
                          year: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </td>
                      <td style={{ padding: '14px 16px' }}>
                        <div style={{ fontWeight: '600', color: '#111827' }}>{tx.employee_name || 'System / Employee'}</div>
                        {tx.employee_code && <div style={{ fontSize: '12px', color: '#6B7280' }}>{tx.employee_code}</div>}
                      </td>
                      <td style={{ padding: '14px 16px' }}>
                        <span style={{ fontWeight: '600', color: '#1F2937' }}>
                          {getTransactionLabel(tx.transaction_type)}
                        </span>
                        {tx.cost_center && (
                          <span style={{ marginLeft: '8px', fontSize: '11px', background: '#E5E7EB', padding: '2px 6px', borderRadius: '4px', color: '#4B5563' }}>
                            {tx.cost_center}
                          </span>
                        )}
                      </td>
                      <td style={{ padding: '14px 16px' }}>
                        <code style={{ background: '#F3F4F6', padding: '3px 8px', borderRadius: '4px', fontSize: '12px', color: '#374151', fontFamily: 'monospace' }}>
                          {tx.reference_id}
                        </code>
                      </td>
                      <td style={{ padding: '14px 16px' }}>
                        <span style={{
                          padding: '4px 10px',
                          borderRadius: '12px',
                          fontSize: '11px',
                          fontWeight: '700',
                          letterSpacing: '0.03em',
                          background: tx.direction === 'CREDIT' ? '#D1FAE5' : '#FEE2E2',
                          color: tx.direction === 'CREDIT' ? '#065F46' : '#991B1B',
                        }}>
                          {tx.direction === 'CREDIT' ? '🟢 CREDIT (+)' : '🔴 DEBIT (-)'}
                        </span>
                      </td>
                      <td style={{ padding: '14px 16px', textAlign: 'right', fontWeight: '700', fontSize: '15px', color: tx.direction === 'CREDIT' ? '#059669' : '#DC2626' }}>
                        {tx.direction === 'CREDIT' ? '+ ' : '- '} {formatINR(tx.amount)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}
    </div>
  );
};

