import { apiClient } from "./client";
import {
  TokenResponse,
  TranslationCreateResponse,
  TranslationJobListResponse,
  TranslationLanguage,
  UserResponse
} from "./types";

interface RegisterPayload {
  email: string;
  password: string;
  full_name?: string;
  organization?: string;
}

export const registerUser = async (payload: RegisterPayload): Promise<UserResponse> => {
  const response = await apiClient.post<UserResponse>("/auth/register", payload);
  return response.data;
};

export const loginUser = async (email: string, password: string): Promise<TokenResponse> => {
  const form = new URLSearchParams();
  form.append("username", email);
  form.append("password", password);
  const response = await apiClient.post<TokenResponse>("/auth/login", form, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" }
  });
  return response.data;
};

export const fetchTranslationLanguages = async (): Promise<TranslationLanguage[]> => {
  const response = await apiClient.get<TranslationLanguage[]>("/translations/languages");
  return response.data;
};

export const fetchTranslationJobs = async (): Promise<TranslationJobListResponse> => {
  const response = await apiClient.get<TranslationJobListResponse>("/translations");
  return response.data;
};

export const translatePdf = async (file: File, languages: string[]): Promise<TranslationCreateResponse> => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("languages", JSON.stringify(languages));

  const response = await apiClient.post<TranslationCreateResponse>("/translations/translate", formData, {
    headers: { "Content-Type": "multipart/form-data" }
  });
  return response.data;
};

export const downloadTranslationBundle = async (jobId: number): Promise<Blob> => {
  const response = await apiClient.get(`/translations/${jobId}/download`, {
    responseType: "blob"
  });
  return response.data;
};
