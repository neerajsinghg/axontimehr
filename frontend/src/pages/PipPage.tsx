import React, { useState } from 'react';

export const PipPage: React.FC = () => {
  const [empName, setEmpName] = useState('');
  const [reason, setReason] = useState('');
  const [actionItems, setActionItems] = useState('');
  const [durationDays, setDurationDays] = useState('60');

  const handleCreatePip = (e: React.FormEvent) => {
    e.preventDefault();
    alert(`Performance Improvement Plan (PIP) created for ${empName}!`);
    setEmpName('');
    setReason('');
    setActionItems('');
  };

  return (
    <div style={{ padding: '24px', fontFamily: 'sans-serif' }}>
      <div style={{ marginBottom: '24px' }}>
        <h2>📈 Performance Improvement Plans (PIP)</h2>
        <p style={{ color: '#6B7280', fontSize: '14px' }}>
          Structured 30/60/90-day growth framework with clear milestone goals, weekly check-ins, and outcome reviews.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
        <div style={{ background: '#fff', padding: '24px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h3>Initiate Performance Growth Plan</h3>
          <form onSubmit={handleCreatePip}>
            <div style={{ marginBottom: '12px' }}>
              <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Employee Name</label>
              <input
                type="text"
                value={empName}
                onChange={(e) => setEmpName(e.target.value)}
                placeholder="e.g. John Doe"
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }}
                required
              />
            </div>

            <div style={{ marginBottom: '12px' }}>
              <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>PIP Duration</label>
              <select
                value={durationDays}
                onChange={(e) => setDurationDays(e.target.value)}
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }}
              >
                <option value="30">30 Days Accelerated Growth</option>
                <option value="60">60 Days Standard Plan</option>
                <option value="90">90 Days Extended Framework</option>
              </select>
            </div>

            <div style={{ marginBottom: '12px' }}>
              <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Performance Gap Reason</label>
              <textarea
                rows={3}
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder="Specific areas requiring improvement (e.g. Code quality standards, sprint velocity)..."
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }}
                required
              />
            </div>

            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Action Items & Measurable Deliverables</label>
              <textarea
                rows={4}
                value={actionItems}
                onChange={(e) => setActionItems(e.target.value)}
                placeholder="1. Complete AWS Security Certification&#10;2. Pass 100% unit test coverage on assigned services..."
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }}
                required
              />
            </div>

            <button type="submit" style={{ padding: '10px 18px', background: '#DC2626', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>
              Initiate PIP Framework
            </button>
          </form>
        </div>

        <div style={{ background: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', height: 'fit-content' }}>
          <h3>📋 PIP Outcome Statuses</h3>
          <ul style={{ fontSize: '13px', color: '#4B5563', paddingLeft: '20px', lineHeight: '1.8' }}>
            <li><strong style={{ color: '#10B981' }}>SUCCESSFUL</strong>: Meets all action item criteria and resumes normal track.</li>
            <li><strong style={{ color: '#F59E0B' }}>EXTENDED</strong>: 30-day extension granted for final milestone validation.</li>
            <li><strong style={{ color: '#EF4444' }}>UNSUCCESSFUL</strong>: Escalates to HR transition / role adjustment.</li>
          </ul>
        </div>
      </div>
    </div>
  );
};
