# SLR Data Extraction Log
## Traceable extraction from downloaded papers

Each entry records: paper ID, extraction date, decision, and specific page/section references.

---

### Paper 1: Fan (2021) - "Job Scheduling in High Performance Computing"
- **File:** 2021_Job_scheduling_in_high_performance_computing.pdf
- **Authors:** Yuping Fan, Illinois Institute of Technology
- **Source:** arXiv:2109.09269
- **Year:** 2021
- **Decision:** RECLASSIFY as related_survey (not primary research)
- **Reason:** This is a review/survey chapter, not a paper proposing a specific optimization method. It reviews existing HPC scheduling approaches (FCFS, backfilling, EASY/conservative, hierarchical, distributed, multi-resource, energy-aware, workflow scheduling) and proposes a high-level framework (Section III, p.4-5) but does not implement or evaluate any specific algorithm.
- **Evidence:**
  - Abstract (p.1): "we have investigated challenges faced by HPC scheduling and state-of-art scheduling methods to overcome these challenges"
  - Section II (p.1-4): Reviews existing algorithms (FCFS, backfilling, hierarchical, distributed, multi-resource, energy-aware, workflow)
  - Section III (p.4-5): Proposes framework with 4 components (resource manager, job manager, scheduling decision maker, performance monitor) but no implementation or evaluation
  - No experimental results, no quantitative comparison
- **Useful for SLR:** Yes, as a reference for HPC scheduling taxonomy and challenges (Section II covers 8 subcategories)
- **Key topics covered:** FCFS, backfilling (EASY/conservative), hierarchical scheduling (Flux), distributed scheduling, multi-resource scheduling (DRF), energy-aware (DVFS), checkpoint/restart, moldable/malleable jobs, workflow scheduling (DAG)

---

### Paper 2: Prongnuch et al. (2020) - "A Heuristic Approach for Scheduling in Heterogeneous Distributed Embedded Systems"
- **File:** 2020_A_heuristic_approach_for_scheduling_in_heterogeneous_distrib.pdf
- **Authors:** Sethakarn Prongnuch, Suchada Sitjongsataporn, Theerayod Wiangtong
- **Venue:** International Journal of Intelligent Engineering and Systems, Vol.13, No.1, 2020
- **DOI:** 10.22266/ijies.2020.0229.13
- **Decision:** INCLUDE
- **Year:** 2020

#### Bibliographic
- Venue type: Journal
- Affiliation: Mahanakorn Univ. of Technology + King Mongkut's IT, Bangkok, Thailand

#### System Characteristics
- **system_scope:** HPC/Embedded (heterogeneous distributed embedded system - HDES)
  - Source: Abstract p.135 "heterogeneous distributed embedded system (HDES)"
- **heterogeneity:** Hetero
  - Source: p.137 Section 3.1 "N heterogeneous embedded machines (HEMs)" with GPP, coprocessor, hardware accelerator per machine
- **resource_types:** CPU (GPP), Coprocessor (Epiphany 16-core), Hardware Accelerator (FPGA)
  - Source: p.138 Section 3.2, p.137 Fig.1 shows GPP, CO-PRO, HW-ACC per HEM
- **network_aware:** Yes
  - Source: p.139 Section 3.4 "Communication time, which is a product of data and bus speed, depends on the types of buses" (GPP bus, CO bus, HW bus, EX bus, NET bus)
- **data_transfer_aware:** Yes
  - Source: p.138 Fig.3 shows edges with communication weights (5, 10, 15 bytes)

#### Workload Characteristics
- **workload_type:** Workflow/DAG
  - Source: p.138 Section 3.4 "data-dominated application with nine tasks... modeled in directed acyclic graphs (DAGs)"
- **task_dependencies:** Yes
  - Source: p.138 Fig.3 shows 9-task DAG with precedence edges
- **dynamic_workload:** Static
- **real_world_workload:** No (random task graphs)
  - Source: p.143 Section 5.2 "DAGs random task graphs are randomly generated"

#### Constraints
- **assignment_uniqueness:** Yes (implicit - each task assigned to one processor)
- **capacity_limits:** Yes
  - Source: p.140 Algorithm 1 "Constraint" checks N_cores <= Max_cores and Per_logic
