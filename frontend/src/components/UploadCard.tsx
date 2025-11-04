import { ChangeEvent, useRef } from "react";

interface UploadCardProps {
  onSelect: (file: File) => void;
  isUploading: boolean;
}

export const UploadCard: React.FC<UploadCardProps> = ({ onSelect, isUploading }) => {
  const inputRef = useRef<HTMLInputElement | null>(null);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      onSelect(file);
    }
  };

  const triggerPicker = () => inputRef.current?.click();

  return (
    <div className="card upload-card">
      <div className="card__header">
        <div>
          <h2>Upload PDF for translation</h2>
          <p>Drop in any PDF and the AI will deliver fluent translations in your selected languages.</p>
        </div>
      </div>
      <div className="upload-card__body" onClick={triggerPicker} role="presentation">
        <input
          ref={inputRef}
          className="upload-card__input"
          type="file"
          accept="application/pdf"
          onChange={handleFileChange}
          disabled={isUploading}
        />
        <div className="upload-card__dropzone">
          <span className="upload-card__icon" aria-hidden>
            🗎
          </span>
          <p className="upload-card__title">Drag & drop your PDF document</p>
          <p className="upload-card__subtitle">or click to browse files (max 100MB)</p>
          <button type="button" className="btn" disabled={isUploading}>
            {isUploading ? "Uploading..." : "Select PDF"}
          </button>
        </div>
      </div>
    </div>
  );
};
