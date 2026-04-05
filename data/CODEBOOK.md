# SLR Extraction Codebook

This document defines every field in `SLR_Comprehensive_Extraction_Updated.csv` (145 papers, 48 fields).
All coding decisions are documented here for reproducibility and independent verification.

## 1. Bibliographic Fields

| Field | Type | Description | Coding Rule |
|-------|------|-------------|-------------|
| ID | Integer | Sequential paper identifier (1-145) | Assigned after deduplication |
| title | String | Full paper title | Verbatim from source |
| authors | String | Author names | As listed in paper, comma-separated |
| year | Integer | Publication year (2017-2025) | Year of first publication (not preprint) |
| venue | String | Journal/conference name | Full name preferred; abbreviated if source truncated |
| url | String | Access URL or DOI link | Persistent URL preferred (DOI > publisher > Google Scholar) |
| paper_or_abstract | Enum: paper/abstract | Whether full text was available | "paper" = full PDF available; "abstract" = only abstract/first page |

## 2. System Characteristics

| Field | Type | Description | Coding Rule |
|-------|------|-------------|-------------|
| system_scope | String | Computing environment | Coded from paper's stated target platform. Values: HPC, Cloud, Edge/Fog, Hybrid (if multiple platforms), Other |
| heterogeneity | Enum: Hetero/Homo/Unknown | Whether system is heterogeneous | "Hetero" if paper explicitly targets heterogeneous resources or uses heterogeneous execution time matrices |
| resource_types | String | Types of resources modeled | Comma-separated. Detected from paper text: CPU, GPU, FPGA, TPU, VM, Container |

## 3. Workload Characteristics

| Field | Type | Description | Coding Rule |
|-------|------|-------------|-------------|
| workload_type | String | Type of workload model | "Workflow/DAG" if paper models tasks with dependencies as directed acyclic graph. "Batch" if independent jobs. "Container" if container/pod scheduling |
| task_dependencies | Enum: Y/N | Whether tasks have dependencies | "Y" if paper models precedence constraints or DAG edges |
| dynamic_workload | Enum: Dynamic/Static/Unknown | Whether workload arrives over time | "Dynamic" if paper mentions online scheduling, arrival rates, dynamic environment. "Static" if all tasks known at scheduling time |

## 4. Mapping and Scheduling

| Field | Type | Description | Coding Rule |
|-------|------|-------------|-------------|
| addresses_mapping | Enum: Y/N/Unknown | Whether paper optimizes task-to-resource assignment | "Y" if paper explicitly decides which processor handles which task as part of the optimization |
| addresses_scheduling | Enum: Y/N/Unknown | Whether paper optimizes execution ordering/timing | "Y" if paper determines start times, priority ordering, or execution sequence |
| mapping_scheduling | Enum: Joint/Scheduling-only/Mapping-only | Combined classification | "Joint" if both mapping and scheduling are optimized together. "Scheduling-only" if mapping is implicit (e.g., HEFT assigns tasks to processors as part of scheduling but the paper frames it as scheduling) |

**Important note on mapping_scheduling coding:** Many list-scheduling algorithms (HEFT, CPOP) technically perform both mapping and scheduling. We coded based on the paper's **framing**: if the paper presents the contribution as a scheduling algorithm that includes processor selection, we coded "Scheduling-only." Only papers that explicitly formulate mapping as a separate optimization decision or jointly formulate assignment + ordering were coded "Joint."

## 5. Solver Classification

| Field | Type | Description | Coding Rule |
|-------|------|-------------|-------------|
| solver_class | String | Primary optimization method category | Classified using the 4-criterion decision table (Table 2 in paper): Optimality guarantee, Stochastic search, Learning component, Composite. See Section 5.2 of paper |
| specific_method | String | Named algorithms used | Comma-separated list of all specific algorithms mentioned as proposed or evaluated. Detected by keyword matching with manual verification |
| algorithm_strategy | String | High-level strategy description | E.g., "Constructive/Priority", "Population-based", "Learning-based" |
| hybrid_approach | Enum: Y/N | Whether paper combines multiple solver classes | "Y" if paper explicitly combines methods from different solver classes (e.g., HEFT + GA) |

**Solver class decision rules:**
- **Exact**: Paper formulates and solves a mathematical program (MILP, CP, B&B, DP) with optimality guarantee
- **Heuristic**: Paper proposes/uses a deterministic, polynomial-time constructive method (list scheduling, greedy, clustering) without stochastic search
- **Metaheuristic**: Paper uses a stochastic population-based or trajectory-based search (GA, PSO, ACO, DE, SA, etc.) without a learning component
- **ML/AI**: Paper's primary contribution involves learning from data/experience (RL, DRL, GNN, supervised learning, hyper-heuristics with learned selection)
- **Hybrid**: Paper explicitly combines methods from two or more of the above classes as its primary contribution

