import React, { useState, useEffect } from 'react';
import { financialApi, SalaryAdvance } from '../services/api/financial';

export const SalaryAdvancesPage: React.FC = () => {
  const [advances, setAdvances] = useState<SalaryAdvance[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [amount, setAmount] = useState('');
  const [recoveryMonths, setRecoveryMonths] = useState('1');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const res = await financialApi.getAdvances();
      setAdvances(res.data);
    } catch (err) {
      console.error('Failed to load advances', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRequestAdvance = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await financialApi.requestAdvance({
        amount: parseFloat(amount),
        recovery_months: parseInt(recoveryMonths, 10),
      });
      setShowModal(false);
      setAmount('');
      fetchData();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Salary advance request failed');
    }
  };

  return (
    <div style={{ padding: '24px', fontFamily: 'sans-serif' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px' }}>
        <h2>💵 Salary Advance & Recovery Tracking</h2>
        <button
          onClick={() => setShowModal(true)}
          style={{ padding: '10px 18px', background: '#F59E0B', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer' }}
        >
          + Request Salary Advance
        </button>
      </div>

      {loading ? (
        <p>Loading salary advances...</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: '8px', overflow: 'hidden', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <thead>
            <tr style={{ background: '#F3F4F6', textAlign: 'left', borderBottom: '1px solid #E5E7EB' }}>
              <th style={{ padding: '12px 16px' }}>Advance #</th>
              <th style={{ padding: '12px 16px' }}>Amount (₹)</th>
              <th style={{ padding: '12px 16px' }}>Recovery Terms</th>
              <th style={{ padding: '12px 16px' }}>Monthly Recovery</th>
              <th style={{ padding: '12px 16px' }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {advances.map((adv) => (
              <tr key={adv.id} style={{ borderBottom: '1px solid #F3F4F6' }}>
                <td style={{ padding: '12px 16px', fontWeight: 'bold' }}>{adv.advance_number}</td>
                <td style={{ padding: '12px 16px', fontWeight: '600' }}>₹ {adv.approved_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
                <td style={{ padding: '12px 16px' }}>{adv.recovery_months} Months</td>
                <td style={{ padding: '12px 16px', color: '#D97706', fontWeight: 'bold' }}>₹ {adv.monthly_recovery_amount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</td>
                <td style={{ padding: '12px 16px' }}>
                  <span style={{
                    padding: '4px 10px',
                    borderRadius: '12px',
                    fontSize: '12px',
                    fontWeight: '600',
                    background: adv.status === 'DISBURSED' ? '#D1FAE5' : '#FEF3C7',
                    color: adv.status === 'DISBURSED' ? '#065F46' : '#92400E',
                  }}>
                    {adv.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {showModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ background: '#fff', padding: '24px', borderRadius: '8px', width: '400px' }}>
            <h3>Request Salary Advance</h3>
            <form onSubmit={handleRequestAdvance}>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Amount (₹)</label>
                <input type="number" step="500" value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="10000" style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>

              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Recovery Duration (Months)</label>
                <input type="number" min="1" max="6" value={recoveryMonths} onChange={(e) => setRecoveryMonths(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                <button type="button" onClick={() => setShowModal(false)} style={{ padding: '8px 16px', background: '#9CA3AF', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Cancel</button>
                <button type="submit" style={{ padding: '8px 16px', background: '#F59E0B', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Submit</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
