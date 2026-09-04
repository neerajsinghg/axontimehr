import React, { useState, useEffect } from 'react';
import {
  Shield,
  Plus,
  RefreshCw,
  CheckCircle,
  Building,
  Compass
} from 'lucide-react';
import { locationApi, AttendanceLocation, AttendanceLocationPolicy } from '../../services/api/location';

export const LocationSettingsTab: React.FC = () => {
  const [locations, setLocations] = useState<AttendanceLocation[]>([]);
  const [policy, setPolicy] = useState<AttendanceLocationPolicy | null>(null);
  const [loading, setLoading] = useState(true);
  const [savingPolicy, setSavingPolicy] = useState(false);

  // Modal State
  const [showAddModal, setShowAddModal] = useState(false);
  const [formData, setFormData] = useState({
    code: '',
    name: '',
    latitude: 28.4595,
    longitude: 77.0266,
    radius_meters: 100,
    accuracy_requirement: 50.0
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [locList, polData] = await Promise.all([
        locationApi.getLocations(),
        locationApi.getPolicy()
      ]);
      setLocations(locList);
      setPolicy(polData);
    } catch (err) {
      console.error('Failed to load location settings:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSavePolicy = async () => {
    if (!policy) return;
    setSavingPolicy(true);
    try {
      const updated = await locationApi.updatePolicy({
        location_required: policy.location_required,
        geofence_enabled: policy.geofence_enabled,
        allowed_radius: policy.allowed_radius,
        minimum_accuracy: policy.minimum_accuracy,
        outside_geofence_action: policy.outside_geofence_action,
        selfie_required: policy.selfie_required
      });
      setPolicy(updated);
      alert('Attendance Location Policy updated successfully!');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to update policy');
    } finally {
      setSavingPolicy(false);
    }
  };

  const handleCreateLocation = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await locationApi.createLocation(formData);
      setShowAddModal(false);
      setFormData({
        code: '',
        name: '',
        latitude: 28.4595,
        longitude: 77.0266,
        radius_meters: 100,
        accuracy_requirement: 50.0
      });
      fetchData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to create location');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <RefreshCw className="animate-spin text-emerald-600 h-8 w-8" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* 1. Global Geofence Policy Settings */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-6">
        <div className="flex items-center justify-between border-b border-slate-100 pb-4">
          <div className="flex items-center space-x-3">
            <Shield className="h-6 w-6 text-emerald-600" />
            <div>
              <h3 className="text-lg font-bold text-slate-800">Geofence & Location Policy</h3>
              <p className="text-xs text-slate-500">Configure global enforcement rules for GPS geofencing & identity verification.</p>
            </div>
          </div>
          <button
            onClick={handleSavePolicy}
            disabled={savingPolicy}
            className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-medium text-sm flex items-center space-x-2 transition"
          >
            {savingPolicy ? <RefreshCw className="animate-spin h-4 w-4" /> : <CheckCircle className="h-4 w-4" />}
            <span>Save Policy Changes</span>
          </button>
        </div>

        {policy && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <label className="flex items-center space-x-3 p-3 rounded-lg border border-slate-100 hover:bg-slate-50 cursor-pointer">
                <input
                  type="checkbox"
                  checked={policy.location_required}
                  onChange={(e) => setPolicy({ ...policy, location_required: e.target.checked })}
                  className="h-4 w-4 text-emerald-600 rounded focus:ring-emerald-500"
                />
                <div>
                  <span className="text-sm font-semibold text-slate-800">Require GPS Location Capture</span>
                  <p className="text-xs text-slate-500">Employees must capture live GPS coordinates to check in or out.</p>
                </div>
              </label>

              <label className="flex items-center space-x-3 p-3 rounded-lg border border-slate-100 hover:bg-slate-50 cursor-pointer">
                <input
                  type="checkbox"
                  checked={policy.geofence_enabled}
                  onChange={(e) => setPolicy({ ...policy, geofence_enabled: e.target.checked })}
                  className="h-4 w-4 text-emerald-600 rounded focus:ring-emerald-500"
                />
                <div>
                  <span className="text-sm font-semibold text-slate-800">Strict Geofence Enforcement</span>
                  <p className="text-xs text-slate-500">Validate distance against assigned branch or site center point.</p>
                </div>
              </label>

              <label className="flex items-center space-x-3 p-3 rounded-lg border border-slate-100 hover:bg-slate-50 cursor-pointer">
                <input
                  type="checkbox"
                  checked={policy.selfie_required}
                  onChange={(e) => setPolicy({ ...policy, selfie_required: e.target.checked })}
                  className="h-4 w-4 text-emerald-600 rounded focus:ring-emerald-500"
                />
                <div>
                  <span className="text-sm font-semibold text-slate-800">Selfie Identity Verification</span>
                  <p className="text-xs text-slate-500">Require photo upload with facial match check upon punching.</p>
                </div>
              </label>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                  Outside Geofence Action Policy
                </label>
                <select
                  value={policy.outside_geofence_action}
                  onChange={(e) => setPolicy({ ...policy, outside_geofence_action: e.target.value as any })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500"
                >
                  <option value="REJECT">REJECT (Block punch completely)</option>
                  <option value="ALLOW_WITH_WARNING">ALLOW_WITH_WARNING (Flag in Exceptions)</option>
                  <option value="REQUIRE_APPROVAL">REQUIRE_APPROVAL (Send for Manager Review)</option>
                  <option value="RECORD_EXCEPTION">RECORD_EXCEPTION (Log silently for Audit)</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                    Allowed Radius (Meters)
                  </label>
                  <input
                    type="number"
                    value={policy.allowed_radius}
                    onChange={(e) => setPolicy({ ...policy, allowed_radius: parseInt(e.target.value) || 100 })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                    Min GPS Accuracy (Meters)
                  </label>
                  <input
                    type="number"
                    value={policy.minimum_accuracy}
                    onChange={(e) => setPolicy({ ...policy, minimum_accuracy: parseFloat(e.target.value) || 50.0 })}
                    className="w-full px-3 py-2 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-emerald-500"
                  />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 2. Office & Site Locations Master Table */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Building className="h-6 w-6 text-emerald-600" />
            <div>
              <h3 className="text-lg font-bold text-slate-800">Office & Site Locations Master</h3>
              <p className="text-xs text-slate-500">Manage GPS centers and geofence radii for physical company offices.</p>
            </div>
          </div>
          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-medium flex items-center space-x-2 transition"
          >
            <Plus className="h-4 w-4" />
            <span>Add Location</span>
          </button>
        </div>

        <div className="overflow-x-auto border border-slate-200 rounded-lg">
          <table className="w-full text-left text-sm text-slate-700">
            <thead className="bg-slate-50 text-xs uppercase font-semibold text-slate-500 border-b border-slate-200">
              <tr>
                <th className="px-4 py-3">Code</th>
                <th className="px-4 py-3">Location Name</th>
                <th className="px-4 py-3">Latitude / Longitude</th>
                <th className="px-4 py-3">Radius</th>
                <th className="px-4 py-3">Accuracy</th>
                <th className="px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {locations.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-6 text-center text-slate-400">
                    No office locations added yet. Click "Add Location" above.
                  </td>
                </tr>
              ) : (
                locations.map((loc) => (
                  <tr key={loc.id} className="hover:bg-slate-50/50">
                    <td className="px-4 py-3 font-mono text-xs font-bold text-emerald-700">{loc.code}</td>
                    <td className="px-4 py-3 font-medium text-slate-800">{loc.name}</td>
                    <td className="px-4 py-3 font-mono text-xs text-slate-600">
                      {loc.latitude.toFixed(6)}, {loc.longitude.toFixed(6)}
                    </td>
                    <td className="px-4 py-3 text-xs">{loc.radius_meters} meters</td>
                    <td className="px-4 py-3 text-xs">{loc.accuracy_requirement} meters</td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
                        {loc.status}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Location Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-md w-full p-6 shadow-xl border border-slate-200 space-y-4">
            <div className="flex justify-between items-center border-b pb-3">
              <h4 className="font-bold text-slate-800">Add New Office Location</h4>
              <button onClick={() => setShowAddModal(false)} className="text-slate-400 hover:text-slate-600">✕</button>
            </div>
            <form onSubmit={handleCreateLocation} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Location Code</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. LOC-HQ-01"
                  value={formData.code}
                  onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Location Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Gurugram Tech Park Office"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg text-sm"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Latitude</label>
                  <input
                    type="number"
                    step="any"
                    required
                    value={formData.latitude}
                    onChange={(e) => setFormData({ ...formData, latitude: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-2 border rounded-lg text-sm font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Longitude</label>
                  <input
                    type="number"
                    step="any"
                    required
                    value={formData.longitude}
                    onChange={(e) => setFormData({ ...formData, longitude: parseFloat(e.target.value) || 0 })}
                    className="w-full px-3 py-2 border rounded-lg text-sm font-mono"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Radius (Meters)</label>
                  <input
                    type="number"
                    required
                    value={formData.radius_meters}
                    onChange={(e) => setFormData({ ...formData, radius_meters: parseInt(e.target.value) || 100 })}
                    className="w-full px-3 py-2 border rounded-lg text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Min Accuracy</label>
                  <input
                    type="number"
                    required
                    value={formData.accuracy_requirement}
                    onChange={(e) => setFormData({ ...formData, accuracy_requirement: parseFloat(e.target.value) || 50 })}
                    className="w-full px-3 py-2 border rounded-lg text-sm"
                  />
                </div>
              </div>

              {/* Visual Geofence Radius Map Preview */}
              <div className="p-4 bg-emerald-50/50 rounded-lg border border-emerald-100 text-center space-y-2">
                <Compass className="h-6 w-6 text-emerald-600 mx-auto animate-pulse" />
                <p className="text-xs font-semibold text-emerald-800">Visual Geofence Radius Preview</p>
                <p className="text-xs text-emerald-600">
                  Center ({formData.latitude.toFixed(4)}, {formData.longitude.toFixed(4)}) with a circular perimeter of {formData.radius_meters}m.
                </p>
              </div>

              <div className="flex justify-end space-x-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 border border-slate-300 rounded-lg text-sm font-medium text-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-medium"
                >
                  Save Location
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
