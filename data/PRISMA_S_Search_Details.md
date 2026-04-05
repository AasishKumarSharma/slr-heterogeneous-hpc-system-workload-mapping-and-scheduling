# PRISMA-S: Search Strategy Details

Following PRISMA-S (PRISMA for Searching) reporting guidelines.

## 1. Database and Platform

| Item | Detail |
|------|--------|
| Primary database | Google Scholar (scholar.google.com) |
| Supplementary database | Semantic Scholar API (api.semanticscholar.org) |
| Indexed sources via Google Scholar | IEEE Xplore, ACM Digital Library, Springer, Elsevier/ScienceDirect, Wiley, MDPI, arXiv |
| Search interface | Google Scholar web interface (standard) |
| Date of searches | January 15 - March 20, 2025 |
| Search operator support | AND, OR, quoted phrases |

## 2. Search Queries and Results

| Query ID | Search String | Date Executed | Results Retrieved |
|----------|---------------|---------------|-------------------|
| Q1 | "workload mapping" AND "scheduling" AND "heterogeneous" AND "HPC" | 2025-01-15 | 100 (first page) |
| Q2 | "task scheduling" AND "heterogeneous computing" AND "optimization" | 2025-01-20 | 100 |
| Q3 | "workflow scheduling" AND "HPC" AND ("MILP" OR "heuristic" OR "metaheuristic" OR "machine learning") | 2025-02-01 | 100 |
| Q4 | "DAG scheduling" AND "heterogeneous" AND ("makespan" OR "resource utilization") | 2025-02-10 | 100 |
| Q5 | "resource allocation" AND "heterogeneous cluster" AND "scheduling optimization" | 2025-02-15 | 100 |

**Note:** Google Scholar returns results sorted by relevance. For each query, the first 100 results were collected. Total before deduplication: ~500 records. After deduplication across queries: 309 unique records.

## 3. Search Parameters

| Parameter | Setting |
|-----------|---------|
| Language | English |
| Date range | 2017-2025 |
| Sort order | Relevance (Google Scholar default) |
| Results per query | First 100 |
| Collection method | Automated Python script using scholarly/serpapi |
| Export format | CSV (title, authors, year, venue, abstract, URL, citation count) |

## 4. Snowballing

| Item | Detail |
|------|--------|
| Snowball type | Forward and backward |
| Seed papers | 124 (from initial screening of Q1-Q5 results) |
| Tool | Semantic Scholar API (citation graph traversal) |
| Candidate references identified | 2,313 |
| Citation edges recorded | 2,789 |
| Snowball data file | `snowballing/snowball_results.xlsx` (Sheets: Seeds, Candidates, Edges, Log, Config) |

**Snowball purpose:** The 2,313 candidates were used to verify search completeness. Papers identified through snowballing that met inclusion criteria were cross-checked against the 309 database results. All qualifying snowball papers were already captured by the database search, confirming adequate search coverage.

## 5. Screening Process

### Stage 1: Title/Abstract Screening (309 records)

| Criterion | Type | Applied to | Decision |
|-----------|------|------------|----------|
| Addresses workload mapping or scheduling optimization | Inclusion | Title + abstract | Include if yes |
| Targets heterogeneous computing | Inclusion | Title + abstract | Include if yes |
| Proposes or evaluates algorithmic method | Inclusion | Title + abstract | Include if yes |
| Published 2017-2025 | Inclusion | Metadata | Include if yes |
| English language | Inclusion | Full text | Include if yes |
| Pure survey without novel method | Exclusion | Abstract | Exclude (catalog as survey) |
| Homogeneous systems only | Exclusion | Abstract | Exclude |
| Network/storage scheduling only | Exclusion | Abstract | Exclude |

**Screening method:** Automated keyword-based screening with manual review of borderline cases by first author.
**Results:** 148 excluded, 14 identified as related surveys, 161 passed to full-text eligibility.

### Stage 2: Full-Text Eligibility (161 records)

| Check | Result |
|-------|--------|
| Full text retrievable | 161/161 (full text or abstract PDF) |
| Confirmed peer-reviewed | All 161 |
| Duplicate detection | 2 duplicates identified and removed |
| Surveys reclassified | 14 moved to related surveys catalog |
| Final included | 145 primary studies |

**Duplicate detection method:** Title similarity using Python SequenceMatcher (threshold >= 0.8). Confirmed pairs:
1. Zhang 2021 (ID 27 vs 100): "Bi-objective workflow scheduling..." - identical paper, different title capitalization
2. Bhagwan 2021 (ID 77 vs 97): "HC-CSO" vs "H-CSO" - same paper, different abbreviation in title

## 6. Data Collection Tools

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.10+ | All scripts |
| PyMuPDF (fitz) | 1.27+ | PDF text extraction |
| pandas | 1.5+ | Data processing |
| openpyxl | 3.0+ | Excel I/O |
| matplotlib | 3.6+ | Figure generation |
| Semantic Scholar API | v1 | Metadata enrichment, snowballing |

## 7. File Manifest

| File | Records | Description |
|------|---------|-------------|
| `strict_screening_results.csv` | 309 | All database search results with screening decisions |
| `included_papers_for_slr.csv` | 145 | Final included papers |
| `SLR_Comprehensive_Extraction_Updated.csv` | 145 | Full extraction (48 fields per paper) |
| `SLR_Extracted_From_PDFs.csv` | 290 | Raw automated extraction from all available PDFs |
| `SLR_Extracted_From_PDFs.json` | 290 | Extraction with page-level source references |
