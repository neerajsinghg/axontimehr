import React, { useState, useEffect } from 'react';
import { performanceApi, PerformanceCycle, PerformanceReview } from '../services/api/performance';

export const PerformanceReviewsPage: React.FC = () => {
  const [cycles, setCycles] = useState<PerformanceCycle[]>([]);
  const [selectedCycleId, setSelectedCycleId] = useState('');
  const [review, setReview] = useState<PerformanceReview | null>(null);
  const [loading, setLoading] = useState(true);

  const [selfScore, setSelfScore] = useState('4.0');
  const [selfComments, setSelfComments] = useState('');
  const [mgrScore, setMgrScore] = useState('4.5');

  useEffect(() => {
    fetchCycles();
  }, []);

  const fetchCycles = async () => {
    try {
      setLoading(true);
      const data = await performanceApi.getCycles();
      setCycles(data);
      if (data.length > 0) {
        setSelectedCycleId(data[0].id);
        fetchReview(data[0].id);
      } else {
        setLoading(false);
      }
    } catch (err) {
      console.error('Failed to load cycles', err);
      setLoading(false);
    }
  };

  const fetchReview = async (cId: string) => {
    try {
      setLoading(true);
      const rData = await performanceApi.getMyReview(cId);
      setReview(rData);
    } catch (err) {
      console.error('Failed to load review', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitSelf = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!review) return;
    try {
      const updated = await performanceApi.submitSelfAssessment(review.id, {
        self_score: parseFloat(selfScore),
        employee_comments: selfComments,
      });
      setReview(updated);
      alert('Self-assessment submitted successfully!');
    } catch (err) {
      alert('Failed to submit self-assessment');
    }
  };

  const handleSubmitManager = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!review) return;
    try {
      const updated = await performanceApi.submitManagerAssessment(review.id, {
        manager_score: parseFloat(mgrScore),
      });
      setReview(updated);
      alert('Manager assessment submitted successfully!');
    } catch (err) {
      alert('Failed to submit manager assessment');
    }
  };

  return (
    <div style={{ padding: '24px', fontFamily: 'sans-serif' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <h2>📝 Performance Appraisals & Self-Evaluation</h2>
          <p style={{ color: '#6B7280', fontSize: '14px', margin: 0 }}>
            Complete your self-assessment, review manager feedback, and track your overall rating score.
          </p>
        </div>
        {cycles.length > 0 && (
          <select
            value={selectedCycleId}
            onChange={(e) => {
              setSelectedCycleId(e.target.value);
              fetchReview(e.target.value);
            }}
            style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #D1D5DB' }}
          >
            {cycles.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        )}
      </div>

      {loading ? (
        <p>Loading appraisal details...</p>
      ) : !review ? (
        <p style={{ color: '#6B7280' }}>No active performance review record found for this cycle.</p>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
          {/* Self Assessment Form */}
          <div style={{ background: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <h3>1️⃣ Employee Self-Assessment</h3>
            <form onSubmit={handleSubmitSelf}>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Self Rating (1.0 to 5.0)</label>
                <input
                  type="number"
                  step="0.1"
                  min="1.0"
                  max="5.0"
                  value={selfScore}
                  onChange={(e) => setSelfScore(e.target.value)}
                  style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }}
                  disabled={review.status !== 'SELF_ASSESSMENT_PENDING'}
                  required
                />
              </div>

              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Key Accomplishments & Notes</label>
                <textarea
                  rows={4}
                  value={selfComments}
                  onChange={(e) => setSelfComments(e.target.value)}
                  placeholder="Summarize your key achievements, challenges overcome, and growth areas..."
                  style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }}
                  disabled={review.status !== 'SELF_ASSESSMENT_PENDING'}
                  required
                />
              </div>

              {review.status === 'SELF_ASSESSMENT_PENDING' && (
                <button type="submit" style={{ padding: '10px 18px', background: '#3B82F6', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>
                  Submit Self-Assessment
                </button>
              )}
              {review.self_score !== null && (
                <p style={{ color: '#10B981', fontWeight: 'bold' }}>✓ Self Assessment Submitted ({review.self_score} / 5.0)</p>
              )}
            </form>
          </div>

          {/* Manager Assessment Form */}
          <div style={{ background: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <h3>2️⃣ Manager Evaluation & Overall Score</h3>
            <form onSubmit={handleSubmitManager}>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Manager Rating (1.0 to 5.0)</label>
                <input
                  type="number"
                  step="0.1"
                  min="1.0"
                  max="5.0"
                  value={mgrScore}
                  onChange={(e) => setMgrScore(e.target.value)}
                  style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }}
                  disabled={review.status !== 'MANAGER_REVIEW_PENDING'}
                  required
                />
              </div>

              <div style={{ padding: '16px', background: '#F3F4F6', borderRadius: '8px', marginBottom: '16px' }}>
                <p style={{ margin: '0 0 4px 0', fontSize: '12px', color: '#6B7280' }}>Calculated Final Rating Score</p>
                <h2 style={{ margin: 0, color: '#10B981' }}>
                  {review.final_score ? `${review.final_score} / 5.0` : 'Pending Evaluation'}
                </h2>
              </div>

              {review.status === 'MANAGER_REVIEW_PENDING' && (
                <button type="submit" style={{ padding: '10px 18px', background: '#10B981', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>
                  Submit Manager Evaluation
                </button>
              )}
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
