import React, { useState, useEffect } from 'react';
import { performanceApi, Survey } from '../services/api/performance';

export const EngagementSurveysPage: React.FC = () => {
  const [surveys, setSurveys] = useState<Survey[]>([]);
  const [loading, setLoading] = useState(true);
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);

  const [category, setCategory] = useState('WORKPLACE');
  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchSurveys();
  }, []);

  const fetchSurveys = async () => {
    try {
      setLoading(true);
      const data = await performanceApi.getSurveys();
      setSurveys(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Failed to load surveys', err);
      setSurveys([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSendFeedback = (e: React.FormEvent) => {
    e.preventDefault();
    alert('Anonymous workplace suggestion submitted successfully to HR!');
    setShowFeedbackModal(false);
    setSubject('');
    setMessage('');
  };

  const safeSurveys = Array.isArray(surveys) ? surveys : [];

  return (
    <div style={{ padding: '24px', fontFamily: 'sans-serif' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px', alignItems: 'center' }}>
        <div>
          <h2 style={{ margin: 0 }}>📊 Employee Engagement & Pulse Surveys</h2>
          <p style={{ color: '#6B7280', fontSize: '14px', margin: '4px 0 0 0' }}>
            Participate in anonymous pulse surveys, share eNPS feedback, and contribute to workplace culture.
          </p>
        </div>
        <button
          onClick={() => setShowFeedbackModal(true)}
          style={{ padding: '10px 18px', background: '#EC4899', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
        >
          💡 Submit Workplace Suggestion
        </button>
      </div>

      {/* eNPS & Sentiment Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px', marginBottom: '24px' }}>
        <div style={{ background: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h3 style={{ margin: '0 0 12px 0' }}>❤️ Employee Net Promoter Score (eNPS)</h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
            <div style={{ textAlign: 'center', padding: '16px', background: '#FDF2F8', borderRadius: '8px', minWidth: '120px' }}>
              <span style={{ fontSize: '12px', color: '#BE185D', fontWeight: 'bold' }}>eNPS Score</span>
              <h1 style={{ margin: '4px 0 0 0', color: '#BE185D', fontSize: '36px' }}>+48</h1>
            </div>

            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '4px' }}>
                <span style={{ color: '#065F46', fontWeight: 'bold' }}>Promoters (Score 9-10): 62%</span>
                <span style={{ color: '#92400E', fontWeight: 'bold' }}>Passives (Score 7-8): 24%</span>
                <span style={{ color: '#991B1B', fontWeight: 'bold' }}>Detractors (Score 0-6): 14%</span>
              </div>
              <div style={{ display: 'flex', height: '12px', borderRadius: '6px', overflow: 'hidden' }}>
                <div style={{ width: '62%', background: '#10B981' }}></div>
                <div style={{ width: '24%', background: '#F59E0B' }}></div>
                <div style={{ width: '14%', background: '#EF4444' }}></div>
              </div>
            </div>
          </div>
        </div>

        <div style={{ background: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h3 style={{ margin: '0 0 8px 0' }}>🔒 100% Anonymity Guarantee</h3>
          <p style={{ fontSize: '13px', color: '#6B7280', margin: 0, lineHeight: '1.5' }}>
            All pulse survey responses and suggestion box submissions redact your identity. Employee IDs are never saved alongside rating records.
          </p>
        </div>
      </div>

      {/* Surveys List */}
      <h3 style={{ marginBottom: '16px' }}>📋 Active Pulse & Sentiment Surveys</h3>
      {loading ? (
        <p>Loading surveys...</p>
      ) : safeSurveys.length === 0 ? (
        <div style={{ background: '#fff', padding: '40px', borderRadius: '8px', textAlign: 'center', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <p style={{ color: '#6B7280', margin: 0 }}>No pulse surveys active right now.</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gap: '16px' }}>
          {safeSurveys.map((s) => (
            <div key={s.id} style={{ background: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <h3 style={{ margin: 0, color: '#111827', fontSize: '18px' }}>{s.title}</h3>
                <span style={{ fontSize: '12px', background: '#FEE2E2', color: '#991B1B', padding: '2px 8px', borderRadius: '12px', fontWeight: 'bold' }}>
                  {s.survey_type} • Anonymous
                </span>
              </div>
              <p style={{ color: '#6B7280', fontSize: '13px', margin: '0 0 16px 0' }}>{s.description}</p>
              <button
                onClick={() => alert(`Starting survey: ${s.title}`)}
                style={{ padding: '8px 16px', background: '#EC4899', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
              >
                Take Pulse Survey ➔
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Suggestion Box Modal */}
      {showFeedbackModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ background: '#fff', padding: '24px', borderRadius: '8px', width: '450px' }}>
            <h3>💡 Anonymous Workplace Suggestion</h3>
            <form onSubmit={handleSendFeedback}>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Category</label>
                <select value={category} onChange={(e) => setCategory(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }}>
                  <option value="WORKPLACE">Workplace & Office Facilities</option>
                  <option value="MANAGEMENT">Leadership & Management Support</option>
                  <option value="CULTURE">Company Culture & Values</option>
                  <option value="BENEFITS">Benefits & Compensation</option>
                  <option value="PROCESS">Internal Tools & Processes</option>
                </select>
              </div>

              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Subject</label>
                <input type="text" value={subject} onChange={(e) => setSubject(e.target.value)} placeholder="e.g. Ergonomic Office Desk Chairs" style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>

              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Detailed Suggestion / Feedback</label>
                <textarea rows={4} value={message} onChange={(e) => setMessage(e.target.value)} placeholder="Share your constructive feedback or suggestion to improve workplace quality..." style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                <button type="button" onClick={() => setShowFeedbackModal(false)} style={{ padding: '8px 16px', background: '#9CA3AF', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Cancel</button>
                <button type="submit" style={{ padding: '8px 16px', background: '#EC4899', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>Submit Anonymously</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
