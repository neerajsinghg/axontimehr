import React, { useState, useEffect } from 'react';
import { workforceApi, HeadcountPlan, GapAnalysis, WorkforceForecast } from '../services/api/workforce';

export const HeadcountPlanningPage: React.FC = () => {
  const [plans, setPlans] = useState<HeadcountPlan[]>([]);
  const [gaps, setGaps] = useState<GapAnalysis[]>([]);
  const [forecast, setForecast] = useState<WorkforceForecast | null>(null);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);

  const [year, setYear] = useState('2026');
  const [target, setTarget] = useState('37');
  const [plannedHiring, setPlannedHiring] = useState('15');
  const [budget, setBudget] = useState('18000000');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [pData, gData, fData] = await Promise.all([
        workforceApi.getHeadcountPlans(),
        workforceApi.getGapAnalysis(),
        workforceApi.getForecast(),
      ]);
      setPlans(pData);
      setGaps(gData);
      setForecast(fData);
    } catch (err) {
      console.error('Failed to load workforce planning data', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePlan = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await workforceApi.createHeadcountPlan({
        planning_year: parseInt(year, 10),
        target_headcount: parseInt(target, 10),
        planned_hiring: parseInt(plannedHiring, 10),
        allocated_budget: parseFloat(budget),
      });
      setShowModal(false);
      fetchData();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to create headcount plan');
    }
  };

  return (
    <div style={{ padding: '24px', fontFamily: 'sans-serif' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px', alignItems: 'center' }}>
        <div>
          <h2 style={{ margin: 0 }}>📊 Strategic Workforce Planning & Gap Analysis</h2>
          <p style={{ color: '#6B7280', fontSize: '14px', margin: '4px 0 0 0' }}>
            Model annual headcount targets, staffing gap analysis, skill-based requirements, and labor budget forecasts.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          style={{ padding: '10px 18px', background: '#2563EB', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
        >
          + Create Headcount Plan
        </button>
      </div>

      {/* KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '24px' }}>
        <div style={{ background: '#fff', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', borderLeft: '4px solid #2563EB' }}>
          <p style={{ margin: 0, fontSize: '12px', color: '#6B7280' }}>Target Headcount (2026)</p>
          <h2 style={{ margin: '4px 0 0 0', color: '#1E40AF' }}>{plans[0]?.target_headcount || 37} Staff</h2>
        </div>
        <div style={{ background: '#fff', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', borderLeft: '4px solid #F59E0B' }}>
          <p style={{ margin: 0, fontSize: '12px', color: '#6B7280' }}>Headcount Staffing Gap</p>
          <h2 style={{ margin: '4px 0 0 0', color: '#B45309' }}>{gaps[0]?.headcount_gap || 12} Positions Needed</h2>
        </div>
        <div style={{ background: '#fff', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', borderLeft: '4px solid #10B981' }}>
          <p style={{ margin: 0, fontSize: '12px', color: '#6B7280' }}>Planned Hiring Budget</p>
          <h2 style={{ margin: '4px 0 0 0', color: '#065F46' }}>₹1,80,00,000</h2>
        </div>
        <div style={{ background: '#fff', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', borderLeft: '4px solid #8B5CF6' }}>
          <p style={{ margin: 0, fontSize: '12px', color: '#6B7280' }}>Forecast Confidence</p>
          <h2 style={{ margin: '4px 0 0 0', color: '#5B21B6' }}>High (94%)</h2>
        </div>
      </div>

      {loading ? (
        <p>Loading workforce plans and gap analysis...</p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* Gap Analysis Card */}
          <div style={{ background: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <h3 style={{ marginTop: 0, borderBottom: '1px solid #E5E7EB', paddingBottom: '10px' }}>Department Headcount & Skill Gap Breakdown</h3>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '13px' }}>
              <thead>
                <tr style={{ background: '#F9FAFB', borderBottom: '2px solid #E5E7EB' }}>
                  <th style={{ padding: '10px' }}>Department</th>
                  <th style={{ padding: '10px' }}>Current Staff</th>
                  <th style={{ padding: '10px' }}>Target Requirement</th>
                  <th style={{ padding: '10px' }}>Headcount Gap</th>
                  <th style={{ padding: '10px' }}>Skill Gap Items</th>
                  <th style={{ padding: '10px' }}>Advisory Recommendation</th>
                </tr>
              </thead>
              <tbody>
                {gaps.map((item, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid #F3F4F6' }}>
                    <td style={{ padding: '10px', fontWeight: 'bold' }}>{item.department_name}</td>
                    <td style={{ padding: '10px' }}>{item.current_headcount}</td>
                    <td style={{ padding: '10px' }}>{item.required_headcount}</td>
                    <td style={{ padding: '10px', color: '#DC2626', fontWeight: 'bold' }}>+{item.headcount_gap} Positions</td>
                    <td style={{ padding: '10px' }}>{item.skill_gap_count} Skills Missing</td>
                    <td style={{ padding: '10px', color: '#2563EB', fontWeight: 'bold' }}>{item.advisory_recommendation}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Labor Cost Forecast Card */}
          {forecast && (
            <div style={{ background: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', borderLeft: '4px solid #8B5CF6' }}>
              <h3 style={{ marginTop: 0 }}>Labor Cost Forecast ({forecast.forecast_period})</h3>
              <p style={{ fontSize: '13px', color: '#4B5563', margin: '0 0 12px 0' }}>
                Estimated labor expenditure including projected increments, new headcount salaries, and benefit accruals.
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', background: '#F9FAFB', padding: '16px', borderRadius: '6px' }}>
                <div>
                  <span style={{ fontSize: '12px', color: '#6B7280' }}>Expected Total Headcount</span>
                  <p style={{ margin: '4px 0 0 0', fontWeight: 'bold', fontSize: '16px' }}>{forecast.expected_headcount} Employees</p>
                </div>
                <div>
                  <span style={{ fontSize: '12px', color: '#6B7280' }}>Hiring Need</span>
                  <p style={{ margin: '4px 0 0 0', fontWeight: 'bold', fontSize: '16px', color: '#D97706' }}>+{forecast.expected_hiring_need} Hires</p>
                </div>
                <div>
                  <span style={{ fontSize: '12px', color: '#6B7280' }}>Projected Annual Labor Budget</span>
                  <p style={{ margin: '4px 0 0 0', fontWeight: 'bold', fontSize: '16px', color: '#059669' }}>₹{Number(forecast.expected_labor_cost).toLocaleString('en-IN')}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Modal: Create Headcount Plan */}
      {showModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ background: '#fff', padding: '24px', borderRadius: '8px', width: '450px' }}>
            <h3>Create Annual Headcount Plan</h3>
            <form onSubmit={handleCreatePlan}>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Planning Year</label>
                <input type="number" value={year} onChange={(e) => setYear(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Target Headcount</label>
                <input type="number" value={target} onChange={(e) => setTarget(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Planned Hiring Count</label>
                <input type="number" value={plannedHiring} onChange={(e) => setPlannedHiring(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Allocated Hiring Budget (₹)</label>
                <input type="number" value={budget} onChange={(e) => setBudget(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                <button type="button" onClick={() => setShowModal(false)} style={{ padding: '8px 16px', background: '#9CA3AF', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Cancel</button>
                <button type="submit" style={{ padding: '8px 16px', background: '#2563EB', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>Approve Plan</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
