import React from "react";
import { Link } from "react-router-dom";

const items = [
  { label: "Home", to: "/" },
  { label: "Upload", to: "/upload" },
  { label: "Institute", to: "/institute" },
  { label: "Reviewer", to: "/reviewer" },
  { label: "Admin", to: "/admin" },
];

export default function Sidebar() {
  return (
    <aside className="w-56 bg-[#071018] min-h-screen border-r border-gray-800 p-4">
      <div className="text-white font-bold text-lg mb-6">EduTrack</div>
      <nav className="flex flex-col gap-2">
        {items.map((it) => (
          <Link key={it.to} to={it.to} className="px-3 py-2 rounded hover:bg-gray-800 text-gray-200 text-sm">
            {it.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
