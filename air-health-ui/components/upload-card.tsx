"use client";

import { useRef, useState } from "react";
import { FileText, LoaderCircle, UploadCloud } from "lucide-react";
import { extractPaper, uploadPaper } from "@/lib/api";
import { Extraction } from "@/lib/types";

export function UploadCard({
  onComplete
}: {
  onComplete: (paperId: string, extraction: Extraction) => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [state, setState] = useState<"idle" | "uploading" | "extracting">("idle");
  const [error, setError] = useState("");

  async function run() {
    if (!file) return;
    setError("");

    try {
      setState("uploading");
      const uploaded = await uploadPaper(file);

      setState("extracting");
      const extraction = await extractPaper(uploaded.paper_id);

      onComplete(uploaded.paper_id, extraction);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setState("idle");
    }
  }

  return (
    <section className="glass relative overflow-hidden rounded-[2rem] p-6 md:p-8">
      <div className="pointer-events-none absolute -right-20 -top-20 h-64 w-64 rounded-full bg-cyan-300/10 blur-3xl" />
      <div className="relative grid gap-7 lg:grid-cols-[1.1fr_.9fr]">
        <div>
          <span className="inline-flex rounded-full border border-cyan-300/20 bg-cyan-300/10 px-3 py-1 text-xs font-medium text-cyan-200">
            AI paper ingestion
          </span>
          <h2 className="mt-5 max-w-2xl text-3xl font-semibold tracking-tight md:text-4xl">
            AI Literature Agent for Air Quality and Health
          </h2>
          <p className="mt-4 max-w-xl text-sm leading-6 text-slate-400 md:text-base">
            Upload an air quality or environmental health paper. The AI agent extracts structured scientific evidence, generates
            summaries, reconstructs study workflows, builds a knowledge graph, and enables cross-paper comparison for researchers
          </p>

          <div className="mt-7 flex flex-wrap gap-3">
            <button
              onClick={() => inputRef.current?.click()}
              className="rounded-2xl bg-cyan-300 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:-translate-y-0.5 hover:bg-cyan-200"
            >
              Choose PDF
            </button>
            <button
              onClick={run}
              disabled={!file || state !== "idle"}
              className="rounded-2xl border border-white/10 bg-white/5 px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-40"
            >
              {state === "idle" ? "Run extraction" : state === "uploading" ? "Uploading…" : "Extracting…"}
            </button>
          </div>
          <input
            ref={inputRef}
            hidden
            type="file"
            accept="application/pdf"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          />
          {error && <p className="mt-4 text-sm text-rose-300">{error}</p>}
        </div>

        <div
          onClick={() => inputRef.current?.click()}
          className="grid min-h-60 cursor-pointer place-items-center rounded-[1.75rem] border border-dashed border-cyan-200/25 bg-slate-950/25 p-5 text-center transition hover:border-cyan-200/50 hover:bg-cyan-300/5"
        >
          {state !== "idle" ? (
            <div>
              <LoaderCircle className="mx-auto animate-spin text-cyan-200" size={36} />
              <p className="mt-4 text-sm font-medium">
                {state === "uploading" ? "Uploading paper" : "Building structured extraction"}
              </p>
              <p className="mt-2 text-xs text-slate-400">This may take a moment.</p>
            </div>
          ) : file ? (
            <div>
              <FileText className="mx-auto text-emerald-300" size={38} />
              <p className="mt-4 font-medium">{file.name}</p>
              <p className="mt-2 text-xs text-slate-400">
                {(file.size / 1024 / 1024).toFixed(2)} MB · Ready to process
              </p>
            </div>
          ) : (
            <div>
              <UploadCloud className="mx-auto text-cyan-200" size={42} />
              <p className="mt-4 font-medium">Drop or choose a PDF</p>
              <p className="mt-2 text-xs text-slate-400">Machine-readable academic PDFs work best.</p>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
