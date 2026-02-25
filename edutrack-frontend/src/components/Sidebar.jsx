import React from "react";
import { NavLink } from "react-router-dom";

const items = [
  { label: "Home", to: "/" },
  { label: "Upload", to: "/upload" },
  { label: "Institute", to: "/institute" },
  { label: "Rank List", to: "/rank-list" },
  { label: "Reviewer", to: "/reviewer" },
  { label: "Admin", to: "/admin" },
];

export default function Sidebar() {
  return (
    <aside className="hidden md:flex md:w-64 lg:w-72 border-r border-slate-800/80 bg-slate-950/55 backdrop-blur-xl">
      <div className="w-full p-4 lg:p-5">
        <div className="panel p-4 mb-5">
          <div className="text-xs uppercase tracking-[0.16em] text-emerald-300/85">EduTrack</div>
          <div className="text-lg font-semibold mt-1">Compliance Console</div>
          <p className="text-xs text-slate-400 mt-1">AI-assisted institutional approvals</p>
        </div>

        <nav className="space-y-2">
          {items.map((it) => (
            <NavLink
              key={it.to}
              to={it.to}
              className={({ isActive }) =>
                `block rounded-lg px-3 py-2.5 text-sm border ${
                  isActive
                    ? "border-emerald-400/50 bg-emerald-500/15 text-emerald-100"
                    : "border-transparent text-slate-300 hover:text-white hover:bg-slate-800/50"
                }`
              }
            >
              {it.label}
            </NavLink>
          ))}
        </nav>

        <div className="mt-6 panel-soft p-3 text-xs text-slate-400">
          <div className="font-medium text-slate-200 mb-1">System Status</div>
          Models: Active
          <br />
          Queue: Normal
        </div>
      </div>
    </aside>
  );
}


