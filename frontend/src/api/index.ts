import { apiClient } from "./client";
import { DocumentListResponse, RuleConfig, TokenResponse, UserResponse } from "./types";

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

export const fetchDocuments = async (): Promise<DocumentListResponse> => {
  const response = await apiClient.get<DocumentListResponse>("/documents");
  return response.data;
};

export const analyzeDocument = async (
  file: File,
  ruleConfig: RuleConfig
): Promise<{ document_id: number; analysis_id: number; status: string; summary_preview: string }> => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("rule_config", JSON.stringify(ruleConfig));

  const response = await apiClient.post("/documents/analyze", formData, {
    headers: { "Content-Type": "multipart/form-data" }
  });
  return response.data;
};

export const downloadBundle = async (documentId: number): Promise<Blob> => {
  const response = await apiClient.get(`/documents/${documentId}/download`, {
    responseType: "blob"
  });
  return response.data;
};

export const emailAnalysis = async (
  analysisId: number,
  recipients: string[],
  subject?: string,
  message?: string
): Promise<void> => {
  const params = new URLSearchParams();
  params.set("recipients", recipients.join(","));
  if (subject) params.set("subject", subject);
  if (message) params.set("message", message);
  await apiClient.post(`/documents/${analysisId}/email?${params.toString()}`);
};
