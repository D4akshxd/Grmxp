import { useEffect, useMemo, useState } from "react";
import toast from "react-hot-toast";

import { TranslationJob, TranslationOutput } from "../api/types";
import { LanguageSelect } from "../components/LanguageSelect";
import { TranslationHistory } from "../components/TranslationHistory";
import { TranslationViewer } from "../components/TranslationViewer";
import { UploadCard } from "../components/UploadCard";
import { DashboardLayout } from "../components/layout/DashboardLayout";
import { useTranslations } from "../hooks/useTranslations";

export const DashboardPage: React.FC = () => {
  const {
    languages,
    jobs,
    isLoadingJobs,
    isLoadingLanguages,
    isUploading,
    translate,
    download
  } = useTranslations();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedLanguages, setSelectedLanguages] = useState<string[]>([]);
  const [activeTranslations, setActiveTranslations] = useState<TranslationOutput[]>([]);
  const [activeJobId, setActiveJobId] = useState<number | null>(null);

  const sortedLanguages = useMemo(
    () => [...languages].sort((a, b) => a.name.localeCompare(b.name)),
    [languages]
  );

  useEffect(() => {
    if (sortedLanguages.length > 0 && selectedLanguages.length === 0) {
      setSelectedLanguages([sortedLanguages[0].code]);
    }
  }, [sortedLanguages, selectedLanguages.length]);

  useEffect(() => {
    if (!activeTranslations.length && jobs.length > 0) {
      setActiveTranslations(jobs[0].translations);
      setActiveJobId(jobs[0].id);
    }
  }, [jobs, activeTranslations.length]);

  const handleTranslate = async () => {
    if (!selectedFile) {
      toast.error("Select a PDF to translate.");
      return;
    }
    if (selectedLanguages.length === 0) {
      toast.error("Pick at least one target language.");
      return;
    }

    try {
      const response = await translate(selectedFile, selectedLanguages);
      setActiveTranslations(response.translations);
      setActiveJobId(response.job_id);
      setSelectedFile(null);
    } catch (error) {
      // Notification handled inside the hook
    }
  };

  const handleSelectJob = (job: TranslationJob) => {
    setActiveTranslations(job.translations);
    setActiveJobId(job.id);
  };

  return (
    <DashboardLayout>
      <div className="grid">
        <div className="grid__col">
          <UploadCard onSelect={setSelectedFile} isUploading={isUploading} />

          <LanguageSelect
            languages={sortedLanguages}
            selected={selectedLanguages}
            onChange={setSelectedLanguages}
            isLoading={isLoadingLanguages}
            disabled={isUploading}
          />

          {selectedFile && (
            <div className="card card--inline">
              <div className="card__header">
                <div>
                  <h3>Ready to translate</h3>
                  <p>{selectedFile.name}</p>
                </div>
                <button className="btn" onClick={handleTranslate} disabled={isUploading}>
                  {isUploading ? "Translating..." : "Translate PDF"}
                </button>
              </div>
              <p className="card__note">
                {selectedLanguages.length} language(s) selected. Larger files may take a little longer to process.
              </p>
            </div>
          )}
        </div>

        <div className="grid__col">
          <TranslationViewer translations={activeTranslations} />
          <TranslationHistory
            jobs={jobs}
            isLoading={isLoadingJobs}
            onView={handleSelectJob}
            onDownload={download}
            activeJobId={activeJobId}
          />
        </div>
      </div>
    </DashboardLayout>
  );
};
