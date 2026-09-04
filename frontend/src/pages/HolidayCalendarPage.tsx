import React, { useState, useEffect } from 'react';
import {
  Calendar as CalendarIcon,
  Plus,
  Search,
  Download,
  CheckCircle2,
  Sparkles,
  CalendarDays,
  Tag,
  Clock,
  Filter,
  FileText,
  Table as TableIcon,
  Grid as GridIcon,
  Printer
} from 'lucide-react';
import { holidayApi } from '../services/api/holiday';

interface HolidayItem {
  id: string;
  holiday_date: string;
  day_of_week: string;
  holiday_name: string;
  holiday_type: 'MANDATORY' | 'OPTIONAL' | 'RESTRICTED';
  category: 'NATIONAL' | 'FESTIVAL' | 'REGIONAL';
  description: string;
  is_long_weekend?: boolean;
}

export const HolidayCalendarPage: React.FC = () => {
  const [selectedYear, setSelectedYear] = useState<number>(2026);
  const [activeTab, setActiveTab] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [viewMode, setViewMode] = useState<'TABLE' | 'GRID'>('TABLE');

  // Modals
  const [isHolidayModalOpen, setIsHolidayModalOpen] = useState<boolean>(false);

  // New Holiday Form
  const [newHDate, setNewHDate] = useState<string>('');
  const [newHName, setNewHName] = useState<string>('');
  const [newHType, setNewHType] = useState<'MANDATORY' | 'OPTIONAL' | 'RESTRICTED'>('MANDATORY');
  const [newHDesc, setNewHDesc] = useState<string>('');

  // 2026 Master Pre-Populated Official Holiday List
  const [holidays2026, setHolidays2026] = useState<HolidayItem[]>([
    {
      id: 'h-2026-01',
      holiday_date: '2026-01-01',
      day_of_week: 'Thursday',
      holiday_name: "New Year's Day",
      holiday_type: 'MANDATORY',
      category: 'NATIONAL',
      description: 'First day of the year in the Gregorian calendar.',
      is_long_weekend: false
    },
    {
      id: 'h-2026-02',
      holiday_date: '2026-01-26',
      day_of_week: 'Monday',
      holiday_name: 'Republic Day',
      holiday_type: 'MANDATORY',
      category: 'NATIONAL',
      description: 'Honors the date on which the Constitution of India came into effect.',
      is_long_weekend: true
    },
    {
      id: 'h-2026-03',
      holiday_date: '2026-03-04',
      day_of_week: 'Wednesday',
      holiday_name: 'Maha Shivratri',
      holiday_type: 'RESTRICTED',
      category: 'FESTIVAL',
      description: 'Annual festival in honor of Lord Shiva.',
      is_long_weekend: false
    },
    {
      id: 'h-2026-04',
      holiday_date: '2026-03-20',
      day_of_week: 'Friday',
      holiday_name: 'Holi (Festival of Colors)',
      holiday_type: 'MANDATORY',
      category: 'FESTIVAL',
      description: 'Spring festival celebrating love and colors.',
      is_long_weekend: true
    },
    {
      id: 'h-2026-05',
      holiday_date: '2026-04-03',
      day_of_week: 'Friday',
      holiday_name: 'Good Friday',
      holiday_type: 'MANDATORY',
      category: 'REGIONAL',
      description: 'Christian holiday commemorating the crucifixion of Jesus.',
      is_long_weekend: true
    },
    {
      id: 'h-2026-06',
      holiday_date: '2026-04-14',
      day_of_week: 'Tuesday',
      holiday_name: 'Dr. B.R. Ambedkar Jayanti',
      holiday_type: 'MANDATORY',
      category: 'NATIONAL',
      description: 'Birth anniversary of Dr. B.R. Ambedkar, father of the Indian Constitution.',
      is_long_weekend: false
    },
    {
      id: 'h-2026-07',
      holiday_date: '2026-05-01',
      day_of_week: 'Friday',
      holiday_name: "International Workers' Day",
      holiday_type: 'MANDATORY',
      category: 'NATIONAL',
      description: 'Celebration of laborers and the working class.',
      is_long_weekend: true
    },
    {
      id: 'h-2026-08',
      holiday_date: '2026-08-15',
      day_of_week: 'Saturday',
      holiday_name: 'Independence Day',
      holiday_type: 'MANDATORY',
      category: 'NATIONAL',
      description: 'Commemorates India independence from the United Kingdom.',
      is_long_weekend: false
    },
    {
      id: 'h-2026-09',
      holiday_date: '2026-09-04',
      day_of_week: 'Friday',
      holiday_name: 'Janmashtami',
      holiday_type: 'OPTIONAL',
      category: 'FESTIVAL',
      description: 'Annual Hindu festival celebrating the birth of Krishna.',
      is_long_weekend: true
    },
    {
      id: 'h-2026-10',
      holiday_date: '2026-10-02',
      day_of_week: 'Friday',
      holiday_name: 'Mahatma Gandhi Jayanti',
      holiday_type: 'MANDATORY',
      category: 'NATIONAL',
      description: 'Birth anniversary of Mahatma Gandhi, Father of the Nation.',
      is_long_weekend: true
    },
    {
      id: 'h-2026-11',
      holiday_date: '2026-10-20',
      day_of_week: 'Tuesday',
      holiday_name: 'Dussehra (Vijayadashami)',
      holiday_type: 'MANDATORY',
      category: 'FESTIVAL',
      description: 'Major Hindu festival celebrating the victory of good over evil.',
      is_long_weekend: false
    },
    {
      id: 'h-2026-12',
      holiday_date: '2026-11-08',
      day_of_week: 'Sunday',
      holiday_name: 'Diwali (Deepavali)',
      holiday_type: 'MANDATORY',
      category: 'FESTIVAL',
      description: 'Festival of lights celebrated across the nation.',
      is_long_weekend: false
    },
    {
      id: 'h-2026-13',
      holiday_date: '2026-11-24',
      day_of_week: 'Tuesday',
      holiday_name: 'Guru Nanak Jayanti',
      holiday_type: 'OPTIONAL',
      category: 'REGIONAL',
      description: 'Birth anniversary of the first Sikh Guru.',
      is_long_weekend: false
    },
    {
      id: 'h-2026-14',
      holiday_date: '2026-12-25',
      day_of_week: 'Friday',
      holiday_name: 'Christmas Day',
      holiday_type: 'MANDATORY',
      category: 'NATIONAL',
      description: 'Annual festival commemorating the birth of Jesus Christ.',
      is_long_weekend: true
    }
  ]);

  useEffect(() => {
    holidayApi.getCalendars(selectedYear).catch(() => null);
  }, [selectedYear]);

  const handleAddHoliday = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newHDate || !newHName) return;

    const dateObj = new Date(newHDate);
    const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const dayName = dayNames[dateObj.getUTCDay()];
    const isWeekend = dayName === 'Friday' || dayName === 'Monday';

    const newItem: HolidayItem = {
      id: `h-custom-${Date.now()}`,
      holiday_date: newHDate,
      day_of_week: dayName,
      holiday_name: newHName,
      holiday_type: newHType,
      category: 'FESTIVAL',
      description: newHDesc || 'Custom corporate holiday schedule.',
      is_long_weekend: isWeekend
    };

    setHolidays2026((prev) => [newItem, ...prev].sort((a, b) => a.holiday_date.localeCompare(b.holiday_date)));
    setIsHolidayModalOpen(false);
    setNewHDate('');
    setNewHName('');
    setNewHDesc('');
  };

  const handleExportCSV = () => {
    const csvContent =
      'Date,Day,Holiday Name,Type,Category,Long Weekend,Description\n' +
      holidays2026
        .map(
          (h) =>
            `"${h.holiday_date}","${h.day_of_week}","${h.holiday_name}","${h.holiday_type}","${h.category}","${h.is_long_weekend ? 'YES' : 'NO'}","${h.description}"`
        )
        .join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `AxonTimeHR_Holiday_Calendar_${selectedYear}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handlePrintPDF = () => {
    const printWindow = window.open('', '_blank');
    if (!printWindow) return;

    const totalCount = holidays2026.length;
    const mandatoryCount = holidays2026.filter((h) => h.holiday_type === 'MANDATORY').length;
    const optionalCount = holidays2026.filter((h) => h.holiday_type === 'OPTIONAL' || h.holiday_type === 'RESTRICTED').length;
    const longWeekendCount = holidays2026.filter((h) => h.is_long_weekend).length;

    const tableRows = filteredHolidays
      .map(
        (h) => `
      <tr>
        <td style="padding:10px; border:1px solid #e2e8f0; font-weight:bold; font-family:monospace;">${h.holiday_date}</td>
        <td style="padding:10px; border:1px solid #e2e8f0;">${h.day_of_week}</td>
        <td style="padding:10px; border:1px solid #e2e8f0; font-weight:bold;">${h.holiday_name}</td>
        <td style="padding:10px; border:1px solid #e2e8f0; text-align:center;">
          <span style="padding:3px 8px; border-radius:12px; font-size:10px; font-weight:bold; ${
            h.holiday_type === 'MANDATORY'
              ? 'background:#d1fae5; color:#065f46;'
              : h.holiday_type === 'RESTRICTED'
              ? 'background:#fef3c7; color:#92400e;'
              : 'background:#e0e7ff; color:#3730a3;'
          }">${h.holiday_type}</span>
        </td>
        <td style="padding:10px; border:1px solid #e2e8f0; text-align:center;">${h.category}</td>
        <td style="padding:10px; border:1px solid #e2e8f0; text-align:center; font-weight:bold; color:${h.is_long_weekend ? '#4f46e5' : '#64748b'};">
          ${h.is_long_weekend ? '✨ YES' : 'NO'}
        </td>
        <td style="padding:10px; border:1px solid #e2e8f0; font-size:11px; color:#475569;">${h.description}</td>
      </tr>`
      )
      .join('');

    printWindow.document.write(`
      <!DOCTYPE html>
      <html>
        <head>
          <title>AxonTimeHR Official ${selectedYear} Holiday Calendar Report</title>
          <style>
            body { font-family: 'Helvetica Neue', Arial, sans-serif; color: #1e293b; padding: 25px; }
            h1 { color: #065f46; margin-bottom: 4px; }
            p { color: #64748b; font-size: 12px; margin-top: 0; }
            .kpi-container { display: flex; gap: 15px; margin: 20px 0; }
            .kpi-box { flex: 1; padding: 12px; border: 1px solid #cbd5e1; border-radius: 8px; background: #f8fafc; text-align: center; }
            .kpi-val { font-size: 20px; font-weight: bold; color: #0f172a; }
            .kpi-lbl { font-size: 10px; text-transform: uppercase; color: #64748b; font-weight: bold; }
            table { width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 12px; }
            th { background: #065f46; color: white; padding: 10px; text-align: left; font-size: 11px; text-transform: uppercase; }
            footer { margin-top: 30px; font-size: 10px; color: #94a3b8; text-align: center; border-top: 1px solid #e2e8f0; padding-top: 10px; }
          </style>
        </head>
        <body>
          <h1>AxonTimeHR Enterprise — Official ${selectedYear} Holiday Calendar</h1>
          <p>Generated on ${new Date().toLocaleDateString()} • Multi-Tenant Statutory & Corporate Compliance Schedule</p>
          
          <div class="kpi-container">
            <div class="kpi-box"><div class="kpi-val">${totalCount}</div><div class="kpi-lbl">Total Holidays</div></div>
            <div class="kpi-box"><div class="kpi-val">${mandatoryCount}</div><div class="kpi-lbl">Paid Mandatory</div></div>
            <div class="kpi-box"><div class="kpi-val">${optionalCount}</div><div class="kpi-lbl">Optional Quota</div></div>
            <div class="kpi-box"><div class="kpi-val">${longWeekendCount}</div><div class="kpi-lbl">Long Weekends</div></div>
          </div>

          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Day</th>
                <th>Holiday Name</th>
                <th>Type</th>
                <th>Category</th>
                <th>Long Weekend</th>
                <th>Description & Insights</th>
              </tr>
            </thead>
            <tbody>
              ${tableRows}
            </tbody>
          </table>

          <footer>AxonTimeHR SaaS Platform • Enterprise HRMS & Attendance Engine • Confidential Report</footer>
          <script>window.print();</script>
        </body>
      </html>
    `);
    printWindow.document.close();
  };

  // Filtered Holidays
  const filteredHolidays = holidays2026.filter((h) => {
    const matchesTab = activeTab === 'ALL' || h.holiday_type === activeTab;
    const matchesQuery =
      h.holiday_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      h.holiday_date.includes(searchQuery) ||
      h.day_of_week.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesTab && matchesQuery;
  });

  const totalCount = holidays2026.length;
  const mandatoryCount = holidays2026.filter((h) => h.holiday_type === 'MANDATORY').length;
  const optionalCount = holidays2026.filter((h) => h.holiday_type === 'OPTIONAL' || h.holiday_type === 'RESTRICTED').length;
  const longWeekendCount = holidays2026.filter((h) => h.is_long_weekend).length;

  return (
    <div className="space-y-6 p-6 max-w-7xl mx-auto">
      {/* Top Header & Actions */}
      <div className="p-6 rounded-2xl border border-emerald-700/80 bg-gradient-to-r from-emerald-950 via-teal-950 to-slate-900 text-white shadow-xl flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="px-3 py-1 rounded-full bg-emerald-900/90 text-emerald-300 border border-emerald-500/60 text-xs font-extrabold font-mono tracking-wider flex items-center gap-1.5 shadow-sm">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              OFFICIAL 2026 HOLIDAY REPORT & PDF INSIGHTS TABLE
            </span>
          </div>
          <h1 className="text-2xl font-extrabold tracking-tight text-white drop-shadow-sm flex items-center gap-2">
            <CalendarIcon className="text-emerald-400" /> 2026 Enterprise Holiday Master Center
          </h1>
          <p className="text-xs text-slate-200 font-medium max-w-xl">
            Multi-branch gazetted, national, festival, and optional holidays integrated with attendance policy & leave engines.
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            onClick={handlePrintPDF}
            className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-extrabold text-xs rounded-xl shadow-lg shadow-indigo-600/30 transition flex items-center gap-2"
          >
            <Printer size={16} /> Export 2026 PDF Report
          </button>
          <button
            onClick={handleExportCSV}
            className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-white font-extrabold text-xs rounded-xl transition flex items-center gap-2 border border-slate-700 shadow-md"
          >
            <Download size={16} /> Export CSV
          </button>
          <button
            onClick={() => setIsHolidayModalOpen(true)}
            className="px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-xs rounded-xl shadow-lg shadow-emerald-600/30 transition flex items-center gap-2"
          >
            <Plus size={16} /> Add Holiday
          </button>
        </div>
      </div>

      {/* KPI Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl glass-card border border-emerald-200 bg-white/90 dark:bg-slate-800/90 shadow-sm space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Total 2026 Holidays</span>
            <CalendarDays size={18} className="text-emerald-600" />
          </div>
          <div className="text-2xl font-extrabold text-slate-900 dark:text-white">{totalCount} Days</div>
          <span className="text-[10px] text-slate-500 font-semibold">Active Tenant Calendar</span>
        </div>

        <div className="p-5 rounded-2xl glass-card border border-teal-200 bg-white/90 dark:bg-slate-800/90 shadow-sm space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Mandatory Holidays</span>
            <CheckCircle2 size={18} className="text-teal-600" />
          </div>
          <div className="text-2xl font-extrabold text-slate-900 dark:text-white">{mandatoryCount} Days</div>
          <span className="text-[10px] text-emerald-700 font-bold">100% Paid Company Days</span>
        </div>

        <div className="p-5 rounded-2xl glass-card border border-amber-200 bg-white/90 dark:bg-slate-800/90 shadow-sm space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Restricted / Optional</span>
            <Tag size={18} className="text-amber-600" />
          </div>
          <div className="text-2xl font-extrabold text-slate-900 dark:text-white">{optionalCount} Days</div>
          <span className="text-[10px] text-amber-700 font-bold">Employee Choice Quota</span>
        </div>

        <div className="p-5 rounded-2xl glass-card border border-indigo-200 bg-white/90 dark:bg-slate-800/90 shadow-sm space-y-1">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Long Weekends (3+ Days)</span>
            <Sparkles size={18} className="text-indigo-600" />
          </div>
          <div className="text-2xl font-extrabold text-indigo-900 dark:text-indigo-300">{longWeekendCount} Opportunities</div>
          <span className="text-[10px] text-indigo-700 font-bold">Optimal Vacation Periods</span>
        </div>
      </div>

      {/* Filter & View Mode Toolbar */}
      <div className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        {/* Type Tabs */}
        <div className="flex items-center gap-2 text-xs font-extrabold">
          <Filter size={16} className="text-emerald-600" />
          {['ALL', 'MANDATORY', 'RESTRICTED', 'OPTIONAL'].map((t) => (
            <button
              key={t}
              onClick={() => setActiveTab(t)}
              className={`px-3 py-1.5 rounded-lg transition ${
                activeTab === t
                  ? 'bg-emerald-700 text-white font-bold shadow-sm'
                  : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-200'
              }`}
            >
              {t === 'ALL' ? 'All Holidays' : t}
            </button>
          ))}
        </div>

        {/* Search Input, Year Selector & View Mode Switch */}
        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          <div className="relative flex-1 md:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={14} />
            <input
              type="text"
              placeholder="Search holiday name, month..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 bg-slate-50 dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-emerald-500 text-slate-800 dark:text-white"
            />
          </div>

          <select
            value={selectedYear}
            onChange={(e) => setSelectedYear(parseInt(e.target.value))}
            className="px-3 py-1.5 bg-slate-50 dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-lg text-xs font-bold text-slate-800 dark:text-white focus:outline-none"
          >
            <option value={2026}>Year 2026</option>
            <option value={2025}>Year 2025</option>
            <option value={2027}>Year 2027</option>
          </select>

          {/* View Mode Toggle Button Group */}
          <div className="flex items-center bg-slate-100 dark:bg-slate-700 p-1 rounded-lg border border-slate-300 dark:border-slate-600">
            <button
              onClick={() => setViewMode('TABLE')}
              className={`px-3 py-1 rounded-md text-xs font-extrabold flex items-center gap-1.5 transition ${
                viewMode === 'TABLE' ? 'bg-white dark:bg-slate-800 text-emerald-700 dark:text-emerald-400 shadow-sm' : 'text-slate-600 dark:text-slate-300'
              }`}
            >
              <TableIcon size={14} /> Insights Table
            </button>
            <button
              onClick={() => setViewMode('GRID')}
              className={`px-3 py-1 rounded-md text-xs font-extrabold flex items-center gap-1.5 transition ${
                viewMode === 'GRID' ? 'bg-white dark:bg-slate-800 text-emerald-700 dark:text-emerald-400 shadow-sm' : 'text-slate-600 dark:text-slate-300'
              }`}
            >
              <GridIcon size={14} /> Cards View
            </button>
          </div>
        </div>
      </div>

      {/* Main Content View Switcher */}
      {viewMode === 'TABLE' ? (
        /* Data Table View with Insights */
        <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden">
          <div className="p-4 border-b border-slate-100 dark:border-slate-700 flex justify-between items-center bg-slate-50 dark:bg-slate-900/50">
            <h2 className="font-extrabold text-sm text-slate-800 dark:text-white flex items-center gap-2">
              <FileText className="text-emerald-600" size={16} /> 2026 Master Holiday Insights Table ({filteredHolidays.length} items)
            </h2>
            <span className="text-xs font-mono text-slate-500 font-bold">Auto-Synced with Leave Policy</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-100 dark:bg-slate-700/60 text-slate-700 dark:text-slate-200 font-extrabold uppercase tracking-wider border-b border-slate-200 dark:border-slate-600">
                <tr>
                  <th className="py-3.5 px-4">Date</th>
                  <th className="py-3.5 px-4">Day</th>
                  <th className="py-3.5 px-4">Holiday Name</th>
                  <th className="py-3.5 px-4">Type</th>
                  <th className="py-3.5 px-4">Category</th>
                  <th className="py-3.5 px-4">Long Weekend</th>
                  <th className="py-3.5 px-4">Description & Policy Notes</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                {filteredHolidays.map((h) => (
                  <tr key={h.id} className="hover:bg-emerald-50/40 dark:hover:bg-slate-700/40 transition">
                    <td className="py-3.5 px-4 font-mono font-bold text-slate-900 dark:text-white whitespace-nowrap">
                      {h.holiday_date}
                    </td>
                    <td className="py-3.5 px-4 text-slate-700 dark:text-slate-300 font-medium whitespace-nowrap">
                      {h.day_of_week}
                    </td>
                    <td className="py-3.5 px-4 font-extrabold text-slate-900 dark:text-white whitespace-nowrap">
                      {h.holiday_name}
                    </td>
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <span
                        className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase ${
                          h.holiday_type === 'MANDATORY'
                            ? 'bg-emerald-100 text-emerald-900 border border-emerald-300'
                            : h.holiday_type === 'RESTRICTED'
                            ? 'bg-amber-100 text-amber-900 border border-amber-300'
                            : 'bg-indigo-100 text-indigo-900 border border-indigo-300'
                        }`}
                      >
                        {h.holiday_type}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-600 dark:text-slate-300 font-semibold whitespace-nowrap">
                      {h.category}
                    </td>
                    <td className="py-3.5 px-4 whitespace-nowrap font-bold">
                      {h.is_long_weekend ? (
                        <span className="text-indigo-600 dark:text-indigo-400 flex items-center gap-1 text-[11px]">
                          <Sparkles size={12} /> Long Weekend
                        </span>
                      ) : (
                        <span className="text-slate-400 text-[11px]">Standard</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 text-slate-600 dark:text-slate-300 max-w-md">
                      {h.description}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        /* Card Grid View */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredHolidays.map((h) => (
            <div
              key={h.id}
              className="p-5 rounded-2xl glass-card bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-sm space-y-3 relative hover:border-emerald-400 transition-all group"
            >
              <div className="flex justify-between items-start">
                <div className="space-y-1">
                  <span
                    className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase ${
                      h.holiday_type === 'MANDATORY'
                        ? 'bg-emerald-100 text-emerald-900 border border-emerald-300'
                        : h.holiday_type === 'RESTRICTED'
                        ? 'bg-amber-100 text-amber-900 border border-amber-300'
                        : 'bg-indigo-100 text-indigo-900 border border-indigo-300'
                    }`}
                  >
                    {h.holiday_type}
                  </span>
                  <h3 className="font-extrabold text-base text-slate-900 dark:text-white pt-1">{h.holiday_name}</h3>
                </div>

                {h.is_long_weekend && (
                  <span className="px-2 py-0.5 rounded bg-indigo-50 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 border border-indigo-200 text-[10px] font-extrabold flex items-center gap-1">
                    <Sparkles size={12} /> Long Weekend
                  </span>
                )}
              </div>

              <div className="flex items-center gap-3 text-xs text-slate-600 dark:text-slate-300 font-semibold pt-1">
                <div className="flex items-center gap-1">
                  <CalendarDays size={14} className="text-emerald-600" />
                  <span className="font-mono font-bold">{h.holiday_date}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Clock size={14} className="text-slate-400" />
                  <span>{h.day_of_week}</span>
                </div>
              </div>

              <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed border-t border-slate-100 dark:border-slate-700 pt-2.5">
                {h.description}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* Add Holiday Modal */}
      {isHolidayModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4 border border-slate-200 dark:border-slate-700">
            <div className="flex justify-between items-center border-b border-slate-200 dark:border-slate-700 pb-3">
              <h3 className="text-base font-extrabold text-slate-800 dark:text-white">Add 2026 Company Holiday</h3>
              <button onClick={() => setIsHolidayModalOpen(false)} className="text-slate-400 hover:text-slate-600">✕</button>
            </div>

            <form onSubmit={handleAddHoliday} className="space-y-3.5 text-xs">
              <div>
                <label className="block font-bold text-slate-700 dark:text-slate-200 mb-1">Holiday Date</label>
                <input
                  type="date"
                  value={newHDate}
                  onChange={(e) => setNewHDate(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-xl focus:ring-2 focus:ring-emerald-500 outline-none text-slate-800 dark:text-white"
                  required
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 dark:text-slate-200 mb-1">Holiday Name</label>
                <input
                  type="text"
                  placeholder="e.g. Founder's Day"
                  value={newHName}
                  onChange={(e) => setNewHName(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-xl focus:ring-2 focus:ring-emerald-500 outline-none text-slate-800 dark:text-white"
                  required
                />
              </div>

              <div>
                <label className="block font-bold text-slate-700 dark:text-slate-200 mb-1">Holiday Type</label>
                <select
                  value={newHType}
                  onChange={(e) => setNewHType(e.target.value as any)}
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-xl focus:ring-2 focus:ring-emerald-500 outline-none text-slate-800 dark:text-white"
                >
                  <option value="MANDATORY">Mandatory (Paid)</option>
                  <option value="RESTRICTED">Restricted (Optional)</option>
                  <option value="OPTIONAL">Optional Floating</option>
                </select>
              </div>

              <div>
                <label className="block font-bold text-slate-700 dark:text-slate-200 mb-1">Description / Notes</label>
                <textarea
                  rows={2}
                  placeholder="Optional details or policy notes..."
                  value={newHDesc}
                  onChange={(e) => setNewHDesc(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-xl focus:ring-2 focus:ring-emerald-500 outline-none text-slate-800 dark:text-white"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setIsHolidayModalOpen(false)}
                  className="px-4 py-2 text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-xl font-bold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl shadow-md"
                >
                  Add Holiday
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
