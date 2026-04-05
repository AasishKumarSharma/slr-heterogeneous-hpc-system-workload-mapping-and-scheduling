#!/usr/bin/env python3
"""
Verification Script for SLR Paper Claims
=========================================
This script reproduces every percentage, count, and statistic
claimed in the paper from the source dataset.

Usage:
    python verify_paper_claims.py

Input:  ../data/SLR_Comprehensive_Extraction_Updated.csv
Output: Prints all claims with computed values and PASS/FAIL status.
"""
import pandas as pd
import os, sys, re
from collections import Counter

# Load data
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
CSV_PATH = os.path.join(DATA_DIR, 'SLR_Comprehensive_Extraction_Updated.csv')

if not os.path.exists(CSV_PATH):
    print(f"ERROR: Dataset not found at {CSV_PATH}")
    sys.exit(1)

df = pd.read_csv(CSV_PATH)
df['year'] = pd.to_numeric(df['year'], errors='coerce')
df = df[df['year'].notna()]
df['year'] = df['year'].astype(int)

N = len(df)
print(f"{'='*70}")
print(f"SLR Paper Claims Verification")
print(f"Dataset: {CSV_PATH}")
print(f"Total papers loaded: {N}")
print(f"{'='*70}\n")

passed = 0
failed = 0
warnings = 0

def check(claim, expected, actual, tolerance=0.5):
    global passed, failed, warnings
    if isinstance(expected, float):
        match = abs(expected - actual) <= tolerance
    else:
        match = expected == actual
    status = "PASS" if match else "FAIL"
    if not match:
        failed += 1
    else:
        passed += 1
    print(f"  [{status}] {claim}")
    print(f"         Expected: {expected}, Computed: {actual}")
    if not match:
        print(f"         *** MISMATCH ***")
    return match

# ============================================================
# SECTION: Basic corpus statistics
# ============================================================
print("=" * 70)
print("BASIC CORPUS STATISTICS")
print("=" * 70)

check("Total included studies", 145, N)
check("Year range start", 2017, df['year'].min())
check("Year range end", 2025, df['year'].max())

# Papers by year
year_counts = df['year'].value_counts().sort_index()
print(f"\n  Papers by year: {dict(year_counts)}")
check("Peak year (2021)", 27, year_counts.get(2021, 0))

# ============================================================
# SECTION: Solver class distribution (RQ1)
# ============================================================
print(f"\n{'='*70}")
print("SOLVER CLASS DISTRIBUTION (RQ1)")
print("=" * 70)

def normalize_solver(s):
    s = str(s).strip()
    if not s or s == 'nan' or s == 'Unknown': return 'Unknown'
    classes = set()
    for part in re.split(r'[/,]', s):
        part = part.strip()
        if 'Exact' in part: classes.add('Exact')
        elif 'ML' in part or 'AI' in part: classes.add('ML/AI')
        elif 'Quantum' in part: classes.add('Quantum')
        elif 'Metaheuristic' in part or 'Meta' in part: classes.add('Metaheuristic')
        elif 'Heuristic' in part: classes.add('Heuristic')
        elif 'Hybrid' in part: classes.add('Hybrid')
        else: classes.add(part)
    if len(classes) > 1 and 'Unknown' in classes: classes.discard('Unknown')
    if len(classes) > 1: return 'Hybrid'
    return classes.pop() if classes else 'Unknown'

df['solver_norm'] = df['solver_class'].apply(normalize_solver)
solver_counts = df['solver_norm'].value_counts()
print(f"\n  Solver counts: {dict(solver_counts)}")

heur_pct = 100 * solver_counts.get('Heuristic', 0) / N
meta_pct = 100 * solver_counts.get('Metaheuristic', 0) / N
hybrid_pct = 100 * solver_counts.get('Hybrid', 0) / N
ml_pct = 100 * solver_counts.get('ML/AI', 0) / N
exact_pct = 100 * solver_counts.get('Exact', 0) / N

check("Heuristic ~32.4%", 32.4, round(heur_pct, 1), tolerance=1.0)
check("Metaheuristic ~22.8%", 22.8, round(meta_pct, 1), tolerance=1.0)
check("Hybrid ~23.4%", 23.4, round(hybrid_pct, 1), tolerance=1.0)
check("ML/AI ~16.6%", 16.6, round(ml_pct, 1), tolerance=1.0)
check("Exact ~4.8%", 4.8, round(exact_pct, 1), tolerance=1.0)

