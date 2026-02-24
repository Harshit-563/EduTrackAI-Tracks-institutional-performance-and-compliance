import React from "react";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";

export default function Layout({ children }) {
  return (
    <div className="flex bg-[#071018] min-h-screen text-gray-200">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Topbar />
        <div className="flex gap-6 p-6">
          <div className="flex-1">{children}</div>
          {/* right sidebar placed at page level for consistent spacing */}
        </div>
      </div>
    </div>
  );
}