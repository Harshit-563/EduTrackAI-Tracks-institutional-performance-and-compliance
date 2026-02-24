import React from "react";
import Card from "./ui/Card";

export default function RightSidebar() {
  return (
    <div className="space-y-4">
      <Card className="w-72">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm text-gray-400">Company Wise Sheet</div>
            <div className="text-xs text-gray-500">Last Updated: Today</div>
          </div>
          <div className="text-2xl font-bold">18</div>
        </div>

        <div className="mt-4 space-y-2 max-h-36 overflow-y-auto">
          <div className="flex items-center gap-3">
            <div className="w-7 h-7 bg-white/10 rounded flex items-center justify-center">G</div>
            <div className="text-sm">Google</div>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-7 h-7 bg-white/10 rounded flex items-center justify-center">A</div>
            <div className="text-sm">Amazon</div>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-7 h-7 bg-white/10 rounded flex items-center justify-center">M</div>
            <div className="text-sm">Meta</div>
          </div>
        </div>
      </Card>

      <Card className="w-72">
        <div>Try the Codolio Extension</div>
      </Card>
    </div>
  );
}