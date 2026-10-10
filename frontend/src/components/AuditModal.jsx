import React, { useState, useEffect } from 'react';
import { X, Clock, Cpu, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { getAuditRecord } from '../lib/api';

export default function AuditModal({ traceId, onClose }) {
  const [audit, setAudit] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!traceId) return;
    setLoading(true);
    getAuditRecord(traceId)
      .then((data) => {
        setAudit(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [traceId]);

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full border border-slate-200 overflow-hidden transform transition-all">
        {/* Modal Header */}
        <div className="px-6 py-4 bg-navy-800 text-white flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold flex items-center">
              <FileText className="w-5 h-5 mr-2" />
              Audit Trace Record
            </h3>
            <p className="text-xs text-navy-200 font-mono mt-0.5">Trace ID: {traceId}</p>
          </div>
          <button
            onClick={onClose}
            className="text-navy-200 hover:text-white p-1 rounded-lg hover:bg-navy-700 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 max-h-[75vh] overflow-y-auto space-y-4">
          {loading && (
            <div className="py-12 text-center text-slate-500 text-sm">Loading audit record...</div>
          )}

          {error && (
            <div className="p-4 bg-rose-50 border border-rose-200 rounded-lg text-rose-700 text-sm flex items-center">
              <AlertCircle className="w-5 h-5 mr-2 flex-shrink-0" />
              {error}
            </div>
          )}

          {audit && (
            <div className="space-y-4 text-xs text-slate-700">
              {/* Metadata Stats */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 bg-slate-50 p-3 rounded-lg border border-slate-200">
                <div>
                  <span className="text-slate-400 block uppercase font-semibold">Category</span>
                  <span className="font-medium text-slate-900">{audit.question_category}</span>
                </div>
                <div>
                  <span className="text-slate-400 block uppercase font-semibold">Model Used</span>
                  <span className="font-medium text-slate-900">{audit.model}</span>
                </div>
                <div>
                  <span className="text-slate-400 block uppercase font-semibold">Latency</span>
                  <span className="font-medium text-slate-900">{audit.latency_ms} ms</span>
                </div>
                <div>
                  <span className="text-slate-400 block uppercase font-semibold">Tokens</span>
                  <span className="font-medium text-slate-900">{audit.tokens}</span>
                </div>
              </div>

              {/* Original Question */}
              <div>
                <span className="text-slate-500 font-bold block mb-1">Inquiry Text:</span>
                <p className="p-2.5 bg-slate-100 rounded-md text-slate-900 font-medium">{audit.question}</p>
              </div>

              {/* Precedence Decision */}
              {audit.precedence_decision && (
                <div>
                  <span className="text-slate-500 font-bold block mb-1">Annex A Precedence Decision:</span>
                  <p className="p-2 bg-amber-50 border border-amber-200 text-amber-900 rounded-md">
                    {audit.precedence_decision}
                  </p>
                </div>
              )}

              {/* Sources Retrieved */}
              <div>
                <span className="text-slate-500 font-bold block mb-1">Retrieved Sources ({audit.sources_retrieved.length}):</span>
                {audit.sources_retrieved.length === 0 ? (
                  <p className="text-slate-400 italic">No document chunks retrieved.</p>
                ) : (
                  <div className="space-y-1.5">
                    {audit.sources_retrieved.map((s, idx) => (
                      <div key={idx} className="flex justify-between items-center p-2 bg-slate-50 rounded border border-slate-200">
                        <span className="font-mono font-semibold text-navy-800">{s.doc_id}</span>
                        <span className="text-slate-500">Clause: {s.section || 'General'}</span>
                        <span className="text-slate-400">Score: {s.score ?? 'N/A'}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Tools Invoked */}
              <div>
                <span className="text-slate-500 font-bold block mb-1">Deterministic Tools Invoked ({audit.tools_invoked.length}):</span>
                {audit.tools_invoked.length === 0 ? (
                  <p className="text-slate-400 italic">No tools invoked for this query.</p>
                ) : (
                  <pre className="p-3 bg-slate-900 text-slate-100 rounded-lg text-xs overflow-x-auto">
                    {JSON.stringify(audit.tools_invoked, null, 2)}
                  </pre>
                )}
              </div>

              {/* Applied Rules */}
              <div>
                <span className="text-slate-500 font-bold block mb-1">Applied Rules ({audit.applied_rules.length}):</span>
                {audit.applied_rules.length === 0 ? (
                  <p className="text-slate-400 italic">No rules applied.</p>
                ) : (
                  <div className="flex flex-wrap gap-1.5">
                    {audit.applied_rules.map((r, idx) => (
                      <span key={idx} className="px-2 py-0.5 bg-navy-50 text-navy-800 font-mono text-xs rounded border border-navy-200">
                        {r}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 bg-slate-50 border-t border-slate-200 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-slate-200 hover:bg-slate-300 text-slate-800 rounded-lg text-xs font-semibold transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
