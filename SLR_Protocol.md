# Systematic Literature Review Protocol

## Title
"Tools and Techniques for Optimization of Workload Mapping and Scheduling in Heterogeneous HPC Systems: A Systematic Literature Review"

## Authors
Aasish Kumar Sharma, Julian Kunkel

## Thesis Context
PhD thesis: "Optimization of Workload Mapping and Scheduling in Heterogeneous HPC Landscape"
This SLR is the foundation chapter - identifying what tools and techniques the community uses.

---

## 1. Research Questions

**RQ1:** What optimization techniques are used for workload mapping and scheduling in heterogeneous HPC systems, and how are they classified?
- Sub: What solver classes (exact, heuristic, metaheuristic, ML/AI, quantum-inspired)?
- Sub: What specific algorithms within each class?

**RQ2:** What objectives and performance metrics are targeted?
- Sub: Which papers optimize for makespan, resource utilization, energy, cost, etc.?
- Sub: Single-objective vs multi-objective approaches?

**RQ3:** What problem characteristics and constraints are addressed?
- Sub: System heterogeneity (CPU, GPU, FPGA, cloud, edge)?
- Sub: Workflow structure (DAG, dependencies, data transfer)?
- Sub: Constraints (capacity, features, deadlines, communication)?

**RQ4:** What is the state of experimental evaluation?
- Sub: Problem sizes tested (max tasks, max resources)?
- Sub: Evaluation method (simulation, real system, synthetic)?
- Sub: Reproducibility (open source, benchmarks used)?

**RQ5:** What are the open challenges and research gaps?

---

## 2. Search Strategy

### 2.1 Databases
- Google Scholar (primary)
- Semantic Scholar (supplementary)
- IEEE Xplore, ACM DL, Springer, Elsevier (via Google Scholar)

### 2.2 Search Queries
- Q1: "workload mapping" AND "scheduling" AND "heterogeneous" AND "HPC"
- Q2: "task scheduling" AND "heterogeneous computing" AND "optimization"
- Q3: "workflow scheduling" AND "HPC" AND ("MILP" OR "heuristic" OR "metaheuristic" OR "machine learning")
- Q4: "DAG scheduling" AND "heterogeneous" AND ("makespan" OR "resource utilization")
- Q5: "quantum" AND "scheduling" AND "QUBO" OR "quantum annealing"

### 2.3 Time Range
2017 to 2025 (9 years)

### 2.4 Snowballing
Forward and backward from seed papers (124 seeds identified)

---

## 3. Inclusion/Exclusion Criteria

### Inclusion
- IC1: Proposes or evaluates an optimization method for task/workflow mapping or scheduling
- IC2: Targets heterogeneous compute resources (HPC, cloud+HPC, edge+cloud, multi-architecture)
- IC3: Published in peer-reviewed venue (journal, conference, workshop) or significant arXiv preprint
- IC4: Published 2017-2025
- IC5: Written in English
- IC6: Reports quantitative evaluation (not purely theoretical)

### Exclusion
- EC1: Pure survey/review papers (used as related work only)
- EC2: Focuses exclusively on homogeneous systems
- EC3: Focuses on container orchestration only (no scheduling optimization)
- EC4: Focuses on network scheduling without compute resource mapping
- EC5: Poster-only or abstract-only publications
- EC6: Duplicate or superseded version of same work

---

## 4. Data Extraction Form

### 4.1 Bibliographic Data
| Field | Description |
|-------|-------------|
| paper_id | Unique identifier |
| title | Paper title |
| authors | Author list |
| year | Publication year |
| venue | Journal/Conference name |
| venue_type | Journal / Conference / Workshop / ArXiv |
| doi | DOI if available |

### 4.2 System Characteristics
| Field | Values | Description |
|-------|--------|-------------|
| system_scope | HPC / Cloud / Edge / Hybrid / IoT | Target computing environment |
| heterogeneity_type | Homo / Hetero / Both | Homogeneous or heterogeneous resources |
| resource_types | CPU, GPU, FPGA, TPU, etc. | Types of compute resources considered |
| network_aware | Yes / No | Considers network/communication costs |
| data_transfer_aware | Yes / No | Considers data transfer between nodes |

### 4.3 Workload Characteristics
| Field | Values | Description |
|-------|--------|-------------|
| workload_type | Independent / DAG / Workflow / Bag-of-tasks | Task dependency structure |
| task_dependencies | Yes / No | Has precedence constraints |
| dynamic_workload | Static / Dynamic / Both | Workload arrival pattern |
| real_world_workload | Yes / No | Uses real HPC/cloud traces |

### 4.4 Constraint Types (checkmark columns, like Ahmad et al.)
| Constraint | Yes/No |
|------------|--------|
| assignment_uniqueness | Each task to exactly one resource |
| capacity_limits | Resource capacity constraints (CPU, memory) |
| feature_compatibility | Task-resource feature matching |
| precedence_ordering | Task dependency/ordering |
| communication_cost | Inter-node data transfer |
| deadline_slo | Time deadlines or SLOs |
| energy_power | Energy/power constraints |
| budget_cost | Monetary cost constraints |
| fault_tolerance | Reliability/fault tolerance |
| security | Security constraints |

