// src/components/Topbar.jsx
import React from "react";

export default function Topbar() {
  return (
    <header className="flex items-center justify-between px-6 py-3 border-b border-gray-800 bg-[#06121a]">
      <div className="flex items-center gap-4">
        <button className="p-2 rounded-lg hover:bg-gray-800 text-gray-300">
          {/* simple menu icon */}
          <svg width="18" height="18" viewBox="0 0 24 24" className="text-gray-300"><path fill="currentColor" d="M3 6h18v2H3zM3 11h18v2H3zM3 16h18v2H3z"/></svg>
        </button>

        <div className="relative">
          <input
            placeholder="Search institutions, documents, reviews..."
            className="pl-10 pr-4 py-2 rounded-lg bg-black/20 border border-gray-800 text-sm text-gray-200 focus:outline-none"
            style={{ width: 420 }}
          />
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
            {/* small inline search SVG */}
            <svg width="16" height="16" viewBox="0 0 24 24" className="text-gray-400">
              <path fill="currentColor" d="M21 20l-4.35-4.35a8 8 0 10-1.41 1.41L20 21l1-1zM10 16a6 6 0 110-12 6 6 0 010 12z"/>
            </svg>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button className="py-2 px-4 bg-black/20 rounded-full border border-gray-700 text-sm">Compliance Kit</button>

        <button className="p-2 rounded-full hover:bg-gray-800 text-gray-300" title="Toggle theme">
          {/* sun icon inline svg */}
          <svg width="18" height="18" viewBox="0 0 24 24" className="text-gray-300">
            <path fill="currentColor" d="M6.76 4.84l-1.8-1.79L3.17 4.84l1.79 1.8 1.8-1.8zM1 13h3v-2H1v2zm10 8h2v-3h-2v3zm7.03-1.03l1.79 1.8 1.79-1.79-1.8-1.8-1.78 1.79zM17.24 4.84l1.79-1.79L17.24 1.26l-1.79 1.79 1.79 1.79zM21 11v2h3v-2h-3zM4.22 19.78l1.79-1.79-1.79-1.79L2.43 18l1.79 1.78zM12 5a7 7 0 100 14 7 7 0 000-14z"/>
          </svg>
        </button>

        <div className="w-9 h-9 rounded-full overflow-hidden border border-gray-700">
          <img src="/avatar.png" alt="avatar" className="w-full h-full object-cover" />
        </div>
      </div>
    </header>
  );
}
