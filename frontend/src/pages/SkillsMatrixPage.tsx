import React, { useState, useEffect } from 'react';
import { performanceApi, EmployeeSkill } from '../services/api/performance';

export const SkillsMatrixPage: React.FC = () => {
  const [skills, setSkills] = useState<EmployeeSkill[]>([]);
  const [loading, setLoading] = useState(true);

  const [skillName, setSkillName] = useState('');
  const [currentLevel, setCurrentLevel] = useState('3');
  const [targetLevel, setTargetLevel] = useState('5');

  useEffect(() => {
    fetchSkills();
  }, []);

  const fetchSkills = async () => {
    try {
      setLoading(true);
      const data = await performanceApi.getSkillsMatrix();
      setSkills(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Failed to load skills matrix', err);
      setSkills([]);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateSkill = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await performanceApi.updateSkill({
        skill_name: skillName,
        current_level: parseInt(currentLevel, 10),
        target_level: parseInt(targetLevel, 10),
      });
      setSkillName('');
      fetchSkills();
    } catch (err: any) {
      alert('Failed to update skill');
    }
  };

  const safeSkills = Array.isArray(skills) ? skills : [];

  return (
    <div style={{ padding: '24px', fontFamily: 'sans-serif' }}>
      <div style={{ marginBottom: '24px' }}>
        <h2>🧠 Competency & Skills Matrix Gap Analysis</h2>
        <p style={{ color: '#6B7280', fontSize: '14px' }}>
          Evaluate current vs target competency levels and identify skill gaps for career development.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
        {/* Skill Matrix Table */}
        <div style={{ background: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h3>Team Skill Competencies</h3>
          {loading ? (
            <p>Loading skill matrix...</p>
          ) : safeSkills.length === 0 ? (
            <p style={{ color: '#6B7280', marginTop: '12px' }}>No competency skills recorded yet.</p>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '12px' }}>
              <thead>
                <tr style={{ background: '#F9FAFB', textAlign: 'left', borderBottom: '1px solid #E5E7EB' }}>
                  <th style={{ padding: '10px' }}>Skill Name</th>
                  <th style={{ padding: '10px' }}>Category</th>
                  <th style={{ padding: '10px' }}>Current Level</th>
                  <th style={{ padding: '10px' }}>Target Level</th>
                  <th style={{ padding: '10px' }}>Skill Gap</th>
                </tr>
              </thead>
              <tbody>
                {safeSkills.map((s) => (
                  <tr key={s.id} style={{ borderBottom: '1px solid #E5E7EB' }}>
                    <td style={{ padding: '10px', fontWeight: 'bold' }}>{s.skill_name}</td>
                    <td style={{ padding: '10px' }}>{s.category || 'TECHNICAL'}</td>
                    <td style={{ padding: '10px' }}>Level {s.current_level} / 5</td>
                    <td style={{ padding: '10px' }}>Level {s.target_level} / 5</td>
                    <td style={{ padding: '10px' }}>
                      <span style={{
                        padding: '3px 10px',
                        borderRadius: '12px',
                        fontSize: '11px',
                        fontWeight: 'bold',
                        background: s.skill_gap > 0 ? '#FDE8E8' : '#DEF7EC',
                        color: s.skill_gap > 0 ? '#9B1C1C' : '#03543F'
                      }}>
                        {s.skill_gap > 0 ? `Gap: -${s.skill_gap}` : '✓ Target Met'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Add/Update Skill Form */}
        <div style={{ background: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', height: 'fit-content' }}>
          <h3>Update Skill Assessment</h3>
          <form onSubmit={handleUpdateSkill}>
            <div style={{ marginBottom: '12px' }}>
              <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Skill Name</label>
              <input type="text" value={skillName} onChange={(e) => setSkillName(e.target.value)} placeholder="e.g. System Design" style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
            </div>
            <div style={{ marginBottom: '12px' }}>
              <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Current Level (1-5)</label>
              <input type="number" min="1" max="5" value={currentLevel} onChange={(e) => setCurrentLevel(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
            </div>
            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Target Level (1-5)</label>
              <input type="number" min="1" max="5" value={targetLevel} onChange={(e) => setTargetLevel(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
            </div>
            <button type="submit" style={{ width: '100%', padding: '10px', background: '#10B981', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>
              Save Skill Assessment
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
