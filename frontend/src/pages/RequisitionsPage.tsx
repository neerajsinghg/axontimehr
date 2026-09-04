import React, { useState, useEffect } from 'react';
import { recruitmentApi, JobRequisition, JobPosting } from '../services/api/recruitment';

export const RequisitionsPage: React.FC = () => {
  const [requisitions, setRequisitions] = useState<JobRequisition[]>([]);
  const [jobPostings, setJobPostings] = useState<JobPosting[]>([]);
  const [loading, setLoading] = useState(true);
  const [showReqModal, setShowReqModal] = useState(false);
  const [showJobModal, setShowJobModal] = useState(false);

  // Form states
  const [positions, setPositions] = useState('2');
  const [location, setLocation] = useState('Bengaluru HQ');
  const [minExp, setMinExp] = useState('3');
  const [maxExp, setMaxExp] = useState('7');
  const [skills, setSkills] = useState('Python, FastAPI, React, PostgreSQL');
  const [salaryMin, setSalaryMin] = useState('1200000');
  const [salaryMax, setSalaryMax] = useState('1800000');

  const [jobTitle, setJobTitle] = useState('');
  const [jobDesc, setJobDesc] = useState('');
  const [jobReqs, setJobReqs] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [reqData, jobData] = await Promise.all([
        recruitmentApi.getRequisitions(),
        recruitmentApi.getJobPostings(),
      ]);
      setRequisitions(reqData);
      setJobPostings(jobData);
    } catch (err) {
      console.error('Failed to load recruitment requisitions', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRequisition = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await recruitmentApi.createRequisition({
        positions_count: parseInt(positions, 10),
        location,
        min_experience: parseInt(minExp, 10),
        max_experience: parseInt(maxExp, 10),
        required_skills: skills,
        salary_min: parseFloat(salaryMin),
        salary_max: parseFloat(salaryMax),
      });
      setShowReqModal(false);
      fetchData();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to create job requisition');
    }
  };

  const handleCreateJobPosting = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await recruitmentApi.createJobPosting({
        title: jobTitle,
        description: jobDesc,
        requirements: jobReqs,
        location,
        openings_count: parseInt(positions, 10),
      });
      setShowJobModal(false);
      setJobTitle('');
      setJobDesc('');
      setJobReqs('');
      fetchData();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to publish job posting');
    }
  };

  return (
    <div style={{ padding: '24px', fontFamily: 'sans-serif' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px', alignItems: 'center' }}>
        <div>
          <h2 style={{ margin: 0 }}>📋 Job Requisitions & Career Postings</h2>
          <p style={{ color: '#6B7280', fontSize: '14px', margin: '4px 0 0 0' }}>
            Manage headcount requisition approvals, hiring budgets, and publish public job listings.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            onClick={() => setShowReqModal(true)}
            style={{ padding: '10px 18px', background: '#2563EB', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
          >
            + Create Requisition
          </button>
          <button
            onClick={() => setShowJobModal(true)}
            style={{ padding: '10px 18px', background: '#059669', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
          >
            + Publish Job Listing
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '24px' }}>
        <div style={{ background: '#fff', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', borderLeft: '4px solid #2563EB' }}>
          <p style={{ margin: 0, fontSize: '12px', color: '#6B7280' }}>Active Requisitions</p>
          <h2 style={{ margin: '4px 0 0 0', color: '#1E40AF' }}>{requisitions.length} Requisitions</h2>
        </div>
        <div style={{ background: '#fff', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', borderLeft: '4px solid #059669' }}>
          <p style={{ margin: 0, fontSize: '12px', color: '#6B7280' }}>Published Job Postings</p>
          <h2 style={{ margin: '4px 0 0 0', color: '#065F46' }}>{jobPostings.length} Live Listings</h2>
        </div>
        <div style={{ background: '#fff', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', borderLeft: '4px solid #8B5CF6' }}>
          <p style={{ margin: 0, fontSize: '12px', color: '#6B7280' }}>Approved Hiring Budget</p>
          <h2 style={{ margin: '4px 0 0 0', color: '#5B21B6' }}>₹54,00,000</h2>
        </div>
        <div style={{ background: '#fff', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', borderLeft: '4px solid #F59E0B' }}>
          <p style={{ margin: 0, fontSize: '12px', color: '#6B7280' }}>Avg. Time-to-Fill</p>
          <h2 style={{ margin: '4px 0 0 0', color: '#B45309' }}>21 Days</h2>
        </div>
      </div>

      {loading ? (
        <p>Loading requisitions and career postings...</p>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
          {/* Requisitions Section */}
          <div style={{ background: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <h3 style={{ marginTop: 0, borderBottom: '1px solid #E5E7EB', paddingBottom: '10px' }}>Active Job Requisitions</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {requisitions.map((req) => (
                <div key={req.id} style={{ border: '1px solid #E5E7EB', borderRadius: '6px', padding: '12px', background: '#F9FAFB' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontWeight: 'bold', fontSize: '14px', color: '#111827' }}>Location: {req.location || 'HQ'}</span>
                    <span style={{ fontSize: '11px', background: '#D1FAE5', color: '#065F46', padding: '2px 8px', borderRadius: '10px', fontWeight: 'bold' }}>
                      {req.status}
                    </span>
                  </div>
                  <p style={{ fontSize: '12px', color: '#4B5563', margin: '6px 0' }}>
                    Target Positions: <b>{req.positions_count}</b> | Exp: <b>{req.min_experience}-{req.max_experience} Yrs</b>
                  </p>
                  <p style={{ fontSize: '12px', color: '#6B7280', margin: 0 }}>
                    Skills: {req.required_skills}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Job Postings Section */}
          <div style={{ background: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
            <h3 style={{ marginTop: 0, borderBottom: '1px solid #E5E7EB', paddingBottom: '10px' }}>Published Career Listings</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {jobPostings.map((job) => (
                <div key={job.id} style={{ border: '1px solid #E5E7EB', borderRadius: '6px', padding: '12px', background: '#F9FAFB' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontWeight: 'bold', fontSize: '14px', color: '#111827' }}>{job.title}</span>
                    <span style={{ fontSize: '11px', background: '#DBEAFE', color: '#1E40AF', padding: '2px 8px', borderRadius: '10px', fontWeight: 'bold' }}>
                      {job.location_type}
                    </span>
                  </div>
                  <p style={{ fontSize: '12px', color: '#4B5563', margin: '6px 0' }}>{job.description}</p>
                  <p style={{ fontSize: '11px', color: '#059669', margin: 0, fontWeight: 'bold' }}>
                    🔗 Public Portal URL: /careers/{job.slug}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Modal: Create Requisition */}
      {showReqModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ background: '#fff', padding: '24px', borderRadius: '8px', width: '450px' }}>
            <h3>Create Job Requisition</h3>
            <form onSubmit={handleCreateRequisition}>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Open Positions Count</label>
                <input type="number" value={positions} onChange={(e) => setPositions(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Location</label>
                <input type="text" value={location} onChange={(e) => setLocation(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '12px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', marginBottom: '4px' }}>Min Exp (Yrs)</label>
                  <input type="number" value={minExp} onChange={(e) => setMinExp(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', marginBottom: '4px' }}>Max Exp (Yrs)</label>
                  <input type="number" value={maxExp} onChange={(e) => setMaxExp(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
                </div>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '12px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', marginBottom: '4px' }}>Salary Min (₹)</label>
                  <input type="number" value={salaryMin} onChange={(e) => setSalaryMin(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '12px', marginBottom: '4px' }}>Salary Max (₹)</label>
                  <input type="number" value={salaryMax} onChange={(e) => setSalaryMax(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
                </div>
              </div>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Required Skills</label>
                <input type="text" value={skills} onChange={(e) => setSkills(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px', marginTop: '16px' }}>
                <button type="button" onClick={() => setShowReqModal(false)} style={{ padding: '8px 16px', background: '#9CA3AF', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Cancel</button>
                <button type="submit" style={{ padding: '8px 16px', background: '#2563EB', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>Submit Requisition</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Publish Job Listing */}
      {showJobModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ background: '#fff', padding: '24px', borderRadius: '8px', width: '450px' }}>
            <h3>Publish Public Job Listing</h3>
            <form onSubmit={handleCreateJobPosting}>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Job Title</label>
                <input type="text" value={jobTitle} onChange={(e) => setJobTitle(e.target.value)} placeholder="e.g. Lead Cloud Architect" style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Description</label>
                <textarea value={jobDesc} onChange={(e) => setJobDesc(e.target.value)} placeholder="Job role overview..." style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Requirements</label>
                <textarea value={jobReqs} onChange={(e) => setJobReqs(e.target.value)} placeholder="Key candidate qualifications..." style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px', marginTop: '16px' }}>
                <button type="button" onClick={() => setShowJobModal(false)} style={{ padding: '8px 16px', background: '#9CA3AF', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Cancel</button>
                <button type="submit" style={{ padding: '8px 16px', background: '#059669', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>Publish Job</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