- **feature_compatibility:** Yes (implicit - tasks map to compatible processor types GPP/COPRO/HWACC)
- **precedence_ordering:** Yes
  - Source: p.138 "directed edge e(i,j) represents dependency constraint"
- **communication_cost:** Yes
  - Source: p.139 Eq.3-4 "t_com(d_i) is the data communication dependencies between tasks"
- **deadline_slo:** No
- **energy_power:** No

#### Objectives (following Ahmad et al. table format)
- **makespan:** Y
  - Source: p.139 Eq.1-2 "makespan = AFT(v_exit)" and "objective function... to be minimized"
- **resource_utilization:** N
- **energy:** N
- **cost:** N
- **load_balancing:** N
- **throughput:** N
- **latency:** N
- **single_vs_multi:** Single (minimize makespan only)

#### Solution Approach
- **solver_class:** Metaheuristic
- **specific_methods:** GA, ACO, MGGA (Modified Greedy GA), MGACO (Modified Greedy ACO), GSA (Genetic Simulated Annealing)
  - Source: p.140 Section 4 "four meta-heuristic algorithms: genetic algorithm (GA), ant colony optimization algorithm (ACO), modified greedy genetic algorithm (MGGA), and modified greedy ant colony optimization algorithm (MGACO)"
- **algorithm_strategy:** Population-based (GA, ACO) + Greedy hybrid
- **problem_formulation:** DAG scheduling with computation matrix MAT
  - Source: p.140 Eq.5 "computation matrix MAT stores the execution time of tasks V running on HEM M"
- **hybrid_approach:** Yes (greedy step added to GA and ACO)
  - Source: p.141 Section 4.2 "MGGA is similar to the GA, but one greedy step is added on" and Algorithm 2
- **addresses_mapping:** Y (task-to-processor assignment)
- **addresses_scheduling:** Y (schedule with precedence and communication)
- **mapping_and_scheduling:** Joint

#### Evaluation
- **max_tasks_tested:** 500
  - Source: p.143 Section 5.2 "number of task nodes in a DAG is {10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400, 500}"
- **max_resources_tested:** 9 HEMs (each with 3 processor types = 27 processing elements)
  - Source: p.142-143 Section 5.1 "nine of the Parallella boards" Fig.7
- **evaluation_type:** Real-system (actual Parallella cluster)
  - Source: p.142 Section 5.1 actual hardware setup with 9 Parallella boards, D-Link switch
- **benchmark_used:** Random DAG generator with varying parameters
  - Source: p.143 Section 5.2 CCR ratios, heterogeneity factors, parallelism degrees
- **comparison_baselines:** GA, ACO, GSA (GA+SA hybrid), MGGA, MGACO
- **reproducible:** Partial (algorithms described but code not shared)
- **tool_framework:** C/C++ with GCC/G++ on Parallella (Parabuntu Linux)
  - Source: p.143 "All algorithms are written in C/C++, complied by GCC/G++"
- **metrics_used:** Makespan, SLR (Schedule Length Ratio, Eq.6), Speedup (Eq.7)
  - Source: p.140 Eq.6-7

#### Quality Assessment
- **strengths:**
  - Real hardware evaluation on actual heterogeneous embedded cluster (9 Parallella boards)
  - Communication-aware scheduling considering 5 bus types
  - Greedy enhancement improves metaheuristics by 33%
  - Source: p.144 "MGACO outperforms... by 33% more result quality"
- **limitations:**
  - No comparison with exact methods (MILP, CP-SAT) or classical heuristics (HEFT)
  - No energy optimization despite embedded context
  - Only static DAGs, no dynamic workloads
  - Specific to embedded systems, limited generalizability to HPC clusters

#### Key Numbers
- MGACO avg makespan: 240 min (best), ACO: 247, GSA: 251, MGGA: 259, GA: 266
  - Source: p.144 "average makespan of MGACO is 240 minutes"
- MGACO improves speedup by 30% for small graphs, 33% at 80 tasks
  - Source: p.144 "MGACO improves speedup by 30 percent for a small graph size"

---

### Paper 3: [TO BE EXTRACTED]
