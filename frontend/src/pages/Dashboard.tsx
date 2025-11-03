import { useState } from "react";

import { defaultRuleConfig, RuleConfig } from "../api/types";
import { DocumentCard } from "../components/DocumentCard";
import { RuleConfigForm } from "../components/RuleConfigForm";
import { UploadCard } from "../components/UploadCard";
import { DashboardLayout } from "../components/layout/DashboardLayout";
import { useDocuments } from "../hooks/useDocuments";

export const DashboardPage: React.FC = () => {
  const [ruleConfig, setRuleConfig] = useState<RuleConfig>(defaultRuleConfig);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const { documents, isLoading, isUploading, upload, download, email } = useDocuments();

  const handleUpload = async () => {
    if (!selectedFile) return;
    await upload(selectedFile, ruleConfig);
    setSelectedFile(null);
  };

  return (
    <DashboardLayout>
      <div className="grid">
        <div className="grid__col">
          <UploadCard
            onSelect={(file) => setSelectedFile(file)}
            isUploading={isUploading}
          />
          {selectedFile && (
            <div className="card card--inline">
              <div className="card__header">
                <div>
                  <h3>Ready to analyze</h3>
                  <p>{selectedFile.name}</p>
                </div>
                <button className="btn" onClick={handleUpload} disabled={isUploading}>
                  {isUploading ? "Processing..." : "Run analysis"}
                </button>
              </div>
              <p className="card__note">The PDF will be parsed, summarized, and packaged with your rule set.</p>
            </div>
          )}
          <RuleConfigForm value={ruleConfig} onChange={setRuleConfig} />
        </div>

        <div className="grid__col">
          <div className="card">
            <div className="card__header">
              <div>
                <h2>Recent analyses</h2>
                <p>Track every bid package your team has processed.</p>
              </div>
              <span className="badge">{documents.length}</span>
            </div>
            {isLoading ? (
              <p>Loading documents...</p>
            ) : documents.length === 0 ? (
              <p>No tenders processed yet. Upload your first PDF to get started.</p>
            ) : (
              <div className="document-list">
                {documents.map((doc) => (
                  <DocumentCard
                    key={doc.id}
                    document={doc}
                    onDownload={download}
                    onEmail={email}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};
