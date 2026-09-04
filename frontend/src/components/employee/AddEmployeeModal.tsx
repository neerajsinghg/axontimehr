import React, { useState } from 'react';
import { X, UserPlus } from 'lucide-react';
import { employeeApi, Employee } from '../../services/api/employee';
import { Branch, Department, Designation } from '../../services/api/organization';

interface AddEmployeeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  departments: Department[];
  designations: Designation[];
  branches: Branch[];
  managers: Employee[];
}

export const AddEmployeeModal: React.FC<AddEmployeeModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  departments,
  designations,
  branches,
  managers,
}) => {
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [createLoginAccount, setCreateLoginAccount] = useState(false);

  const [formData, setFormData] = useState({
    employee_id: `EMP-${Math.floor(1000 + Math.random() * 9000)}`,
    first_name: '',
    middle_name: '',
    last_name: '',
    email: '',
    phone_number: '',
    joining_date: new Date().toISOString().split('T')[0],
    gender: 'MALE',
    employment_type: 'FULL_TIME',
    department_id: '',
    designation_id: '',
    branch_id: '',
    manager_id: '',
  });

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      setErrorMsg('');

      const payload: any = {
        ...formData,
        department_id: formData.department_id || undefined,
        designation_id: formData.designation_id || undefined,
        branch_id: formData.branch_id || undefined,
        manager_id: formData.manager_id || undefined,
        create_user_account: createLoginAccount,
      };

      await employeeApi.createEmployee(payload);
      onSuccess();
      onClose();
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || 'Failed to register employee');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="glass-card bg-white w-full max-w-2xl rounded-2xl border border-emerald-200 shadow-2xl overflow-hidden text-xs">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-emerald-100 flex items-center justify-between bg-emerald-50/60">
          <div className="flex items-center gap-2">
            <UserPlus size={18} className="text-emerald-600" />
            <h2 className="font-extrabold text-sm text-slate-900">Add New Employee</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4 max-h-[80vh] overflow-y-auto">
          {errorMsg && (
            <div className="p-3 rounded-xl bg-rose-100 border border-rose-300 text-rose-900 font-bold">
              {errorMsg}
            </div>
          )}

          {/* Section 1: Basic Information */}
          <div>
            <h3 className="font-bold text-slate-900 border-b border-emerald-100 pb-1 mb-3 uppercase text-[10px] tracking-wider text-emerald-800">
              Basic Employee Profile
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="block text-slate-600 font-bold mb-1">Employee ID *</label>
                <input
                  type="text"
                  value={formData.employee_id}
                  onChange={(e) => setFormData({ ...formData, employee_id: e.target.value })}
                  className="w-full bg-emerald-50/50 border border-emerald-200 rounded-xl px-3 py-2 text-slate-900 font-mono font-bold"
                  required
                />
              </div>
              <div>
                <label className="block text-slate-600 font-bold mb-1">First Name *</label>
                <input
                  type="text"
                  value={formData.first_name}
                  onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                  placeholder="e.g. John"
                  className="w-full bg-emerald-50/50 border border-emerald-200 rounded-xl px-3 py-2 text-slate-900 font-medium"
                  required
                />
              </div>
              <div>
                <label className="block text-slate-600 font-bold mb-1">Last Name *</label>
                <input
                  type="text"
                  value={formData.last_name}
                  onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                  placeholder="e.g. Smith"
                  className="w-full bg-emerald-50/50 border border-emerald-200 rounded-xl px-3 py-2 text-slate-900 font-medium"
                  required
                />
              </div>
            </div>
          </div>

          {/* Section 2: Contact Information */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-slate-600 font-bold mb-1">Work Email *</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder="john.smith@axontimehr.com"
                className="w-full bg-emerald-50/50 border border-emerald-200 rounded-xl px-3 py-2 text-slate-900 font-medium"
                required
              />
            </div>
            <div>
              <label className="block text-slate-600 font-bold mb-1">Phone Number</label>
              <input
                type="text"
                value={formData.phone_number}
                onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                placeholder="+1 555-0192"
                className="w-full bg-emerald-50/50 border border-emerald-200 rounded-xl px-3 py-2 text-slate-900 font-medium"
              />
            </div>
          </div>

          {/* Section 3: Organization & Work Mapping */}
          <div>
            <h3 className="font-bold text-slate-900 border-b border-emerald-100 pb-1 mb-3 uppercase text-[10px] tracking-wider text-emerald-800">
              Department & Position Mapping
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-slate-600 font-bold mb-1">Department</label>
                <select
                  value={formData.department_id}
                  onChange={(e) => setFormData({ ...formData, department_id: e.target.value })}
                  className="w-full bg-emerald-50/50 border border-emerald-200 text-slate-800 rounded-xl px-3 py-2 font-medium"
                >
                  <option value="">Select Department</option>
                  {departments.map((d) => (
                    <option key={d.id} value={d.id}>{d.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-slate-600 font-bold mb-1">Designation</label>
                <select
                  value={formData.designation_id}
                  onChange={(e) => setFormData({ ...formData, designation_id: e.target.value })}
                  className="w-full bg-emerald-50/50 border border-emerald-200 text-slate-800 rounded-xl px-3 py-2 font-medium"
                >
                  <option value="">Select Designation</option>
                  {designations.map((des) => (
                    <option key={des.id} value={des.id}>{des.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-slate-600 font-bold mb-1">Branch Location</label>
                <select
                  value={formData.branch_id}
                  onChange={(e) => setFormData({ ...formData, branch_id: e.target.value })}
                  className="w-full bg-emerald-50/50 border border-emerald-200 text-slate-800 rounded-xl px-3 py-2 font-medium"
                >
                  <option value="">Select Branch</option>
                  {branches.map((b) => (
                    <option key={b.id} value={b.id}>{b.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-slate-600 font-bold mb-1">Reporting Manager</label>
                <select
                  value={formData.manager_id}
                  onChange={(e) => setFormData({ ...formData, manager_id: e.target.value })}
                  className="w-full bg-emerald-50/50 border border-emerald-200 text-slate-800 rounded-xl px-3 py-2 font-medium"
                >
                  <option value="">No Reporting Manager</option>
                  {managers.map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.first_name} {m.last_name} ({m.employee_id})
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Section 4: Employment Details */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-slate-600 font-bold mb-1">Joining Date *</label>
              <input
                type="date"
                value={formData.joining_date}
                onChange={(e) => setFormData({ ...formData, joining_date: e.target.value })}
                className="w-full bg-emerald-50/50 border border-emerald-200 rounded-xl px-3 py-2 text-slate-900 font-medium"
                required
              />
            </div>

            <div>
              <label className="block text-slate-600 font-bold mb-1">Employment Type</label>
              <select
                value={formData.employment_type}
                onChange={(e) => setFormData({ ...formData, employment_type: e.target.value })}
                className="w-full bg-emerald-50/50 border border-emerald-200 text-slate-800 rounded-xl px-3 py-2 font-medium"
              >
                <option value="FULL_TIME">Full Time</option>
                <option value="PART_TIME">Part Time</option>
                <option value="CONTRACT">Contract</option>
                <option value="INTERN">Intern</option>
                <option value="CONSULTANT">Consultant</option>
              </select>
            </div>
          </div>

          {/* Section 5: Auto User Login Account */}
          <div className="p-3 rounded-xl bg-emerald-50/80 border border-emerald-200 flex items-center justify-between">
            <div>
              <p className="font-bold text-slate-900">Provision App User Account</p>
              <p className="text-[10px] text-slate-500">Automatically creates login credentials using work email.</p>
            </div>
            <input
              type="checkbox"
              checked={createLoginAccount}
              onChange={(e) => setCreateLoginAccount(e.target.checked)}
              className="w-4 h-4 text-emerald-600 border-emerald-300 rounded focus:ring-emerald-500"
            />
          </div>

          {/* Modal Actions */}
          <div className="flex justify-end gap-2 pt-3 border-t border-emerald-100">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-slate-100 text-slate-600 font-bold"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold shadow-md shadow-emerald-600/20"
            >
              {loading ? 'Registering...' : 'Register Employee'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
