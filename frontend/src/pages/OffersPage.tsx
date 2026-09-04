import React, { useState, useEffect } from 'react';
import { recruitmentApi, Offer, Candidate } from '../services/api/recruitment';

export const OffersPage: React.FC = () => {
  const [offers, setOffers] = useState<Offer[]>([]);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  const [candidateId, setCandidateId] = useState('');
  const [baseSalary, setBaseSalary] = useState('1600000');
  const [variablePay, setVariablePay] = useState('200000');
  const [joiningDate, setJoiningDate] = useState('2026-10-01');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [offData, candData] = await Promise.all([
        recruitmentApi.getOffers(),
        recruitmentApi.getCandidates(),
      ]);
      setOffers(offData);
      setCandidates(candData);
      if (candData.length > 0) setCandidateId(candData[0].id);
    } catch (err) {
      console.error('Failed to load offer letters', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateOffer = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await recruitmentApi.createOffer({
        candidate_id: candidateId,
        offer_number: `OFF-${Date.now().toString().slice(-6)}`,
        base_salary: parseFloat(baseSalary),
        variable_pay: parseFloat(variablePay),
        joining_date: joiningDate,
      });
      setShowModal(false);
      fetchData();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to generate offer letter');
    }
  };

  const handleConvertEmployee = async (offerId: string) => {
    try {
      const res = await recruitmentApi.convertCandidateToEmployee(offerId);
      alert(`🎉 ${res.message}\nNew Employee Code: ${res.employee_code}`);
      fetchData();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Conversion failed');
    }
  };

  return (
    <div style={{ padding: '24px', fontFamily: 'sans-serif' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px', alignItems: 'center' }}>
        <div>
          <h2 style={{ margin: 0 }}>📄 Offer Management & Employee Conversion</h2>
          <p style={{ color: '#6B7280', fontSize: '14px', margin: '4px 0 0 0' }}>
            Generate formal employment offers, track candidate acceptance, and convert hired candidates directly into Active Employees.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          style={{ padding: '10px 18px', background: '#059669', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
        >
          + Generate Offer Letter
        </button>
      </div>

      {loading ? (
        <p>Loading offer letters...</p>
      ) : offers.length === 0 ? (
        <div style={{ background: '#fff', padding: '40px', borderRadius: '8px', textAlign: 'center', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <p style={{ color: '#6B7280', margin: 0 }}>No offer letters currently active.</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px' }}>
          {offers.map((off) => {
            const cand = candidates.find((c) => c.id === off.candidate_id);
            const isAccepted = off.status === 'ACCEPTED';
            return (
              <div key={off.id} style={{ background: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', borderLeft: '4px solid #059669' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <span style={{ fontSize: '12px', fontWeight: 'bold', color: '#1E40AF' }}>{off.offer_number}</span>
                  <span style={{ fontSize: '11px', background: isAccepted ? '#D1FAE5' : '#DBEAFE', color: isAccepted ? '#065F46' : '#1E40AF', padding: '2px 8px', borderRadius: '12px', fontWeight: 'bold' }}>
                    {off.status}
                  </span>
                </div>

                <h3 style={{ margin: '4px 0 6px 0', color: '#111827', fontSize: '16px' }}>
                  {cand ? `${cand.first_name} ${cand.last_name}` : 'Candidate Offer'}
                </h3>
                <p style={{ fontSize: '13px', color: '#4B5563', margin: '0 0 6px 0' }}>
                  Annual Fixed CTC: <b>₹{Number(off.base_salary).toLocaleString('en-IN')}</b> | Variable Pay: <b>₹{Number(off.variable_pay).toLocaleString('en-IN')}</b>
                </p>
                <p style={{ fontSize: '12px', color: '#6B7280', margin: '0 0 16px 0' }}>
                  Target Joining Date: <b>{off.joining_date}</b>
                </p>

                <button
                  onClick={() => handleConvertEmployee(off.id)}
                  disabled={isAccepted}
                  style={{
                    width: '100%',
                    padding: '8px',
                    background: isAccepted ? '#9CA3AF' : '#10B981',
                    color: '#fff',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: isAccepted ? 'default' : 'pointer',
                    fontSize: '12px',
                    fontWeight: 'bold',
                  }}
                >
                  {isAccepted ? '✓ Converted to Active Employee' : '⚡ 1-Click Candidate → Employee Conversion'}
                </button>
              </div>
            );
          })}
        </div>
      )}

      {/* Modal: Generate Offer */}
      {showModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ background: '#fff', padding: '24px', borderRadius: '8px', width: '450px' }}>
            <h3>Generate Employment Offer Letter</h3>
            <form onSubmit={handleCreateOffer}>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Select Candidate</label>
                <select value={candidateId} onChange={(e) => setCandidateId(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }}>
                  {candidates.map((c) => (
                    <option key={c.id} value={c.id}>{c.first_name} {c.last_name} ({c.email})</option>
                  ))}
                </select>
              </div>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Base Fixed Salary (Annual ₹)</label>
                <input type="number" value={baseSalary} onChange={(e) => setBaseSalary(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Variable Pay / Performance Bonus (₹)</label>
                <input type="number" value={variablePay} onChange={(e) => setVariablePay(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Joining Date</label>
                <input type="date" value={joiningDate} onChange={(e) => setJoiningDate(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                <button type="button" onClick={() => setShowModal(false)} style={{ padding: '8px 16px', background: '#9CA3AF', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Cancel</button>
                <button type="submit" style={{ padding: '8px 16px', background: '#059669', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>Generate & Issue Offer</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
