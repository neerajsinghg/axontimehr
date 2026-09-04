import React, { useState, useEffect } from 'react';
import { recruitmentApi, Interview, Candidate } from '../services/api/recruitment';

export const InterviewsPage: React.FC = () => {
  const [interviews, setInterviews] = useState<Interview[]>([]);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [selectedInterviewId, setSelectedInterviewId] = useState<string | null>(null);

  // Form states
  const [candidateId, setCandidateId] = useState('');
  const [interviewType, setInterviewType] = useState('TECHNICAL');
  const [meetingUrl, setMeetingUrl] = useState('https://meet.google.com/axon-interview');

  // Feedback states
  const [techScore, setTechScore] = useState('4.5');
  const [commScore, setCommScore] = useState('4.0');
  const [overallRating, setOverallRating] = useState('4.5');
  const [recommendation, setRecommendation] = useState('HIRE');
  const [comments, setComments] = useState('Strong analytical candidate with excellent technical problem-solving capabilities.');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [intData, candData] = await Promise.all([
        recruitmentApi.getInterviews(),
        recruitmentApi.getCandidates(),
      ]);
      setInterviews(intData);
      setCandidates(candData);
      if (candData.length > 0) setCandidateId(candData[0].id);
    } catch (err) {
      console.error('Failed to load interviews', err);
    } finally {
      setLoading(false);
    }
  };

  const handleScheduleInterview = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await recruitmentApi.scheduleInterview({
        candidate_id: candidateId,
        interview_type: interviewType,
        scheduled_at: new Date().toISOString(),
        duration_minutes: 45,
        meeting_url: meetingUrl,
      });
      setShowScheduleModal(false);
      fetchData();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to schedule interview');
    }
  };

  const handleSubmitFeedback = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedInterviewId) return;
    try {
      await recruitmentApi.submitInterviewFeedback({
        interview_id: selectedInterviewId,
        technical_score: parseFloat(techScore),
        communication_score: parseFloat(commScore),
        culture_fit_score: 4.0,
        problem_solving_score: 4.5,
        overall_rating: parseFloat(overallRating),
        recommendation,
        comments,
      });
      setShowFeedbackModal(false);
      alert('Panel interview feedback submitted successfully!');
      fetchData();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to submit feedback');
    }
  };

  return (
    <div style={{ padding: '24px', fontFamily: 'sans-serif' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px', alignItems: 'center' }}>
        <div>
          <h2 style={{ margin: 0 }}>🎙️ Panel Interview Management</h2>
          <p style={{ color: '#6B7280', fontSize: '14px', margin: '4px 0 0 0' }}>
            Schedule interviews, manage panel member slots, and record structured candidate evaluations.
          </p>
        </div>
        <button
          onClick={() => setShowScheduleModal(true)}
          style={{ padding: '10px 18px', background: '#2563EB', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
        >
          + Schedule New Interview
        </button>
      </div>

      {loading ? (
        <p>Loading scheduled interviews...</p>
      ) : interviews.length === 0 ? (
        <div style={{ background: '#fff', padding: '40px', borderRadius: '8px', textAlign: 'center', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <p style={{ color: '#6B7280', margin: 0 }}>No active interview slots scheduled.</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
          {interviews.map((item) => {
            const cand = candidates.find((c) => c.id === item.candidate_id);
            return (
              <div key={item.id} style={{ background: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <span style={{ fontSize: '11px', background: '#DBEAFE', color: '#1E40AF', padding: '2px 8px', borderRadius: '12px', fontWeight: 'bold' }}>
                    {item.interview_type}
                  </span>
                  <span style={{ fontSize: '11px', background: item.status === 'COMPLETED' ? '#D1FAE5' : '#FEF3C7', color: item.status === 'COMPLETED' ? '#065F46' : '#92400E', padding: '2px 8px', borderRadius: '12px', fontWeight: 'bold' }}>
                    {item.status}
                  </span>
                </div>
                <h3 style={{ margin: '6px 0 4px 0', fontSize: '16px', color: '#111827' }}>
                  {cand ? `${cand.first_name} ${cand.last_name}` : 'Candidate Profile'}
                </h3>
                <p style={{ fontSize: '12px', color: '#6B7280', margin: '0 0 12px 0' }}>
                  Scheduled: {new Date(item.scheduled_at).toLocaleString()} (45 Mins)
                </p>

                {item.meeting_url && (
                  <div style={{ marginBottom: '14px' }}>
                    <a
                      href={item.meeting_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ fontSize: '12px', color: '#2563EB', fontWeight: 'bold', textDecoration: 'none', background: '#EFF6FF', padding: '4px 8px', borderRadius: '4px' }}
                    >
                      🎥 Join Meeting Room ↗
                    </a>
                  </div>
                )}

                {item.status !== 'COMPLETED' && (
                  <button
                    onClick={() => { setSelectedInterviewId(item.id); setShowFeedbackModal(true); }}
                    style={{ width: '100%', padding: '8px', background: '#10B981', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '12px', fontWeight: 'bold' }}
                  >
                    Submit Panel Evaluation Feedback
                  </button>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Modal: Schedule Interview */}
      {showScheduleModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ background: '#fff', padding: '24px', borderRadius: '8px', width: '450px' }}>
            <h3>Schedule Interview Slot</h3>
            <form onSubmit={handleScheduleInterview}>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Select Candidate</label>
                <select value={candidateId} onChange={(e) => setCandidateId(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }}>
                  {candidates.map((c) => (
                    <option key={c.id} value={c.id}>{c.first_name} {c.last_name} ({c.email})</option>
                  ))}
                </select>
              </div>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Interview Type</label>
                <select value={interviewType} onChange={(e) => setInterviewType(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }}>
                  <option value="TECHNICAL">TECHNICAL</option>
                  <option value="MANAGERIAL">MANAGERIAL</option>
                  <option value="HR">HR</option>
                  <option value="PANEL">PANEL</option>
                </select>
              </div>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Meeting URL</label>
                <input type="text" value={meetingUrl} onChange={(e) => setMeetingUrl(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                <button type="button" onClick={() => setShowScheduleModal(false)} style={{ padding: '8px 16px', background: '#9CA3AF', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Cancel</button>
                <button type="submit" style={{ padding: '8px 16px', background: '#2563EB', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>Confirm Schedule</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Submit Feedback */}
      {showFeedbackModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ background: '#fff', padding: '24px', borderRadius: '8px', width: '450px' }}>
            <h3>Submit Panel Evaluation Feedback</h3>
            <form onSubmit={handleSubmitFeedback}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '12px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', marginBottom: '4px' }}>Technical Score (1-5)</label>
                  <input type="number" step="0.1" value={techScore} onChange={(e) => setTechScore(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', marginBottom: '4px' }}>Communication Score</label>
                  <input type="number" step="0.1" value={commScore} onChange={(e) => setCommScore(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
                </div>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '12px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', marginBottom: '4px' }}>Overall Rating (1-5)</label>
                  <input type="number" step="0.1" value={overallRating} onChange={(e) => setOverallRating(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', marginBottom: '4px' }}>Recommendation</label>
                  <select value={recommendation} onChange={(e) => setRecommendation(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }}>
                    <option value="STRONG_HIRE">STRONG_HIRE</option>
                    <option value="HIRE">HIRE</option>
                    <option value="HOLD">HOLD</option>
                    <option value="NO_HIRE">NO_HIRE</option>
                  </select>
                </div>
              </div>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '12px', marginBottom: '4px' }}>Interviewer Evaluation Notes</label>
                <textarea value={comments} onChange={(e) => setComments(e.target.value)} rows={3} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                <button type="button" onClick={() => setShowFeedbackModal(false)} style={{ padding: '8px 16px', background: '#9CA3AF', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Cancel</button>
                <button type="submit" style={{ padding: '8px 16px', background: '#10B981', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>Submit Feedback</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
