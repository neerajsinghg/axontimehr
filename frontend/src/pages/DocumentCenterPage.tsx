import React, { useEffect, useState } from 'react';
import { FileText, Download, Plus, Eye, Sparkles } from 'lucide-react';
import { employeeExperienceApi, HRDocumentTemplate, GeneratedHRLetter } from '../services/api/employeeExperience';

export const DocumentCenterPage: React.FC = () => {
  const [templates, setTemplates] = useState<HRDocumentTemplate[]>([]);
  const [letters, setLetters] = useState<GeneratedHRLetter[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [previewHtml, setPreviewHtml] = useState<string | null>(null);

  useEffect(() => {
    loadDocs();
  }, []);

  const loadDocs = async () => {
    try {
      const [tData, lData] = await Promise.all([
        employeeExperienceApi.getDocumentTemplates(),
        employeeExperienceApi.getMyLetters()
      ]);
      setTemplates(tData);
      setLetters(lData);
      if (tData.length > 0) setSelectedTemplate(tData[0].id);
    } catch (err) {
      console.error('Failed to load documents', err);
    }
  };

  const handleGenerate = async () => {
    if (!selectedTemplate) return;
    try {
      const newLetter = await employeeExperienceApi.generateHrLetter({
        template_id: selectedTemplate,
        employee_id: 'me'
      });
      alert(`Letter generated successfully! Number: ${newLetter.letter_number}`);
      loadDocs();
    } catch (err) {
      alert('Error generating letter');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 flex items-center gap-2">
            📑 Digital HR Document Center & Letter Generator
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Generate official HR letters, view employment certificates, and download immutable PDF snapshots.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Letter Generator */}
        <div className="glass-card p-6 rounded-2xl border border-slate-200 bg-white shadow-sm space-y-4">
          <h3 className="font-extrabold text-sm text-slate-900 border-b border-slate-100 pb-2 flex items-center gap-2">
            <Sparkles size={16} className="text-emerald-600" /> Generate Official HR Letter
          </h3>

          <div>
            <label className="block text-xs font-extrabold text-slate-700 mb-1">Select Document Template</label>
            <select
              value={selectedTemplate}
              onChange={(e) => setSelectedTemplate(e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs font-bold text-slate-900"
            >
              {templates.map(t => (
                <option key={t.id} value={t.id}>{t.title} ({t.category})</option>
              ))}
            </select>
          </div>

          <button
            onClick={handleGenerate}
            className="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs flex items-center justify-center gap-2 shadow-md shadow-emerald-600/20"
          >
            <Plus size={16} /> Generate Letter Snapshot
          </button>
        </div>

        {/* Right Column: Issued Letters List */}
        <div className="lg:col-span-2 glass-card p-6 rounded-2xl border border-slate-200 bg-white shadow-sm space-y-4">
          <h3 className="font-extrabold text-sm text-slate-900 border-b border-slate-100 pb-2 flex items-center gap-2">
            <FileText size={16} className="text-emerald-600" /> Issued HR Letters & Certificates
          </h3>

          <div className="space-y-3 text-xs">
            {letters.length === 0 ? (
              <div className="p-8 text-center text-slate-400 font-bold">No issued HR letters found. Click Generate to create one.</div>
            ) : (
              letters.map(letter => (
                <div key={letter.id} className="p-4 rounded-xl border border-slate-200 bg-slate-50/70 hover:bg-slate-50 flex items-center justify-between">
                  <div>
                    <div className="font-extrabold text-slate-900 flex items-center gap-2">
                      {letter.title} <span className="px-2 py-0.5 rounded bg-slate-200 text-slate-700 text-[10px]">{letter.letter_number}</span>
                    </div>
                    <div className="text-[11px] text-slate-500 mt-1">Generated: {new Date(letter.created_at).toLocaleDateString()}</div>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setPreviewHtml(letter.snapshot_html)}
                      className="px-3 py-1.5 rounded-lg border border-slate-300 bg-white hover:bg-slate-100 text-slate-700 font-extrabold flex items-center gap-1 text-[11px]"
                    >
                      <Eye size={14} /> Preview
                    </button>
                    <button
                      onClick={() => alert(`Downloading PDF for ${letter.letter_number}...`)}
                      className="px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-white font-extrabold flex items-center gap-1 text-[11px]"
                    >
                      <Download size={14} /> Download PDF
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* HTML Preview Modal */}
      {previewHtml && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full p-6 space-y-4 max-h-[80vh] overflow-y-auto shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-200 pb-3">
              <h3 className="font-extrabold text-base text-slate-900">📄 HR Document Letter Snapshot</h3>
              <button onClick={() => setPreviewHtml(null)} className="text-slate-400 hover:text-slate-600 font-bold">✕</button>
            </div>
            <div className="p-6 bg-slate-50 border border-slate-200 rounded-xl font-serif text-slate-800 text-sm leading-relaxed" dangerouslySetInnerHTML={{ __html: previewHtml }} />
            <div className="flex justify-end">
              <button onClick={() => setPreviewHtml(null)} className="px-5 py-2 rounded-xl bg-slate-900 text-white font-extrabold text-xs">Close Preview</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
