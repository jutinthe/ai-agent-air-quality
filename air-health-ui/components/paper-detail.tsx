"use client";

import {
  ArrowLeft,
  Database,
  FileText,
  MapPin,
  Microscope,
  Network,
  Users
} from "lucide-react";
import { useState } from "react";
import { Extraction } from "@/lib/types";
import { KnowledgeGraph } from "@/components/knowledge-graph";

function Section({
  title,
  children
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="glass rounded-3xl p-6">
      <h3 className="text-sm font-semibold uppercase tracking-[0.16em] text-cyan-200">
        {title}
      </h3>
      <div className="mt-4 text-sm leading-7 text-slate-300">{children}</div>
    </section>
  );
}

export function PaperDetail({
  paperId,
  extraction,
  onBack
}: {
  paperId: string;
  extraction: Extraction;
  onBack: () => void;
}) {
  const [tab, setTab] = useState<"summary" | "graph">("summary");
  const result = extraction.quantitative_results.primary_result;

  return (
    <div className="space-y-6">
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-sm text-slate-400 hover:text-white"
      >
        <ArrowLeft size={17} />
        Back to dashboard
      </button>

      <section className="glass rounded-[2rem] p-7 md:p-9">
        <div className="flex flex-wrap items-center gap-2 text-xs text-cyan-200">
          <span className="rounded-full bg-cyan-300/10 px-3 py-1">
            {extraction.pollutants_or_exposures[0]?.name ?? "Exposure"}
          </span>
          <span className="rounded-full bg-emerald-300/10 px-3 py-1 text-emerald-200">
            Structured extraction complete
          </span>
        </div>

        <h1 className="mt-5 max-w-4xl text-3xl font-semibold tracking-tight md:text-5xl">
          {extraction.paper_metadata.title}
        </h1>

        <p className="mt-4 text-sm text-slate-400">
          {extraction.paper_metadata.authors.join(", ")}
          {extraction.paper_metadata.journal
            ? ` · ${extraction.paper_metadata.journal}`
            : ""}
          {extraction.paper_metadata.publication_year
            ? ` · ${extraction.paper_metadata.publication_year}`
            : ""}
        </p>

        <div className="mt-8 grid gap-4 md:grid-cols-4">
          {[
            [Users, "Population", extraction.population_studied.description],
            [MapPin, "Location", extraction.geographic_location.description],
            [Microscope, "Study design", extraction.study_design.description],
            [
              Database,
              "Outcome",
              extraction.health_outcomes[0]?.name ?? "Not reported"
            ]
          ].map(([Icon, label, value]) => {
            const IconComponent = Icon as typeof Users;
            return (
              <div
                key={String(label)}
                className="rounded-2xl border border-white/10 bg-white/[.025] p-4"
              >
                <IconComponent size={18} className="text-cyan-200" />
                <div className="mt-3 text-xs uppercase tracking-wider text-slate-500">
                  {String(label)}
                </div>
                <div className="mt-2 text-sm leading-5">{String(value)}</div>
              </div>
            );
          })}
        </div>
      </section>

      <div className="glass inline-flex rounded-2xl p-1.5">
        <button
          onClick={() => setTab("summary")}
          className={`flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm transition ${
            tab === "summary"
              ? "bg-cyan-300 text-slate-950"
              : "text-slate-400 hover:text-white"
          }`}
        >
          <FileText size={16} />
          Research package
        </button>
        <button
          onClick={() => setTab("graph")}
          className={`flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm transition ${
            tab === "graph"
              ? "bg-cyan-300 text-slate-950"
              : "text-slate-400 hover:text-white"
          }`}
        >
          <Network size={16} />
          Knowledge graph
        </button>
      </div>

      {tab === "graph" ? (
        <KnowledgeGraph paperId={paperId} />
      ) : (
        <div className="grid gap-6 xl:grid-cols-[1.15fr_.85fr]">
          <div className="space-y-6">
            <Section title="Plain-language summary">
              {extraction.key_conclusions.conclusions.join(" ")}
            </Section>

            <Section title="Main quantitative finding">
              <div className="rounded-2xl bg-cyan-300/5 p-5 text-base text-white">
                {result?.reported_text ??
                  "No primary quantitative result was reported."}
              </div>
              {result?.value != null && (
                <div className="mt-4 grid grid-cols-3 gap-3">
                  <Metric label="Effect estimate" value={String(result.value)} />
                  <Metric
                    label="Lower CI"
                    value={String(result.confidence_interval_lower ?? "—")}
                  />
                  <Metric
                    label="Upper CI"
                    value={String(result.confidence_interval_upper ?? "—")}
                  />
                </div>
              )}
            </Section>

            <Section title="Methods reconstruction">
              <ol className="list-decimal space-y-2 pl-5">
                <li>
                  Assemble the study population and apply eligibility criteria.
                </li>
                <li>
                  Link exposure estimates using{" "}
                  {extraction.exposure_assessment.measurement_methods.join(", ")}.
                </li>
                <li>
                  Define the primary outcome:{" "}
                  {extraction.health_outcomes[0]?.name}.
                </li>
                <li>
                  Fit{" "}
                  {extraction.statistical_methods.primary_models.join(", ")}.
                </li>
                <li>
                  Adjust for{" "}
                  {extraction.statistical_methods.covariates.join(", ")}.
                </li>
              </ol>
            </Section>
          </div>

          <div className="space-y-6">
            <Section title="Bias and limitations">
              <div className="space-y-3">
                {extraction.limitations.limitations.map((item) => (
                  <div
                    key={item.description}
                    className="rounded-2xl border border-rose-300/10 bg-rose-300/5 p-4"
                  >
                    <div className="text-xs font-medium text-rose-200">
                      {item.category ?? "Limitation"}
                    </div>
                    <div className="mt-2 leading-6">{item.description}</div>
                  </div>
                ))}
              </div>
            </Section>

            <Section title="Data sources">
              <div className="space-y-4">
                <SourceGroup
                  label="Exposure"
                  values={extraction.data_sources.exposure_sources.map(
                    (item) => item.name
                  )}
                />
                <SourceGroup
                  label="Health"
                  values={extraction.data_sources.health_sources.map(
                    (item) => item.name
                  )}
                />
              </div>
            </Section>

            <Section title="Relationship direction">
              <div className="rounded-2xl bg-rose-300/8 p-4">
                <div className="font-medium text-rose-200">
                  {extraction.relationship.direction.replaceAll("_", " ")}
                </div>
                <p className="mt-2 leading-6">
                  {extraction.relationship.description}
                </p>
              </div>
            </Section>
          </div>
        </div>
      )}
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[.025] p-4 text-center">
      <div className="text-xs text-slate-500">{label}</div>
      <div className="mt-2 text-xl font-semibold">{value}</div>
    </div>
  );
}

function SourceGroup({
  label,
  values
}: {
  label: string;
  values: string[];
}) {
  return (
    <div>
      <div className="text-xs uppercase tracking-wider text-slate-500">
        {label}
      </div>
      <div className="mt-2 flex flex-wrap gap-2">
        {values.map((value) => (
          <span
            key={value}
            className="rounded-full bg-white/5 px-3 py-1 text-xs text-slate-300"
          >
            {value}
          </span>
        ))}
      </div>
    </div>
  );
}
