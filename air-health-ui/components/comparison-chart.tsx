"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

const data = [
  { pollutant: "PM2.5", studies: 28 },
  { pollutant: "Smoke", studies: 17 },
  { pollutant: "Ozone", studies: 14 },
  { pollutant: "NO₂", studies: 11 },
  { pollutant: "Heat", studies: 9 }
];

export function ComparisonChart() {
  return (
    <div className="glass rounded-[2rem] p-6">
      <div className="mb-6">
        <h3 className="font-semibold">Evidence coverage</h3>
        <p className="mt-1 text-xs text-slate-400">Processed studies by exposure category</p>
      </div>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid stroke="rgba(148,163,184,.08)" vertical={false} />
            <XAxis dataKey="pollutant" stroke="#738399" tickLine={false} axisLine={false} />
            <YAxis stroke="#738399" tickLine={false} axisLine={false} />
            <Tooltip
              cursor={{ fill: "rgba(255,255,255,.025)" }}
              contentStyle={{
                background: "#0b1928",
                border: "1px solid rgba(148,163,184,.16)",
                borderRadius: 16
              }}
            />
            <Bar dataKey="studies" fill="#67e8f9" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
