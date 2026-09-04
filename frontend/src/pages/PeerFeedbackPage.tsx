import React, { useState } from 'react';

export const PeerFeedbackPage: React.FC = () => {
  const [peerName, setPeerName] = useState('');
  const [rating, setRating] = useState('4.5');
  const [strengths, setStrengths] = useState('');
  const [improvements, setImprovements] = useState('');
  const [isAnonymous, setIsAnonymous] = useState(true);

  const handleSubmitPeerReview = (e: React.FormEvent) => {
    e.preventDefault();
    alert(`360° Peer Feedback submitted for ${peerName}!`);
    setPeerName('');
    setStrengths('');
    setImprovements('');
  };

  return (
    <div style={{ padding: '24px', fontFamily: 'sans-serif' }}>
      <div style={{ marginBottom: '24px' }}>
        <h2>🔄 360° Peer Feedback & Nominations</h2>
        <p style={{ color: '#6B7280', fontSize: '14px' }}>
          Provide multi-rater 360-degree feedback, recognize team competencies, and nominate peers for appraisals.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
        <div style={{ background: '#fff', padding: '24px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h3>Submit 360° Peer Evaluation</h3>
          <form onSubmit={handleSubmitPeerReview}>
            <div style={{ marginBottom: '12px' }}>
              <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Peer / Colleague Name</label>
              <input
                type="text"
                value={peerName}
                onChange={(e) => setPeerName(e.target.value)}
                placeholder="e.g. Alex Morgan (Senior Software Engineer)"
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }}
                required
              />
            </div>

            <div style={{ marginBottom: '12px' }}>
              <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Overall Peer Rating (1.0 - 5.0)</label>
              <input
                type="number"
                step="0.1"
                min="1.0"
                max="5.0"
                value={rating}
                onChange={(e) => setRating(e.target.value)}
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }}
                required
              />
            </div>

            <div style={{ marginBottom: '12px' }}>
              <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Key Strengths & Collaboration Accomplishments</label>
              <textarea
                rows={3}
                value={strengths}
                onChange={(e) => setStrengths(e.target.value)}
                placeholder="Describe exceptional teamwork, technical leadership, or problem solving..."
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }}
                required
              />
            </div>

            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Constructive Growth Suggestions</label>
              <textarea
                rows={3}
                value={improvements}
                onChange={(e) => setImprovements(e.target.value)}
                placeholder="Areas where colleague can improve communication, velocity, or process..."
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }}
                required
              />
            </div>

            <div style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <input
                type="checkbox"
                id="anon"
                checked={isAnonymous}
                onChange={(e) => setIsAnonymous(e.target.checked)}
              />
              <label htmlFor="anon" style={{ fontSize: '14px', color: '#374151' }}>
                Keep feedback 100% anonymous (Hide my identity from colleague)
              </label>
            </div>

            <button type="submit" style={{ padding: '10px 18px', background: '#3B82F6', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>
              Submit 360° Peer Feedback
            </button>
          </form>
        </div>

        <div style={{ background: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', height: 'fit-content' }}>
          <h3>📌 360° Review Guidelines</h3>
          <ul style={{ fontSize: '13px', color: '#4B5563', paddingLeft: '20px', lineHeight: '1.6' }}>
            <li>Provide specific, objective examples of recent teamwork and deliverables.</li>
            <li>Focus on core leadership competencies and behavioral alignment.</li>
            <li>Constructive growth points help managers evaluate calibration accurately.</li>
          </ul>
        </div>
      </div>
    </div>
  );
};
