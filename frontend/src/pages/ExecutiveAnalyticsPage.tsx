import React, { useState, useEffect } from 'react';
import { analyticsApi, ExecutiveSummary, AttritionAnalytics, LaborCostAnalytics } from '../services/api/analytics';

export const ExecutiveAnalyticsPage: React.FC = () => {
  const [summary, setSummary] = useState<ExecutiveSummary | null>(null);
  const [attrition, setAttrition] = useState<AttritionAnalytics | null>(null);
  const [laborCost, setLaborCost] = useState<LaborCostAnalytics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [sData, aData, lData] = await Promise.all([
        analyticsApi.getExecutiveSummary(),
        analyticsApi.getAttritionAnalytics(),
        analyticsApi.getLaborCostAnalytics(),
      ]);
      setSummary(sData);
      setAttrition(aData);
      setLaborCost(lData);
    } catch (err) {
      console.error('Failed to load executive analytics data', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '24px', fontFamily: 'sans-serif' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px', alignItems: 'center' }}>
        <div>
          <h2 style={{ margin: 0 }}>📈 Executive HR Analytics Dashboard</h2>
          <p style={{ color: '#6B7280', fontSize: '14px', margin: '4px 0 0 0' }}>
            Single-pane organizational oversight. Monitor attrition trends, labor expenditures, department KPIs, and employee performance.
          </p>
        </div>
        <button
          onClick={fetchData}
          style={{ padding: '8px 16px', background: '#F3F4F6', color: '#374151', border: '1px solid #D1D5DB', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold', fontSize: '12px' }}
        >
          🔄 Refresh Metrics
        </button>
      </div>

      {loading ? (
        <p>Calculating server-side aggregated metrics...</p>
      ) : summary && attrition && laborCost ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {/* Executive Summary Metrics Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
            <div style={{ background: '#fff', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', borderLeft: '4px solid #2563EB' }}>
              <p style={{ margin: 0, fontSize: '12px', color: '#6B7280' }}>Total Active Headcount</p>
              <h2 style={{ margin: '4px 0 0 0', color: '#1E40AF' }}>{summary.active_employees} Employees</h2>
            </div>
            <div style={{ background: '#fff', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', borderLeft: '4px solid #EF4444' }}>
              <p style={{ margin: 0, fontSize: '12px', color: '#6B7280' }}>Annualized Attrition Rate</p>
              <h2 style={{ margin: '4px 0 0 0', color: '#991B1B' }}>{summary.attrition_rate_pct}%</h2>
            </div>
            <div style={{ background: '#fff', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', borderLeft: '4px solid #10B981' }}>
              <p style={{ margin: 0, fontSize: '12px', color: '#6B7280' }}>Gross Monthly Payroll Spend</p>
              <h2 style={{ margin: '4px 0 0 0', color: '#065F46' }}>₹{Number(summary.total_payroll_cost_inr).toLocaleString('en-IN')}</h2>
            </div>
            <div style={{ background: '#fff', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', borderLeft: '4px solid #8B5CF6' }}>
              <p style={{ margin: 0, fontSize: '12px', color: '#6B7280' }}>Avg. Performance Score</p>
              <h2 style={{ margin: '4px 0 0 0', color: '#5B21B6' }}>{summary.avg_performance_rating} / 5.0</h2>
            </div>
          </div>

          {/* Department Breakdown Table */}
          <div style={{ background: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <h3 style={{ marginTop: 0, borderBottom: '1px solid #E5E7EB', paddingBottom: '10px' }}>Department Headcount & Cost Distribution</h3>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '13px' }}>
              <thead>
                <tr style={{ background: '#F9FAFB', borderBottom: '2px solid #E5E7EB' }}>
                  <th style={{ padding: '10px' }}>Department</th>
                  <th style={{ padding: '10px' }}>Active Staff</th>
                  <th style={{ padding: '10px' }}>Monthly Payroll Spend</th>
                  <th style={{ padding: '10px' }}>Department Attrition</th>
                  <th style={{ padding: '10px' }}>Avg. Performance</th>
                </tr>
              </thead>
              <tbody>
                {attrition.department_breakdown.map((dept, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid #F3F4F6' }}>
                    <td style={{ padding: '10px', fontWeight: 'bold' }}>{dept.department_name}</td>
                    <td style={{ padding: '10px' }}>{dept.headcount} Staff</td>
                    <td style={{ padding: '10px', color: '#059669', fontWeight: 'bold' }}>₹{Number(dept.payroll_cost_inr).toLocaleString('en-IN')}</td>
                    <td style={{ padding: '10px', color: dept.attrition_rate_pct > 5 ? '#DC2626' : '#10B981', fontWeight: 'bold' }}>
                      {dept.attrition_rate_pct}%
                    </td>
                    <td style={{ padding: '10px', fontWeight: 'bold' }}>⭐ {dept.avg_performance} / 5.0</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Monthly Attrition Trend */}
          <div style={{ background: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', borderLeft: '4px solid #F59E0B' }}>
            <h3 style={{ marginTop: 0 }}>Monthly Organizational Attrition Trend</h3>
            <div style={{ display: 'flex', gap: '20px', marginTop: '16px', alignItems: 'flex-end', height: '140px', padding: '16px 0', borderBottom: '1px solid #E5E7EB' }}>
              {attrition.monthly_trend.map((item, idx) => (
                <div key={idx} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 1 }}>
                  <div style={{ fontSize: '11px', fontWeight: 'bold', marginBottom: '4px', color: '#B45309' }}>{item.attrition_pct}%</div>
                  <div style={{ width: '100%', maxWidth: '40px', height: `${item.attrition_pct * 20}px`, background: '#F59E0B', borderRadius: '4px 4px 0 0' }}></div>
                  <span style={{ fontSize: '12px', color: '#6B7280', marginTop: '8px', fontWeight: 'bold' }}>{item.month}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};
