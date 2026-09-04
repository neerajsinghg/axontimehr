import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { performanceApi, PerformanceCycle, Goal } from '../services/api/performance';

export const PerformanceDashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [cycles, setCycles] = useState<PerformanceCycle[]>([]);
  const [goals, setGoals] = useState<Goal[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [cycleData, goalData] = await Promise.all([
        performanceApi.getCycles(),
        performanceApi.getGoals(),
      ]);
      setCycles(cycleData);
      setGoals(goalData);
    } catch (err) {
      console.error('Failed to load performance data', err);
    } finally {
      setLoading(false);
    }
  };

  const avgProgress = goals.length
    ? (goals.reduce((acc, g) => acc + Number(g.progress_pct), 0) / goals.length).toFixed(1)
    : '0.0';

  return (
    <div style={{ padding: '24px', fontFamily: 'sans-serif' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px', alignItems: 'center' }}>
        <div>
          <h2 style={{ margin: 0 }}>🎯 Performance & Goal Management Hub</h2>
          <p style={{ color: '#6B7280', fontSize: '14px', margin: '4px 0 0 0' }}>
            Monitor performance cycle timelines, active cascading goals, appraisal reviews, and skill readiness.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            onClick={() => navigate('/performance/goals')}
            style={{ padding: '10px 18px', background: '#3B82F6', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
          >
            🎯 View Goals & OKRs
          </button>
          <button
            onClick={() => navigate('/performance/reviews')}
            style={{ padding: '10px 18px', background: '#10B981', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
          >
            📝 Start Self-Assessment
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        <div style={{ background: '#fff', padding: '16px', borderRadius: '8px', borderLeft: '4px solid #10B981', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <p style={{ color: '#6B7280', fontSize: '12px', margin: 0 }}>Active Performance Cycles</p>
          <h3 style={{ fontSize: '24px', margin: '4px 0 0 0', color: '#111827' }}>{cycles.length}</h3>
        </div>

        <div style={{ background: '#fff', padding: '16px', borderRadius: '8px', borderLeft: '4px solid #3B82F6', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <p style={{ color: '#6B7280', fontSize: '12px', margin: 0 }}>Total Assigned Goals</p>
          <h3 style={{ fontSize: '24px', margin: '4px 0 0 0', color: '#111827' }}>{goals.length}</h3>
        </div>

        <div style={{ background: '#fff', padding: '16px', borderRadius: '8px', borderLeft: '4px solid #8B5CF6', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <p style={{ color: '#6B7280', fontSize: '12px', margin: 0 }}>Average Goal Completion</p>
          <h3 style={{ fontSize: '24px', margin: '4px 0 0 0', color: '#111827' }}>{avgProgress}%</h3>
        </div>

        <div style={{ background: '#fff', padding: '16px', borderRadius: '8px', borderLeft: '4px solid #F59E0B', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <p style={{ color: '#6B7280', fontSize: '12px', margin: 0 }}>Company Target Rating</p>
          <h3 style={{ fontSize: '24px', margin: '4px 0 0 0', color: '#B45309' }}>4.2 / 5.0</h3>
        </div>
      </div>

      {/* Target Bell Curve & 9-Box Grid Overview */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px', marginBottom: '24px' }}>
        <div style={{ background: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h3 style={{ margin: '0 0 12px 0' }}>📊 Target Bell-Curve Rating Distribution</h3>
          <p style={{ color: '#6B7280', fontSize: '13px', margin: '0 0 16px 0' }}>
            Recommended appraisal distribution targets for annual rating calibration:
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '12px', textAlign: 'center' }}>
            <div style={{ background: '#FEF2F2', padding: '12px', borderRadius: '6px', border: '1px solid #FCA5A5' }}>
              <span style={{ fontSize: '12px', color: '#991B1B', fontWeight: 'bold' }}>Rating 1 (Needs Imp.)</span>
              <h2 style={{ margin: '6px 0 0 0', color: '#991B1B' }}>5%</h2>
            </div>
            <div style={{ background: '#FFFBEB', padding: '12px', borderRadius: '6px', border: '1px solid #FCD34D' }}>
              <span style={{ fontSize: '12px', color: '#92400E', fontWeight: 'bold' }}>Rating 2 (Developing)</span>
              <h2 style={{ margin: '6px 0 0 0', color: '#92400E' }}>15%</h2>
            </div>
            <div style={{ background: '#EFF6FF', padding: '12px', borderRadius: '6px', border: '1px solid #93C5FD' }}>
              <span style={{ fontSize: '12px', color: '#1E40AF', fontWeight: 'bold' }}>Rating 3 (Solid Perf.)</span>
              <h2 style={{ margin: '6px 0 0 0', color: '#1E40AF' }}>50%</h2>
            </div>
            <div style={{ background: '#ECFDF5', padding: '12px', borderRadius: '6px', border: '1px solid #6EE7B7' }}>
              <span style={{ fontSize: '12px', color: '#065F46', fontWeight: 'bold' }}>Rating 4 (Exceeds)</span>
              <h2 style={{ margin: '6px 0 0 0', color: '#065F46' }}>20%</h2>
            </div>
            <div style={{ background: '#F5F3FF', padding: '12px', borderRadius: '6px', border: '1px solid #C4B5FD' }}>
              <span style={{ fontSize: '12px', color: '#5B21B6', fontWeight: 'bold' }}>Rating 5 (Outstanding)</span>
              <h2 style={{ margin: '6px 0 0 0', color: '#5B21B6' }}>10%</h2>
            </div>
          </div>
        </div>

        <div style={{ background: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h3 style={{ margin: '0 0 12px 0' }}>⚡ Quick Links</h3>
          <div style={{ display: 'grid', gap: '10px' }}>
            <button onClick={() => navigate('/performance/calibration')} style={{ textAlign: 'left', padding: '12px', background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '6px', cursor: 'pointer', fontWeight: '600' }}>
              ⚖️ HR Rating Calibration Matrix ➔
            </button>
            <button onClick={() => navigate('/training')} style={{ textAlign: 'left', padding: '12px', background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '6px', cursor: 'pointer', fontWeight: '600' }}>
              🎓 L&D Training Catalog ➔
            </button>
            <button onClick={() => navigate('/skills/matrix')} style={{ textAlign: 'left', padding: '12px', background: '#F9FAFB', border: '1px solid #E5E7EB', borderRadius: '6px', cursor: 'pointer', fontWeight: '600' }}>
              🧠 Skills & Competency Matrix ➔
            </button>
          </div>
        </div>
      </div>

      {/* Active Cycles Section */}
      <div style={{ background: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
        <h3>📅 Active Performance Cycles</h3>
        {loading ? (
          <p>Loading cycles...</p>
        ) : cycles.length === 0 ? (
          <p style={{ color: '#6B7280' }}>No active performance cycles found.</p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '12px' }}>
            <thead>
              <tr style={{ background: '#F9FAFB', textAlign: 'left', borderBottom: '1px solid #E5E7EB' }}>
                <th style={{ padding: '10px' }}>Cycle Name</th>
                <th style={{ padding: '10px' }}>Type</th>
                <th style={{ padding: '10px' }}>Start Date</th>
                <th style={{ padding: '10px' }}>End Date</th>
                <th style={{ padding: '10px' }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {cycles.map((c) => (
                <tr key={c.id} style={{ borderBottom: '1px solid #E5E7EB' }}>
                  <td style={{ padding: '10px', fontWeight: 'bold' }}>{c.name}</td>
                  <td style={{ padding: '10px' }}>{c.cycle_type}</td>
                  <td style={{ padding: '10px' }}>{c.start_date}</td>
                  <td style={{ padding: '10px' }}>{c.end_date}</td>
                  <td style={{ padding: '10px' }}>
                    <span style={{ padding: '3px 8px', borderRadius: '12px', fontSize: '11px', background: '#DEF7EC', color: '#03543F', fontWeight: 'bold' }}>
                      {c.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
