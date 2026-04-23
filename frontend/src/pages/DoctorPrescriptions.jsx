import React, { useState, useEffect } from 'react';
import { FileText, Plus, Search, Calendar, Pill, Activity, ExternalLink } from 'lucide-react';
import { prescriptionDashboardAPI } from '../services/api';
import { useNavigate } from 'react-router-dom';

export default function DoctorPrescriptions() {
  const [prescriptions, setPrescriptions] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [activeDiagnosis, setActiveDiagnosis] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    try {
      setActiveDiagnosis(JSON.parse(localStorage.getItem('activeDiagnosis') || 'null'));
    } catch {
      setActiveDiagnosis(null);
    }

    prescriptionDashboardAPI.getPrescriptions()
      .then(res => {
        const data = res?.data || [];
        const normalized = data.map((p, i) => ({
          id: p._id || i,
          patientName: p.patient_name || 'Unknown Patient',
          date: p.date ? (typeof p.date === 'string' ? p.date.slice(0, 10) : new Date(p.date).toISOString().slice(0, 10)) : '',
          diagnosis: p.diagnosis || '',
          medicines: p.medicines || [],
          status: p.status || 'active',
        }));
        setPrescriptions(normalized);
      })
      .catch(() => {});
  }, []);

  const getStatusBadge = (status) => {
    const styles = {
      active: 'bg-green-50 dark:bg-green-500/10 text-green-600 dark:text-green-400',
      completed: 'bg-blue-50 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400',
      cancelled: 'bg-red-50 dark:bg-red-500/10 text-red-600 dark:text-red-400',
    };
    return styles[status] || styles.active;
  };

  const filtered = prescriptions.filter(p => {
    const matchSearch = !searchTerm ||
      p.patientName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.diagnosis.toLowerCase().includes(searchTerm.toLowerCase());
    const matchStatus = filterStatus === 'all' || p.status === filterStatus;
    return matchSearch && matchStatus;
  });

  const diagnosisRoutes = activeDiagnosis?.module_routes || {};

  return (
    <div className="flex-1 overflow-y-auto bg-gray-50 dark:bg-[#101922]">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-white dark:bg-[#111418] border-b border-gray-200 dark:border-[#283039] px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-xl bg-green-500/10 flex items-center justify-center">
              <FileText className="w-5 h-5 text-green-500" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-900 dark:text-white">Prescriptions</h1>
              <p className="text-xs text-gray-500 dark:text-[#9dabb9]">Manage patient prescriptions</p>
            </div>
          </div>
          <button className="flex items-center gap-2 bg-primary text-white px-4 py-2 rounded-xl hover:bg-blue-600 transition text-sm font-medium">
            <Plus className="w-4 h-4" />
            New
          </button>
        </div>
      </div>

      <div className="p-6 space-y-4">
        {activeDiagnosis?.disease && (
          <div className="bg-white dark:bg-[#1b252f] border border-cyan-200 dark:border-cyan-500/20 rounded-2xl p-5 shadow-sm">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-xl bg-cyan-500/10 flex items-center justify-center shrink-0">
                  <Activity className="w-5 h-5 text-cyan-500" />
                </div>
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-cyan-500">Active Diagnosis Context</p>
                  <h2 className="text-lg font-bold text-gray-900 dark:text-white mt-1">{activeDiagnosis.disease}</h2>
                  <p className="text-sm text-gray-500 dark:text-[#9dabb9] mt-1">
                    {Math.round((activeDiagnosis.confidence || 0) * 100)}% confidence · {activeDiagnosis.doctor?.specialty || 'General Physician'}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-300 mt-2">
                    Use the context below to align medicines, tests, and follow-up.
                  </p>
                </div>
              </div>

              <div className="flex flex-wrap gap-2">
                {[
                  { key: 'doctor_portal', label: 'Doctor Portal', fallback: '/doctor-dashboard' },
                  { key: 'prescription_module', label: 'Prescriptions', fallback: '/doctor/prescriptions' },
                  { key: 'lab_tests', label: 'Lab Tests', fallback: '/lab-tests' },
                  { key: 'pharmacy', label: 'Pharmacy', fallback: '/pharmacy' },
                  { key: 'health_tracking', label: 'Health Tracking', fallback: '/health-tracking' },
                ].map(({ key, label, fallback }) => {
                  const route = diagnosisRoutes[key] || fallback;
                  if (!route) return null;
                  return (
                    <button
                      key={key}
                      onClick={() => navigate(route)}
                      className="inline-flex items-center gap-2 rounded-full border border-cyan-200 dark:border-cyan-500/30 bg-cyan-500/10 px-3 py-2 text-xs font-semibold text-cyan-700 dark:text-cyan-200 hover:bg-cyan-500/15 transition-colors"
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                      {label}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white dark:bg-[#1b252f] rounded-2xl border border-gray-100 dark:border-[#283039] p-4">
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search by patient or diagnosis..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-9 pr-4 py-2.5 border border-gray-200 dark:border-[#3d4d5d] rounded-xl bg-gray-50 dark:bg-[#283039] text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-[#9dabb9] focus:outline-none focus:ring-2 focus:ring-primary text-sm"
              />
            </div>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-3 py-2.5 border border-gray-200 dark:border-[#3d4d5d] rounded-xl bg-gray-50 dark:bg-[#283039] text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-3">
          {[
            { label: 'Total', value: prescriptions.length, color: 'text-gray-900 dark:text-white' },
            { label: 'Active', value: prescriptions.filter(p => p.status === 'active').length, color: 'text-green-600 dark:text-green-400' },
            { label: 'This Week', value: 12, color: 'text-blue-600 dark:text-blue-400' },
          ].map((s, i) => (
            <div key={i} className="bg-white dark:bg-[#1b252f] rounded-2xl border border-gray-100 dark:border-[#283039] p-4">
              <p className="text-xs text-gray-500 dark:text-[#9dabb9]">{s.label}</p>
              <p className={`text-2xl font-bold mt-1 ${s.color}`}>{s.value}</p>
            </div>
          ))}
        </div>

        {/* List */}
        <div className="space-y-3">
          {filtered.map((rx) => (
            <div key={rx.id} className="bg-white dark:bg-[#1b252f] border border-gray-100 dark:border-[#283039] rounded-2xl p-5 hover:border-primary/30 dark:hover:border-primary/30 transition-all">
              <div className="flex items-start gap-4 mb-4">
                <div className="w-12 h-12 rounded-2xl bg-green-500/10 flex items-center justify-center shrink-0">
                  <FileText className="w-6 h-6 text-green-500" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1 flex-wrap">
                    <h3 className="font-bold text-gray-900 dark:text-white text-sm">{rx.patientName}</h3>
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getStatusBadge(rx.status)}`}>
                      {rx.status}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 dark:text-[#9dabb9] flex items-center gap-1">
                    <Calendar className="w-3.5 h-3.5" />{rx.date}
                  </p>
                </div>
              </div>

              <div className="bg-gray-50 dark:bg-[#283039] rounded-xl p-3 mb-3">
                <p className="text-xs text-gray-500 dark:text-[#9dabb9] mb-0.5">Diagnosis</p>
                <p className="text-sm font-semibold text-gray-900 dark:text-white">{rx.diagnosis}</p>
              </div>

              <div className="mb-4">
                <p className="text-xs font-semibold text-gray-500 dark:text-[#9dabb9] uppercase tracking-wide mb-2">Medicines</p>
                <div className="space-y-2">
                  {rx.medicines.map((med, idx) => (
                    <div key={idx} className="flex items-center gap-3 bg-gray-50 dark:bg-[#283039] rounded-xl p-3">
                      <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center shrink-0">
                        <Pill className="w-4 h-4 text-blue-500" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-gray-900 dark:text-white">{med.name}</p>
                        <p className="text-xs text-gray-500 dark:text-[#9dabb9]">{med.dosage} · {med.frequency}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex gap-2">
                <button className="px-3 py-1.5 bg-primary text-white rounded-xl hover:bg-blue-600 transition text-xs font-medium">View Details</button>
                <button className="px-3 py-1.5 border border-gray-200 dark:border-[#283039] text-gray-600 dark:text-[#9dabb9] rounded-xl hover:bg-gray-50 dark:hover:bg-[#283039] transition text-xs font-medium">Edit</button>
                <button className="px-3 py-1.5 border border-gray-200 dark:border-[#283039] text-gray-600 dark:text-[#9dabb9] rounded-xl hover:bg-gray-50 dark:hover:bg-[#283039] transition text-xs font-medium">Print</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}