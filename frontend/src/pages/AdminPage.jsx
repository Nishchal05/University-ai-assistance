import React, { useState, useEffect } from 'react';
import { Upload, FileText, ShieldAlert, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react';
import { getSources, ingestDocument } from '../lib/api';

export default function AdminPage() {
  const [sources, setSources] = useState([]);
  const [loadingSources, setLoadingSources] = useState(true);

  // Ingestion form state
  const [selectedFile, setSelectedFile] = useState(null);
  const [metadata, setMetadata] = useState({
    doc_id: '',
    title: '',
    issuer: 'Office of the Dean (Academics)',
    authority_level: 2,
    doc_type: 'circular',
    version: '1.0',
    effective_from: '2026-10-10',
    effective_to: '',
    supersedes: '',
    scope_programmes: 'ALL',
    scope_batches: 'ALL',
    provenance: 'https://university.edu/admin/live_upload',
    retrieved_on: '2026-10-10',
    synthetic: 'N'
  });
  const [isIngesting, setIsIngesting] = useState(false);
  const [ingestStatus, setIngestStatus] = useState(null);

  const fetchSources = () => {
    setLoadingSources(true);
    getSources()
      .then((data) => {
        setSources(data);
        setLoadingSources(false);
      })
      .catch((err) => {
        console.error(err);
        setLoadingSources(false);
      });
  };

  useEffect(() => {
    fetchSources();
  }, []);

  const handleIngestSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile || !metadata.doc_id || !metadata.title) {
      alert('Please provide a file, Document ID, and Document Title.');
      return;
    }

    setIsIngesting(true);
    setIngestStatus(null);

    try {
      const res = await ingestDocument(selectedFile, metadata);
      setIngestStatus({
        success: true,
        message: `Success! ${res.doc_id} indexed with ${res.chunks_indexed} chunks. Document is immediately available in the vector DB without restarting.`
      });
      // Reset form
      setSelectedFile(null);
      setMetadata((prev) => ({ ...prev, doc_id: '', title: '' }));
      // Refresh Source Register
      fetchSources();
    } catch (err) {
      setIngestStatus({
        success: false,
        message: err.message
      });
    } finally {
      setIsIngesting(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8">
      {/* Notice Banner */}
      <div className="bg-slate-100 border border-slate-200 rounded-xl p-4 flex items-center space-x-3 text-slate-800 text-xs shadow-sm">
        <ShieldAlert className="w-5 h-5 flex-shrink-0 text-navy-800" />
        <div>
          <span className="font-bold block uppercase tracking-wider text-navy-900">Knowledge Base & Policy Administration</span>
          Manage university official documents, circulars, and academic ordinances. Ingest new documents directly into the ChromaDB vector database and inspect the live Source Register.
        </div>
      </div>

      {/* Document Ingestion Form */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
        <div className="flex items-center space-x-2">
          <Upload className="w-5 h-5 text-navy-800" />
          <h3 className="text-base font-bold text-slate-900">Live Document Ingestion (POST /ingest)</h3>
        </div>
        <p className="text-xs text-slate-500">
          Upload new policies or circulars. The system extracts text, chunks, computes embeddings, and updates the Vector DB & Source Register immediately.
        </p>

        {ingestStatus && (
          <div className={`p-3 rounded-lg text-xs flex items-center ${
            ingestStatus.success ? 'bg-emerald-50 border border-emerald-200 text-emerald-800' : 'bg-rose-50 border border-rose-200 text-rose-800'
          }`}>
            {ingestStatus.success ? <CheckCircle2 className="w-4 h-4 mr-2 flex-shrink-0" /> : <AlertCircle className="w-4 h-4 mr-2 flex-shrink-0" />}
            {ingestStatus.message}
          </div>
        )}

        <form onSubmit={handleIngestSubmit} className="space-y-4 text-xs">
          {/* File Upload */}
          <div>
            <label className="block font-semibold text-slate-700 mb-1">Document File (.pdf, .docx, .md, .txt)</label>
            <input
              type="file"
              accept=".pdf,.docx,.md,.txt"
              onChange={(e) => setSelectedFile(e.target.files[0] || null)}
              required
              className="w-full border border-slate-300 rounded-lg p-2 text-xs file:mr-3 file:py-1 file:px-2.5 file:rounded file:border-0 file:text-xs file:font-semibold file:bg-navy-50 file:text-navy-800 hover:file:bg-navy-100"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Document ID (e.g. CIRC-2026-99)</label>
              <input
                type="text"
                value={metadata.doc_id}
                onChange={(e) => setMetadata({ ...metadata, doc_id: e.target.value })}
                placeholder="ACAD-NOTIF-2026"
                required
                className="w-full border border-slate-300 rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-navy-800"
              />
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Authority Level (1 to 5)</label>
              <select
                value={metadata.authority_level}
                onChange={(e) => setMetadata({ ...metadata, authority_level: parseInt(e.target.value) })}
                className="w-full border border-slate-300 rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-navy-800"
              >
                <option value={1}>1 (Highest: Regulations, Ordinances)</option>
                <option value={2}>2 (Dean / Registrar Circulars)</option>
                <option value={3}>3 (Department Notices)</option>
                <option value={4}>4 (Handbooks & FAQs)</option>
                <option value={5}>5 (Informational Only / Untrusted)</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">Document Title</label>
            <input
              type="text"
              value={metadata.title}
              onChange={(e) => setMetadata({ ...metadata, title: e.target.value })}
              placeholder="Revised Examination Guidelines"
              required
              className="w-full border border-slate-300 rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-navy-800"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Effective From</label>
              <input
                type="date"
                value={metadata.effective_from}
                onChange={(e) => setMetadata({ ...metadata, effective_from: e.target.value })}
                required
                className="w-full border border-slate-300 rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-navy-800"
              />
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Supersedes (Optional Clause)</label>
              <input
                type="text"
                value={metadata.supersedes}
                onChange={(e) => setMetadata({ ...metadata, supersedes: e.target.value })}
                placeholder="ACAD-REG-2024#7.2"
                className="w-full border border-slate-300 rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-navy-800"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Programme Scope</label>
              <input
                type="text"
                value={metadata.scope_programmes}
                onChange={(e) => setMetadata({ ...metadata, scope_programmes: e.target.value })}
                placeholder="ALL or B.Tech CSE"
                className="w-full border border-slate-300 rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-navy-800"
              />
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Batch Scope</label>
              <input
                type="text"
                value={metadata.scope_batches}
                onChange={(e) => setMetadata({ ...metadata, scope_batches: e.target.value })}
                placeholder="ALL or 2024+"
                className="w-full border border-slate-300 rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-navy-800"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isIngesting}
            className="w-full mt-2 bg-navy-800 hover:bg-navy-900 disabled:opacity-50 text-white font-semibold py-2 px-4 rounded-lg shadow-sm transition-colors text-xs flex items-center justify-center cursor-pointer"
          >
            <Upload className="w-3.5 h-3.5 mr-1.5" />
            {isIngesting ? 'Ingesting & Indexing...' : 'Ingest Document Now'}
          </button>
        </form>
      </div>

      {/* Live Source Register Table */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <FileText className="w-5 h-5 text-navy-800" />
            <h3 className="text-base font-bold text-slate-900">Source Register (GET /sources)</h3>
          </div>
          <button
            onClick={fetchSources}
            className="flex items-center px-2.5 py-1 text-xs text-navy-800 hover:bg-navy-50 rounded border border-slate-200 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 mr-1 ${loadingSources ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 text-slate-400 uppercase font-semibold">
                <th className="py-2.5 px-3">Doc ID</th>
                <th className="py-2.5 px-3">Title</th>
                <th className="py-2.5 px-3">Authority</th>
                <th className="py-2.5 px-3">Type</th>
                <th className="py-2.5 px-3">Effective From</th>
                <th className="py-2.5 px-3">Supersedes</th>
                <th className="py-2.5 px-3">Chunks</th>
                <th className="py-2.5 px-3">Synthetic</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {sources.map((s) => (
                <tr key={s.doc_id} className="hover:bg-slate-50 transition-colors">
                  <td className="py-3 px-3 font-mono font-bold text-navy-800">{s.doc_id}</td>
                  <td className="py-3 px-3 font-medium text-slate-900">{s.title}</td>
                  <td className="py-3 px-3">
                    <span className="px-2 py-0.5 rounded bg-slate-100 font-bold text-slate-700">
                      Level {s.authority_level}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-slate-600">{s.doc_type}</td>
                  <td className="py-3 px-3 text-slate-600 font-mono">{s.effective_from}</td>
                  <td className="py-3 px-3 text-slate-500 font-mono text-[11px]">{s.supersedes || '-'}</td>
                  <td className="py-3 px-3 font-mono text-slate-700">{s.chunks_count}</td>
                  <td className="py-3 px-3">
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                      s.synthetic === 'Y' ? 'bg-amber-100 text-amber-800' : 'bg-slate-100 text-slate-600'
                    }`}>
                      {s.synthetic}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
