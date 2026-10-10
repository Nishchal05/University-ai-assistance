import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  User,
  Bot,
  Trash2,
  ChevronDown,
  ChevronUp,
  FileText,
  Calculator,
  AlertTriangle,
  Info,
  ShieldAlert,
  Sparkles,
  HelpCircle,
  ExternalLink
} from 'lucide-react';
import { askQuestion } from '../lib/api';
import AuditModal from '../components/AuditModal';

const SUGGESTIONS = [
  "What is the minimum attendance required to appear for end-semester exams?",
  "What is the attendance condonation criteria under Academic Regulations?",
  "What is the placement and internship eligibility criteria for students?",
  "What is the revised attendance norm for Batch 2024 onward?",
  "Who is eligible to appear in supplementary examinations?",
  "What is the One-Student One-Job policy in campus placements?"
];

export default function ChatPage() {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'assistant',
      text: "Hello! I am your AI-powered University Student Services Assistant. You can ask me questions about academic regulations, attendance criteria, placement policies, exam guidelines, and official university circulars.",
      answer_type: 'retrieved_fact',
      citations: [
        {
          doc_id: 'ACAD-REG-2024',
          title: 'Academic Regulations for B.Tech Programmes',
          section: 'Section 1',
          page: 1,
          version: '3.1',
          effective_from: '2024-07-01'
        }
      ]
    }
  ]);
  const [inputQuestion, setInputQuestion] = useState('');
  const [asOfDate, setAsOfDate] = useState('2026-10-10');
  const [isLoading, setIsLoading] = useState(false);
  const [activeAuditTraceId, setActiveAuditTraceId] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (questionText = inputQuestion) => {
    const q = questionText.trim();
    if (!q || isLoading) return;

    const userMsgId = String(Date.now());
    const userMsg = {
      id: userMsgId,
      sender: 'user',
      text: q
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputQuestion('');
    setIsLoading(true);

    try {
      const response = await askQuestion(q, asOfDate, null);
      const assistantMsg = {
        id: response.trace_id || String(Date.now() + 1),
        sender: 'assistant',
        text: response.answer,
        answer_type: response.answer_type,
        citations: response.citations || [],
        tools_invoked: response.tools_invoked || [],
        applied_rules: response.applied_rules || [],
        conflicts_detected: response.conflicts_detected || [],
        explanation: response.explanation,
        trace_id: response.trace_id,
        as_of_date: response.as_of_date
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: String(Date.now() + 1),
          sender: 'assistant',
          text: `Error: ${err.message}`,
          answer_type: 'refused',
          citations: []
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-6 flex flex-col h-[calc(100vh-4rem)]">
      {/* Top Controls Header */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 mb-4 shadow-sm flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 rounded-lg bg-navy-800 flex items-center justify-center text-white">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <div className="text-xs text-slate-500 font-medium">Assistant Mode</div>
            <div className="text-sm font-bold text-slate-900">
              Official University Knowledge Base & Policy Inquiry
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-3 text-xs">
          <div className="flex items-center space-x-1.5">
            <span className="text-slate-500 font-medium">As Of Date:</span>
            <input
              type="date"
              value={asOfDate}
              onChange={(e) => setAsOfDate(e.target.value)}
              className="border border-slate-300 rounded px-2 py-1 text-xs text-slate-800 focus:outline-none focus:ring-1 focus:ring-navy-800"
            />
          </div>
          <button
            onClick={clearChat}
            className="flex items-center px-2.5 py-1 text-slate-500 hover:text-rose-600 hover:bg-rose-50 rounded border border-slate-200 transition-colors"
            title="Clear Chat Thread"
          >
            <Trash2 className="w-3.5 h-3.5 mr-1" />
            Clear
          </button>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-1 pb-4">
        {messages.map((msg) => (
          <MessageBubble
            key={msg.id}
            message={msg}
            onOpenAudit={(traceId) => setActiveAuditTraceId(traceId)}
          />
        ))}

        {isLoading && (
          <div className="flex items-start space-x-3 text-slate-500">
            <div className="w-8 h-8 rounded-full bg-navy-800 text-white flex items-center justify-center font-bold text-xs">
              AI
            </div>
            <div className="bg-white border border-slate-200 rounded-xl px-4 py-3 shadow-sm flex items-center space-x-2">
              <div className="w-2 h-2 rounded-full bg-navy-600 animate-bounce" style={{ animationDelay: '0ms' }} />
              <div className="w-2 h-2 rounded-full bg-navy-600 animate-bounce" style={{ animationDelay: '150ms' }} />
              <div className="w-2 h-2 rounded-full bg-navy-600 animate-bounce" style={{ animationDelay: '300ms' }} />
              <span className="text-xs text-slate-500 ml-2 font-medium">Evaluating rules and deterministic tools...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Questions Chips */}
      {messages.length <= 2 && (
        <div className="mb-3">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 flex items-center">
            <Sparkles className="w-3.5 h-3.5 mr-1 text-amber-500" />
            Suggested Questions
          </div>
          <div className="flex flex-wrap gap-1.5">
            {SUGGESTIONS.map((item, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(item)}
                className="text-left text-xs bg-white hover:bg-navy-50 text-slate-700 hover:text-navy-900 border border-slate-200 hover:border-navy-300 rounded-lg px-3 py-1.5 transition-all shadow-2xs"
              >
                {item}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Question Input Box */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="bg-white rounded-xl border border-slate-300 shadow-sm p-2 flex items-center space-x-2 focus-within:border-navy-800 focus-within:ring-1 focus-within:ring-navy-800 transition-all"
      >
        <input
          type="text"
          value={inputQuestion}
          onChange={(e) => setInputQuestion(e.target.value)}
          placeholder="Ask general university policy or regulation questions..."
          className="flex-1 bg-transparent px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none"
        />
        <button
          type="submit"
          disabled={isLoading || !inputQuestion.trim()}
          className="bg-navy-800 hover:bg-navy-900 disabled:opacity-50 text-white rounded-lg px-4 py-2 text-sm font-semibold flex items-center transition-colors shadow-sm"
        >
          <span>Ask</span>
          <Send className="w-4 h-4 ml-1.5" />
        </button>
      </form>

      {/* Audit Modal */}
      {activeAuditTraceId && (
        <AuditModal
          traceId={activeAuditTraceId}
          onClose={() => setActiveAuditTraceId(null)}
        />
      )}
    </div>
  );
}

function MessageBubble({ message, onOpenAudit }) {
  const isUser = message.sender === 'user';
  const [showDetails, setShowDetails] = useState(false);

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="bg-navy-800 text-white rounded-2xl rounded-tr-xs px-4 py-3 max-w-lg shadow-sm">
          <p className="text-sm font-normal">{message.text}</p>
        </div>
      </div>
    );
  }

  // Assistant Response Card
  const { answer_type, text, citations, tools_invoked, applied_rules, conflicts_detected, explanation, trace_id } = message;

  // Answer type badge mapping
  const badgeColors = {
    calculated: 'bg-blue-100 text-blue-800 border-blue-200',
    retrieved_fact: 'bg-emerald-100 text-emerald-800 border-emerald-200',
    not_found: 'bg-amber-100 text-amber-800 border-amber-200',
    refused: 'bg-rose-100 text-rose-800 border-rose-200',
    conflict_flagged: 'bg-purple-100 text-purple-800 border-purple-200',
    clarification_needed: 'bg-slate-100 text-slate-800 border-slate-200'
  };

  return (
    <div className="flex items-start space-x-3 text-slate-800">
      <div className="w-8 h-8 rounded-full bg-navy-800 text-white flex items-center justify-center font-bold text-xs flex-shrink-0 shadow-sm">
        AI
      </div>
      <div className="flex-1 bg-white border border-slate-200 rounded-2xl rounded-tl-xs p-4 shadow-sm space-y-3">
        {/* Header: Answer Type Badge & Trace ID */}
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center space-x-2">
            <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold border uppercase tracking-wider ${badgeColors[answer_type] || 'bg-slate-100 text-slate-800'}`}>
              {answer_type ? answer_type.replace('_', ' ') : 'retrieved fact'}
            </span>
            {conflicts_detected && conflicts_detected.length > 0 && (
              <span className="flex items-center text-xs text-purple-700 bg-purple-50 px-2 py-0.5 rounded border border-purple-200 font-semibold">
                <AlertTriangle className="w-3.5 h-3.5 mr-1" />
                Conflict Flagged
              </span>
            )}
          </div>

          {trace_id && (
            <button
              onClick={() => onOpenAudit(trace_id)}
              className="text-[11px] font-mono text-slate-400 hover:text-navy-800 hover:bg-slate-100 px-2 py-0.5 rounded transition-colors flex items-center"
              title="Inspect Audit Log"
            >
              <span>Trace: {trace_id}</span>
              <ExternalLink className="w-3 h-3 ml-1" />
            </button>
          )}
        </div>

        {/* Answer Text */}
        <div className="text-sm text-slate-900 leading-relaxed font-normal whitespace-pre-wrap">
          {text}
        </div>

        {/* Conflict Warning Notice if detected */}
        {conflicts_detected && conflicts_detected.length > 0 && (
          <div className="p-3 bg-purple-50 border border-purple-200 rounded-lg text-xs text-purple-900 space-y-1">
            <div className="font-bold flex items-center">
              <AlertTriangle className="w-4 h-4 mr-1 text-purple-700" />
              Precedence Notice:
            </div>
            {conflicts_detected.map((c, idx) => (
              <p key={idx}>{c.description}</p>
            ))}
          </div>
        )}

        {/* Deterministic Tool Summary Card (if tool invoked) */}
        {tools_invoked && tools_invoked.length > 0 && (
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 space-y-2">
            <div className="text-xs font-bold text-slate-700 flex items-center">
              <Calculator className="w-3.5 h-3.5 mr-1.5 text-navy-700" />
              Deterministic Calculation Breakdown
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
              {tools_invoked.map((t, idx) => {
                const out = t.output || {};
                return (
                  <div key={idx} className="bg-white p-2 rounded border border-slate-200 space-y-1">
                    <div className="font-mono font-bold text-navy-800 text-[11px]">{t.tool}</div>
                    {out.attendance_pct !== undefined && (
                      <div className="text-slate-600">
                        Attendance: <span className="font-bold text-slate-900">{out.attendance_pct}%</span> ({out.classes_attended}/{out.classes_held} held)
                      </div>
                    )}
                    {out.result && (
                      <div className="text-slate-600">
                        Outcome: <span className="font-bold text-navy-900 bg-navy-50 px-1 py-0.5 rounded">{out.result}</span>
                      </div>
                    )}
                    {out.reason && (
                      <div className="text-slate-500 text-[11px] italic">{out.reason}</div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Citations Section */}
        {citations && citations.length > 0 && (
          <div className="border-t border-slate-100 pt-2.5">
            <div className="text-xs font-bold text-slate-600 mb-1.5 flex items-center">
              <FileText className="w-3.5 h-3.5 mr-1 text-slate-500" />
              Authorised Sources Cited:
            </div>
            <div className="flex flex-wrap gap-2">
              {citations.map((c, idx) => (
                <div key={idx} className="bg-slate-50 border border-slate-200 rounded-md px-2.5 py-1 text-xs text-slate-700 flex items-center space-x-1.5">
                  <span className="font-bold text-navy-800 font-mono">{c.doc_id}</span>
                  <span className="text-slate-400">|</span>
                  <span className="text-slate-600">{c.section || 'General'}</span>
                  {c.page && <span className="text-slate-400 font-mono text-[11px]">(p.{c.page})</span>}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Expandable Explanation & Rule Registry details */}
        {(explanation || (applied_rules && applied_rules.length > 0)) && (
          <div className="pt-1">
            <button
              onClick={() => setShowDetails(!showDetails)}
              className="text-xs font-semibold text-navy-700 hover:text-navy-900 flex items-center transition-colors"
            >
              <span>{showDetails ? 'Hide Policy Details' : 'View Policy Trace & Rules'}</span>
              {showDetails ? <ChevronUp className="w-3.5 h-3.5 ml-1" /> : <ChevronDown className="w-3.5 h-3.5 ml-1" />}
            </button>

            {showDetails && (
              <div className="mt-2.5 p-3 bg-slate-50 rounded-lg text-xs space-y-2 border border-slate-200">
                {explanation && (
                  <div>
                    <span className="font-bold text-slate-600 block mb-0.5">Explanation:</span>
                    <p className="text-slate-800">{explanation}</p>
                  </div>
                )}

                {applied_rules && applied_rules.length > 0 && (
                  <div>
                    <span className="font-bold text-slate-600 block mb-1">Rules Applied from Rule Registry:</span>
                    <div className="space-y-1">
                      {applied_rules.map((r, idx) => (
                        <div key={idx} className="flex items-center space-x-2 text-[11px] font-mono">
                          <span className="bg-white border border-slate-300 px-1.5 py-0.5 rounded font-bold text-navy-800">{r.rule_id}</span>
                          <span className="text-slate-600">Threshold: {r.value}</span>
                          <span className="text-slate-400">({r.source_doc_id})</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
