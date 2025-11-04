import React from "react";

import { TranslationJob } from "../api/types";

interface TranslationHistoryProps {
  jobs: TranslationJob[];
  isLoading: boolean;
  onView: (job: TranslationJob) => void;
  onDownload: (jobId: number, documentName?: string) => void;
  activeJobId: number | null;
}

export const TranslationHistory: React.FC<TranslationHistoryProps> = ({
  jobs,
  isLoading,
  onView,
  onDownload,
  activeJobId
}) => {
  return (
    <div className="card translation-history">
      <div className="card__header">
        <div>
          <h2>Recent translations</h2>
          <p>Track completed translation runs and download the bundled outputs.</p>
        </div>
        <span className="badge">{jobs.length}</span>
      </div>

      {isLoading ? (
        <p>Loading translation history...</p>
      ) : jobs.length === 0 ? (
        <p>No translations yet. Upload a PDF to get started.</p>
      ) : (
        <ul className="translation-history__list">
          {jobs.map((job) => {
            const createdAt = new Date(job.created_at);
            const isActive = activeJobId === job.id;
            return (
              <li
                key={job.id}
                className={`translation-history__item${isActive ? " translation-history__item--active" : ""}`}
              >
                <div className="translation-history__meta">
                  <h3>{job.document_name}</h3>
                  <p>{createdAt.toLocaleString()}</p>
                </div>
                <div className="translation-history__languages">
                  {job.target_languages.map((code) => (
                    <span key={code} className="chip">
                      {code.toUpperCase()}
                    </span>
                  ))}
                </div>
                <div className="translation-history__status">
                  <span className={`status-badge status-badge--${job.status}`}>{job.status}</span>
                </div>
                <div className="translation-history__actions">
                  <button type="button" className="btn btn--ghost" onClick={() => onView(job)}>
                    View
                  </button>
                  <button
                    type="button"
                    className="btn"
                    onClick={() => onDownload(job.id, job.document_name)}
                    disabled={!job.download_url}
                  >
                    Download
                  </button>
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
};
