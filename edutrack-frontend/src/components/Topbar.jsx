import React from "react";

function formatToday() {
  return new Date().toLocaleDateString(undefined, {
    weekday: "short",
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export default function Topbar() {
  return (
    <header className="sticky top-0 z-20 border-b border-slate-800/80 bg-[#0f1612]/75 backdrop-blur-xl">
      <div className="mx-auto w-full max-w-[1400px] px-4 md:px-6 lg:px-7 py-3 flex items-center gap-3">
        <div className="hidden md:block panel-soft px-3 py-1.5 text-xs text-slate-300">{formatToday()}</div>

        <div className="relative flex-1 max-w-xl">
          <input
            placeholder="Search institution, document id, or reviewer"
            className="w-full pl-10 pr-4 py-2.5 rounded-lg bg-[#18231c]/80 border border-emerald-900/60 text-sm text-slate-200 placeholder:text-slate-400"
          />
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
            <svg width="16" height="16" viewBox="0 0 24 24" className="text-slate-400">
              <path fill="currentColor" d="M21 20l-4.35-4.35a8 8 0 10-1.41 1.41L20 21l1-1zM10 16a6 6 0 110-12 6 6 0 010 12z" />
            </svg>
          </div>
        </div>

        <button className="btn-subtle px-3 py-2 rounded-lg text-sm text-slate-200">Export Reports</button>
        <button className="btn-primary px-3.5 py-2 rounded-lg text-sm font-semibold">New Review</button>

        <div className="w-9 h-9 rounded-full overflow-hidden border border-slate-700">
          <img src="/avatar.png" alt="avatar" className="w-full h-full object-cover" />
        </div>
      </div>
    </header>
  );
}

