import React, { useState } from 'react';

export const PromotionsPage: React.FC = () => {
  const [empName, setEmpName] = useState('');
  const [currentDesig, setCurrentDesig] = useState('Software Engineer');
  const [proposedDesig, setProposedDesig] = useState('Senior Software Engineer');
  const [reason, setReason] = useState('');

  const handleRecommendPromotion = (e: React.FormEvent) => {
    e.preventDefault();
    alert(`Promotion recommendation submitted for ${empName} (${currentDesig} ➔ ${proposedDesig})!`);
    setEmpName('');
    setReason('');
  };

  return (
    <div style={{ padding: '24px', fontFamily: 'sans-serif' }}>
      <div style={{ marginBottom: '24px' }}>
        <h2>🏆 Promotion Recommendations & Succession Planning</h2>
        <p style={{ color: '#6B7280', fontSize: '14px' }}>
          Nominate high performers for career advancement, designation band upgrades, and key leadership succession roles.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
        <div style={{ background: '#fff', padding: '24px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h3>Submit Manager Promotion Recommendation</h3>
          <form onSubmit={handleRecommendPromotion}>
            <div style={{ marginBottom: '12px' }}>
              <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Employee Name</label>
              <input
                type="text"
                value={empName}
                onChange={(e) => setEmpName(e.target.value)}
                placeholder="e.g. Sarah Connor"
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }}
                required
              />
            </div>

            <div style={{ marginBottom: '12px' }}>
              <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Current Designation Band</label>
              <input
                type="text"
                value={currentDesig}
                onChange={(e) => setCurrentDesig(e.target.value)}
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }}
                required
              />
            </div>

            <div style={{ marginBottom: '12px' }}>
              <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Proposed Promotion Designation</label>
              <input
                type="text"
                value={proposedDesig}
                onChange={(e) => setProposedDesig(e.target.value)}
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }}
                required
              />
            </div>

            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Promotion Business Rationale & Achievements</label>
              <textarea
                rows={4}
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder="Detail high-impact achievements, rating consistency, and team leadership..."
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }}
                required
              />
            </div>

            <button type="submit" style={{ padding: '10px 18px', background: '#8B5CF6', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>
              Submit Promotion Nomination
            </button>
          </form>
        </div>

        <div style={{ background: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', height: 'fit-content' }}>
          <h3>🎯 Promotion Eligibility Criteria</h3>
          <ul style={{ fontSize: '13px', color: '#4B5563', paddingLeft: '20px', lineHeight: '1.8' }}>
            <li>Minimum 12 months tenure in current designation band.</li>
            <li>Consecutive rating of <strong>4.0+ (Exceeds / Outstanding)</strong> in recent appraisal cycles.</li>
            <li>No active PIP flags or pending compliance holds.</li>
          </ul>
        </div>
      </div>
    </div>
  );
};
