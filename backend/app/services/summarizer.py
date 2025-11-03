from __future__ import annotations

import logging
from typing import List

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize


LOGGER = logging.getLogger(__name__)


def _ensure_nltk_data() -> None:
    resources = [
        ("punkt", "tokenizers/punkt"),
        ("stopwords", "corpora/stopwords"),
    ]
    for resource, path in resources:
        try:
            nltk.data.find(path)
        except LookupError:
            LOGGER.info("Downloading NLTK resource %s", resource)
            nltk.download(resource)


def _rank_sentences(sentences: List[str], stop_words: List[str]) -> List[tuple[int, float]]:
    word_freq = {}
    for sentence in sentences:
        words = word_tokenize(sentence.lower())
        for word in words:
            if word.isalpha() and word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1

    if not word_freq:
        return [(index, 0.0) for index, _ in enumerate(sentences)]

    max_freq = max(word_freq.values())
    for word in word_freq:
        word_freq[word] = word_freq[word] / max_freq

    sentence_scores = []
    for index, sentence in enumerate(sentences):
        words = word_tokenize(sentence.lower())
        score = sum(word_freq.get(word, 0) for word in words)
        sentence_scores.append((index, score))

    return sentence_scores


def summarize_text(text: str, max_sentences: int = 5) -> str:
    if not text:
        return ""

    _ensure_nltk_data()

    sentences = sent_tokenize(text)
    if len(sentences) <= max_sentences:
        return " ".join(sentences)

    stop_words = stopwords.words("english")
    ranked = sorted(_rank_sentences(sentences, stop_words), key=lambda item: item[1], reverse=True)
    selected_indices = sorted(index for index, _ in ranked[:max_sentences])
    summary_sentences = [sentences[index] for index in selected_indices]
    return " ".join(summary_sentences)
