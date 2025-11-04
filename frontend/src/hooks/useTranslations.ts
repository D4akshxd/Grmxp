import { useCallback, useEffect, useState } from "react";
import toast from "react-hot-toast";

import {
  downloadTranslationBundle,
  fetchTranslationJobs,
  fetchTranslationLanguages,
  translatePdf
} from "../api";
import { TranslationCreateResponse, TranslationJob, TranslationLanguage } from "../api/types";

interface UseTranslationsState {
  jobs: TranslationJob[];
  languages: TranslationLanguage[];
  isLoadingJobs: boolean;
  isLoadingLanguages: boolean;
  isUploading: boolean;
}

const makeDownloadFileName = (documentName: string | undefined, jobId: number) => {
  if (!documentName) {
    return `translation-${jobId}.zip`;
  }
  const safe = documentName
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return `${safe || `translation-${jobId}`}-translations.zip`;
};

export const useTranslations = () => {
  const [state, setState] = useState<UseTranslationsState>({
    jobs: [],
    languages: [],
    isLoadingJobs: false,
    isLoadingLanguages: false,
    isUploading: false
  });

  const loadLanguages = useCallback(async () => {
    setState((prev) => ({ ...prev, isLoadingLanguages: true }));
    try {
      const response = await fetchTranslationLanguages();
      setState((prev) => ({ ...prev, languages: response }));
    } catch (error) {
      console.error(error);
      toast.error("Unable to load languages.");
    } finally {
      setState((prev) => ({ ...prev, isLoadingLanguages: false }));
    }
  }, []);

  const loadJobs = useCallback(async () => {
    setState((prev) => ({ ...prev, isLoadingJobs: true }));
    try {
      const response = await fetchTranslationJobs();
      setState((prev) => ({ ...prev, jobs: response.items }));
    } catch (error) {
      console.error(error);
      toast.error("Unable to load translation history.");
    } finally {
      setState((prev) => ({ ...prev, isLoadingJobs: false }));
    }
  }, []);

  useEffect(() => {
    loadLanguages();
    loadJobs();
  }, [loadLanguages, loadJobs]);

  const translate = useCallback(
    async (file: File, languageCodes: string[]): Promise<TranslationCreateResponse> => {
      setState((prev) => ({ ...prev, isUploading: true }));
      try {
        const response = await translatePdf(file, languageCodes);
        toast.success("Translation completed.");
        await loadJobs();
        return response;
      } catch (error) {
        console.error(error);
        toast.error("Translation failed. Please try again.");
        throw error;
      } finally {
        setState((prev) => ({ ...prev, isUploading: false }));
      }
    },
    [loadJobs]
  );

  const download = useCallback(async (jobId: number, documentName?: string) => {
    try {
      const blob = await downloadTranslationBundle(jobId);
      const url = window.URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = makeDownloadFileName(documentName, jobId);
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error(error);
      toast.error("Unable to download translation bundle.");
    }
  }, []);

  return {
    languages: state.languages,
    jobs: state.jobs,
    isLoadingJobs: state.isLoadingJobs,
    isLoadingLanguages: state.isLoadingLanguages,
    isUploading: state.isUploading,
    translate,
    download,
    refresh: loadJobs
  };
};