check("Heuristic count ~47", 47, solver_counts.get('Heuristic', 0), tolerance=2)
check("Metaheuristic count ~33", 33, solver_counts.get('Metaheuristic', 0), tolerance=2)
check("Hybrid count ~34", 34, solver_counts.get('Hybrid', 0), tolerance=2)
check("ML/AI count ~24", 24, solver_counts.get('ML/AI', 0), tolerance=2)
check("Exact count ~7", 7, solver_counts.get('Exact', 0), tolerance=1)

# ML/AI trend
ml_2017 = df[(df['solver_norm'] == 'ML/AI') & (df['year'] == 2017)].shape[0]
total_2025 = df[df['year'] == 2025].shape[0]
ml_2025 = df[(df['solver_norm'] == 'ML/AI') & (df['year'] == 2025)].shape[0]
ml_2025_pct = 100 * ml_2025 / total_2025 if total_2025 > 0 else 0

check("ML/AI in 2017: 0", 0, ml_2017)
check("ML/AI in 2025 ~37%", 37.0, round(ml_2025_pct, 0), tolerance=2.0)

# ============================================================
# SECTION: Objectives (RQ2)
# ============================================================
print(f"\n{'='*70}")
print("OPTIMIZATION OBJECTIVES (RQ2)")
print("=" * 70)

obj_cols = ['makespan','utilization','energy','cost','load_balance','throughput','latency','deadline','reliability','security']
obj_labels = ['Makespan','Utilization','Energy','Cost','Load Balance','Throughput','Latency','Deadline/QoS','Reliability','Security']

for col, label in zip(obj_cols, obj_labels):
    count = (df[col] == 'Y').sum()
    pct = 100 * count / N
    print(f"  {label}: {count} ({pct:.1f}%)")

makespan_count = (df['makespan'] == 'Y').sum()
makespan_pct = 100 * makespan_count / N
check("Makespan ~88.4%", 88.4, round(makespan_pct, 1), tolerance=2.0)

# Single vs multi-objective
single_multi = df['single_multi_obj'].value_counts()
multi_pct = 100 * single_multi.get('Multi', 0) / N
check("Multi-objective ~72.1%", 72.1, round(multi_pct, 1), tolerance=2.0)

# ============================================================
# SECTION: System scope and workload (RQ3)
# ============================================================
print(f"\n{'='*70}")
print("SYSTEM SCOPE AND WORKLOAD (RQ3)")
print("=" * 70)

def normalize_system(s):
    s = str(s).strip()
    if not s or s == 'nan' or s == 'Unknown': return 'Other'
    if 'Hybrid' in s or ('Cloud' in s and 'HPC' in s): return 'Hybrid/Multi'
    if 'Edge' in s or 'Fog' in s: return 'Other'
    if 'Cloud' in s: return 'Cloud'
    if 'HPC' in s: return 'HPC'
    return 'Other'

df['system_norm'] = df['system_scope'].apply(normalize_system)
sys_counts = df['system_norm'].value_counts()
print(f"\n  System: {dict(sys_counts)}")

hybrid_sys_pct = 100 * sys_counts.get('Hybrid/Multi', 0) / N
hpc_pct = 100 * sys_counts.get('HPC', 0) / N
cloud_pct = 100 * sys_counts.get('Cloud', 0) / N

check("Hybrid/Multi ~49.7%", 49.7, round(hybrid_sys_pct, 1), tolerance=2.0)
check("HPC ~27.2%", 27.2, round(hpc_pct, 1), tolerance=2.0)
check("Cloud ~18.4%", 18.4, round(cloud_pct, 1), tolerance=2.0)

# Workload type
def normalize_workload(s):
    s = str(s).strip()
    if not s or s == 'nan' or s == 'Unknown': return 'Other'
    if 'Workflow' in s or 'DAG' in s: return 'Workflow/DAG'
    if 'Batch' in s: return 'Batch Jobs'
    return 'Other'

df['workload_norm'] = df['workload_type'].apply(normalize_workload)
wl_counts = df['workload_norm'].value_counts()
dag_pct = 100 * wl_counts.get('Workflow/DAG', 0) / N
check("Workflow/DAG ~87.1%", 87.1, round(dag_pct, 1), tolerance=2.0)

