import React, { useState, useEffect } from 'react';
import { recruitmentApi, Candidate } from '../services/api/recruitment';

const PIPELINE_STAGES = [
  { id: 'APPLIED', title: 'Applied', color: '#6B7280' },
  { id: 'SCREENING', title: 'Screening', color: '#D97706' },
  { id: 'SHORTLISTED', title: 'Shortlisted', color: '#2563EB' },
  { id: 'INTERVIEW', title: 'Interviewing', color: '#8B5CF6' },
  { id: 'OFFER', title: 'Offer Extended', color: '#059669' },
  { id: 'HIRED', title: 'Hired & Converted', color: '#10B981' },
];

export const CandidatePipelinePage: React.FC = () => {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [company, setCompany] = useState('');
  const [salary, setSalary] = useState('1600000');
  const [skills, setSkills] = useState('Python, React, FastAPI');

  useEffect(() => {
    fetchCandidates();
  }, []);

  const fetchCandidates = async () => {
    try {
      setLoading(true);
      const data = await recruitmentApi.getCandidates();
      setCandidates(data);
    } catch (err) {
      console.error('Failed to load candidate pipeline', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddCandidate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await recruitmentApi.createCandidate({
        first_name: firstName,
        last_name: lastName,
        email,
        phone,
        current_company: company,
        expected_salary: parseFloat(salary),
        skills_list: skills,
      });
      setShowModal(false);
      setFirstName('');
      setLastName('');
      setEmail('');
      fetchCandidates();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to add candidate');
    }
  };

  const handleMoveStage = async (candidateId: string, currentStage: string) => {
    const stageOrder = ['APPLIED', 'SCREENING', 'SHORTLISTED', 'INTERVIEW', 'OFFER', 'HIRED'];
    const idx = stageOrder.indexOf(currentStage);
    if (idx < stageOrder.length - 1) {
      const nextStage = stageOrder[idx + 1];
      try {
        await recruitmentApi.updateCandidateStage(candidateId, nextStage, 'Moved via Pipeline Board');
        fetchCandidates();
      } catch (err: any) {
        alert(err?.response?.data?.detail || 'Failed to update candidate stage');
      }
    }
  };

  return (
    <div style={{ padding: '24px', fontFamily: 'sans-serif' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px', alignItems: 'center' }}>
        <div>
          <h2 style={{ margin: 0 }}>👥 Candidate Recruitment Pipeline</h2>
          <p style={{ color: '#6B7280', fontSize: '14px', margin: '4px 0 0 0' }}>
            Interactive Applicant Tracking Pipeline. Monitor applicant evaluation, scores, and stage progression.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          style={{ padding: '10px 18px', background: '#2563EB', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
        >
          + Add Candidate Profile
        </button>
      </div>

      {loading ? (
        <p>Loading candidate pipeline...</p>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '12px', overflowX: 'auto', paddingBottom: '16px' }}>
          {PIPELINE_STAGES.map((stage) => {
            const stageCandidates = candidates.filter((c) => c.status === stage.id);
            return (
              <div key={stage.id} style={{ background: '#F3F4F6', borderRadius: '8px', padding: '12px', minHeight: '500px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px', borderBottom: `3px solid ${stage.color}`, paddingBottom: '6px' }}>
                  <span style={{ fontWeight: 'bold', fontSize: '13px', color: '#1F2937' }}>{stage.title}</span>
                  <span style={{ fontSize: '11px', background: stage.color, color: '#fff', padding: '2px 6px', borderRadius: '10px', fontWeight: 'bold' }}>
                    {stageCandidates.length}
                  </span>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {stageCandidates.map((c) => (
                    <div key={c.id} style={{ background: '#fff', padding: '12px', borderRadius: '6px', boxShadow: '0 1px 2px rgba(0,0,0,0.1)', borderLeft: `4px solid ${stage.color}` }}>
                      <h4 style={{ margin: '0 0 4px 0', fontSize: '14px', color: '#111827' }}>{c.first_name} {c.last_name}</h4>
                      <p style={{ margin: '0 0 4px 0', fontSize: '11px', color: '#6B7280' }}>{c.current_company || 'Independent Candidate'}</p>
                      <p style={{ margin: '0 0 8px 0', fontSize: '11px', color: '#059669', fontWeight: 'bold' }}>⭐ Score: {c.overall_score}%</p>
                      <div style={{ fontSize: '10px', background: '#EFF6FF', color: '#1E40AF', padding: '4px', borderRadius: '4px', marginBottom: '8px' }}>
                        {c.skills_list || 'General Developer'}
                      </div>
                      {stage.id !== 'HIRED' && (
                        <button
                          onClick={() => handleMoveStage(c.id, c.status)}
                          style={{ width: '100%', padding: '4px', background: '#2563EB', color: '#fff', border: 'none', borderRadius: '4px', fontSize: '10px', cursor: 'pointer', fontWeight: 'bold' }}
                        >
                          Advance Stage ➔
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Modal: Add Candidate */}
      {showModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ background: '#fff', padding: '24px', borderRadius: '8px', width: '450px' }}>
            <h3>Add New Candidate Profile</h3>
            <form onSubmit={handleAddCandidate}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '12px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', marginBottom: '4px' }}>First Name</label>
                  <input type="text" value={firstName} onChange={(e) => setFirstName(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', marginBottom: '4px' }}>Last Name</label>
                  <input type="text" value={lastName} onChange={(e) => setLastName(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
                </div>
              </div>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '12px', marginBottom: '4px' }}>Email Address</label>
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '12px', marginBottom: '4px' }}>Current Company</label>
                <input type="text" value={company} onChange={(e) => setCompany(e.target.value)} placeholder="e.g. Acme Tech Solutions" style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '12px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', marginBottom: '4px' }}>Phone</label>
                  <input type="text" value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="+91 9876543210" style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', marginBottom: '4px' }}>Expected Salary (₹)</label>
                  <input type="number" value={salary} onChange={(e) => setSalary(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} />
                </div>
              </div>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '12px', marginBottom: '4px' }}>Skills List</label>
                <input type="text" value={skills} onChange={(e) => setSkills(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                <button type="button" onClick={() => setShowModal(false)} style={{ padding: '8px 16px', background: '#9CA3AF', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Cancel</button>
                <button type="submit" style={{ padding: '8px 16px', background: '#2563EB', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>Add Candidate</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
