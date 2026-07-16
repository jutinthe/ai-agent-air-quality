import { Extraction, PaperSummary } from "./types";

export const papers: PaperSummary[] = [
  {
    id: "demo-1",
    title: "Long-Term PM2.5 Exposure and Cardiovascular Mortality",
    authors: ["Elena Martinez", "Robert Chen", "Maya Patel"],
    year: 2025,
    pollutant: "PM2.5",
    population: "Older adults",
    outcome: "Cardiovascular mortality",
    location: "United States",
    direction: "Increased risk",
    status: "Completed"
  },
  {
    id: "demo-2",
    title: "Wildfire Smoke and Pediatric Asthma Emergency Visits",
    authors: ["Noah Williams", "Ava Thompson"],
    year: 2024,
    pollutant: "Wildfire smoke",
    population: "Children",
    outcome: "Asthma ED visits",
    location: "Western United States",
    direction: "Increased risk",
    status: "Completed"
  },
  {
    id: "demo-3",
    title: "Ozone Exposure and Respiratory Symptoms in Urban Adults",
    authors: ["Sophia Kim", "Daniel Brooks"],
    year: 2023,
    pollutant: "Ozone",
    population: "Urban adults",
    outcome: "Respiratory symptoms",
    location: "South Korea",
    direction: "Mixed",
    status: "Completed"
  }
];

export const demoExtraction: Extraction = {
  paper_metadata: {
    title: "Long-Term PM2.5 Exposure and Cardiovascular Mortality",
    authors: ["Elena Martinez", "Robert Chen", "Maya Patel"],
    journal: "Environmental Health Intelligence",
    publication_year: 2025,
    doi: "10.1000/demo.2025.001"
  },
  population_studied: {
    description: "Adults aged 65 years and older enrolled in a national health insurance cohort.",
    sample_size: 1254000
  },
  geographic_location: {
    description: "Contiguous United States, county-level national cohort."
  },
  pollutants_or_exposures: [
    { name: "Fine particulate matter", category: "pm2.5" }
  ],
  exposure_assessment: {
    exposure_period: "Annual mean exposure during 2010–2021",
    measurement_methods: [
      "EPA ground monitoring",
      "Satellite aerosol optical depth",
      "Ensemble exposure model"
    ]
  },
  health_outcomes: [
    { name: "Cardiovascular mortality", category: "Mortality" }
  ],
  study_design: {
    description: "Retrospective longitudinal cohort study"
  },
  statistical_methods: {
    primary_models: ["Cox proportional hazards model"],
    covariates: ["Age", "Sex", "Income", "Smoking prevalence", "Temperature"]
  },
  quantitative_results: {
    primary_result: {
      reported_text: "A 10 µg/m³ increase in annual PM2.5 was associated with an 8% higher cardiovascular mortality risk.",
      value: 1.08,
      confidence_interval_lower: 1.05,
      confidence_interval_upper: 1.11
    }
  },
  relationship: {
    direction: "increased_risk",
    description: "Higher long-term PM2.5 exposure was associated with increased cardiovascular mortality."
  },
  key_conclusions: {
    conclusions: [
      "Long-term PM2.5 exposure was associated with elevated cardiovascular mortality.",
      "Associations persisted below current regulatory thresholds."
    ],
    public_health_implications: [
      "Further reductions in population PM2.5 exposure may prevent cardiovascular deaths."
    ]
  },
  limitations: {
    limitations: [
      { description: "Residential exposure assignment may cause exposure misclassification.", category: "Exposure measurement" },
      { description: "Residual confounding may remain despite extensive adjustment.", category: "Confounding" },
      { description: "Results may not generalize to adults younger than 65.", category: "Generalizability" }
    ]
  },
  data_sources: {
    exposure_sources: [
      { name: "EPA Air Quality System" },
      { name: "Satellite aerosol optical depth products" }
    ],
    health_sources: [
      { name: "National mortality registry" }
    ]
  }
};
