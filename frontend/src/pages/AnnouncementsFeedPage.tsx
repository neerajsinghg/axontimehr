import React, { useEffect, useState } from 'react';
import { Award, Sparkles, Megaphone } from 'lucide-react';
import { employeeExperienceApi, CompanyAnnouncement } from '../services/api/employeeExperience';

export const AnnouncementsFeedPage: React.FC = () => {
  const [announcements, setAnnouncements] = useState<CompanyAnnouncement[]>([]);

  useEffect(() => {
    fetchFeed();
  }, []);

  const fetchFeed = async () => {
    try {
      const aData = await employeeExperienceApi.getAnnouncements();
      setAnnouncements(aData);
    } catch (err) {
      console.error('Failed to load feed', err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="border-b border-slate-200 pb-4">
        <h1 className="text-2xl font-black text-slate-900 flex items-center gap-2">
          📢 Internal Communications & Kudos Recognition Feed
        </h1>
        <p className="text-xs text-slate-500 mt-1">Company announcements, townhall notices, emergency updates, and peer recognition cards.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Feed: Announcements */}
        <div className="lg:col-span-2 space-y-4">
          <h3 className="font-extrabold text-sm text-slate-900 flex items-center gap-2">
            <Megaphone size={16} className="text-indigo-600" /> Targeted Company Announcements
          </h3>

          {announcements.map(ann => (
            <div key={ann.id} className="glass-card p-6 rounded-2xl border border-slate-200 bg-white shadow-sm space-y-3 text-xs">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="px-2.5 py-0.5 rounded bg-indigo-100 text-indigo-800 font-extrabold text-[10px]">{ann.category}</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-extrabold ${ann.priority === 'URGENT' ? 'bg-rose-100 text-rose-800' : 'bg-slate-100 text-slate-700'}`}>
                    {ann.priority}
                  </span>
                </div>
                <span className="text-[10px] text-slate-400 font-bold">{new Date(ann.publish_date).toLocaleDateString()}</span>
              </div>

              <h2 className="text-base font-extrabold text-slate-900">{ann.title}</h2>
              <p className="text-slate-600 bg-slate-50 p-4 rounded-xl border border-slate-200 leading-relaxed">{ann.content}</p>
            </div>
          ))}
        </div>

        {/* Right Sidebar: Kudos Recognition Wall */}
        <div className="space-y-4">
          <h3 className="font-extrabold text-sm text-slate-900 flex items-center gap-2">
            <Award size={16} className="text-amber-500" /> Peer Recognition Wall (Kudos)
          </h3>

          <div className="glass-card p-6 rounded-2xl border border-slate-200 bg-white shadow-sm space-y-4 text-xs">
            <div className="p-4 rounded-xl bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-200 space-y-2">
              <div className="font-extrabold text-amber-900 flex items-center gap-1.5">
                <Sparkles size={14} className="text-amber-600" /> Send Kudos to a Colleague
              </div>
              <p className="text-[11px] text-slate-600">Recognize team members for great work, innovation, or leadership!</p>
              <button
                onClick={() => alert('Kudos recognition card submitted!')}
                className="w-full py-2 rounded-xl bg-amber-600 hover:bg-amber-700 text-white font-extrabold text-xs shadow-md shadow-amber-600/20"
              >
                + Give Kudos
              </button>
            </div>

            <div className="space-y-3">
              <div className="p-3.5 rounded-xl border border-slate-200 bg-slate-50 space-y-1.5">
                <div className="flex items-center justify-between font-extrabold text-slate-900">
                  <span>Vikram Aditya ➔ Me</span>
                  <span className="text-[10px] text-amber-600">INNOVATION 💡</span>
                </div>
                <p className="text-slate-600 text-[11px]">"Fantastic architecture execution on Phase 11 ESS Self-Service Portal!"</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
