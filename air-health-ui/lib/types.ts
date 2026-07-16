export type PaperSummary = {
  id: string;
  title: string;
  authors: string[];
  year: number;
  pollutant: string;
  population: string;
  outcome: string;
  location: string;
  direction: "Increased risk" | "No clear association" | "Mixed";
  status: "Completed" | "Processing";
};

export type Extraction = {
  paper_metadata: {
    title: string;
    authors: string[];
    journal?: string | null;
    publication_year?: number | null;
    doi?: string | null;
  };
  population_studied: { description: string; sample_size?: number | null };
  geographic_location: { description: string };
  pollutants_or_exposures: { name: string; category: string }[];
  exposure_assessment: {
    exposure_period: string;
    measurement_methods: string[];
  };
  health_outcomes: { name: string; category?: string | null }[];
  study_design: { description: string };
  statistical_methods: {
    primary_models: string[];
    covariates: string[];
  };
  quantitative_results: {
    primary_result?: {
      reported_text: string;
      value?: number | null;
      confidence_interval_lower?: number | null;
      confidence_interval_upper?: number | null;
    } | null;
  };
  relationship: { direction: string; description: string };
  key_conclusions: { conclusions: string[]; public_health_implications: string[] };
  limitations: {
    limitations: { description: string; category?: string | null }[];
  };
  data_sources: {
    exposure_sources: { name: string }[];
    health_sources: { name: string }[];
  };
};