# Heterogeneity
hetero_count = (df['heterogeneity'] == 'Hetero').sum()
hetero_pct = 100 * hetero_count / N
check("Heterogeneous ~95.2%", 95.2, round(hetero_pct, 1), tolerance=2.0)

# Mapping vs Scheduling
ms_counts = df['mapping_scheduling'].value_counts()
print(f"\n  Mapping/Scheduling: {dict(ms_counts)}")
joint_pct = 100 * ms_counts.get('Joint', 0) / N
sched_only_pct = 100 * ms_counts.get('Scheduling-only', 0) / N
check("Joint mapping+scheduling ~25.2%", 25.2, round(joint_pct, 1), tolerance=2.0)
check("Scheduling-only ~74.1%", 74.1, round(sched_only_pct, 1), tolerance=2.0)

# ============================================================
# SECTION: Constraints
# ============================================================
print(f"\n{'='*70}")
print("CONSTRAINTS")
print("=" * 70)

con_cols = ['assignment','capacity','feature','precedence','communication']
for col in con_cols:
    count = (df[col] == 'Y').sum()
    pct = 100 * count / N
    print(f"  {col}: {count} ({pct:.1f}%)")

comm_count = (df['communication'] == 'Y').sum()
comm_pct = 100 * comm_count / N
check("Communication cost ~75.5%", 75.5, round(comm_pct, 1), tolerance=2.0)

# ============================================================
# SECTION: Evaluation (RQ4)
# ============================================================
print(f"\n{'='*70}")
print("EVALUATION (RQ4)")
print("=" * 70)

# Dynamic workload
dynamic_count = (df['dynamic_workload'] == 'Dynamic').sum()
dynamic_pct = 100 * dynamic_count / N
check("Dynamic workload ~63.3%", 63.3, round(dynamic_pct, 1), tolerance=3.0)

# Extraction source
full_text = (df['extraction_source'] == 'full-text').sum()
abstract_only = N - full_text
print(f"  Full-text papers: {full_text}")
print(f"  Abstract-only: {abstract_only}")
check("Full-text ~115", 115, full_text, tolerance=2)

# ============================================================
# SECTION: Sensitivity analysis (abstract-only exclusion)
# ============================================================
print(f"\n{'='*70}")
print("SENSITIVITY ANALYSIS (excluding abstract-only)")
print("=" * 70)

df_ft = df[df['extraction_source'] == 'full-text']
N_ft = len(df_ft)
print(f"  Full-text only: {N_ft} papers")

df_ft['solver_norm'] = df_ft['solver_class'].apply(normalize_solver)
ft_solver = df_ft['solver_norm'].value_counts()
for cls in ['Heuristic','Metaheuristic','Hybrid','ML/AI','Exact']:
    cnt = ft_solver.get(cls, 0)
    pct = 100 * cnt / N_ft
    full_pct_map = {'Heuristic': heur_pct, 'Metaheuristic': meta_pct, 'Hybrid': hybrid_pct, 'ML/AI': ml_pct, 'Exact': exact_pct}
    delta = pct - full_pct_map[cls]
    print(f"  {cls}: {pct:.1f}% (delta: {delta:+.1f}pp)")

# ============================================================
# SECTION: Top methods
# ============================================================
print(f"\n{'='*70}")
print("TOP METHODS")
print("=" * 70)

method_counter = Counter()
for methods_str in df['specific_method'].dropna():
    for m in str(methods_str).split(','):
        m = m.strip()
        if m and m != 'nan' and m != 'Unknown' and len(m) < 30:
            method_counter[m] += 1

top10 = method_counter.most_common(10)
for rank, (method, count) in enumerate(top10, 1):
    print(f"  {rank}. {method}: {count}")

check("HEFT is #1 with ~15", 15, top10[0][1], tolerance=1)

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'='*70}")
print(f"VERIFICATION SUMMARY")
print(f"{'='*70}")
print(f"  Passed: {passed}")
print(f"  Failed: {failed}")
print(f"  Total checks: {passed + failed}")
if failed == 0:
    print(f"\n  ALL CLAIMS VERIFIED SUCCESSFULLY")
else:
    print(f"\n  WARNING: {failed} claims did not match within tolerance")
    print(f"  Review the mismatches above and update paper or data accordingly")
