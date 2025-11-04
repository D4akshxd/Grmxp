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

export interface TranslationLanguage {
  code: string;
  name: string;
}

export interface TranslationPage {
  page_number: number;
  original_text: string;
  translated_text: string;
}

export interface TranslationOutput {
  language_code: string;
  language_name: string;
  pages: TranslationPage[];
  full_text: string;
  word_count: number;
  character_count: number;
}

export interface TranslationJob {
  id: number;
  document_id: number;
  document_name: string;
  created_at: string;
  status: string;
  target_languages: string[];
  translations: TranslationOutput[];
  download_url?: string | null;
}

export interface TranslationJobListResponse {
  items: TranslationJob[];
  total: number;
}

export interface TranslationCreateResponse {
  document_id: number;
  job_id: number;
  status: string;
  translations: TranslationOutput[];
  download_url?: string | null;
}
