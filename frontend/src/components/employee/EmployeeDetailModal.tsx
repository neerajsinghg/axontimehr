import React, { useState, useEffect } from 'react';
import {
  X,
  FileText,
  Trash2,
  CheckCircle2,
} from 'lucide-react';
import { employeeApi, Employee, EmployeeDocument } from '../../services/api/employee';

interface EmployeeDetailModalProps {
  employeeId: string | null;
  onClose: () => void;
  onStatusChange: () => void;
}

export const EmployeeDetailModal: React.FC<EmployeeDetailModalProps> = ({
  employeeId,
  onClose,
  onStatusChange,
}) => {
  const [employee, setEmployee] = useState<Employee | null>(null);
  const [documents, setDocuments] = useState<EmployeeDocument[]>([]);
  const [activeTab, setActiveTab] = useState<'profile' | 'documents' | 'status'>('profile');
  const [loading, setLoading] = useState(false);
  const [updating, setUpdating] = useState(false);

  // Status Lifecycle change form
  const [newStatus, setNewStatus] = useState<string>('ACTIVE');
  const [statusReason, setStatusReason] = useState('');

  // Document upload metadata form
  const [docType, setDocType] = useState('CONTRACT');
  const [docName, setDocName] = useState('');
  const [docKey, setDocKey] = useState('');

  const fetchDetail = async () => {
    if (!employeeId) return;
    try {
      setLoading(true);
      const [emp, docs] = await Promise.all([
        employeeApi.getEmployee(employeeId),
        employeeApi.getDocuments(employeeId),
      ]);
      setEmployee(emp);
      setDocuments(docs);
      setNewStatus(emp.status);
    } catch (err) {
      console.error('Failed to load employee detail:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetail();
  }, [employeeId]);

  if (!employeeId) return null;

  const handleUpdateStatus = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!employee) return;
    try {
      setUpdating(true);
      await employeeApi.updateStatus(employee.id, newStatus, statusReason);
      await fetchDetail();
      onStatusChange();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to update status');
    } finally {
      setUpdating(false);
    }
  };

  const handleAddDocument = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!employee || !docName || !docKey) return;
    try {
      setUpdating(true);
      const added = await employeeApi.addDocument(employee.id, {
        document_type: docType,
        file_name: docName,
        storage_key: docKey,
      });
      setDocuments([...documents, added]);
      setDocName('');
      setDocKey('');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to attach document metadata');
    } finally {
      setUpdating(false);
    }
  };

  const handleDeleteDocument = async (docId: string) => {
    if (!employee || !confirm('Are you sure you want to remove this document metadata reference?')) return;
    try {
      await employeeApi.deleteDocument(employee.id, docId);
      setDocuments(documents.filter((d) => d.id !== docId));
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to delete document');
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="glass-card bg-white w-full max-w-3xl rounded-2xl border border-emerald-200 shadow-2xl overflow-hidden text-xs">
        {/* Modal Top Bar */}
        <div className="px-6 py-4 border-b border-emerald-100 flex items-center justify-between bg-emerald-50/60">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-600 text-white font-bold flex items-center justify-center text-sm shadow-md">
              {employee ? `${employee.first_name[0]}${employee.last_name[0]}` : 'E'}
            </div>
            <div>
              <h2 className="font-extrabold text-sm text-slate-900">
                {employee ? `${employee.first_name} ${employee.last_name}` : 'Employee Detail'}
              </h2>
              <p className="text-[11px] text-slate-500 font-mono">ID: {employee?.employee_id}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {loading ? (
          <div className="p-12 text-center text-slate-500 font-medium">Loading profile details...</div>
        ) : !employee ? (
          <div className="p-12 text-center text-rose-500 font-medium">Employee record not found.</div>
        ) : (
          <div>
            {/* Modal Navigation Tabs */}
            <div className="px-6 pt-4 border-b border-emerald-100 flex gap-4 bg-emerald-50/30">
              <button
                onClick={() => setActiveTab('profile')}
                className={`pb-3 font-bold border-b-2 transition-all ${
                  activeTab === 'profile'
                    ? 'border-emerald-600 text-emerald-800'
                    : 'border-transparent text-slate-500 hover:text-slate-800'
                }`}
              >
                Overview & Profile
              </button>
              <button
                onClick={() => setActiveTab('documents')}
                className={`pb-3 font-bold border-b-2 transition-all ${
                  activeTab === 'documents'
                    ? 'border-emerald-600 text-emerald-800'
                    : 'border-transparent text-slate-500 hover:text-slate-800'
                }`}
              >
                Documents ({documents.length})
              </button>
              <button
                onClick={() => setActiveTab('status')}
                className={`pb-3 font-bold border-b-2 transition-all ${
                  activeTab === 'status'
                    ? 'border-emerald-600 text-emerald-800'
                    : 'border-transparent text-slate-500 hover:text-slate-800'
                }`}
              >
                Lifecycle & Status
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 space-y-4 max-h-[70vh] overflow-y-auto">
              {/* Tab 1: Profile */}
              {activeTab === 'profile' && (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 p-4 rounded-xl bg-emerald-50/60 border border-emerald-200">
                    <div>
                      <span className="text-[10px] text-slate-500 uppercase font-bold">Department</span>
                      <p className="font-bold text-slate-900 mt-0.5">{employee.department?.name || 'Unassigned'}</p>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-500 uppercase font-bold">Designation</span>
                      <p className="font-bold text-slate-900 mt-0.5">{employee.designation?.name || 'Standard'}</p>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-500 uppercase font-bold">Branch Location</span>
                      <p className="font-bold text-slate-900 mt-0.5">{employee.branch?.name || 'HQ Office'}</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="p-4 rounded-xl border border-emerald-100 bg-white space-y-2">
                      <h4 className="font-bold text-slate-900 uppercase text-[10px] tracking-wider text-emerald-800">
                        Contact Details
                      </h4>
                      <p className="text-slate-700"><strong>Work Email:</strong> {employee.email}</p>
                      <p className="text-slate-700"><strong>Personal Email:</strong> {employee.personal_email || 'N/A'}</p>
                      <p className="text-slate-700"><strong>Phone:</strong> {employee.phone || 'N/A'}</p>
                    </div>

                    <div className="p-4 rounded-xl border border-emerald-100 bg-white space-y-2">
                      <h4 className="font-bold text-slate-900 uppercase text-[10px] tracking-wider text-emerald-800">
                        Employment Metadata
                      </h4>
                      <p className="text-slate-700"><strong>Status:</strong> <span className="font-bold text-emerald-700">{employee.status}</span></p>
                      <p className="text-slate-700"><strong>Joining Date:</strong> {employee.joining_date}</p>
                      <p className="text-slate-700">
                        <strong>Reporting Manager:</strong>{' '}
                        {employee.manager
                          ? `${employee.manager.first_name} ${employee.manager.last_name}`
                          : 'No Direct Manager'}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Tab 2: Documents */}
              {activeTab === 'documents' && (
                <div className="space-y-4">
                  {/* Add Document Metadata Form */}
                  <form onSubmit={handleAddDocument} className="p-4 rounded-xl bg-emerald-50/60 border border-emerald-200 space-y-3">
                    <h4 className="font-bold text-slate-900">Attach Document Reference</h4>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                      <select
                        value={docType}
                        onChange={(e) => setDocType(e.target.value)}
                        className="bg-white border border-emerald-200 rounded-lg px-2.5 py-1.5 font-medium"
                      >
                        <option value="CONTRACT">Employment Contract</option>
                        <option value="ID_PROOF">Government ID</option>
                        <option value="TAX_FORM">Tax Document</option>
                        <option value="CERTIFICATE">Certificate</option>
                      </select>
                      <input
                        type="text"
                        placeholder="Document File Name"
                        value={docName}
                        onChange={(e) => setDocName(e.target.value)}
                        className="bg-white border border-emerald-200 rounded-lg px-2.5 py-1.5 font-medium"
                        required
                      />
                      <input
                        type="text"
                        placeholder="Storage S3/Cloud Key"
                        value={docKey}
                        onChange={(e) => setDocKey(e.target.value)}
                        className="bg-white border border-emerald-200 rounded-lg px-2.5 py-1.5 font-medium"
                        required
                      />
                    </div>
                    <div className="flex justify-end">
                      <button
                        type="submit"
                        disabled={updating}
                        className="px-3 py-1.5 rounded-lg bg-emerald-600 text-white font-bold text-xs"
                      >
                        Add Document Metadata
                      </button>
                    </div>
                  </form>

                  {/* Documents List Table */}
                  <div className="rounded-xl border border-emerald-100 overflow-hidden bg-white">
                    <table className="w-full text-left text-xs text-slate-700">
                      <thead className="bg-emerald-50 text-emerald-900 font-bold uppercase border-b border-emerald-100">
                        <tr>
                          <th className="px-4 py-2.5">Type</th>
                          <th className="px-4 py-2.5">File Name</th>
                          <th className="px-4 py-2.5">Key / Path</th>
                          <th className="px-4 py-2.5 text-right">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-emerald-50">
                        {documents.length === 0 ? (
                          <tr>
                            <td colSpan={4} className="px-4 py-6 text-center text-slate-400">
                              No attached documents found.
                            </td>
                          </tr>
                        ) : (
                          documents.map((doc) => (
                            <tr key={doc.id} className="hover:bg-emerald-50/40">
                              <td className="px-4 py-2.5 font-bold text-emerald-800">{doc.document_type}</td>
                              <td className="px-4 py-2.5 flex items-center gap-1.5 font-semibold text-slate-800">
                                <FileText size={14} className="text-emerald-600" />
                                {doc.file_name}
                              </td>
                              <td className="px-4 py-2.5 font-mono text-[11px] text-slate-500">{doc.storage_key}</td>
                              <td className="px-4 py-2.5 text-right">
                                <button
                                  onClick={() => handleDeleteDocument(doc.id)}
                                  className="p-1 rounded text-rose-500 hover:bg-rose-50"
                                >
                                  <Trash2 size={14} />
                                </button>
                              </td>
                            </tr>
                          ))
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Tab 3: Status */}
              {activeTab === 'status' && (
                <form onSubmit={handleUpdateStatus} className="p-4 rounded-xl bg-emerald-50/60 border border-emerald-200 space-y-4">
                  <h4 className="font-bold text-slate-900">Manage Employee Lifecycle Status</h4>
                  <div>
                    <label className="block text-slate-600 font-bold mb-1">Current Status</label>
                    <select
                      value={newStatus}
                      onChange={(e) => setNewStatus(e.target.value)}
                      className="w-full bg-white border border-emerald-200 rounded-xl px-3 py-2 text-slate-900 font-bold"
                    >
                      <option value="ACTIVE">ACTIVE</option>
                      <option value="PROBATION">PROBATION</option>
                      <option value="ON_NOTICE">ON_NOTICE</option>
                      <option value="ON_LEAVE">ON_LEAVE</option>
                      <option value="SUSPENDED">SUSPENDED</option>
                      <option value="INACTIVE">INACTIVE</option>
                      <option value="TERMINATED">TERMINATED</option>
                      <option value="RESIGNED">RESIGNED</option>
                      <option value="RETIRED">RETIRED</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-slate-600 font-bold mb-1">Reason / Status Note</label>
                    <textarea
                      value={statusReason}
                      onChange={(e) => setStatusReason(e.target.value)}
                      placeholder="Audit note explaining this status transition"
                      className="w-full bg-white border border-emerald-200 rounded-xl px-3 py-2 text-slate-800 font-medium h-20 text-xs"
                    />
                  </div>

                  <div className="flex justify-end">
                    <button
                      type="submit"
                      disabled={updating}
                      className="px-4 py-2 rounded-xl bg-emerald-600 text-white font-bold text-xs flex items-center gap-1.5 shadow-sm"
                    >
                      <CheckCircle2 size={16} /> Update Employee Status
                    </button>
                  </div>
                </form>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
