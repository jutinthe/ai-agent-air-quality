import { LucideIcon } from "lucide-react";

export function StatCard({
  label,
  value,
  note,
  icon: Icon
}: {
  label: string;
  value: string;
  note: string;
  icon: LucideIcon;
}) {
  return (
    <div className="glass rounded-3xl p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">{label}</p>
          <p className="mt-3 text-3xl font-semibold">{value}</p>
        </div>
        <div className="rounded-2xl bg-white/5 p-3 text-cyan-200">
          <Icon size={19} />
        </div>
      </div>
      <p className="mt-4 text-xs text-slate-400">{note}</p>
    </div>
  );
}
