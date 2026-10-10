import React, { useState, useEffect } from 'react';
import { User, BookOpen, GraduationCap, Award, AlertCircle, CheckCircle2, Clock, BarChart3 } from 'lucide-react';
import { getStudentProfile } from '../lib/api';

export default function DashboardPage({ selectedStudentId, onSelectStudent }) {
  const [profileData, setProfileData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!selectedStudentId) {
      setProfileData(null);
      return;
    }

    setLoading(true);
    setError(null);
    getStudentProfile(selectedStudentId)
      .then((data) => {
        setProfileData(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [selectedStudentId]);

  if (!selectedStudentId) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <div className="w-16 h-16 bg-navy-100 rounded-full flex items-center justify-center mx-auto mb-4 text-navy-800">
          <User className="w-8 h-8" />
        </div>
        <h2 className="text-xl font-bold text-slate-900 mb-2">Student Login Required</h2>
        <p className="text-sm text-slate-600 max-w-md mx-auto mb-6">
          To view personalized academic standing, course attendance records, and examination results, please select a synthetic student from the demo identity selector in the top bar.
        </p>
        <div className="flex justify-center gap-2 flex-wrap">
          <button
            onClick={() => onSelectStudent('S1001')}
            className="px-3 py-1.5 bg-navy-800 text-white rounded-lg text-xs font-semibold hover:bg-navy-900 transition-colors"
          >
            Select S1001 (Aarav Sharma - 75% Attendance)
          </button>
          <button
            onClick={() => onSelectStudent('S1002')}
            className="px-3 py-1.5 bg-white border border-slate-300 text-slate-700 rounded-lg text-xs font-semibold hover:bg-slate-50 transition-colors"
          >
            Select S1002 (Diya Patel - 72.5% Attendance)
          </button>
          <button
            onClick={() => onSelectStudent('S1005')}
            className="px-3 py-1.5 bg-white border border-slate-300 text-slate-700 rounded-lg text-xs font-semibold hover:bg-slate-50 transition-colors"
          >
            Select S1005 (Kabir Mehta - Detained)
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-16 text-center text-slate-500 text-sm">
        Loading student academic profile...
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-8">
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-sm flex items-center">
          <AlertCircle className="w-5 h-5 mr-2 flex-shrink-0" />
          {error}
        </div>
      </div>
    );
  }

  if (!profileData) return null;

  const { student, attendance, results } = profileData;

  // Placement eligibility calculation (CGPA >= 6.5 and backlogs == 0)
  const isPlacementEligible = student.cgpa >= 6.5 && student.active_backlogs === 0;

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-6">
      {/* Student Identity Banner */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center space-x-4">
          <div className="w-14 h-14 rounded-xl bg-navy-800 text-white flex items-center justify-center font-bold text-xl shadow-md">
            {student.full_name.charAt(0)}
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-xl font-bold text-slate-900">{student.full_name}</h2>
              <span className="bg-navy-100 text-navy-800 text-xs px-2 py-0.5 rounded font-mono font-bold">
                {student.student_id}
              </span>
            </div>
            <p className="text-sm text-slate-500 mt-0.5">
              {student.programme} • Batch {student.batch_year} • Semester {student.current_semester}
            </p>
          </div>
        </div>

        {/* Academic Highlights */}
        <div className="flex items-center space-x-6 border-t md:border-t-0 md:border-l border-slate-200 pt-4 md:pt-0 md:pl-6">
          <div>
            <span className="text-xs text-slate-400 block font-semibold uppercase">CGPA</span>
            <span className="text-2xl font-black text-slate-900">{student.cgpa.toFixed(2)}</span>
          </div>
          <div>
            <span className="text-xs text-slate-400 block font-semibold uppercase">Active Backlogs</span>
            <span className={`text-2xl font-black ${student.active_backlogs > 0 ? 'text-rose-600' : 'text-emerald-600'}`}>
              {student.active_backlogs}
            </span>
          </div>
          <div>
            <span className="text-xs text-slate-400 block font-semibold uppercase">Placement Status</span>
            <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-bold mt-1 ${
              isPlacementEligible ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'
            }`}>
              {isPlacementEligible ? 'Eligible' : 'Ineligible'}
            </span>
          </div>
        </div>
      </div>

      {/* Course Attendance Section */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold text-slate-900 flex items-center">
            <BarChart3 className="w-5 h-5 mr-2 text-navy-800" />
            Course Attendance Record (Computed Dynamically)
          </h3>
          <span className="text-xs text-slate-500 font-medium">Threshold: 75% Min | 65% Condonable</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 text-slate-400 uppercase font-semibold">
                <th className="py-2.5 px-3">Course</th>
                <th className="py-2.5 px-3">Classes Held</th>
                <th className="py-2.5 px-3">Attended</th>
                <th className="py-2.5 px-3">Computed %</th>
                <th className="py-2.5 px-3">Attendance Progress</th>
                <th className="py-2.5 px-3">Exam Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {attendance.map((att) => {
                const pct = att.attendance_pct;
                let statusBadge = (
                  <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded font-bold">Eligible</span>
                );
                let progressColor = 'bg-emerald-500';

                if (pct < 65) {
                  statusBadge = <span className="px-2 py-0.5 bg-rose-100 text-rose-800 rounded font-bold">Detained</span>;
                  progressColor = 'bg-rose-500';
                } else if (pct < 75) {
                  statusBadge = <span className="px-2 py-0.5 bg-amber-100 text-amber-800 rounded font-bold">Condonation Required</span>;
                  progressColor = 'bg-amber-500';
                }

                return (
                  <tr key={att.course_code} className="hover:bg-slate-50 transition-colors">
                    <td className="py-3 px-3 font-medium text-slate-900">
                      <span className="font-mono font-bold text-navy-800">{att.course_code}</span>
                      {att.course_name && <span className="text-slate-500 ml-2">({att.course_name})</span>}
                    </td>
                    <td className="py-3 px-3 text-slate-600">{att.classes_held}</td>
                    <td className="py-3 px-3 text-slate-600">{att.classes_attended}</td>
                    <td className="py-3 px-3 font-bold text-slate-900 font-mono">{pct.toFixed(1)}%</td>
                    <td className="py-3 px-3 w-48">
                      <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden border border-slate-200">
                        <div
                          className={`h-full ${progressColor} transition-all`}
                          style={{ width: `${Math.min(100, pct)}%` }}
                        />
                      </div>
                    </td>
                    <td className="py-3 px-3">{statusBadge}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Examination Results History */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4">
        <h3 className="text-base font-bold text-slate-900 flex items-center">
          <Award className="w-5 h-5 mr-2 text-navy-800" />
          Examination Results History
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-200 text-slate-400 uppercase font-semibold">
                <th className="py-2.5 px-3">Course</th>
                <th className="py-2.5 px-3">Session</th>
                <th className="py-2.5 px-3">Type</th>
                <th className="py-2.5 px-3">Internal</th>
                <th className="py-2.5 px-3">External</th>
                <th className="py-2.5 px-3">Total / Max</th>
                <th className="py-2.5 px-3">Result</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {results.map((res, idx) => (
                <tr key={idx} className="hover:bg-slate-50 transition-colors">
                  <td className="py-3 px-3 font-medium text-slate-900">
                    <span className="font-mono font-bold text-navy-800">{res.course_code}</span>
                    {res.course_name && <span className="text-slate-500 ml-2">({res.course_name})</span>}
                  </td>
                  <td className="py-3 px-3 text-slate-600">{res.exam_session}</td>
                  <td className="py-3 px-3 text-slate-600 font-medium">{res.exam_type}</td>
                  <td className="py-3 px-3 text-slate-600">{res.internal_marks}</td>
                  <td className="py-3 px-3 text-slate-600">{res.external_marks}</td>
                  <td className="py-3 px-3 font-bold text-slate-900 font-mono">
                    {res.total_marks} / {res.max_marks}
                  </td>
                  <td className="py-3 px-3">
                    <span className={`px-2.5 py-0.5 rounded text-[11px] font-bold ${
                      res.result === 'PASS'
                        ? 'bg-emerald-100 text-emerald-800'
                        : res.result === 'FAIL'
                        ? 'bg-rose-100 text-rose-800'
                        : res.result === 'ABSENT'
                        ? 'bg-amber-100 text-amber-800'
                        : 'bg-purple-100 text-purple-800'
                    }`}>
                      {res.result}
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
