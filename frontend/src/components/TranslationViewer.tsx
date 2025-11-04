import { useEffect, useState } from "react";

import { TranslationOutput } from "../api/types";

interface TranslationViewerProps {
  translations: TranslationOutput[];
}

export const TranslationViewer: React.FC<TranslationViewerProps> = ({ translations }) => {
  const [activeIndex, setActiveIndex] = useState(0);

  const safeTranslations = translations || [];
  const clampedIndex = Math.min(activeIndex, Math.max(safeTranslations.length - 1, 0));
  const activeTranslation = safeTranslations[clampedIndex];

  useEffect(() => {
    setActiveIndex(0);
  }, [translations?.length]);

  if (!safeTranslations.length) {
    return (
      <div className="card translation-viewer">
        <div className="card__header">
          <div>
            <h2>Translation preview</h2>
            <p>The translated document will appear here once ready.</p>
          </div>
        </div>
        <p>No translation selected.</p>
      </div>
    );
  }

  return (
    <div className="card translation-viewer">
      <div className="card__header">
        <div>
          <h2>Translation preview</h2>
          <p>Switch languages to review the translated output.</p>
        </div>
      </div>

      <div className="translation-viewer__tabs">
        {safeTranslations.map((translation, index) => (
          <button
            key={translation.language_code}
            type="button"
            className={`translation-viewer__tab${index === clampedIndex ? " translation-viewer__tab--active" : ""}`}
            onClick={() => setActiveIndex(index)}
          >
            {translation.language_name}
          </button>
        ))}
      </div>

      {activeTranslation && (
        <div className="translation-viewer__summary">
          <div>
            <span className="translation-viewer__metric">{activeTranslation.word_count} words</span>
            <span className="translation-viewer__metric">{activeTranslation.character_count} characters</span>
          </div>
          <span className="translation-viewer__code">{activeTranslation.language_code.toUpperCase()}</span>
        </div>
      )}

      <div className="translation-viewer__content">
        {activeTranslation?.pages.map((page, idx) => (
          <details key={page.page_number} className="translation-viewer__section" defaultOpen={idx === 0}>
            <summary>Page {page.page_number}</summary>
            <div className="translation-viewer__section-body">
              <div className="translation-viewer__translated">
                {page.translated_text ? (
                  <p>{page.translated_text}</p>
                ) : (
                  <p className="translation-viewer__placeholder">No translated text detected for this page.</p>
                )}
              </div>
              <div className="translation-viewer__original">
                <span>Original text</span>
                <p>{page.original_text || "No source text extracted."}</p>
              </div>
            </div>
          </details>
        ))}
      </div>
    </div>
  );
};
