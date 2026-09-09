import React, { useState, useEffect } from 'react';
import { 
  LayoutTemplate, Check, Save, Sparkles, CheckCircle2, 
  ArrowUp, ArrowDown, Eye, EyeOff, ShieldCheck
} from 'lucide-react';
import { api } from '../services/api';
import { DocumentTemplate, TemplateBlock } from '../types';

export const TemplatesPage: React.FC = () => {
  const [templates, setTemplates] = useState<DocumentTemplate[]>([]);
  const [selectedKey, setSelectedKey] = useState<string>('completion_certificate');
  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    api.getTemplates().then((data) => {
      setTemplates(data);
      if (data.length > 0 && !selectedKey) {
        setSelectedKey(data[0].template_key);
      }
    });
  }, []);

  const currentTemplate = templates.find((t) => t.template_key === selectedKey);

  const handleToggleBlock = (blockId: string) => {
    if (!currentTemplate) return;
    const updatedBlocks = currentTemplate.blocks.map((b) =>
      b.id === blockId ? { ...b, enabled: !b.enabled } : b
    );
    setTemplates((prev) =>
      prev.map((t) => (t.template_key === selectedKey ? { ...t, blocks: updatedBlocks } : t))
    );
  };

  const handleMoveBlock = (index: number, direction: 'up' | 'down') => {
    if (!currentTemplate) return;
    const blocks = [...currentTemplate.blocks];
    const targetIndex = direction === 'up' ? index - 1 : index + 1;
    if (targetIndex < 0 || targetIndex >= blocks.length) return;
    const temp = blocks[index];
    blocks[index] = blocks[targetIndex];
    blocks[targetIndex] = temp;

    setTemplates((prev) =>
      prev.map((t) => (t.template_key === selectedKey ? { ...t, blocks } : t))
    );
  };

  const handleTitleChange = (newTitle: string) => {
    if (!currentTemplate) return;
    setTemplates((prev) =>
      prev.map((t) => (t.template_key === selectedKey ? { ...t, title: newTitle } : t))
    );
  };

  const handleSave = async () => {
    if (!currentTemplate) return;
    setSaving(true);
    setSavedSuccess(false);
    try {
      await api.updateTemplate(currentTemplate.template_key, currentTemplate.title, currentTemplate.blocks);
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (e: any) {
      alert(`Save failed: ${e.message}`);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-in fade-in duration-300">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-serif font-bold text-slate-900 tracking-tight">
            Document Templates & Visual Block Customizer
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Configure layout blocks, headers, signature areas, and verification elements across all official documents.
          </p>
        </div>

        {currentTemplate && (
          <button
            onClick={handleSave}
            disabled={saving}
            className="inline-flex items-center space-x-1.5 px-5 py-2.5 rounded-xl bg-brand-700 hover:bg-brand-800 text-white text-xs font-bold shadow-sm transition-all active:scale-95 disabled:opacity-50"
          >
            <Save className="w-4 h-4 text-gold-400" />
            <span>{saving ? 'Saving...' : 'Save Template Blocks'}</span>
          </button>
        )}
      </div>

      {savedSuccess && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold rounded-xl flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          <span>Template layout blocks updated and saved successfully.</span>
        </div>
      )}

      {/* Template Select Tabs */}
      <div className="flex overflow-x-auto pb-2 gap-2 border-b border-slate-200 scrollbar-thin">
        {templates.map((tpl) => (
          <button
            key={tpl.template_key}
            onClick={() => setSelectedKey(tpl.template_key)}
            className={`px-3.5 py-2 rounded-lg text-xs font-semibold whitespace-nowrap transition-all ${
              selectedKey === tpl.template_key
                ? 'bg-brand-700 text-white shadow-xs'
                : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
            }`}
          >
            {tpl.title}
          </button>
        ))}
      </div>

      {currentTemplate && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-xs p-6 space-y-6">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Document Title
            </label>
            <input
              type="text"
              value={currentTemplate.title}
              onChange={(e) => handleTitleChange(e.target.value)}
              className="w-full px-3.5 py-2 text-xs font-bold text-slate-900 border border-slate-300 rounded-lg bg-white focus:ring-2 focus:ring-blue-600"
            />
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                Configurable Document Layout Blocks
              </span>
              <span className="text-[11px] text-slate-400 font-mono">
                TOGGLE VISIBILITY / REORDER BLOCKS
              </span>
            </div>

            <div className="space-y-2">
              {currentTemplate.blocks.map((block, idx) => (
                <div
                  key={block.id}
                  className={`flex items-center justify-between p-3.5 rounded-xl border transition-all ${
                    block.enabled
                      ? 'bg-white border-slate-200 shadow-2xs'
                      : 'bg-slate-50/70 border-slate-200/60 opacity-60'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <span className="w-6 h-6 rounded-full bg-slate-100 text-slate-600 text-xs font-bold flex items-center justify-center font-mono">
                      {idx + 1}
                    </span>
                    <div>
                      <div className="text-xs font-bold text-slate-900">{block.label}</div>
                      <div className="text-[10px] text-slate-400 font-mono">block_id: {block.id}</div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleMoveBlock(idx, 'up')}
                      disabled={idx === 0}
                      className="p-1 rounded text-slate-400 hover:text-slate-700 disabled:opacity-30"
                      title="Move Up"
                    >
                      <ArrowUp className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => handleMoveBlock(idx, 'down')}
                      disabled={idx === currentTemplate.blocks.length - 1}
                      className="p-1 rounded text-slate-400 hover:text-slate-700 disabled:opacity-30"
                      title="Move Down"
                    >
                      <ArrowDown className="w-3.5 h-3.5" />
                    </button>

                    <button
                      onClick={() => handleToggleBlock(block.id)}
                      className={`inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold transition-colors ${
                        block.enabled
                          ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                          : 'bg-slate-100 text-slate-500 border border-slate-200'
                      }`}
                    >
                      {block.enabled ? (
                        <>
                          <Eye className="w-3 h-3 text-emerald-600" />
                          <span>Enabled</span>
                        </>
                      ) : (
                        <>
                          <EyeOff className="w-3 h-3 text-slate-400" />
                          <span>Disabled</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
