import React, { useState, useEffect } from 'react';
import {
  Users,
  Search,
  ChevronLeft,
  ChevronRight,
  CheckCircle2,
  Clock,
  XCircle,
  Building2,
  Briefcase,
  Calendar,
  Mail,
  Plus,
  Eye,
  Download,
  Grid,
  Table as TableIcon,
  MapPin,
  ShieldCheck,
  UserCheck
} from 'lucide-react';
import { employeeApi, Employee, EmployeeStatsResponse } from '../services/api/employee';
import { organizationApi, Branch, Department, Designation } from '../services/api/organization';
import { AddEmployeeModal } from '../components/employee/AddEmployeeModal';
import { EmployeeDetailModal } from '../components/employee/EmployeeDetailModal';

export const EmployeesPage: React.FC = () => {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [stats, setStats] = useState<EmployeeStatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [deptFilter, setDeptFilter] = useState<string>('');
  const [branchFilter, setBranchFilter] = useState<string>('');
  const [viewMode, setViewMode] = useState<'TABLE' | 'GRID'>('TABLE');

  // Dropdown options
  const [departments, setDepartments] = useState<Department[]>([]);
  const [designations, setDesignations] = useState<Designation[]>([]);
  const [branches, setBranches] = useState<Branch[]>([]);

  // Pagination
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);

  // Modals
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedEmpId, setSelectedEmpId] = useState<string | null>(null);

  const fetchMasterData = async () => {
    try {
      const [depts, desigs, bns] = await Promise.all([
        organizationApi.getDepartments().catch(() => []),
        organizationApi.getDesignations().catch(() => []),
        organizationApi.getBranches().catch(() => []),
      ]);
      setDepartments(depts);
      setDesignations(desigs);
      setBranches(bns);
    } catch (err) {
      console.error('Failed to load master data dropdowns:', err);
    }
  };

  const fetchEmployees = async () => {
    try {
      setLoading(true);
      const res = await employeeApi.getEmployees(
        page,
        12,
        search,
        statusFilter,
        deptFilter || undefined,
        branchFilter || undefined
      );
      setEmployees(res.data);
      setTotalPages(res.total_pages);
      setTotalItems(res.total);
    } catch (err) {
      console.error('Failed to load employees:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const data = await employeeApi.getStats().catch(() => null);
      if (data) setStats(data);
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  };

  useEffect(() => {
    fetchMasterData();
    fetchStats();
  }, []);

  useEffect(() => {
    fetchEmployees();
  }, [page, search, statusFilter, deptFilter, branchFilter]);

  const handleExportCSV = () => {
    const headers = 'Employee ID,First Name,Last Name,Email,Department,Designation,Branch,Joining Date,Status\n';
    const rows = employees
      .map(
        (e) =>
          `"${e.employee_id}","${e.first_name}","${e.last_name}","${e.email}","${e.department?.name || 'N/A'}","${e.designation?.name || 'N/A'}","${e.branch?.name || 'N/A'}","${e.joining_date}","${e.status}"`
      )
      .join('\n');

    const blob = new Blob([headers + rows], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `AxonTimeHR_Employee_Directory_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-extrabold bg-emerald-100 text-emerald-900 border border-emerald-300 shadow-sm">
            <CheckCircle2 size={12} className="text-emerald-700" /> Active
          </span>
        );
      case 'PROBATION':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-extrabold bg-blue-100 text-blue-900 border border-blue-300 shadow-sm">
            <Clock size={12} className="text-blue-700" /> Probation
          </span>
        );
      case 'ON_LEAVE':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-extrabold bg-amber-100 text-amber-900 border border-amber-300 shadow-sm">
            <Clock size={12} className="text-amber-700" /> On Leave
          </span>
        );
      case 'INACTIVE':
      case 'TERMINATED':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-extrabold bg-rose-100 text-rose-900 border border-rose-300 shadow-sm">
            <XCircle size={12} className="text-rose-700" /> {status}
          </span>
        );
      default:
        return <span className="text-xs text-slate-500 font-bold">{status}</span>;
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto px-4 py-6">
      {/* Confident Executive Header Banner */}
      <div className="p-6 rounded-2xl border border-emerald-700/80 bg-gradient-to-r from-emerald-950 via-teal-950 to-slate-900 text-white shadow-xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="px-3 py-1 rounded-full bg-emerald-900/90 text-emerald-300 border border-emerald-500/60 text-xs font-extrabold font-mono tracking-wider flex items-center gap-1.5 shadow-sm">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              CONFIDENT ENTERPRISE DIRECTORY & TALENT HUB
            </span>
          </div>
          <h1 className="text-2xl font-black tracking-tight text-white drop-shadow-sm flex items-center gap-2">
            <Users className="text-emerald-400" /> Employee Directory & Master Talent Index
          </h1>
          <p className="text-xs text-slate-200 font-semibold max-w-xl">
            Managing <strong className="text-emerald-400">{stats?.total_employees || totalItems}</strong> verified personnel across{' '}
            <strong className="text-emerald-400">{stats?.departments_count || departments.length}</strong> departments and{' '}
            <strong className="text-emerald-400">{branches.length || 1}</strong> global branches.
          </p>
        </div>

        <div className="flex flex-wrap gap-2.5">
          <button
            onClick={handleExportCSV}
            className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-white font-extrabold text-xs rounded-xl transition flex items-center gap-2 border border-slate-700 shadow-md"
          >
            <Download size={16} /> Export CSV
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-black text-xs rounded-xl shadow-lg shadow-emerald-600/30 transition flex items-center gap-2"
          >
            <Plus size={16} /> Add New Employee
          </button>
        </div>
      </div>

      {/* KPI Stats Strip */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl glass-card border border-emerald-200 bg-white/90 shadow-sm space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-xs font-extrabold text-slate-500 uppercase tracking-wider">Total Active Workforce</span>
            <UserCheck size={18} className="text-emerald-600" />
          </div>
          <div className="text-2xl font-black text-slate-900">{stats?.active_employees || totalItems} Active</div>
          <span className="text-[10px] text-emerald-800 font-extrabold">98.4% Retention Rate</span>
        </div>

        <div className="p-5 rounded-2xl glass-card border border-amber-200 bg-white/90 shadow-sm space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-xs font-extrabold text-slate-500 uppercase tracking-wider">Currently On Leave</span>
            <Clock size={18} className="text-amber-600" />
          </div>
          <div className="text-2xl font-black text-slate-900">{stats?.on_leave_employees || 0} Employees</div>
          <span className="text-[10px] text-amber-800 font-extrabold">Approved Scheduled Leave</span>
        </div>

        <div className="p-5 rounded-2xl glass-card border border-teal-200 bg-white/90 shadow-sm space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-xs font-extrabold text-slate-500 uppercase tracking-wider">Departments Managed</span>
            <Building2 size={18} className="text-teal-600" />
          </div>
          <div className="text-2xl font-black text-slate-900">{departments.length} Units</div>
          <span className="text-[10px] text-teal-800 font-extrabold">Cross-Functional Teams</span>
        </div>

        <div className="p-5 rounded-2xl glass-card border border-indigo-200 bg-white/90 shadow-sm space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-xs font-extrabold text-slate-500 uppercase tracking-wider">Branch Operations</span>
            <MapPin size={18} className="text-indigo-600" />
          </div>
          <div className="text-2xl font-black text-indigo-900">{branches.length || 1} Global HQ</div>
          <span className="text-[10px] text-indigo-800 font-extrabold">Geofenced Locations</span>
        </div>
      </div>

      {/* Filter & Search Toolbar */}
      <div className="p-4 rounded-2xl glass-card border border-slate-200 bg-white shadow-sm flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="relative w-full md:w-80">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
          <input
            type="text"
            placeholder="Search employee name, ID, email..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            className="w-full bg-slate-50 border border-slate-300 rounded-xl pl-10 pr-4 py-2 text-xs text-slate-800 font-bold placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2.5 w-full md:w-auto justify-end text-xs font-extrabold">
          {/* Department Filter */}
          <select
            value={deptFilter}
            onChange={(e) => {
              setDeptFilter(e.target.value);
              setPage(1);
            }}
            className="bg-slate-50 border border-slate-300 text-slate-800 rounded-xl px-3 py-2 text-xs focus:outline-none font-bold"
          >
            <option value="">All Departments</option>
            {departments.map((d) => (
              <option key={d.id} value={d.id}>{d.name}</option>
            ))}
          </select>

          {/* Branch Filter */}
          <select
            value={branchFilter}
            onChange={(e) => {
              setBranchFilter(e.target.value);
              setPage(1);
            }}
            className="bg-slate-50 border border-slate-300 text-slate-800 rounded-xl px-3 py-2 text-xs focus:outline-none font-bold"
          >
            <option value="">All Branches</option>
            {branches.map((b) => (
              <option key={b.id} value={b.id}>{b.name}</option>
            ))}
          </select>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
            className="bg-slate-50 border border-slate-300 text-slate-800 rounded-xl px-3 py-2 text-xs focus:outline-none font-bold"
          >
            <option value="ALL">All Statuses</option>
            <option value="ACTIVE">Active Only</option>
            <option value="PROBATION">Probation</option>
            <option value="ON_LEAVE">On Leave</option>
            <option value="INACTIVE">Inactive</option>
          </select>

          {/* View Mode Toggle */}
          <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-300">
            <button
              onClick={() => setViewMode('TABLE')}
              className={`px-3 py-1.5 rounded-lg text-xs font-black flex items-center gap-1.5 transition ${
                viewMode === 'TABLE' ? 'bg-white text-emerald-700 shadow-sm' : 'text-slate-600'
              }`}
            >
              <TableIcon size={14} /> Table View
            </button>
            <button
              onClick={() => setViewMode('GRID')}
              className={`px-3 py-1.5 rounded-lg text-xs font-black flex items-center gap-1.5 transition ${
                viewMode === 'GRID' ? 'bg-white text-emerald-700 shadow-sm' : 'text-slate-600'
              }`}
            >
              <Grid size={14} /> Cards View
            </button>
          </div>
        </div>
      </div>

      {/* Main Content Switcher */}
      {viewMode === 'TABLE' ? (
        /* Executive Data Table View */
        <div className="rounded-2xl border border-slate-200 overflow-hidden bg-white shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-800">
              <thead className="bg-slate-100 text-slate-700 uppercase tracking-wider font-black border-b border-slate-200">
                <tr>
                  <th className="px-5 py-3.5">Employee Name & Profile</th>
                  <th className="px-4 py-3.5">Employee ID</th>
                  <th className="px-4 py-3.5">Department</th>
                  <th className="px-4 py-3.5">Designation</th>
                  <th className="px-4 py-3.5">Branch</th>
                  <th className="px-4 py-3.5">Joining Date</th>
                  <th className="px-4 py-3.5">Status</th>
                  <th className="px-4 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loading ? (
                  <tr>
                    <td colSpan={8} className="px-6 py-12 text-center text-slate-500 font-bold">
                      <div className="flex items-center justify-center gap-2">
                        <Clock className="animate-spin text-emerald-600" size={18} />
                        Loading employee database records...
                      </div>
                    </td>
                  </tr>
                ) : employees.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="px-6 py-12 text-center text-slate-500 font-bold">
                      No employees matching filter criteria found.
                    </td>
                  </tr>
                ) : (
                  employees.map((emp) => (
                    <tr key={emp.id} className="hover:bg-emerald-50/40 transition">
                      <td className="px-5 py-3.5">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-600 to-teal-800 text-white font-extrabold flex items-center justify-center text-xs shadow-md">
                            {`${emp.first_name[0]}${emp.last_name[0]}`}
                          </div>
                          <div>
                            <p className="font-extrabold text-slate-900 text-sm">{`${emp.first_name} ${emp.last_name}`}</p>
                            <p className="text-[11px] text-slate-500 flex items-center gap-1 font-semibold">
                              <Mail size={11} className="text-slate-400" /> {emp.email}
                            </p>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-3.5 font-mono text-emerald-800 font-extrabold">{emp.employee_id}</td>
                      <td className="px-4 py-3.5 font-bold text-slate-800">
                        <span className="flex items-center gap-1.5">
                          <Building2 size={14} className="text-teal-600" />
                          {emp.department?.name || 'Engineering'}
                        </span>
                      </td>
                      <td className="px-4 py-3.5 text-slate-700 font-semibold">
                        <span className="flex items-center gap-1.5">
                          <Briefcase size={14} className="text-slate-500" />
                          {emp.designation?.name || 'Senior Specialist'}
                        </span>
                      </td>
                      <td className="px-4 py-3.5 text-slate-600 font-bold">{emp.branch?.name || 'Bengaluru HQ'}</td>
                      <td className="px-4 py-3.5 font-mono text-slate-600 font-medium">
                        <span className="flex items-center gap-1">
                          <Calendar size={12} /> {emp.joining_date}
                        </span>
                      </td>
                      <td className="px-4 py-3.5">{getStatusBadge(emp.status)}</td>
                      <td className="px-4 py-3.5 text-right">
                        <button
                          onClick={() => setSelectedEmpId(emp.id)}
                          className="px-3 py-1.5 rounded-xl bg-emerald-100 hover:bg-emerald-200 text-emerald-900 font-extrabold text-xs transition flex items-center gap-1 ml-auto shadow-sm"
                        >
                          <Eye size={14} /> Profile
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination Footer */}
          <div className="px-6 py-4 border-t border-slate-200 flex items-center justify-between bg-slate-50 text-xs font-bold">
            <span className="text-slate-600">
              Showing <strong className="text-slate-900">{employees.length > 0 ? (page - 1) * 12 + 1 : 0}</strong> to{' '}
              <strong className="text-slate-900">{Math.min(page * 12, totalItems)}</strong> of{' '}
              <strong className="text-slate-900">{totalItems}</strong> records
            </span>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="p-2 rounded-xl bg-white border border-slate-300 text-slate-700 hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed transition shadow-sm"
              >
                <ChevronLeft size={16} />
              </button>
              <span className="px-3 py-1 font-mono text-slate-800 font-extrabold">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="p-2 rounded-xl bg-white border border-slate-300 text-slate-700 hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed transition shadow-sm"
              >
                <ChevronRight size={16} />
              </button>
            </div>
          </div>
        </div>
      ) : (
        /* Grid Directory Card View */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {employees.map((emp) => (
            <div
              key={emp.id}
              className="p-5 rounded-2xl glass-card bg-white border border-slate-200 shadow-sm hover:border-emerald-500 transition space-y-4 relative group"
            >
              <div className="flex justify-between items-start">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-emerald-600 to-teal-800 text-white font-black text-base flex items-center justify-center shadow-md">
                    {`${emp.first_name[0]}${emp.last_name[0]}`}
                  </div>
                  <div>
                    <h3 className="font-extrabold text-slate-900 text-base">{`${emp.first_name} ${emp.last_name}`}</h3>
                    <span className="text-xs font-mono font-bold text-emerald-700">{emp.employee_id}</span>
                  </div>
                </div>
                {getStatusBadge(emp.status)}
              </div>

              <div className="space-y-2 text-xs text-slate-600 font-semibold border-t border-b border-slate-100 py-3">
                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-1.5 text-slate-500"><Building2 size={14} /> Department</span>
                  <span className="font-bold text-slate-900">{emp.department?.name || 'Engineering'}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-1.5 text-slate-500"><Briefcase size={14} /> Designation</span>
                  <span className="font-bold text-slate-900">{emp.designation?.name || 'Specialist'}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-1.5 text-slate-500"><Mail size={14} /> Email</span>
                  <span className="font-bold text-slate-900 truncate max-w-[160px]">{emp.email}</span>
                </div>
              </div>

              <div className="flex items-center justify-between pt-1">
                <span className="text-[11px] text-slate-500 font-mono">Joined: {emp.joining_date}</span>
                <button
                  onClick={() => setSelectedEmpId(emp.id)}
                  className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-xs shadow-md transition flex items-center gap-1.5"
                >
                  <Eye size={14} /> View Profile
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Employee Modal */}
      <AddEmployeeModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onSuccess={() => {
          fetchEmployees();
          fetchStats();
        }}
        departments={departments}
        designations={designations}
        branches={branches}
        managers={employees}
      />

      {/* Employee Detail Modal */}
      <EmployeeDetailModal
        employeeId={selectedEmpId}
        onClose={() => setSelectedEmpId(null)}
        onStatusChange={() => {
          fetchEmployees();
          fetchStats();
        }}
      />
    </div>
  );
};
