import React, { useState } from 'react';
import { performanceApi } from '../services/api/performance';

export const CalibrationPage: React.FC = () => {
  const [reviewId, setReviewId] = useState('');
  const [calibScore, setCalibScore] = useState('4.2');
  const [reason, setReason] = useState('');

  const handleCalibrate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reviewId) {
      alert('Please enter a valid Performance Review ID');
      return;
    }
    try {
      await performanceApi.submitCalibration({
        review_id: reviewId,
        calibrated_score: parseFloat(calibScore),
        reason,
      });
      alert('Rating successfully calibrated and finalized!');
      setReviewId('');
      setReason('');
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to calibrate rating');
    }
  };

  return (
    <div style={{ padding: '24px', fontFamily: 'sans-serif' }}>
      <div style={{ marginBottom: '24px' }}>
        <h2>⚖️ HR Performance Rating Calibration</h2>
        <p style={{ color: '#6B7280', fontSize: '14px' }}>
          Calibrate appraisal ratings across departments to ensure fair bell-curve distribution.
        </p>
      </div>

      <div style={{ background: '#fff', padding: '24px', borderRadius: '8px', maxWidth: '600px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <h3>Submit Rating Calibration Override</h3>
        <form onSubmit={handleCalibrate}>
          <div style={{ marginBottom: '12px' }}>
            <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Performance Review ID</label>
            <input
              type="text"
              value={reviewId}
              onChange={(e) => setReviewId(e.target.value)}
              placeholder="e.g. rev-1234-uuid"
              style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }}
              required
            />
          </div>

          <div style={{ marginBottom: '12px' }}>
            <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Calibrated Final Rating Score (1.0 to 5.0)</label>
            <input
              type="number"
              step="0.1"
              min="1.0"
              max="5.0"
              value={calibScore}
              onChange={(e) => setCalibScore(e.target.value)}
              style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }}
              required
            />
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Calibration Business Justification / Notes</label>
            <textarea
              rows={3}
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="State calibration reason (e.g. Department normalization, exceptional leadership contribution)..."
              style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }}
              required
            />
          </div>

          <button type="submit" style={{ padding: '10px 18px', background: '#8B5CF6', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>
            Finalize Calibrated Rating
          </button>
        </form>
      </div>
    </div>
  );
};
