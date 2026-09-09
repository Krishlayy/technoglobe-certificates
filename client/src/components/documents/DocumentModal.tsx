import React, { useState } from 'react';
import { X, Printer, Download, ExternalLink, Loader2 } from 'lucide-react';
import { api } from '../../services/api';

interface DocumentModalProps {
  isOpen: boolean;
  onClose: () => void;
  internshipId: number;
  docType: string;
  docTitle: string;
  studentName: string;
}

export const DocumentModal: React.FC<DocumentModalProps> = ({
  isOpen,
  onClose,
  internshipId,
  docType,
  docTitle,
  studentName,
}) => {
  const [loading, setLoading] = useState(true);

  if (!isOpen) return null;

  const pdfUrl = api.getDocumentPdfUrl(internshipId, docType);

  const handlePrint = () => {
    const printWindow = window.open(pdfUrl, '_blank');
    if (printWindow) {
      printWindow.onload = () => {
        printWindow.print();
      };
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-5xl h-[90vh] flex flex-col overflow-hidden border border-slate-200 animate-in fade-in zoom-in-95 duration-200">
        {/* Header Bar */}
        <div className="px-6 py-4 bg-brand-700 text-white flex items-center justify-between shrink-0 border-b border-brand-800">
          <div>
            <h3 className="text-base font-serif font-bold text-white tracking-wide">
              {docTitle}
            </h3>
            <p className="text-xs text-gold-300 font-medium">
              Candidate: {studentName} — Official Franchise Document
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={handlePrint}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-brand-800 hover:bg-brand-600 text-white text-xs font-semibold border border-brand-600 transition-colors shadow-xs"
            >
              <Printer className="w-3.5 h-3.5 text-gold-300" />
              <span>Print Official Copy</span>
            </button>

            <a
              href={pdfUrl}
              download={`${docType}_${studentName.replace(/\s+/g, '_')}.pdf`}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-gold-500 hover:bg-gold-600 text-brand-950 text-xs font-bold transition-colors shadow-xs"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download PDF</span>
            </a>

            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-brand-800 transition-colors ml-2"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content Viewer Body */}
        <div className="flex-1 bg-slate-100 relative overflow-hidden flex items-center justify-center">
          {loading && (
            <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-50/80 z-10 text-slate-500">
              <Loader2 className="w-8 h-8 animate-spin text-brand-600 mb-2" />
              <p className="text-xs font-medium">Rendering high-resolution vector PDF...</p>
            </div>
          )}

          <iframe
            src={`${pdfUrl}#toolbar=0`}
            title={docTitle}
            className="w-full h-full border-0"
            onLoad={() => setLoading(false)}
          />
        </div>

        {/* Footer Notice */}
        <div className="px-6 py-2.5 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-[11px] text-slate-500 shrink-0">
          <span>TechnoGlobe Bharatpur Centre — Industrial Training & Documentation System</span>
          <span className="italic text-slate-400">Designated signature & stamp zones provided for physical validation</span>
        </div>
      </div>
    </div>
  );
};
