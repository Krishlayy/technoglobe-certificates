import React, { useState, useEffect } from 'react';
import { 
  Award, Download, Printer, Sparkles, CheckCircle2, ShieldCheck, 
  Trash2, RefreshCw, Eye, GraduationCap, Sun, Globe, FileText, Check
} from 'lucide-react';
import { QRCodeSVG } from 'qrcode.react';
import { api } from '../services/api';
import { useInstitution } from '../contexts/InstitutionContext';
import { AppreciationCertificate } from '../types';

export const AppreciationCertificatePage: React.FC = () => {
  const { institutionId, activeInstitution, selectInstitution, isPoddar, isPoswal, isTechnoglobe, institutions } = useInstitution();
  
  const [formData, setFormData] = useState({
    recipient_name: 'Ananya Sharma',
    institution_id: institutionId || 1,
    title: 'CERTIFICATE OF APPRECIATION',
    subtitle: 'PROUDLY PRESENTED IN RECOGNITION OF EXCELLENCE',
    appreciation_text: 'For outstanding technical performance, exceptional diligence, and remarkable contributions during the advanced practical project execution.',
    event_name: 'Emerging Technologies & Software Development',
    issue_date: new Date().toISOString().split('T')[0],
    certificate_number: '',
    signatory_name: activeInstitution.signatory_name || 'Nitin Agarwal',
    signatory_designation: activeInstitution.signatory_designation || 'Director / Authority',
    include_faculty: false,
    mentor_name: '',
    mentor_designation: 'Faculty Guide / Coordinator'
  });

  const [certificatesList, setCertificatesList] = useState<AppreciationCertificate[]>([]);
  const [loadingList, setLoadingList] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  // Sync institution details when changed
  useEffect(() => {
    setFormData(prev => ({
      ...prev,
      institution_id: institutionId,
      signatory_name: activeInstitution.signatory_name || (institutionId === 2 ? 'Madhuvan Singh Gurjar' : 'Nitin Agarwal'),
      signatory_designation: activeInstitution.signatory_designation || (institutionId === 2 ? 'Authority' : 'Director / Authority'),
      certificate_number: `${activeInstitution.cert_prefix || 'PCTM'}-APP-2026-${Math.floor(1000 + Math.random() * 9000)}`
    }));
  }, [institutionId, activeInstitution]);

  // Load history list
  const loadHistory = async () => {
    try {
      setLoadingList(true);
      const data = await api.getAppreciationCertificates();
      setCertificatesList(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingList(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, [institutionId]);

  const handleQuickPreset = (type: 'excellence' | 'participation' | 'innovation') => {
    if (type === 'excellence') {
      setFormData(prev => ({
        ...prev,
        title: 'CERTIFICATE OF EXCELLENCE',
        subtitle: 'PROUDLY PRESENTED FOR OUTSTANDING ACHIEVEMENT',
        appreciation_text: 'In recognition of superlative performance, exemplary technical proficiency, and high standard of commitment demonstrated during the technical program.'
      }));
    } else if (type === 'participation') {
      setFormData(prev => ({
        ...prev,
        title: 'CERTIFICATE OF APPRECIATION',
        subtitle: 'PRESENTED WITH HEARTFELT COMMENDATION',
        appreciation_text: 'For active participation, consistent attendance, and valuable contributions in the hands-on engineering and software workshop.'
      }));
    } else if (type === 'innovation') {
      setFormData(prev => ({
        ...prev,
        title: 'CERTIFICATE OF MERIT & INNOVATION',
        subtitle: 'HONORING CREATIVE LEADERSHIP & PROJECT EXECUTION',
        appreciation_text: 'For demonstrating outstanding creativity, architectural ingenuity, and practical excellence in the capstone project design and live demonstration.'
      }));
    }
  };

  const handleGenerateAndDownload = async () => {
    try {
      setGenerating(true);
      setErrorMessage('');
      setSuccessMessage('');

      const payload = {
        recipient_name: formData.recipient_name.trim(),
        institution_id: formData.institution_id,
        title: formData.title.trim(),
        subtitle: formData.subtitle.trim(),
        appreciation_text: formData.appreciation_text.trim(),
        event_name: formData.event_name.trim(),
        issue_date: formData.issue_date,
        certificate_number: formData.certificate_number.trim() || undefined,
        signatory_name: formData.signatory_name.trim(),
        signatory_designation: formData.signatory_designation.trim(),
        mentor_name: formData.include_faculty ? formData.mentor_name.trim() : null,
        mentor_designation: formData.include_faculty ? formData.mentor_designation.trim() : null,
      };

      const res = await api.generateAppreciationCertificate(payload);
      setSuccessMessage(`Certificate for "${formData.recipient_name}" generated successfully!`);
      
      // Direct Download
      const pdfUrl = api.getAppreciationPdfUrl(res.id);
      window.open(pdfUrl, '_blank');

      loadHistory();
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to generate appreciation certificate');
    } finally {
      setGenerating(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this appreciation certificate record?')) return;
    try {
      await api.deleteAppreciationCertificate(id);
      loadHistory();
    } catch (e: any) {
      alert(e.message || 'Delete failed');
    }
  };

  // Preview colors & branding
  const primaryColor = isPoswal ? '#6B2222' : (isTechnoglobe ? '#1E3A8A' : '#0A2540');
  const accentColor = isPoswal ? '#B45309' : (isTechnoglobe ? '#F59E0B' : '#EAA824');
  const verifyUrl = `${window.location.protocol}//${window.location.host}/verify?cert=${encodeURIComponent(formData.certificate_number || 'PCTM-APP-2026-0001')}&name=${encodeURIComponent(formData.recipient_name)}&course=${encodeURIComponent(formData.title)}&date=${encodeURIComponent(formData.issue_date)}`;

  return (
    <div className="space-y-8 animate-in fade-in duration-300 pb-16">
      {/* Top Header Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-indigo-950 rounded-3xl p-6 sm:p-8 text-white shadow-xl relative overflow-hidden border border-slate-700">
        <div className="absolute top-0 right-0 w-96 h-96 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-amber-400/20 text-amber-300 border border-amber-400/30 text-xs font-bold uppercase tracking-wider mb-2">
              <Award className="w-4 h-4 text-amber-400" />
              <span>Custom Certification Studio</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-serif font-black text-white tracking-tight">
              Certificate of Appreciation & Excellence
            </h1>
            <p className="text-slate-300 text-xs sm:text-sm mt-1 max-w-2xl leading-relaxed">
              Design, preview, and generate authentic custom certificates with scannable QR verification, authentic signatures, and official institution seals across all 3 independent organizations.
            </p>
          </div>

          {/* Quick Actions */}
          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={() => window.print()}
              className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white text-xs font-bold border border-white/20 transition-all cursor-pointer shadow-sm"
            >
              <Printer className="w-4 h-4 text-slate-300" />
              <span>Print Preview</span>
            </button>
            <button
              onClick={handleGenerateAndDownload}
              disabled={generating || !formData.recipient_name.trim()}
              className="inline-flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-black text-sm transition-all cursor-pointer shadow-lg shadow-amber-500/20 disabled:opacity-50"
            >
              <Download className="w-4 h-4" />
              <span>{generating ? 'Generating PDF...' : 'Generate Official PDF'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* 3-Organization Selector Bar */}
      <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-sm">
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
            Select Issuing Organization (100% Isolated Profile & Branding)
          </span>
          <span className="text-xs font-semibold text-slate-400">
            Active: <b className="text-slate-800">{activeInstitution.name}</b>
          </span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {/* Poddar College */}
          <button
            type="button"
            onClick={() => selectInstitution(1)}
            className={`p-3.5 rounded-xl border-2 flex items-center space-x-3 text-left transition-all cursor-pointer ${
              isPoddar 
                ? 'border-blue-600 bg-blue-50/80 shadow-sm ring-2 ring-blue-500/20' 
                : 'border-slate-200 bg-slate-50/50 hover:border-slate-300'
            }`}
          >
            <div className="w-10 h-10 rounded-lg bg-white p-1 flex items-center justify-center shrink-0 border border-slate-200 shadow-2xs">
              <img src="/poddar_logo.png" alt="Poddar Logo" className="max-h-full max-w-full object-contain" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center space-x-1 text-blue-700 text-[11px] font-bold">
                <GraduationCap className="w-3.5 h-3.5" />
                <span>Poddar College</span>
              </div>
              <div className="text-xs font-bold text-slate-900 truncate">Near SP Office, Bharatpur</div>
              <div className="text-[10px] text-slate-500 truncate">Authority: Nitin Agarwal</div>
            </div>
          </button>

          {/* Poswal Developers */}
          <button
            type="button"
            onClick={() => selectInstitution(2)}
            className={`p-3.5 rounded-xl border-2 flex items-center space-x-3 text-left transition-all cursor-pointer ${
              isPoswal 
                ? 'border-amber-600 bg-amber-50/80 shadow-sm ring-2 ring-amber-500/20' 
                : 'border-slate-200 bg-slate-50/50 hover:border-slate-300'
            }`}
          >
            <div className="w-10 h-10 rounded-lg bg-white p-1 flex items-center justify-center shrink-0 border border-slate-200 shadow-2xs">
              <img src="/poswal_logo.png" alt="Poswal Logo" className="max-h-full max-w-full object-contain" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center space-x-1 text-amber-700 text-[11px] font-bold">
                <Sun className="w-3.5 h-3.5" />
                <span>Poswal Developers</span>
              </div>
              <div className="text-xs font-bold text-slate-900 truncate">Solar PV & Industrial Division</div>
              <div className="text-[10px] text-slate-500 truncate">Authority: Madhuvan Gurjar</div>
            </div>
          </button>

          {/* Technoglobe Jaipur */}
          <button
            type="button"
            onClick={() => selectInstitution(3)}
            className={`p-3.5 rounded-xl border-2 flex items-center space-x-3 text-left transition-all cursor-pointer ${
              isTechnoglobe 
                ? 'border-indigo-600 bg-indigo-50/80 shadow-sm ring-2 ring-indigo-500/20' 
                : 'border-slate-200 bg-slate-50/50 hover:border-slate-300'
            }`}
          >
            <div className="w-10 h-10 rounded-lg bg-white p-1 flex items-center justify-center shrink-0 border border-slate-200 shadow-2xs">
              <img src="/technoglobe_logo.png" alt="Technoglobe Logo" className="max-h-full max-w-full object-contain" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center space-x-1 text-indigo-700 text-[11px] font-bold">
                <Globe className="w-3.5 h-3.5" />
                <span>Technoglobe Jaipur</span>
              </div>
              <div className="text-xs font-bold text-slate-900 truncate">Gopalpura Bypass, Jaipur</div>
              <div className="text-[10px] text-slate-500 truncate">Authority: Nitin Agarwal</div>
            </div>
          </button>
        </div>
      </div>

      {/* Messages */}
      {successMessage && (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-300 text-emerald-800 text-xs font-semibold flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>{successMessage}</span>
          </div>
          <button onClick={() => setSuccessMessage('')} className="text-emerald-700 hover:text-emerald-900 text-xs cursor-pointer">✕</button>
        </div>
      )}

      {errorMessage && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-300 text-red-800 text-xs font-semibold flex items-center justify-between">
          <span>{errorMessage}</span>
          <button onClick={() => setErrorMessage('')} className="text-red-700 hover:text-red-900 text-xs cursor-pointer">✕</button>
        </div>
      )}

      {/* Main 2-Column Studio */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Form Controls (5 cols) */}
        <div className="lg:col-span-5 bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider flex items-center space-x-1.5">
              <Sparkles className="w-4 h-4 text-amber-500" />
              <span>Certificate Parameters</span>
            </h2>
            <div className="flex items-center space-x-1 text-[11px]">
              <span className="text-slate-400">Presets:</span>
              <button onClick={() => handleQuickPreset('excellence')} className="px-2 py-0.5 rounded bg-amber-100 hover:bg-amber-200 text-amber-900 font-bold cursor-pointer">Excellence</button>
              <button onClick={() => handleQuickPreset('innovation')} className="px-2 py-0.5 rounded bg-blue-100 hover:bg-blue-200 text-blue-900 font-bold cursor-pointer">Innovation</button>
              <button onClick={() => handleQuickPreset('participation')} className="px-2 py-0.5 rounded bg-emerald-100 hover:bg-emerald-200 text-emerald-900 font-bold cursor-pointer">Appreciation</button>
            </div>
          </div>

          <div className="space-y-3">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Recipient Full Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={formData.recipient_name}
                onChange={e => setFormData({ ...formData, recipient_name: e.target.value })}
                placeholder="e.g. Rohan Sharma / Ms. Sneha Agarwal"
                className="w-full px-3.5 py-2 text-sm font-bold text-slate-900 rounded-xl border border-slate-300 focus:ring-2 focus:ring-amber-500 focus:border-amber-500 bg-slate-50/50"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-[11px] font-bold text-slate-700 mb-1">
                  Main Title
                </label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={e => setFormData({ ...formData, title: e.target.value })}
                  className="w-full px-3 py-1.5 text-xs font-semibold text-slate-900 rounded-lg border border-slate-300 focus:ring-2 focus:ring-amber-500"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-700 mb-1">
                  Issue Date
                </label>
                <input
                  type="date"
                  value={formData.issue_date}
                  onChange={e => setFormData({ ...formData, issue_date: e.target.value })}
                  className="w-full px-3 py-1.5 text-xs font-semibold text-slate-900 rounded-lg border border-slate-300 focus:ring-2 focus:ring-amber-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-[11px] font-bold text-slate-700 mb-1">
                Subtitle / Commendation Headline
              </label>
              <input
                type="text"
                value={formData.subtitle}
                onChange={e => setFormData({ ...formData, subtitle: e.target.value })}
                placeholder="e.g. PROUDLY PRESENTED IN RECOGNITION OF EXCELLENCE"
                className="w-full px-3 py-1.5 text-xs font-medium text-slate-900 rounded-lg border border-slate-300 focus:ring-2 focus:ring-amber-500"
              />
            </div>

            <div>
              <label className="block text-[11px] font-bold text-slate-700 mb-1">
                Event / Program / Domain Name
              </label>
              <input
                type="text"
                value={formData.event_name}
                onChange={e => setFormData({ ...formData, event_name: e.target.value })}
                placeholder="e.g. Solar PV System Design / AI Machine Learning / Annual Tech Fest"
                className="w-full px-3 py-1.5 text-xs font-medium text-slate-900 rounded-lg border border-slate-300 focus:ring-2 focus:ring-amber-500"
              />
            </div>

            <div>
              <label className="block text-[11px] font-bold text-slate-700 mb-1">
                Appreciation Text / Citation
              </label>
              <textarea
                rows={3}
                value={formData.appreciation_text}
                onChange={e => setFormData({ ...formData, appreciation_text: e.target.value })}
                className="w-full px-3 py-2 text-xs text-slate-900 rounded-lg border border-slate-300 focus:ring-2 focus:ring-amber-500 leading-relaxed resize-none"
              />
            </div>

            <div>
              <label className="block text-[11px] font-bold text-slate-700 mb-1">
                Certificate Number
              </label>
              <input
                type="text"
                value={formData.certificate_number}
                onChange={e => setFormData({ ...formData, certificate_number: e.target.value })}
                className="w-full px-3 py-1.5 text-xs font-mono font-bold text-slate-900 rounded-lg border border-slate-300 focus:ring-2 focus:ring-amber-500"
              />
            </div>

            {/* Authority Signatory Info */}
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-2">
              <div className="flex items-center justify-between text-[11px] font-bold text-slate-800">
                <span>Director / Authority Signatory</span>
                <span className="text-emerald-700 bg-emerald-100 px-1.5 py-0.5 rounded text-[10px]">Autofilled</span>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <input
                  type="text"
                  value={formData.signatory_name}
                  onChange={e => setFormData({ ...formData, signatory_name: e.target.value })}
                  placeholder="Signatory Name"
                  className="px-2.5 py-1 text-xs font-semibold text-slate-900 rounded border border-slate-300 bg-white"
                />
                <input
                  type="text"
                  value={formData.signatory_designation}
                  onChange={e => setFormData({ ...formData, signatory_designation: e.target.value })}
                  placeholder="Designation"
                  className="px-2.5 py-1 text-xs text-slate-700 rounded border border-slate-300 bg-white"
                />
              </div>
            </div>

            {/* Optional Faculty Toggle */}
            <div className="p-3 rounded-xl bg-amber-50/60 border border-amber-200/80 space-y-2.5">
              <div className="flex items-center justify-between">
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.include_faculty}
                    onChange={e => setFormData({ ...formData, include_faculty: e.target.checked })}
                    className="w-4 h-4 rounded text-amber-600 focus:ring-amber-500"
                  />
                  <span className="text-xs font-bold text-slate-900">Include Faculty / Guide Signature (Optional)</span>
                </label>
                <span className="text-[10px] text-amber-800 font-bold">
                  {formData.include_faculty ? 'Dual Signatures' : 'Single Authority'}
                </span>
              </div>
              
              {formData.include_faculty ? (
                <div className="grid grid-cols-2 gap-2 pt-1">
                  <input
                    type="text"
                    value={formData.mentor_name}
                    onChange={e => setFormData({ ...formData, mentor_name: e.target.value })}
                    placeholder="Faculty Name (e.g. Prof. Krishlay)"
                    className="px-2.5 py-1 text-xs font-semibold text-slate-900 rounded border border-amber-300 bg-white"
                  />
                  <input
                    type="text"
                    value={formData.mentor_designation}
                    onChange={e => setFormData({ ...formData, mentor_designation: e.target.value })}
                    placeholder="Faculty Designation"
                    className="px-2.5 py-1 text-xs text-slate-700 rounded border border-amber-300 bg-white"
                  />
                </div>
              ) : (
                <p className="text-[10px] text-slate-600 leading-relaxed">
                  ✓ Leaving unchecked renders a centered, prominent single authority signature for <b>{formData.signatory_name}</b> ({formData.signatory_designation}).
                </p>
              )}
            </div>

            <button
              type="button"
              onClick={handleGenerateAndDownload}
              disabled={generating || !formData.recipient_name.trim()}
              className="w-full py-3 px-4 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs flex items-center justify-center space-x-2 transition-all cursor-pointer shadow-md disabled:opacity-50"
            >
              <Download className="w-4 h-4 text-amber-400" />
              <span>{generating ? 'Processing PDF Generation...' : 'Generate & Download Vector PDF'}</span>
            </button>
          </div>
        </div>

        {/* Right Live Visual Certificate Preview (7 cols) */}
        <div className="lg:col-span-7 bg-white rounded-2xl border border-slate-200 p-5 shadow-sm space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-slate-100">
            <div className="flex items-center space-x-2">
              <Eye className="w-4 h-4 text-blue-600" />
              <span className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                Live A4 Landscape Vector Preview
              </span>
            </div>
            <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full">
              Authentic Layout Matching ReportLab Engine
            </span>
          </div>

          {/* Certificate Canvas / SVG Layout */}
          <div 
            className="w-full aspect-[1.414/1] bg-white rounded-xl shadow-lg border-4 relative overflow-hidden flex flex-col justify-between p-5 select-none"
            style={{ borderColor: primaryColor }}
          >
            {/* Inner Guilloche Border */}
            <div 
              className="absolute inset-2 border-2 pointer-events-none rounded-lg"
              style={{ borderColor: accentColor }}
            />
            {/* Corner Ornaments */}
            <div className="absolute top-3 left-3 w-4 h-4 border-t-2 border-l-2" style={{ borderColor: accentColor }} />
            <div className="absolute top-3 right-3 w-4 h-4 border-t-2 border-r-2" style={{ borderColor: accentColor }} />
            <div className="absolute bottom-3 left-3 w-4 h-4 border-b-2 border-l-2" style={{ borderColor: accentColor }} />
            <div className="absolute bottom-3 right-3 w-4 h-4 border-b-2 border-r-2" style={{ borderColor: accentColor }} />

            {/* Faint Watermark Logo */}
            <div className="absolute inset-0 flex items-center justify-center opacity-10 pointer-events-none">
              <img 
                src={activeInstitution.logo || (isPoswal ? '/poswal_logo.png' : (isTechnoglobe ? '/technoglobe_logo.png' : '/poddar_logo.png'))} 
                alt="Watermark" 
                className="max-h-48 max-w-48 object-contain"
              />
            </div>

            {/* 1. Header Section */}
            <div className="relative z-10 text-center pt-1">
              <div className="flex justify-center mb-1">
                <img 
                  src={isPoswal ? '/poswal_logo.png' : (isTechnoglobe ? '/technoglobe_logo.png' : '/poddar_logo.png')} 
                  alt="Institution Logo" 
                  className="h-8 max-w-[150px] object-contain"
                />
              </div>
              <h3 className="text-xs sm:text-sm font-serif font-black tracking-wide" style={{ color: primaryColor }}>
                {isPoswal ? 'POSWAL DEVELOPERS' : (isTechnoglobe ? 'TECHNOGLOBE - ADVANCED IT TRAINING & DEVELOPMENT' : 'PODDAR COLLEGE OF TECHNOLOGY & MANAGEMENT')}
              </h3>
              <p className="text-[8px] sm:text-[9px] text-slate-500 font-medium">
                {isPoswal ? '214, Bapu Nagar, Ghana Road, Bharatpur (Raj.) | Mob: 9414694727 | GST: 08ABIFP2454N1ZQ' : (isTechnoglobe ? 'Plot No. 4, Gopalpura Bypass Road, Near Triveni Nagar, Jaipur (Raj.) | Email: info@technoglobe.co.in' : 'Near SP Office, Bharatpur (Raj.) | Contact: 9414293370 | Email: nitin_pitm@yahoo.com | Web: poddarcollege.org')}
              </p>
              <div className="w-48 h-0.5 mx-auto mt-1" style={{ backgroundColor: accentColor }} />
            </div>

            {/* 2. Certificate Body */}
            <div className="relative z-10 text-center space-y-1.5 my-auto px-4">
              <div className="text-base sm:text-lg font-serif font-black tracking-widest" style={{ color: primaryColor }}>
                {formData.title.toUpperCase()}
              </div>
              <div className="text-[9px] sm:text-[10px] italic font-serif" style={{ color: accentColor }}>
                {formData.subtitle}
              </div>

              {/* Recipient Name */}
              <div className="pt-1">
                <div className="text-sm sm:text-lg font-serif font-black uppercase tracking-wider text-slate-900">
                  {formData.recipient_name || 'RECIPIENT NAME'}
                </div>
                <div className="w-32 h-0.5 mx-auto mt-0.5" style={{ backgroundColor: accentColor }} />
              </div>

              {/* Event / Recognition Domain */}
              {formData.event_name && (
                <div className="text-[9px] sm:text-[10px] font-bold text-slate-800">
                  In Recognition of Distinguished Performance in {formData.event_name}
                </div>
              )}

              {/* Citation */}
              <p className="text-[8px] sm:text-[9px] text-slate-700 max-w-md mx-auto leading-relaxed line-clamp-3">
                {formData.appreciation_text}
              </p>
            </div>

            {/* 3. Bottom Row: QR Code (Left), Seal (Center), Signatures (Right) */}
            <div className="relative z-10 grid grid-cols-3 items-end gap-2 pt-2 border-t border-slate-100">
              {/* QR Verification Box */}
              <div className="flex items-center space-x-1.5 p-1 rounded-md bg-slate-50 border border-slate-200">
                <div className="p-0.5 bg-white rounded border border-slate-300 shrink-0">
                  <QRCodeSVG value={verifyUrl} size={36} level="M" />
                </div>
                <div className="text-[6.5px] sm:text-[7px] leading-tight text-slate-600">
                  <div className="font-bold text-slate-900 truncate">OFFICIAL RECORD</div>
                  <div className="truncate">No: {formData.certificate_number || 'PCTM-APP-001'}</div>
                  <div className="truncate">Date: {formData.issue_date}</div>
                  <div className="text-emerald-700 font-bold">✓ Verified Record</div>
                </div>
              </div>

              {/* Center Official Seal */}
              <div className="flex flex-col items-center justify-center">
                <div className="w-11 h-11 rounded-full border border-slate-200 p-0.5 bg-white shadow-2xs flex items-center justify-center">
                  <img 
                    src={isPoswal ? '/msme_logo.png' : '/poddar_stamp.png'} 
                    alt="Official Seal" 
                    className="max-h-full max-w-full object-contain"
                  />
                </div>
                <span className="text-[6.5px] font-bold text-slate-500 uppercase tracking-tighter mt-0.5">
                  {isPoswal ? 'MSME Registered' : 'Institutional Seal'}
                </span>
              </div>

              {/* Right Signatures */}
              <div className="flex items-end justify-end space-x-3 text-center">
                {formData.include_faculty && (
                  <div className="flex flex-col items-center">
                    <img 
                      src={isPoswal ? '/mahesh_sign.png' : '/nitin_sign.png'} 
                      alt="Mentor Signature" 
                      className="h-5 w-auto object-contain"
                    />
                    <div className="w-14 border-t border-slate-800 my-0.5" />
                    <span className="text-[7px] font-bold text-slate-900 truncate max-w-[60px]">{formData.mentor_name || 'Faculty'}</span>
                    <span className="text-[6px] text-slate-500">Mentor / Coordinator</span>
                  </div>
                )}

                <div className="flex flex-col items-center">
                  <img 
                    src={isPoswal ? '/madhuvan_sign.png' : '/nitin_sign.png'} 
                    alt="Authority Signature" 
                    className="h-5 w-auto object-contain"
                  />
                  <div className="w-16 border-t border-slate-800 my-0.5" />
                  <span className="text-[7.5px] font-bold text-slate-900">{formData.signatory_name}</span>
                  <span className="text-[6px] text-slate-500">{formData.signatory_designation}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Previously Issued Appreciation Certificates Archive */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div>
            <h2 className="text-base font-bold text-slate-900">
              Appreciation & Excellence Certificates Archive
            </h2>
            <p className="text-xs text-slate-500">
              List of generated custom certificates with instant vector PDF download.
            </p>
          </div>
          <button
            onClick={loadHistory}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-slate-300 bg-slate-50 hover:bg-slate-100 text-xs font-semibold text-slate-700 cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loadingList ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>

        {loadingList ? (
          <div className="text-center py-8 text-xs text-slate-400">Loading certificate records...</div>
        ) : certificatesList.length === 0 ? (
          <div className="text-center py-10 border-2 border-dashed border-slate-200 rounded-xl space-y-2">
            <Award className="w-8 h-8 text-slate-300 mx-auto" />
            <div className="text-xs font-bold text-slate-700">No appreciation certificates generated yet</div>
            <p className="text-[11px] text-slate-400">Use the studio form above to generate your first custom certificate.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-700">
              <thead className="bg-slate-50 text-[10px] font-bold uppercase tracking-wider text-slate-500 border-b border-slate-200">
                <tr>
                  <th className="py-2.5 px-3">Recipient</th>
                  <th className="py-2.5 px-3">Certificate Title</th>
                  <th className="py-2.5 px-3">Organization</th>
                  <th className="py-2.5 px-3">Certificate No</th>
                  <th className="py-2.5 px-3">Issue Date</th>
                  <th className="py-2.5 px-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {certificatesList.map((cert) => (
                  <tr key={cert.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3 px-3 font-bold text-slate-900">
                      {cert.recipient_name}
                    </td>
                    <td className="py-3 px-3">
                      <span className="font-semibold text-slate-800">{cert.title}</span>
                      {cert.event_name && <div className="text-[10px] text-slate-400">{cert.event_name}</div>}
                    </td>
                    <td className="py-3 px-3">
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-800">
                        {cert.institution_name || (cert.institution_id === 2 ? 'Poswal Developers' : (cert.institution_id === 3 ? 'Technoglobe Jaipur' : 'Poddar College'))}
                      </span>
                    </td>
                    <td className="py-3 px-3 font-mono text-slate-600 font-medium">
                      {cert.certificate_number}
                    </td>
                    <td className="py-3 px-3 text-slate-500">
                      {cert.issue_date}
                    </td>
                    <td className="py-3 px-3 text-right space-x-2">
                      <a
                        href={api.getAppreciationPdfUrl(cert.id!)}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center space-x-1 px-2.5 py-1 rounded bg-blue-600 hover:bg-blue-500 text-white font-bold text-[11px] transition-all cursor-pointer shadow-2xs"
                      >
                        <Download className="w-3 h-3" />
                        <span>PDF</span>
                      </a>
                      <button
                        onClick={() => handleDelete(cert.id!)}
                        className="p-1 rounded hover:bg-red-50 text-red-600 hover:text-red-700 transition-colors cursor-pointer"
                        title="Delete record"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default AppreciationCertificatePage;
