"use client";

import { useState } from "react";
import {
  BookOpenCheck,
  CircleCheckBig,
  DatabaseZap,
  FileStack
} from "lucide-react";
import { Sidebar } from "@/components/sidebar";
import { UploadCard } from "@/components/upload-card";
import { StatCard } from "@/components/stat-card";
import { PaperTable } from "@/components/paper-table";
import { ComparisonChart } from "@/components/comparison-chart";
import { PaperDetail } from "@/components/paper-detail";
import { demoExtraction, papers } from "@/lib/mock-data";
import { Extraction } from "@/lib/types";

type SelectedPaper = {
  paperId: string;
  extraction: Extraction;
};

export default function Home() {
  const [active, setActive] = useState("Overview");
  const [selected, setSelected] = useState<SelectedPaper | null>(null);

  if (selected) {
    return (
      <main className="soft-grid min-h-screen p-4 md:p-8">
        <div className="mx-auto max-w-7xl">
          <PaperDetail
            paperId={selected.paperId}
            extraction={selected.extraction}
            onBack={() => setSelected(null)}
          />
        </div>
      </main>
    );
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar active={active} onChange={setActive} />

      <main className="soft-grid min-w-0 flex-1 p-4 md:p-8">
        <div className="mx-auto max-w-7xl space-y-7">
          <header className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.25em] text-cyan-200">
                Research workspace
              </p>
              <h1 className="mt-2 text-2xl font-semibold md:text-3xl">
                {active}
              </h1>
            </div>
            <div className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/[.025] px-4 py-3">
              <div className="h-2 w-2 rounded-full bg-emerald-300 shadow-[0_0_14px_rgba(110,231,183,.8)]" />
              <span className="text-xs text-slate-300">
                Backend connected
              </span>
            </div>
          </header>

          <UploadCard
            onComplete={(paperId, extraction) =>
              setSelected({ paperId, extraction })
            }
          />

          <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <StatCard
              label="Papers Processed"
              value="0"
              note="+12 this month"
              icon={FileStack}
            />
            <StatCard
              label="Structured Extractions"
              value="0"
              note="Scientific records generated"
              icon={DatabaseZap}
            />
            <StatCard
              label="Knowledge Graphs"
              value="0"
              note="Graphs created"
              icon={CircleCheckBig}
            />
            <StatCard
              label="Coverage"
              value="0"
              note="Major exposure categories"
              icon={BookOpenCheck}
            />
          </section>

          <section className="grid gap-6 xl:grid-cols-[1.15fr_.85fr]">
            <PaperTable
              papers={papers}
              onOpen={(paperId) =>
                setSelected({ paperId, extraction: demoExtraction })
              }
            />
            <ComparisonChart />
          </section>
        </div>
      </main>
    </div>
  );
}
