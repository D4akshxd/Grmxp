import { useCallback, useEffect, useState } from "react";
import toast from "react-hot-toast";

import { analyzeDocument, downloadBundle, emailAnalysis, fetchDocuments } from "../api";
import { DocumentRecord, RuleConfig } from "../api/types";

interface UseDocumentsState {
  items: DocumentRecord[];
  isLoading: boolean;
  isUploading: boolean;
}

export const useDocuments = () => {
  const [state, setState] = useState<UseDocumentsState>({ items: [], isLoading: false, isUploading: false });

  const load = useCallback(async () => {
    setState((prev) => ({ ...prev, isLoading: true }));
    try {
      const response = await fetchDocuments();
      setState((prev) => ({ ...prev, items: response.items }));
    } catch (error) {
      console.error(error);
      toast.error("Failed to load documents");
    } finally {
      setState((prev) => ({ ...prev, isLoading: false }));
    }
  }, []);

  const upload = useCallback(async (file: File, ruleConfig: RuleConfig) => {
    setState((prev) => ({ ...prev, isUploading: true }));
    try {
      await analyzeDocument(file, ruleConfig);
      toast.success("Tender uploaded. Analysis will be ready shortly.");
      await load();
    } catch (error) {
      console.error(error);
      toast.error("Upload failed. Please retry.");
    } finally {
      setState((prev) => ({ ...prev, isUploading: false }));
    }
  }, [load]);

  const download = useCallback(async (documentId: number) => {
    try {
      const blob = await downloadBundle(documentId);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `gem-analysis-${documentId}.zip`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error(error);
      toast.error("Unable to download bundle.");
    }
  }, []);

  const email = useCallback(async (analysisId: number, recipients: string[]) => {
    try {
      await emailAnalysis(analysisId, recipients);
      toast.success("Email dispatch queued");
    } catch (error) {
      console.error(error);
      toast.error("Email failed. Check SMTP settings.");
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return {
    documents: state.items,
    isLoading: state.isLoading,
    isUploading: state.isUploading,
    refresh: load,
    upload,
    download,
    email
  };
};
