import React, { useState, useEffect } from 'react';
import { Settings, Building2, Save, Upload, ShieldCheck, CheckCircle2, Globe, QrCode } from 'lucide-react';
import { api } from '../services/api';
import { CentreSettings } from '../types';

export const CentreSettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<CentreSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    setLoading(true);
    try {
      const data = await api.getSettings();
      setSettings(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!settings) return;
    setSaving(true);
    setMessage('');
    try {
      await api.updateSettings(settings);
      setMessage('Centre settings updated successfully!');
      setTimeout(() => setMessage(''), 3000);
    } catch (err: any) {
      alert(err.message || 'Failed to update settings');
    } finally {
      setSaving(false);
    }
  };

  if (loading || !settings) {
    return (
      <div className="flex items-center justify-center min-h-[50vh] text-slate-500 text-xs">
        Loading centre settings...
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-in fade-in duration-300">
      <div>
        <h1 className="text-2xl font-serif font-bold text-slate-900 tracking-tight">
          Franchise Centre Configuration & Branding
        </h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Configure official TechnoGlobe Bharatpur centre credentials, authorized signatories, and numbering prefixes.
        </p>
      </div>

      {message && (
        <div className="p-3 rounded-lg bg-emerald-100 border border-emerald-300 text-emerald-900 text-xs font-semibold">
          {message}
        </div>
      )}

      <form onSubmit={handleSave} className="bg-white rounded-2xl border border-slate-200 shadow-xs p-6 md:p-8 space-y-6">
        {/* Active Official Brand Asset Banner */}
        <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-4">
            <div className="bg-white p-2 rounded-lg border border-slate-200 shadow-2xs">
              <img src="/technoglobe_logo.png" alt="Official TechnoGlobe Logo" className="h-10 w-auto object-contain" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-serif font-bold text-sm text-slate-900">Official TechnoGlobe Registered Logo</span>
                <span className="text-[10px] font-bold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded border border-emerald-300">
                  Active in All Documents
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                Automatically rendered at the top of the Certificate of Completion, all 15 internship documents, and the Academic Project Report.
              </p>
            </div>
          </div>
        </div>

        {/* Section 1: Institutional Identification */}
        <div className="space-y-4">
          <div className="flex items-center space-x-2 pb-2 border-b border-slate-200 text-brand-700 font-serif font-bold text-sm">
            <Building2 className="w-4 h-4 text-gold-500" />
            <span>1. INSTITUTION & FRANCHISE IDENTIFICATION</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Parent Organization Name *
              </label>
              <input
                type="text"
                required
                value={settings.org_name}
                onChange={(e) => setSettings({ ...settings, org_name: e.target.value })}
                className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:ring-2 focus:ring-brand-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Franchise / Centre Name *
              </label>
              <input
                type="text"
                required
                value={settings.centre_name}
                onChange={(e) => setSettings({ ...settings, centre_name: e.target.value })}
                className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:ring-2 focus:ring-brand-500 focus:outline-none font-semibold text-brand-900"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Physical Centre Address *
              </label>
              <input
                type="text"
                required
                value={settings.address}
                onChange={(e) => setSettings({ ...settings, address: e.target.value })}
                className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:ring-2 focus:ring-brand-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Centre Code *
              </label>
              <input
                type="text"
                required
                value={settings.centre_code}
                onChange={(e) => setSettings({ ...settings, centre_code: e.target.value })}
                className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:ring-2 focus:ring-brand-500 focus:outline-none font-mono"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Franchise Authorization Reference
              </label>
              <input
                type="text"
                value={settings.auth_ref || ''}
                onChange={(e) => setSettings({ ...settings, auth_ref: e.target.value })}
                className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:ring-2 focus:ring-brand-500 focus:outline-none font-mono"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Official Contact Phone *
              </label>
              <input
                type="text"
                required
                value={settings.phone}
                onChange={(e) => setSettings({ ...settings, phone: e.target.value })}
                className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:ring-2 focus:ring-brand-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Official Contact Email *
              </label>
              <input
                type="email"
                required
                value={settings.email}
                onChange={(e) => setSettings({ ...settings, email: e.target.value })}
                className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:ring-2 focus:ring-brand-500 focus:outline-none"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Official Website *
              </label>
              <input
                type="url"
                required
                value={settings.website}
                onChange={(e) => setSettings({ ...settings, website: e.target.value })}
                className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:ring-2 focus:ring-brand-500 focus:outline-none"
              />
            </div>
          </div>
        </div>

        {/* Section 2: Authorized Signatory */}
        <div className="space-y-4">
          <div className="flex items-center space-x-2 pb-2 border-b border-slate-200 text-brand-700 font-serif font-bold text-sm">
            <ShieldCheck className="w-4 h-4 text-gold-500" />
            <span>2. AUTHORIZED SIGNATORY CREDENTIALS</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Authorized Signatory Name *
              </label>
              <input
                type="text"
                required
                value={settings.signatory_name}
                onChange={(e) => setSettings({ ...settings, signatory_name: e.target.value })}
                className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:ring-2 focus:ring-brand-500 focus:outline-none font-semibold text-slate-900"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Signatory Designation *
              </label>
              <input
                type="text"
                required
                value={settings.signatory_designation}
                onChange={(e) => setSettings({ ...settings, signatory_designation: e.target.value })}
                className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:ring-2 focus:ring-brand-500 focus:outline-none"
              />
            </div>
          </div>

          {/* Authentic Signature Box Notice */}
          <div className="p-3 bg-amber-50 rounded-lg border border-amber-200 text-amber-900 text-xs">
            <p className="font-bold">Important Authenticity Notice:</p>
            <p className="mt-0.5">
              By default, all generated documents include designated clear blank signature lines and official stamp zones for REAL physical verification by authorized centre personnel. Fake digital signatures are disabled by default.
            </p>
          </div>
        </div>

        {/* Section 3: Certificate Numbering System */}
        <div className="space-y-4">
          <div className="flex items-center space-x-2 pb-2 border-b border-slate-200 text-brand-700 font-serif font-bold text-sm">
            <Settings className="w-4 h-4 text-gold-500" />
            <span>3. AUTOMATED NUMBERING & DOCUMENT PREFIXES</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Certificate Number Prefix
              </label>
              <input
                type="text"
                required
                value={settings.cert_prefix}
                onChange={(e) => setSettings({ ...settings, cert_prefix: e.target.value })}
                className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:ring-2 focus:ring-brand-500 focus:outline-none font-mono"
              />
              <span className="text-[10px] text-slate-400">Generates numbers like TG-BPT-DA-2026-0001</span>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Document Reference Prefix
              </label>
              <input
                type="text"
                required
                value={settings.doc_prefix}
                onChange={(e) => setSettings({ ...settings, doc_prefix: e.target.value })}
                className="w-full px-3 py-2 text-xs rounded-lg border border-slate-300 focus:ring-2 focus:ring-brand-500 focus:outline-none font-mono"
              />
              <span className="text-[10px] text-slate-400">Generates document refs like TG/BPT/OFFER/DA/2026/0001</span>
            </div>
          </div>
        </div>

        {/* Section 4: Public Cloud Verification & QR Code Host */}
        <div className="space-y-4">
          <div className="flex items-center space-x-2 pb-2 border-b border-slate-200 text-brand-700 font-serif font-bold text-sm">
            <Globe className="w-4 h-4 text-gold-500" />
            <span>4. PUBLIC CLOUD VERIFICATION & QR CODE HOST</span>
          </div>

          <div className="space-y-3">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Public Verification Base URL *
              </label>
              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  required
                  value={settings.verification_base_url || ''}
                  onChange={(e) => setSettings({ ...settings, verification_base_url: e.target.value })}
                  placeholder="https://verify.technoglobe.co.in or http://192.168.0.103:8000"
                  className="flex-1 px-3 py-2 text-xs rounded-lg border border-slate-300 focus:ring-2 focus:ring-brand-500 focus:outline-none font-mono"
                />
              </div>
              <p className="text-[11px] text-slate-500 mt-1">
                This domain/host is encoded into all certificate QR codes. When scanned by Google Lens or phone cameras, it opens this URL.
              </p>
            </div>

            {/* Quick Presets */}
            <div className="flex flex-wrap items-center gap-2 pt-1">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Quick Presets:</span>
              <button
                type="button"
                onClick={() => setSettings({ ...settings, verification_base_url: window.location.origin })}
                className="px-2.5 py-1 text-[11px] font-medium rounded-md bg-slate-100 hover:bg-slate-200 text-slate-700 transition-colors"
              >
                Current Host ({window.location.origin})
              </button>
              <button
                type="button"
                onClick={() => setSettings({ ...settings, verification_base_url: 'http://192.168.0.103:8000' })}
                className="px-2.5 py-1 text-[11px] font-medium rounded-md bg-slate-100 hover:bg-slate-200 text-slate-700 transition-colors"
              >
                Local LAN (192.168.0.103:8000)
              </button>
              <button
                type="button"
                onClick={() => setSettings({ ...settings, verification_base_url: 'https://verify.technoglobe.co.in' })}
                className="px-2.5 py-1 text-[11px] font-medium rounded-md bg-brand-50 hover:bg-brand-100 text-brand-800 border border-brand-200 transition-colors"
              >
                Public Cloud Domain (https://verify.technoglobe.co.in)
              </button>
            </div>

            <div className="p-3 bg-blue-50/70 rounded-lg border border-blue-200 text-blue-900 text-xs flex items-start space-x-2.5">
              <QrCode className="w-4 h-4 text-blue-600 mt-0.5 shrink-0" />
              <div>
                <p className="font-bold">Public Mobile Verification Advice:</p>
                <p className="mt-0.5 text-[11px] text-blue-800">
                  For QR codes on printed certificates to work for employers and universities outside your office Wi-Fi, set this to a publicly accessible HTTPS domain (e.g., your custom domain, Cloudflare tunnel, or deployed cloud endpoint).
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="pt-4 border-t border-slate-200 flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="inline-flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-brand-700 hover:bg-brand-800 text-white text-xs font-bold shadow-md transition-transform active:scale-95 disabled:opacity-50"
          >
            <Save className="w-4 h-4 text-gold-400" />
            <span>{saving ? 'Saving Configuration...' : 'Save Centre Configuration'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};
