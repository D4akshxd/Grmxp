import { ChangeEvent } from "react";

import { RuleConfig, RuleSectionConfig } from "../api/types";

interface Props {
  value: RuleConfig;
  onChange: (next: RuleConfig) => void;
}

const titleMap: Record<keyof RuleConfig, string> = {
  technical_specifications: "Technical Specifications",
  certificates: "Certificates & Compliance",
  atc_documents: "ATC Documents",
  boq: "Bill of Quantity",
  eligibility: "Eligibility Criteria",
  important_dates: "Important Dates"
};

const descriptionMap: Partial<Record<keyof RuleConfig, string>> = {
  technical_specifications: "Pick specifications, make/model requirements, performance thresholds.",
  certificates: "Track mandatory registrations like ISO, OEM letters, or local certificates.",
  atc_documents: "Capture any additional terms, amendments and clarification notices.",
  boq: "Highlight pricing tables, quantity splits and commercial notes.",
  eligibility: "Surface turnover, project experience and credential prerequisites.",
  important_dates: "Summarise bid submission, pre-bid, and opening milestones."
};

const updateSection = (
  config: RuleConfig,
  key: keyof RuleConfig,
  next: Partial<RuleSectionConfig>
): RuleConfig => ({
  ...config,
  [key]: {
    ...config[key],
    ...next
  }
});

export const RuleConfigForm: React.FC<Props> = ({ value, onChange }) => {
  const handleToggle = (key: keyof RuleConfig) => (event: ChangeEvent<HTMLInputElement>) => {
    onChange(updateSection(value, key, { enabled: event.target.checked }));
  };

  const handleKeywords = (key: keyof RuleConfig) => (event: ChangeEvent<HTMLInputElement>) => {
    const keywords = event.target.value
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);
    onChange(updateSection(value, key, { keywords }));
  };

  const handleConfidence = (key: keyof RuleConfig) => (event: ChangeEvent<HTMLInputElement>) => {
    onChange(updateSection(value, key, { min_confidence: Number(event.target.value) }));
  };

  return (
    <div className="card">
      <div className="card__header">
        <div>
          <h2>Rule Engine</h2>
          <p>Decide what the analyzer should detect inside each tender pack.</p>
        </div>
      </div>
      <div className="rule-config">
        {(
          Object.keys(value) as Array<keyof RuleConfig>
        ).map((sectionKey) => {
          const section = value[sectionKey];
          return (
            <div className="rule-config__item" key={sectionKey}>
              <div className="rule-config__header">
                <div>
                  <h3>{titleMap[sectionKey]}</h3>
                  {descriptionMap[sectionKey] && <p>{descriptionMap[sectionKey]}</p>}
                </div>
                <label className="switch">
                  <input type="checkbox" checked={section.enabled} onChange={handleToggle(sectionKey)} />
                  <span className="slider" />
                </label>
              </div>
              <div className="rule-config__controls">
                <label>
                  Keywords (comma separated)
                  <input
                    type="text"
                    value={section.keywords.join(", ")}
                    onChange={handleKeywords(sectionKey)}
                    placeholder="Add keywords separated by commas"
                  />
                </label>
                <label>
                  Minimum confidence ({Math.round(section.min_confidence * 100)}%)
                  <input
                    type="range"
                    min={0}
                    max={1}
                    step={0.05}
                    value={section.min_confidence}
                    onChange={handleConfidence(sectionKey)}
                  />
                </label>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