## 6. Objectives

**Coding rule for all objective fields:** A paper is coded "Y" for an objective if it **addresses** that objective in its problem formulation, objective function, or evaluation metrics. This includes papers that optimize the objective directly AND papers that evaluate it as a performance metric. Papers that merely mention the term in related work or motivation without formulating or measuring it are coded empty.

| Field | Type | Description |
|-------|------|-------------|
| makespan | Y/empty | Minimizes total completion time (Cmax) |
| utilization | Y/empty | Maximizes resource utilization or efficiency |
| energy | Y/empty | Minimizes energy consumption, power, or carbon |
| cost | Y/empty | Minimizes monetary cost (cloud pricing, budget) |
| load_balance | Y/empty | Balances workload across resources |
| throughput | Y/empty | Maximizes jobs/tasks per unit time |
| latency | Y/empty | Minimizes response time or turnaround time |
| deadline | Y/empty | Meets deadline/SLA/QoS constraints |
| reliability | Y/empty | Maximizes reliability, fault tolerance, availability |
| security | Y/empty | Addresses security, privacy, or trust |
| single_multi_obj | Enum: Single/Multi | Whether paper uses single or multi-objective formulation |

**Caveat:** These frequencies reflect "addresses" not exclusively "optimizes as primary objective function." A stricter coding limited to papers with explicit objective function terms would yield lower frequencies. See paper Section VI-C for discussion.

## 7. Constraints

**Coding rule:** A constraint is coded "Y" only if the paper **explicitly formulates it as a named constraint** in the mathematical model or algorithm description. Constraints that are inherent to the problem structure (e.g., precedence in DAG scheduling) but not explicitly named are NOT coded.

| Field | Type | Description |
|-------|------|-------------|
| assignment | Y/empty | Assignment uniqueness: each task assigned to exactly one processor |
| capacity | Y/empty | Resource capacity limits (CPU, memory, bandwidth, cores) |
| feature | Y/empty | Feature/type compatibility (task requires specific hardware type) |
| precedence | Y/empty | Precedence ordering explicitly formulated as constraint |
| communication | Y/empty | Communication/data transfer cost between processors |

**Important note on precedence:** The low frequency (3.4%) appears to contradict DAG dominance (87.1%). Most DAG scheduling papers enforce precedence implicitly through topological ordering or ready-list construction. We coded precedence "Y" only when the paper formulated it as a named mathematical constraint (e.g., "subject to: s_j >= s_i + w_i for all (i,j) in E"). See paper Section VI-D for discussion.

## 8. Evaluation

| Field | Type | Description | Coding Rule |
|-------|------|-------------|-------------|
| max_tasks | Integer/empty | Maximum number of tasks evaluated | Largest task count in any experiment |
| max_resources | Integer/empty | Maximum number of processors/resources | Largest resource count |
| eval_type | String | Evaluation methodology | "Simulation" = simulated environment. "Real-system" = actual hardware. "Trace-based" = real workload traces. Combinations joined by "/" |
| benchmark | String | Named benchmarks used | E.g., "Montage, CyberShake, Random DAG, CloudSim" |
| baselines | String | Comparison algorithms | Named algorithms compared against |
| reproducible | Y/N/empty | Whether code/data are shared | "Y" only if paper provides link to code/data |

## 9. Extraction Metadata

| Field | Type | Description |
|-------|------|-------------|
| extraction_source | String | How data was extracted | "full-text" = from complete PDF with page references. "title-only" / "partial-abstract" / "abstract-pdf" = limited extraction |
| confidence | Enum: high/medium/low | Confidence in extraction accuracy | "high" = full-text with 8+ pages read. "medium" = 4-7 pages. "low" = abstract only |
| abstract_length | Integer | Character count of available abstract | |
| abstract_preview | String | First ~200 characters of abstract | For quick reference |

## Extraction Process

1. **Automated extraction**: PyMuPDF-based text extraction from PDFs, followed by keyword pattern matching for each field (see `scripts/extract_all_papers.py`)
2. **Pattern matching**: Regular expressions matched against full text with page-number tracking (see `data/SLR_Extracted_From_PDFs.json` for page references)
3. **Manual verification**: First author verified automated extraction for each paper, correcting misclassifications
4. **Deduplication**: Title similarity matching (SequenceMatcher, threshold 0.8) identified and removed 2 duplicate entries

## Version History

| Date | Change |
|------|--------|
| 2026-04-03 | Initial extraction (147 papers) |
| 2026-04-03 | Deduplication: removed 2 duplicates (145 papers) |
| 2026-04-04 | Verification script created, 2 number mismatches corrected |
