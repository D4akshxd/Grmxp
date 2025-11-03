import { useMemo, useState } from "react";

import { DocumentRecord } from "../api/types";

interface Props {
  document: DocumentRecord;
  onDownload: (documentId: number) => Promise<void>;
  onEmail: (analysisId: number, recipients: string[]) => Promise<void>;
}

export const DocumentCard: React.FC<Props> = ({ document, onDownload, onEmail }) => {
  const [isEmailing, setEmailing] = useState(false);
  const [isDownloading, setDownloading] = useState(false);

  const highlights = useMemo(() => Object.entries(document.latest_analysis?.highlights ?? {}), [document]);

  const handleDownload = async () => {
    setDownloading(true);
    try {
      await onDownload(document.id);
    } finally {
      setDownloading(false);
    }
  };

  const handleEmail = async () => {
    if (!document.latest_analysis) return;
    const recipients = prompt("Enter recipient emails separated by commas")?.split(",").map((item) => item.trim()).filter(Boolean);
    if (!recipients || recipients.length === 0) return;

    setEmailing(true);
    try {
      await onEmail(document.latest_analysis.analysis_id, recipients);
      alert("Email sent successfully");
    } catch (error) {
      console.error(error);
      alert("Failed to send email. Please verify SMTP configuration.");
    } finally {
      setEmailing(false);
    }
  };

  return (
    <div className="card document-card">
      <div className="document-card__header">
        <div>
          <h3>{document.original_filename}</h3>
          <p>Uploaded on {new Date(document.uploaded_at).toLocaleString()}</p>
        </div>
        <span className={`status status--${document.status}`}>{document.status}</span>
      </div>

      {document.latest_analysis ? (
        <div className="document-card__content">
          <p className="document-card__summary">{document.latest_analysis.summary}</p>
          <div className="document-card__highlights">
            {highlights.map(([key, value]) => (
              <div className="pill" key={key}>
                <strong>{key.replace("_", " ").toUpperCase()}</strong>
                <span>{value}</span>
              </div>
            ))}
            {highlights.length === 0 && <p>No highlights extracted.</p>}
          </div>
        </div>
      ) : (
        <p>Analysis is being prepared. Refresh in a moment.</p>
      )}

      <div className="document-card__actions">
        <button className="btn" onClick={handleDownload} disabled={isDownloading || !document.latest_analysis}>
          {isDownloading ? "Preparing..." : "Download bundle"}
        </button>
        <button
          className="btn btn--ghost"
          onClick={handleEmail}
          disabled={isEmailing || !document.latest_analysis}
        >
          {isEmailing ? "Sending..." : "Email summary"}
        </button>
      </div>
    </div>
  );
};
