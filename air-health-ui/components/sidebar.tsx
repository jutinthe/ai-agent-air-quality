"use client";

import {
  BookOpenText,
  ChartNoAxesCombined,
  FileSearch,
  Gauge,
  Settings,
  Sparkles
} from "lucide-react";

const items = [
  { label: "Overview", icon: Gauge },
  { label: "Paper library", icon: BookOpenText },
  { label: "Compare studies", icon: ChartNoAxesCombined },
  { label: "Evidence search", icon: FileSearch }
];

export function Sidebar({
  active,
  onChange
}: {
  active: string;
  onChange: (value: string) => void;
}) {
  return (
    <aside className="glass hidden min-h-screen w-72 shrink-0 flex-col border-y-0 border-l-0 px-5 py-6 lg:flex">
      <div className="mb-10 flex items-center gap-3 px-2">
        <div className="grid h-11 w-11 place-items-center rounded-2xl bg-cyan-300 text-slate-950 shadow-lg shadow-cyan-400/20">
          <Sparkles size={21} />
        </div>
        <div>
          <div className="text-lg font-semibold">

          AI Literature Agent

        </div>
          <div className="text-xs text-slate-400">

          Air Quality and Health

        </div>
        </div>
      </div>

      <nav className="space-y-2">
        {items.map(({ label, icon: Icon }) => (
          <button
            key={label}
            onClick={() => onChange(label)}
            className={`flex w-full items-center gap-3 rounded-2xl px-4 py-3 text-left text-sm transition ${
              active === label
                ? "bg-cyan-300 text-slate-950 shadow-lg shadow-cyan-400/10"
                : "text-slate-300 hover:bg-white/5 hover:text-white"
            }`}
          >
            <Icon size={18} />
            {label}
          </button>
        ))}
      </nav>

      <div className="mt-auto rounded-3xl border border-emerald-300/15 bg-emerald-300/5 p-4">
        <div className="mb-2 flex items-center gap-2 text-sm font-medium text-emerald-200">
          <Sparkles size={16} />
          Extraction agent
        </div>
        <p className="text-xs leading-5 text-slate-400">
          Structured environmental-health extraction with evidence provenance.
        </p>
      </div>

      <button className="mt-3 flex items-center gap-3 rounded-2xl px-4 py-3 text-sm text-slate-400 hover:bg-white/5 hover:text-white">
        <Settings size={18} />
        Settings
      </button>
    </aside>
  );
}
