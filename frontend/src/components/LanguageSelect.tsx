import React from "react";

import { TranslationLanguage } from "../api/types";

interface LanguageSelectProps {
  languages: TranslationLanguage[];
  selected: string[];
  onChange: (codes: string[]) => void;
  isLoading?: boolean;
  disabled?: boolean;
  maxSelection?: number;
}

export const LanguageSelect: React.FC<LanguageSelectProps> = ({
  languages,
  selected,
  onChange,
  isLoading = false,
  disabled = false,
  maxSelection = 6
}) => {
  const handleToggle = (code: string) => {
    if (selected.includes(code)) {
      onChange(selected.filter((item) => item !== code));
    } else {
      if (selected.length >= maxSelection) return;
      onChange([...selected, code]);
    }
  };

  const isLimitReached = selected.length >= maxSelection;

  return (
    <div className="card">
      <div className="card__header">
        <div>
          <h3>Select target languages</h3>
          <p>Pick up to {maxSelection} languages for this translation run.</p>
        </div>
        <span className="badge">
          {selected.length}/{maxSelection}
        </span>
      </div>

      {isLoading ? (
        <p>Loading languages...</p>
      ) : languages.length === 0 ? (
        <p>No languages available.</p>
      ) : (
        <div className="language-select__grid">
          {languages.map((language) => {
            const code = language.code.toLowerCase();
            const isSelected = selected.includes(code);
            const checkboxDisabled =
              disabled || (!isSelected && isLimitReached);

            return (
              <label
                key={code}
                className={`language-select__option${isSelected ? " language-select__option--selected" : ""}`}
              >
                <input
                  type="checkbox"
                  value={code}
                  disabled={checkboxDisabled}
                  checked={isSelected}
                  onChange={() => handleToggle(code)}
                />
                <span className="language-select__name">{language.name}</span>
                <span className="language-select__code">{code.toUpperCase()}</span>
              </label>
            );
          })}
        </div>
      )}

      {isLimitReached && <p className="language-select__notice">Maximum languages selected.</p>}
    </div>
  );
};
