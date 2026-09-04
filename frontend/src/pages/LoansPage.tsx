import React, { useState, useEffect } from 'react';
import { financialApi, LoanType, EmployeeLoan } from '../services/api/financial';

export const LoansPage: React.FC = () => {
  const [loans, setLoans] = useState<EmployeeLoan[]>([]);
  const [loanTypes, setLoanTypes] = useState<LoanType[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  // Form State
  const [loanTypeId, setLoanTypeId] = useState('');
  const [principalAmount, setPrincipalAmount] = useState('50000');
  const [tenureMonths, setTenureMonths] = useState('12');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [loansRes, typesRes] = await Promise.all([
        financialApi.getLoans(),
        financialApi.getLoanTypes(),
      ]);
      setLoans(loansRes.data);
      setLoanTypes(typesRes.data);
      if (typesRes.data.length > 0) setLoanTypeId(typesRes.data[0].id);
    } catch (err) {
      console.error('Failed to load loan data', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRequestLoan = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await financialApi.requestLoan({
        loan_type_id: loanTypeId,
        principal_amount: parseFloat(principalAmount),
        tenure_months: parseInt(tenureMonths, 10),
      });
      setShowModal(false);
      setPrincipalAmount('50000');
      fetchData();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Loan request failed');
    }
  };

  const [showTypeModal, setShowTypeModal] = useState(false);
  const [typeName, setTypeName] = useState('');
  const [typeCode, setTypeCode] = useState('');
  const [typeMax, setTypeMax] = useState('100000');
  const [typeRate, setTypeRate] = useState('0');
  const [interestType, setInterestType] = useState('NO_INTEREST');

  const handleCreateLoanType = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await financialApi.createLoanType({
        name: typeName,
        code: typeCode.toUpperCase().replace(/\s+/g, '_'),
        max_amount: parseFloat(typeMax),
        interest_rate: parseFloat(typeRate),
        interest_type: interestType,
        min_service_months: 3,
        max_salary_multiple: 3,
      });
      setShowTypeModal(false);
      setTypeName('');
      setTypeCode('');
      fetchData();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to create loan type');
    }
  };

  // Helper EMI Calculation
  const selectedType = loanTypes.find(t => t.id === loanTypeId);
  const pVal = parseFloat(principalAmount) || 0;
  const tVal = parseInt(tenureMonths, 10) || 1;
  const rateVal = selectedType?.interest_rate || 0;
  const totalInterest = (pVal * rateVal * (tVal / 12)) / 100;
  const estimatedEMI = (pVal + totalInterest) / tVal;

  // Stat Summary
  const totalPrincipal = loans.reduce((acc, l) => acc + (l.principal_amount || 0), 0);
  const totalEMI = loans.reduce((acc, l) => acc + (l.monthly_installment || 0), 0);

  return (
    <div style={{ padding: '24px', fontFamily: 'sans-serif' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px', alignItems: 'center' }}>
        <div>
          <h2 style={{ margin: 0 }}>💰 Employee Loans & Repayment Schedules</h2>
          <p style={{ color: '#6B7280', fontSize: '14px', margin: '4px 0 0 0' }}>
            Manage low-interest employee loans, auto-generated payroll EMI schedules, and principal recoveries.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            onClick={() => setShowTypeModal(true)}
            style={{ padding: '10px 18px', background: '#4B5563', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
          >
            + Add Loan Type
          </button>
          <button
            onClick={() => setShowModal(true)}
            style={{ padding: '10px 18px', background: '#10B981', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
          >
            + Request Employee Loan
          </button>
        </div>
      </div>

      {/* Summary KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '24px' }}>
        <div style={{ background: '#fff', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', borderLeft: '4px solid #3B82F6' }}>
          <p style={{ margin: 0, fontSize: '13px', color: '#6B7280' }}>Total Loan Records</p>
          <h2 style={{ margin: '6px 0 0 0', color: '#1E40AF' }}>{loans.length} Loans</h2>
        </div>
        <div style={{ background: '#fff', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', borderLeft: '4px solid #10B981' }}>
          <p style={{ margin: 0, fontSize: '13px', color: '#6B7280' }}>Total Disbursed Principal</p>
          <h2 style={{ margin: '6px 0 0 0', color: '#065F46' }}>₹ {totalPrincipal.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</h2>
        </div>
        <div style={{ background: '#fff', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', borderLeft: '4px solid #8B5CF6' }}>
          <p style={{ margin: 0, fontSize: '13px', color: '#6B7280' }}>Monthly Payroll EMI Recovery</p>
          <h2 style={{ margin: '6px 0 0 0', color: '#5B21B6' }}>₹ {totalEMI.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</h2>
        </div>
      </div>

      {loading ? (
        <p>Loading loan records...</p>
      ) : loans.length === 0 ? (
        <div style={{ background: '#fff', padding: '40px', borderRadius: '8px', textAlign: 'center', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <p style={{ color: '#6B7280', margin: 0 }}>No loan applications submitted yet.</p>
        </div>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: '8px', overflow: 'hidden', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <thead>
            <tr style={{ background: '#F3F4F6', textAlign: 'left', borderBottom: '1px solid #E5E7EB' }}>
              <th style={{ padding: '12px 16px' }}>Loan #</th>
              <th style={{ padding: '12px 16px' }}>Principal Amount (₹)</th>
              <th style={{ padding: '12px 16px' }}>Interest Rate</th>
              <th style={{ padding: '12px 16px' }}>Tenure</th>
              <th style={{ padding: '12px 16px' }}>Monthly EMI</th>
              <th style={{ padding: '12px 16px' }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {loans.map((loan) => (
              <tr key={loan.id} style={{ borderBottom: '1px solid #F3F4F6' }}>
                <td style={{ padding: '12px 16px', fontWeight: 'bold' }}>{loan.loan_number}</td>
                <td style={{ padding: '12px 16px', fontWeight: '600' }}>₹ {loan.principal_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
                <td style={{ padding: '12px 16px' }}>{loan.interest_rate}% ({loan.interest_type})</td>
                <td style={{ padding: '12px 16px' }}>{loan.tenure_months} Months</td>
                <td style={{ padding: '12px 16px', color: '#1D4ED8', fontWeight: 'bold' }}>₹ {loan.monthly_installment.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
                <td style={{ padding: '12px 16px' }}>
                  <span style={{
                    padding: '4px 10px',
                    borderRadius: '12px',
                    fontSize: '12px',
                    fontWeight: '600',
                    background: loan.status === 'ACTIVE' ? '#D1FAE5' : loan.status === 'SUBMITTED' ? '#FEF3C7' : '#E0E7FF',
                    color: loan.status === 'ACTIVE' ? '#065F46' : loan.status === 'SUBMITTED' ? '#92400E' : '#3730A3',
                  }}>
                    {loan.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {showModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ background: '#fff', padding: '24px', borderRadius: '8px', width: '480px' }}>
            <h3>Request Employee Loan</h3>
            <form onSubmit={handleRequestLoan}>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Select Loan Category</label>
                <select value={loanTypeId} onChange={(e) => setLoanTypeId(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }}>
                  {loanTypes.map((t) => (
                    <option key={t.id} value={t.id}>{t.name} ({t.interest_rate}% {t.interest_type})</option>
                  ))}
                </select>
              </div>

              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Principal Amount (₹)</label>
                <input type="number" step="500" value={principalAmount} onChange={(e) => setPrincipalAmount(e.target.value)} placeholder="50000" style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>

              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Repayment Tenure (Months)</label>
                <input type="number" min="1" max="60" value={tenureMonths} onChange={(e) => setTenureMonths(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>

              {/* Live EMI Calculator Preview Widget */}
              <div style={{ padding: '14px', background: '#F3F4F6', borderRadius: '6px', marginBottom: '16px' }}>
                <p style={{ margin: '0 0 6px 0', fontSize: '12px', color: '#4B5563', fontWeight: 'bold' }}>🧮 Live EMI Calculator Estimate</p>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '4px' }}>
                  <span>Estimated Monthly EMI:</span>
                  <strong style={{ color: '#10B981' }}>₹ {estimatedEMI.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} / mo</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#6B7280' }}>
                  <span>Total Repayment Interest:</span>
                  <span>₹ {totalInterest.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                <button type="button" onClick={() => setShowModal(false)} style={{ padding: '8px 16px', background: '#9CA3AF', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Cancel</button>
                <button type="submit" style={{ padding: '8px 16px', background: '#10B981', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>Submit Loan Application</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showTypeModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ background: '#fff', padding: '24px', borderRadius: '8px', width: '420px' }}>
            <h3>Create Loan Type</h3>
            <form onSubmit={handleCreateLoanType}>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Loan Type Name</label>
                <input type="text" value={typeName} onChange={(e) => setTypeName(e.target.value)} placeholder="e.g. Housing Advance" style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Loan Code</label>
                <input type="text" value={typeCode} onChange={(e) => setTypeCode(e.target.value)} placeholder="e.g. HOUSING" style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Max Loan Amount (₹)</label>
                <input type="number" step="1000" value={typeMax} onChange={(e) => setTypeMax(e.target.value)} placeholder="200000" style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Annual Interest Rate (%)</label>
                <input type="number" step="0.1" value={typeRate} onChange={(e) => setTypeRate(e.target.value)} placeholder="0.0" style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Interest Type</label>
                <select value={interestType} onChange={(e) => setInterestType(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }}>
                  <option value="NO_INTEREST">NO_INTEREST (0% Interest)</option>
                  <option value="REDUCING_BALANCE">REDUCING_BALANCE (Diminishing)</option>
                  <option value="FLAT">FLAT (Flat Rate)</option>
                </select>
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                <button type="button" onClick={() => setShowTypeModal(false)} style={{ padding: '8px 16px', background: '#9CA3AF', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Cancel</button>
                <button type="submit" style={{ padding: '8px 16px', background: '#4B5563', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>Create Loan Type</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
