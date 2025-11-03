export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface UserResponse {
  id: number;
  email: string;
  full_name?: string;
  organization?: string;
  created_at: string;
}

export interface SectionInsight {
  title: string;
  summary: string;
  importance_score: number;
  keywords_found: string[];
}

export interface AnalysisResult {
  document_id: number;
  analysis_id: number;
  summary: string;
  highlights: Record<string, string>;
  sections: Record<string, SectionInsight>;
  created_at: string;
}

export interface DocumentRecord {
  id: number;
  original_filename: string;
  uploaded_at: string;
  status: string;
  latest_analysis?: AnalysisResult | null;
}

export interface DocumentListResponse {
  items: DocumentRecord[];
  total: number;
}

export interface RuleSectionConfig {
  enabled: boolean;
  keywords: string[];
  min_confidence: number;
}

export interface RuleConfig {
  technical_specifications: RuleSectionConfig;
  certificates: RuleSectionConfig;
  atc_documents: RuleSectionConfig;
  boq: RuleSectionConfig;
  eligibility: RuleSectionConfig;
  important_dates: RuleSectionConfig;
}

export const defaultRuleConfig: RuleConfig = {
  technical_specifications: {
    enabled: true,
    keywords: ["specification", "technical", "compliance"],
    min_confidence: 0.2
  },
  certificates: {
    enabled: true,
    keywords: ["certificate", "certification", "iso"],
    min_confidence: 0.2
  },
  atc_documents: {
    enabled: true,
    keywords: ["atc", "terms", "conditions", "amendment"],
    min_confidence: 0.2
  },
  boq: {
    enabled: true,
    keywords: ["bill of quantity", "boq", "pricing", "rate"],
    min_confidence: 0.2
  },
  eligibility: {
    enabled: true,
    keywords: ["eligibility", "experience", "turnover"],
    min_confidence: 0.2
  },
  important_dates: {
    enabled: true,
    keywords: ["bid end", "submission", "opening"],
    min_confidence: 0.2
  }
};