### 4.5 Objectives (checkmark columns, following Ahmad et al. Tables 1-4)
| Objective | Yes/No | Description |
|-----------|--------|-------------|
| makespan | | Minimize total completion time |
| resource_utilization | | Maximize resource usage efficiency |
| energy | | Minimize energy consumption |
| cost | | Minimize monetary cost |
| load_balancing | | Balance load across resources |
| throughput | | Maximize throughput |
| availability | | Maximize system availability |
| scalability | | Scalability consideration |
| network_bandwidth | | Network optimization |
| latency | | Minimize response time/latency |
| carbon_footprint | | Environmental impact |
| fairness | | Fair resource allocation |
| single_vs_multi | Single / Multi | Single or multi-objective |

### 4.5b Problem Decomposition (Mapping vs Scheduling)
| Field | Values | Description |
|-------|--------|-------------|
| addresses_mapping | Yes / No | Optimizes task-to-resource assignment |
| addresses_scheduling | Yes / No | Optimizes execution order/timing |
| mapping_and_scheduling | Joint / Separate / Mapping-only / Scheduling-only | How mapping and scheduling are treated |
| mapping_approach | Optimization / Heuristic / Learning / Quantum | How mapping is solved |
| scheduling_approach | List-scheduling / CP / Priority-based / Decoder / N/A | How scheduling is derived |
| decoupled | Yes / No | Are mapping and scheduling solved separately? |

### 4.6 Solution Approach (key classification)
| Field | Values | Description |
|-------|--------|-------------|
| solver_class | Exact / Heuristic / Metaheuristic / ML-AI / Hybrid / Quantum-inspired | Primary category (following Ahmad et al.) |
| specific_method | e.g., MILP, CP-SAT, HEFT, GA, PSO, ACO, RL, GNN, QUBO-SA | Specific algorithm/technique |
| algorithm_strategy | Exact / Greedy / Population-based / Trajectory-based / Learning-based / Quantum | Strategy type |
| problem_formulation | ILP/MILP / CP / Graph / QUBO / RL-MDP / Other | Mathematical formulation |
| hybrid_approach | Yes / No | Combines multiple techniques |
| hybrid_details | text | If hybrid, which techniques combined |

### 4.7 Evaluation Details
| Field | Values | Description |
|-------|--------|-------------|
| max_tasks_tested | number | Largest problem size (tasks) |
| max_resources_tested | number | Largest system size (nodes/machines) |
| evaluation_type | Simulation / Real-system / Both / Analytical | How evaluated |
| benchmark_used | text | Which benchmarks (if any) |
| comparison_baselines | text | What methods compared against |
| reproducible | Yes / Partial / No | Code/data available |
| tool_framework | text | e.g., Docker, Kubernetes, Slurm, CloudSim |

### 4.8 Quality Assessment
| Field | Values | Description |
|-------|--------|-------------|
| strengths | text | Key strengths (2-3 bullet points, like Ahmad et al.) |
| limitations | text | Key limitations (2-3 bullet points, like Ahmad et al.) |
| key_contribution | text | Main contribution in one sentence |

---

## 5. Quality Assessment Criteria (for included papers)

Score each paper 0-1 on:
1. Is the research objective clearly stated?
2. Is the optimization method adequately described?
3. Is the experimental evaluation rigorous?
4. Are the results compared to appropriate baselines?
5. Are limitations discussed?

Total quality score: 0-5. Include papers scoring >= 2.

---

## 6. Paper Structure (Target)

1. Introduction (motivation, scope, contributions)
2. Review Methodology (PRISMA, search strategy, inclusion/exclusion)
3. Background (HPC scheduling fundamentals, problem formulation, metrics)
4. Classification Framework (taxonomy diagram)
5. Exact Methods (MILP, CP-SAT, etc.) with summary table
6. Heuristic Methods (HEFT, list scheduling, etc.) with summary table
7. Metaheuristic Methods (GA, PSO, ACO, etc.) with summary table
8. ML/AI Methods (RL, GNN, DL, etc.) with summary table
9. Quantum-Inspired Methods (QUBO, VQE, QAOA) with summary table
10. Hybrid Methods with summary table
11. Cross-cutting Analysis (objectives, constraints, scalability, trends)
12. Open Challenges and Research Directions
13. Conclusion

---

## 7. Summary Tables Format (Following Ahmad et al.)

Each solver class gets a table with columns:

| Reference | Energy | Utilization | Load Bal. | Makespan | Cost | Network | System Type | Strengths | Limitations |

Plus our additional HPC-specific columns:
| Max Tasks | Max Nodes | Has Dependencies | Communication-Aware | Tool/Framework |

---

## 8. Expected Figures

1. PRISMA flow diagram
2. Taxonomy tree (solver classes and subtypes)
3. Publication trend by year
4. Distribution by solver class (pie/bar chart)
5. Objectives frequency analysis
6. Constraint coverage heatmap
7. Scalability scatter plot (max tasks vs year)
8. Venue distribution
9. Comparison matrix: solver class vs objectives
10. Research gaps visualization

---

## 9. Target Venues for Resubmission

1. Future Generation Computer Systems (Elsevier, IF ~7.5)
2. Journal of Systems and Software (Elsevier, IF ~3.5)
3. Computing Surveys (ACM, IF ~16, if expanded significantly)
4. Parallel Computing (Elsevier, IF ~2.2)
5. Journal of Parallel and Distributed Computing (Elsevier, IF ~3.4)
