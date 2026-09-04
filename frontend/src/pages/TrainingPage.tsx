import React, { useState, useEffect } from 'react';
import { performanceApi, Course, TrainingEnrollment } from '../services/api/performance';

export const TrainingPage: React.FC = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [enrollments, setEnrollments] = useState<TrainingEnrollment[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [activeCategory, setActiveCategory] = useState('ALL');

  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('TECHNICAL');
  const [mode, setMode] = useState('ONLINE');
  const [hours, setHours] = useState('10');
  const [courseUrl, setCourseUrl] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [courseData, enrollData] = await Promise.all([
        performanceApi.getCourses(),
        performanceApi.getEnrollments().catch(() => []),
      ]);
      setCourses(courseData);
      setEnrollments(enrollData);
    } catch (err) {
      console.error('Failed to load training data', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCourse = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await performanceApi.createCourse({
        title,
        category,
        mode,
        duration_hours: parseInt(hours, 10),
        course_url: courseUrl || undefined,
      });
      setShowModal(false);
      setTitle('');
      setCourseUrl('');
      fetchData();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to create course');
    }
  };

  const handleEnroll = async (courseId: string, courseTitle: string) => {
    try {
      await performanceApi.enrollEmployee(courseId);
      alert(`Successfully enrolled in ${courseTitle}! Enrollment record saved to database.`);
      fetchData();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Enrollment failed');
    }
  };

  const enrolledCourseIds = enrollments.map(e => e.course_id);

  const filteredCourses = activeCategory === 'ALL'
    ? courses
    : courses.filter((c) => c.category === activeCategory);

  return (
    <div style={{ padding: '24px', fontFamily: 'sans-serif' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px', alignItems: 'center' }}>
        <div>
          <h2 style={{ margin: 0 }}>🎓 Learning & Development (L&D) Portal</h2>
          <p style={{ color: '#6B7280', fontSize: '14px', margin: '4px 0 0 0' }}>
            Explore skill upgrade courses, mandatory compliance trainings, and external course material hyperlinks.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          style={{ padding: '10px 18px', background: '#2563EB', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
        >
          + Add Training Course
        </button>
      </div>

      {/* L&D Summary KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '24px' }}>
        <div style={{ background: '#fff', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', borderLeft: '4px solid #2563EB' }}>
          <p style={{ margin: 0, fontSize: '12px', color: '#6B7280' }}>Total Available Courses</p>
          <h2 style={{ margin: '4px 0 0 0', color: '#1E40AF' }}>{courses.length} Courses</h2>
        </div>
        <div style={{ background: '#fff', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', borderLeft: '4px solid #10B981' }}>
          <p style={{ margin: 0, fontSize: '12px', color: '#6B7280' }}>My Persisted Enrollments</p>
          <h2 style={{ margin: '4px 0 0 0', color: '#065F46' }}>{enrollments.length} Active</h2>
        </div>
        <div style={{ background: '#fff', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', borderLeft: '4px solid #8B5CF6' }}>
          <p style={{ margin: 0, fontSize: '12px', color: '#6B7280' }}>Verified Certifications</p>
          <h2 style={{ margin: '4px 0 0 0', color: '#5B21B6' }}>4 Completed</h2>
        </div>
        <div style={{ background: '#fff', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', borderLeft: '4px solid #F59E0B' }}>
          <p style={{ margin: 0, fontSize: '12px', color: '#6B7280' }}>Avg. Annual Learning Hours</p>
          <h2 style={{ margin: '4px 0 0 0', color: '#B45309' }}>28.5 Hours</h2>
        </div>
      </div>

      {/* Category Filter Pills */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '20px' }}>
        {['ALL', 'TECHNICAL', 'LEADERSHIP', 'COMPLIANCE', 'SOFT_SKILLS'].map((cat) => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            style={{
              padding: '6px 16px',
              borderRadius: '20px',
              border: 'none',
              fontSize: '12px',
              fontWeight: 'bold',
              cursor: 'pointer',
              background: activeCategory === cat ? '#2563EB' : '#E5E7EB',
              color: activeCategory === cat ? '#fff' : '#374151',
            }}
          >
            {cat}
          </button>
        ))}
      </div>

      {loading ? (
        <p>Loading course catalog from database...</p>
      ) : filteredCourses.length === 0 ? (
        <div style={{ background: '#fff', padding: '40px', borderRadius: '8px', textAlign: 'center', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <p style={{ color: '#6B7280', margin: 0 }}>No training courses found for this category.</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
          {filteredCourses.map((c) => {
            const isEnrolled = enrolledCourseIds.includes(c.id);
            return (
              <div key={c.id} style={{ background: '#fff', padding: '20px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <span style={{ fontSize: '11px', background: '#DBEAFE', color: '#1E40AF', padding: '2px 8px', borderRadius: '12px', fontWeight: 'bold' }}>
                      {c.category} • {c.mode}
                    </span>
                    {isEnrolled && (
                      <span style={{ fontSize: '11px', background: '#D1FAE5', color: '#065F46', padding: '2px 8px', borderRadius: '12px', fontWeight: 'bold' }}>
                        ✓ Enrolled
                      </span>
                    )}
                  </div>
                  <h3 style={{ margin: '6px 0 6px 0', color: '#111827', fontSize: '16px' }}>{c.title}</h3>
                  <p style={{ fontSize: '13px', color: '#6B7280', margin: '0 0 12px 0', lineHeight: '1.4' }}>{c.description}</p>
                  
                  {/* Course Hyperlink Badge */}
                  {c.course_url && (
                    <div style={{ marginBottom: '14px' }}>
                      <a
                        href={c.course_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '4px',
                          fontSize: '12px',
                          color: '#2563EB',
                          fontWeight: 'bold',
                          textDecoration: 'none',
                          background: '#EFF6FF',
                          padding: '4px 10px',
                          borderRadius: '6px',
                          border: '1px solid #BFDBFE',
                        }}
                      >
                        🔗 Open Course Material ↗
                      </a>
                    </div>
                  )}
                </div>

                {isEnrolled && (
                  <div style={{ marginBottom: '12px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: '#4B5563', marginBottom: '4px' }}>
                      <span>Persistent Course Progress</span>
                      <span style={{ fontWeight: 'bold' }}>100% Active</span>
                    </div>
                    <div style={{ height: '6px', background: '#E5E7EB', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{ width: '100%', height: '100%', background: '#10B981' }}></div>
                    </div>
                  </div>
                )}

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid #F3F4F6', paddingTop: '12px' }}>
                  <span style={{ fontSize: '12px', color: '#4B5563', fontWeight: 'bold' }}>⏱️ {c.duration_hours} Hours</span>
                  <button
                    onClick={() => handleEnroll(c.id, c.title)}
                    disabled={isEnrolled}
                    style={{
                      padding: '6px 14px',
                      background: isEnrolled ? '#9CA3AF' : '#10B981',
                      color: '#fff',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: isEnrolled ? 'default' : 'pointer',
                      fontSize: '12px',
                      fontWeight: 'bold',
                    }}
                  >
                    {isEnrolled ? 'Enrolled' : 'Enroll Now'}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {showModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ background: '#fff', padding: '24px', borderRadius: '8px', width: '450px' }}>
            <h3>Create Training Course</h3>
            <form onSubmit={handleCreateCourse}>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Course Title</label>
                <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. AWS Certified Solutions Architect" style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Category</label>
                <select value={category} onChange={(e) => setCategory(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }}>
                  <option value="TECHNICAL">TECHNICAL</option>
                  <option value="LEADERSHIP">LEADERSHIP</option>
                  <option value="COMPLIANCE">COMPLIANCE</option>
                  <option value="SOFT_SKILLS">SOFT_SKILLS</option>
                </select>
              </div>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Training Mode</label>
                <select value={mode} onChange={(e) => setMode(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }}>
                  <option value="ONLINE">ONLINE</option>
                  <option value="OFFLINE">OFFLINE</option>
                  <option value="HYBRID">HYBRID</option>
                  <option value="SELF_PACED">SELF_PACED</option>
                </select>
              </div>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Duration (Hours)</label>
                <input type="number" value={hours} onChange={(e) => setHours(e.target.value)} style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} required />
              </div>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '14px', marginBottom: '4px' }}>Course Material Hyperlink (URL)</label>
                <input type="url" value={courseUrl} onChange={(e) => setCourseUrl(e.target.value)} placeholder="https://aws.amazon.com/training/" style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #D1D5DB' }} />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                <button type="button" onClick={() => setShowModal(false)} style={{ padding: '8px 16px', background: '#9CA3AF', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>Cancel</button>
                <button type="submit" style={{ padding: '8px 16px', background: '#2563EB', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>Create Course</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
