# 🕉️ Exploring Srimad Bhagavatam's Wisdom: Benchmarking WordNet Graph-Based Method and Transformer-Based LLMs for NLP Tasks

[![Published](https://img.shields.io/badge/Published-REST%20Conference%20Proceedings%202026-blue)](https://restpublisher.com/wp-content/uploads/2026/01/11.-Exploring-Srimad-Bhagavatams-Wisdom-Benchmarking-WordNet-Graph-Based-Method-and-Transformer-Based-LLMs-for-NLP-Tasks.pdf)
[![Institution](https://img.shields.io/badge/Institution-VIPS--TC%20Delhi-orange)](https://vips.edu)
[![Language](https://img.shields.io/badge/Language-Python-green)](https://python.org)
[![NLP](https://img.shields.io/badge/Domain-Sanskrit%20NLP-purple)]()

---

## 📖 Overview

This research explores the application of **Natural Language Processing (NLP)** on one of the most sacred Sanskrit scriptures — the **Srimad Bhagavatam** (Bhāgavata Purāṇa). The text contains 12 cantos and 18,000 verses (Ślokas) and presents unique challenges for computational analysis due to its complex Sanskrit terminology, context-dependent word senses, and rich cultural depth.

We benchmark two distinct paradigms for **Word Sense Disambiguation (WSD)** and **Sentiment Analysis**:

1. **WordNet Graph-Based Approach** — uses semantic graphs with centrality metrics (Degree & PageRank)
2. **Transformer-Based LLM Approach** — uses DeepSeek-r1 and Gemma-3-12b for contextual understanding

📄 **[Read the Full Paper](https://restpublisher.com/wp-content/uploads/2026/01/11.-Exploring-Srimad-Bhagavatams-Wisdom-Benchmarking-WordNet-Graph-Based-Method-and-Transformer-Based-LLMs-for-NLP-Tasks.pdf)**

---

## 👥 Authors

| Name | Affiliation |
|------|-------------|
| **Hardik** | Vivekananda Institute of Professional Studies - Technical Campus (VIPS-TC), Pitampura, Delhi |
| Drishti Bhutani | VIPS-TC, Pitampura, Delhi |
| Sonakshi Vij *(Corresponding Author)* | VIPS-TC, Pitampura, Delhi |
---

## ⚙️ Methodology

### 1. 🔷 WordNet Graph-Based Approach

```
Input Sanskrit Verse (Image)
        ↓
  OCR Text Extraction
        ↓
  Preprocessing (Tokenization → Lemmatization → Stopword Removal)
        ↓
  WordNet SynSets, Gloss & Category Extraction
        ↓
  Knowledge Graph Construction (Nodes = Words, Edges = Relations)
        ↓
  Centrality Metrics (Degree + PageRank)
        ↓
  Best Synonym Selection via Graph Ranking
        ↓
  English Translation (AI4Bharat) → Summary + Sentiment (BERT)
```

### 2. 🔶 Transformer-Based LLM Approach

```
Input Sanskrit Verse
        ↓
  Preprocessing
        ↓
  LLM (DeepSeek-r1 / Gemma-3-12b) for WSD
        ↓
  Best Synonym + Gloss Extraction
        ↓
  Summary Generation → Sentiment Analysis
```

---

## 🧪 Test Case: Verse ŚB 10.8.33

**Sanskrit Input:**
> सा गृहीत्वा करे कृष्णमुपालभ्य हितैषिणी ।
> यशोदा भयसम्भ्रान्तप्रेक्षणाक्षमभाषत ॥ ३३ ॥

**Translation:** Mother Yaśodā, taking Krishna within her hands, wanted to chastise Him out of maternal anxiety and affection.

### 📊 Results Summary

| Method | WSD Accuracy | Sentiment | Mood |
|--------|-------------|-----------|------|
| **WordNet Graph** | Partial (structural, not contextual) | ❌ Negative (incorrect) | — |
| **DeepSeek-r1** | ✅ High contextual accuracy | ✅ Positive | Devotional & Caring |
| **Gemma-3-12b** | ✅ High contextual accuracy | ✅ Positive | Anxious Tenderness |

---

## 🚀 Getting Started

### Prerequisites

```bash
pip install -r requirements.txt
```

### Key Dependencies

```txt
transformers
torch
nltk
networkx
indic-nlp-library
ai4bharat-transliteration
```

### Run WordNet Approach

```bash
python wordnet_approach/graph_builder.py --input data/verses/sb_10_8_33.png
```

### Run LLM Approach (DeepSeek)

```bash
python llm_approach/deepseek_wsd.py --verse "सा गृहीत्वा करे कृष्णम्..."
```

---

## 📈 Key Findings

- The **WordNet-based approach** effectively identifies structural word relationships but is limited by its dependence on lexical databases, leading to inaccurate contextual mappings (e.g., *karaḥ* = "hand" was incorrectly matched with *nṛpāṃśaḥ* = "tax").
- **DeepSeek-r1** interpreted Yaśodā's actions as a divine protective gesture, yielding a **positive, devotional** sentiment.
- **Gemma-3-12b** highlighted the emotional depth of maternal anxiety while maintaining a **positive, tender** overall sentiment.
- LLMs significantly **outperform** the static WordNet approach for contextually dense classical Sanskrit texts.
- The findings suggest promising directions for **hybrid models** combining LLM contextual understanding with WordNet structural knowledge.

---

## 📚 Citation

If you use this work, please cite:

```bibtex
@inproceedings{vij2026srimadbhagavatam,
  title     = {Exploring Srimad Bhagavatam's Wisdom: Benchmarking WordNet Graph-Based Method and Transformer-Based LLMs for NLP Tasks},
  author    = {Vij, Sonakshi and Bhutani, Drishti and Hardik},
  booktitle = {REST Conference Proceedings},
  volume    = {2},
  number    = {1},
  pages     = {58--62},
  year      = {2026},
  publisher = {REST Publisher},
  isbn      = {978-81-993050-7-6}
}
```

---

## 🔗 Related Work & References

- [SansGPT: Advancing Generative Pre-Training in Sanskrit](https://aclanthology.org/) — ICON 2024
- [Sanskrit Knowledge-based Systems](https://arxiv.org/abs/2406.18276) — Terdalkar, 2024
- [Sanskritshala NLP Toolkit](https://arxiv.org/abs/2302.09527) — Sandhan et al., 2023
- [As-It-Is-Gyan](https://github.com/Hardik596/As-It-Is-gyan) — Related RAG project on Bhagavad Gita by Hardik

---

## 🙏 Acknowledgements

This research was conducted at **Vivekananda Institute of Professional Studies - Technical Campus (VIPS-TC)**, Pitampura, Delhi, India. We thank the creators of AI4Bharat, Sanskrit WordNet, and the open-source NLP community for making Sanskrit computational linguistics more accessible.

---

<p align="center">
  Made with ❤️ for preserving ancient wisdom through modern AI
</p>
