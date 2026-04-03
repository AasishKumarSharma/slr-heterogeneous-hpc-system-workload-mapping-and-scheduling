# Systematic Literature Review: Optimization of Workload Mapping and Scheduling in Heterogeneous HPC Systems

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

This repository contains the supplementary material for the systematic literature review (SLR):

> **A. K. Sharma and J. M. Kunkel**, "Optimization of Workload Mapping and Scheduling in Heterogeneous HPC Systems: A Systematic Literature Review," 2026.

## Overview

We conducted a PRISMA-compliant systematic review of **145 studies** (2017-2025) covering optimization techniques for workload mapping and scheduling in heterogeneous computing environments (HPC, cloud, edge/fog, hybrid).

### Key Findings

- **Five solver classes** identified: Heuristic (32.4%), Hybrid (23.4%), Metaheuristic (22.8%), ML/AI (16.6%), Exact (4.8%)
- **Makespan** is the dominant objective (88.4%), with multi-objective formulations growing (72.1%)
- **ML/AI-based scheduling** grew from 0% (2017) to 37% (2025) of annual publications
- **Mapping-scheduling gap**: Only 25.2% of studies jointly optimize both subproblems
- **Scalability gap**: Most evaluations use fewer than 1,000 tasks

## Repository Structure

```
.
|-- README.md                    # This file
|-- SLR_Protocol.md              # Full SLR protocol (RQs, search strategy, criteria)
|-- LICENSE
|-- data/
|   |-- SLR_Comprehensive_Extraction_Updated.csv   # Final extraction (145 papers, 48 fields)
|   |-- SLR_Comprehensive_Extraction_Updated.xlsx   # Same in Excel format
|   |-- SLR_Extracted_From_PDFs.csv                 # Raw automated extraction (290 PDFs)
|   |-- included_papers_for_slr.csv                 # List of 145 included papers
|   |-- strict_screening_results.csv                # Full screening decisions (309 papers)
|   |-- extraction_log.md                           # Detailed extraction with page references
|-- scripts/
|   |-- extract_all_papers.py     # PDF extraction pipeline (PyMuPDF-based)
|   |-- analysis_and_figures.py   # Analysis and figure generation
|-- figures/
|   |-- fig2_publication_trend.*
|   |-- fig3_solver_classification.*
|   |-- fig4_objectives.*
|   |-- fig5_system_workload.*
|   |-- fig6_constraints.*
|   |-- fig7_mapping_scheduling.*
|   |-- fig8_top_methods.*
|   |-- fig9_evaluation.*
|   |-- fig10_scalability.*
|   |-- fig11_solver_objective_heatmap.*
|   |-- fig12_ml_trend.*
```

## Data Description

### SLR_Comprehensive_Extraction_Updated.csv

Each row represents one of the 145 included studies. The 48 columns are organized into:

| Category | Fields |
|----------|--------|
| Bibliographic | ID, title, authors, year, venue, url, paper_or_abstract |
| System | system_scope, heterogeneity, resource_types |
| Workload | workload_type, task_dependencies, dynamic_workload |
| Mapping/Scheduling | addresses_mapping, addresses_scheduling, mapping_scheduling |
| Solver | solver_class, specific_method, algorithm_strategy, hybrid_approach |
| Objectives | makespan, utilization, energy, cost, load_balance, throughput, latency, deadline, reliability, security, single_multi_obj |
| Constraints | assignment, capacity, feature, precedence, communication, deadline (con), energy (con) |
| Evaluation | max_tasks, max_resources, eval_type, benchmark, baselines, reproducible |
| Meta | extraction_source, confidence, abstract_length, abstract_preview |

### Extraction Sources

- **full-text** (116 papers): Extracted from complete PDF with page-level traceability
- **abstract-pdf** (29 papers): Extracted from abstract printouts only

## Reproducing the Analysis

### Requirements

```bash
pip install pandas matplotlib numpy openpyxl PyMuPDF
```

### Generate Figures

```bash
cd scripts
python analysis_and_figures.py
```

This produces all 11 figures in the `figures/` directory.

### Run Extraction Pipeline

To re-extract data from PDFs (requires the paper PDFs):

```bash
cd scripts
python extract_all_papers.py
```

## Search Strategy

Five queries on Google Scholar (January 2017 - March 2025):
1. "workload mapping" AND "scheduling" AND "heterogeneous" AND "HPC"
2. "task scheduling" AND "heterogeneous computing" AND "optimization"
3. "workflow scheduling" AND "HPC" AND ("MILP" OR "heuristic" OR "metaheuristic" OR "machine learning")
4. "DAG scheduling" AND "heterogeneous" AND ("makespan" OR "resource utilization")
5. "resource allocation" AND "heterogeneous cluster" AND "scheduling optimization"

Supplemented by forward/backward snowballing from 124 seed papers (2,313 candidates).

## Citation

If you use this dataset or analysis in your research, please cite:

```bibtex
@article{Sharma2026SLR,
  author  = {Sharma, Aasish Kumar and Kunkel, Julian M.},
  title   = {Optimization of Workload Mapping and Scheduling in
             Heterogeneous {HPC} Systems: A Systematic Literature Review},
  year    = {2026},
  note    = {Under review}
}
```

## License

The dataset and analysis scripts are released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The reviewed papers remain under their respective publishers' copyright.

## Contact

- Aasish Kumar Sharma - aasish.sharma@uni-goettingen.de
- Julian M. Kunkel - julian.kunkel@gwdg.de

Institute of Computer Science, Georg-August-Universitat Gottingen / GWDG, Germany
