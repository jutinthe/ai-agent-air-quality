import { ArrowUpRight } from "lucide-react";
import { PaperSummary } from "@/lib/types";

export function PaperTable({
  papers,
  onOpen
}: {
  papers: PaperSummary[];
  onOpen: (id: string) => void;
}) {
  return (
    <div className="glass overflow-hidden rounded-[2rem]">
      <div className="flex items-center justify-between border-b border-white/10 px-6 py-5">
        <div>
          <h3 className="font-semibold">Recent evidence packages</h3>
          <p className="mt-1 text-xs text-slate-400">Structured and ready for comparison</p>
        </div>
        <button className="text-sm text-cyan-200 hover:text-cyan-100">View library</button>
      </div>

      <div className="scrollbar overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="text-xs uppercase tracking-wider text-slate-500">
            <tr>
              <th className="px-6 py-4">Paper</th>
              <th className="px-4 py-4">Pollutant</th>
              <th className="px-4 py-4">Population</th>
              <th className="px-4 py-4">Finding</th>
              <th className="px-4 py-4" />
            </tr>
          </thead>
          <tbody>
            {papers.map((paper) => (
              <tr key={paper.id} className="border-t border-white/5 hover:bg-white/[.025]">
                <td className="max-w-md px-6 py-5">
                  <div className="font-medium">{paper.title}</div>
                  <div className="mt-1 text-xs text-slate-500">
                    {paper.authors[0]} et al. · {paper.year}
                  </div>
                </td>
                <td className="px-4 py-5">
                  <span className="rounded-full bg-cyan-300/10 px-3 py-1 text-xs text-cyan-200">
                    {paper.pollutant}
                  </span>
                </td>
                <td className="px-4 py-5 text-slate-300">{paper.population}</td>
                <td className="px-4 py-5">
                  <span className={`rounded-full px-3 py-1 text-xs ${
                    paper.direction === "Increased risk"
                      ? "bg-rose-300/10 text-rose-200"
                      : "bg-amber-300/10 text-amber-200"
                  }`}>
                    {paper.direction}
                  </span>
                </td>
                <td className="px-4 py-5">
                  <button
                    onClick={() => onOpen(paper.id)}
                    className="rounded-xl p-2 text-slate-400 hover:bg-white/5 hover:text-white"
                  >
                    <ArrowUpRight size={17} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
