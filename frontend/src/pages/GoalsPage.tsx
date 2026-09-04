import React, { useState, useEffect } from 'react';
import { performanceApi, Goal, PerformanceCycle } from '../services/api/performance';

export const GoalsPage: React.FC = () => {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [cycles, setCycles] = useState<PerformanceCycle[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  // New Goal Form
  const [cycleId, setCycleId] = useState('');
  const [title, setTitle] = useState('');
  const [goalType, setGoalType] = useState('INDIVIDUAL');
  const [targetValue, setTargetValue] = useState('100');
  const [weightage, setWeightage] = useState('20');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [gData, cData] = await Promise.all([
        performanceApi.getGoals(),
        performanceApi.getCycles(),
      ]);
      setGoals(gData);
      setCycles(cData);
      if (cData.length > 0) {
        setCycleId(cData[0].id);
      }
    } catch (err) {
      console.error('Failed to load goals', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateGoal = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await performanceApi.createGoal({
        cycle_id: cycleId,
        employee_id: 'current_user',
        title,
        goal_type: goalType,
        target_value: parseFloat(targetValue),
        weightage: parseFloat(weightage),
      });
      setShowModal(false);
      setTitle('');
      fetchData();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to create goal');
    }
  };

  const handleUpdateProgress = async (goalId: string, currentVal: number) => {
    const newVal = prompt('Enter new progress value:', String(currentVal));
    if (newVal !== null) {
      try {
        await performanceApi.updateGoalProgress(goalId, { current_value: parseFloat(newVal) });
        fetchData();
      } catch (err: any) {
        alert('Failed to update goal progress');
      }
    }
  };

  return (
    <div style={{ padding: '24px', fontFamily: 'sans-serif' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px' }}>
        <h2>🎯 Cascading Goals & Key Results (OKRs) {cycles.length > 0 && `(${cycles.length} Active Cycles)`}</h2>
        <button
          onClick={() => setShowModal(true)}
          style={{ padding: '10px 18px', background: '#10B981', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer' }}
        >
          + Add Goal / KPI
        </button>
      </div>

      {loading ? (
        <p>Loading goals...</p>
      ) : (
        <div style={{ display: 'grid', gap: '16px' }}>
          {goals.map((g) => (
            <div key={g.id} style={{ background: '#fff', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <h4 style={{ margin: 0, fontSize: '16px', color: '#111827' }}>{g.title}</h4>
                <span style={{ fontSize: '12px', background: '#E0E7FF', color: '#3730A3', padding: '2px 8px', borderRadius: '12px', fontWeight: 'bold' }}>
                  {g.goal_type} • Weight: {g.weightage}%
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                <div style={{ flex: 1, background: '#E5E7EB', borderRadius: '4px', height: '10px', overflow: 'hidden' }}>
                  <div style={{ width: `${g.progress_pct}%`, background: '#10B981', height: '100%' }}></div>
                </div>
                <span style={{ fontSize: '12px', fontWeight: 'bold', color: '#374151' }}>{g.progress_pct}%</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#6B7280' }}>
                <span>Target: {g.target_value} {g.unit}</span>
                <button
                  onClick={() => handleUpdateProgress(g.id, g.current_value)}
                  style={{ background: 'none', border: 'none', color: '#3B82F6', cursor: 'pointer', fontWeight: 'bold' }}
                >
                  ✏️ Update Progress ({g.current_value})
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ background: '#fff', padding: '24px', borderRadius: '8px', width: '400px' }}>
            <h3>Add New Goal</h3>
            <form onSubmit={handleCreateGoal}>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Goal Title</label>
                <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. Achieve ₹ 50 Lakhs Sales Revenue" style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Goal Type</label>
                <select value={goalType} onChange={(e) => setGoalType(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }}>
                  <option value="INDIVIDUAL">INDIVIDUAL</option>
                  <option value="TEAM">TEAM</option>
                  <option value="DEPARTMENT">DEPARTMENT</option>
                  <option value="KPI">KPI</option>
                  <option value="KRA">KRA</option>
                </select>
              </div>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Target Value</label>
                <input type="number" value={targetValue} onChange={(e) => setTargetValue(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Weightage (%)</label>
                <input type="number" value={weightage} onChange={(e) => setWeightage(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                <button type="button" onClick={() => setShowModal(false)} style={{ padding: '8px 16px', background: '#9CA3AF', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Cancel</button>
                <button type="submit" style={{ padding: '8px 16px', background: '#10B981', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Save Goal</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
