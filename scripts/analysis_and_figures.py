#!/usr/bin/env python3
"""
SLR Analysis and Figure Generation
Produces all figures and tables for the survey paper.
"""
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from collections import Counter, defaultdict
import os, re, json

# Setup
BASE = "/home/aasish/Documents/PhD/Others/claude/Papers/ETL_ReviewPapers"
FIG_DIR = os.path.join(BASE, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

plt.rcParams.update({
    'font.size': 10,
    'axes.titlesize': 11,
    'axes.labelsize': 10,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 8,
    'figure.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1,
})

# Load data
df = pd.read_csv(os.path.join(BASE, 'SLR_Comprehensive_Extraction_Updated.csv'))
print(f"Loaded {len(df)} papers")

# Clean year column
df['year'] = pd.to_numeric(df['year'], errors='coerce')
df = df[df['year'].notna()]
df['year'] = df['year'].astype(int)
print(f"After year cleaning: {len(df)} papers, years: {df['year'].min()}-{df['year'].max()}")

# ============================================================
# FIGURE 1: PRISMA Flow Diagram (text-based, will be TikZ in paper)
# ============================================================
print("\n--- Figure 1: PRISMA Flow (generating data) ---")
prisma_data = {
    'identified': 309,
    'snowball_candidates': 2313,
    'total_screened': 309,
    'excluded_screening': 309 - 147 - 14,
    'surveys_identified': 14,
    'included': 147,
    'full_text_available': int((df['extraction_source'] == 'full-text').sum()) + 1,
    'abstract_only': int((df['extraction_source'].isin(['title-only','partial-abstract','title+abstract','title'])).sum()),
}
print(f"PRISMA data: {prisma_data}")

# ============================================================
# FIGURE 2: Publication Trend by Year
# ============================================================
print("\n--- Figure 2: Publication Trend ---")
year_counts = df['year'].value_counts().sort_index()
fig, ax = plt.subplots(figsize=(8, 4))
colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(year_counts)))
bars = ax.bar(year_counts.index, year_counts.values, color=colors, edgecolor='black', linewidth=0.5)
for bar, val in zip(bars, year_counts.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, str(val),
            ha='center', va='bottom', fontsize=9, fontweight='bold')
ax.set_xlabel('Publication Year')
ax.set_ylabel('Number of Papers')
ax.set_title('Distribution of Included Studies by Year (N=147)')
ax.set_xticks(year_counts.index)
ax.grid(axis='y', alpha=0.3)
plt.savefig(os.path.join(FIG_DIR, 'fig2_publication_trend.pdf'))
plt.savefig(os.path.join(FIG_DIR, 'fig2_publication_trend.png'))
plt.close()
print(f"  Year distribution: {dict(year_counts)}")

# ============================================================
# FIGURE 3: Solver Class Distribution (Overall + By Year)
# ============================================================
print("\n--- Figure 3: Solver Classification ---")
# Normalize solver classes
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
    if len(classes) > 1:
        return 'Hybrid'
    return classes.pop() if classes else 'Unknown'

df['solver_norm'] = df['solver_class'].apply(normalize_solver)

solver_counts = df['solver_norm'].value_counts()
print(f"  Solver classes: {dict(solver_counts)}")

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Pie chart
colors_map = {
    'Heuristic': '#2196F3', 'Metaheuristic': '#FF9800', 'ML/AI': '#4CAF50',
    'Exact': '#9C27B0', 'Hybrid': '#F44336', 'Quantum': '#00BCD4', 'Unknown': '#9E9E9E'
}
pie_colors = [colors_map.get(c, '#9E9E9E') for c in solver_counts.index]
wedges, texts, autotexts = axes[0].pie(solver_counts.values, labels=solver_counts.index,
    colors=pie_colors, autopct='%1.0f%%', startangle=90, textprops={'fontsize': 9})
axes[0].set_title('(a) Solver Class Distribution')

# Stacked bar by year
solver_year = pd.crosstab(df['year'], df['solver_norm'])
order = ['Exact','Heuristic','Metaheuristic','ML/AI','Hybrid','Quantum','Unknown']
order = [c for c in order if c in solver_year.columns]
solver_year = solver_year[order]
solver_year.plot(kind='bar', stacked=True, ax=axes[1],
    color=[colors_map.get(c, '#9E9E9E') for c in order], edgecolor='black', linewidth=0.3)
axes[1].set_xlabel('Year')
axes[1].set_ylabel('Number of Papers')
axes[1].set_title('(b) Solver Class Evolution Over Time')
axes[1].legend(loc='upper left', fontsize=7)
axes[1].tick_params(axis='x', rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'fig3_solver_classification.pdf'))
plt.savefig(os.path.join(FIG_DIR, 'fig3_solver_classification.png'))
plt.close()

# ============================================================
# FIGURE 4: Objectives Distribution
# ============================================================
print("\n--- Figure 4: Optimization Objectives ---")
obj_cols = ['makespan','utilization','energy','cost','load_balance','throughput','latency','deadline','reliability','security']
obj_labels = ['Makespan','Resource\nUtilization','Energy','Cost','Load\nBalance','Throughput','Latency','Deadline/\nQoS','Reliability','Security']
obj_counts = [(df[col] == 'Y').sum() for col in obj_cols]

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Bar chart
bar_colors = ['#1976D2' if c > 50 else '#42A5F5' if c > 20 else '#90CAF9' for c in obj_counts]
bars = axes[0].barh(range(len(obj_cols)), obj_counts, color=bar_colors, edgecolor='black', linewidth=0.5)
axes[0].set_yticks(range(len(obj_cols)))
axes[0].set_yticklabels(obj_labels)
axes[0].set_xlabel('Number of Papers')
axes[0].set_title(f'(a) Optimization Objectives (N={len(df)})')
for bar, val in zip(bars, obj_counts):
    axes[0].text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                 str(val), va='center', fontsize=9)
axes[0].invert_yaxis()
axes[0].grid(axis='x', alpha=0.3)

# Single vs Multi-objective
single_multi = df['single_multi_obj'].value_counts()
sm_colors = ['#4CAF50', '#FF9800', '#9E9E9E']
axes[1].pie(single_multi.values, labels=single_multi.index,
            colors=sm_colors[:len(single_multi)], autopct='%1.0f%%',
            startangle=90, textprops={'fontsize': 9})
axes[1].set_title('(b) Single vs Multi-Objective')
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'fig4_objectives.pdf'))
plt.savefig(os.path.join(FIG_DIR, 'fig4_objectives.png'))
plt.close()
print(f"  Objectives: {dict(zip(obj_cols, obj_counts))}")
print(f"  Single/Multi: {dict(single_multi)}")

# ============================================================
# FIGURE 5: System Scope and Workload Types
# ============================================================
print("\n--- Figure 5: System Scope and Workload ---")
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# System scope
def normalize_system(s):
    s = str(s).strip()
    if not s or s == 'nan' or s == 'Unknown': return 'Unknown'
    if 'Hybrid' in s or ('Cloud' in s and 'HPC' in s): return 'Hybrid/Multi'
    if 'Edge' in s or 'Fog' in s: return 'Edge/Fog'
    if 'Cloud' in s: return 'Cloud'
    if 'HPC' in s: return 'HPC'
    return 'Other'

df['system_norm'] = df['system_scope'].apply(normalize_system)
sys_counts = df['system_norm'].value_counts()
sys_colors = {'Cloud': '#42A5F5', 'HPC': '#66BB6A', 'Edge/Fog': '#FFA726',
              'Hybrid/Multi': '#AB47BC', 'Other': '#9E9E9E', 'Unknown': '#BDBDBD'}
axes[0].pie(sys_counts.values, labels=sys_counts.index,
    colors=[sys_colors.get(c, '#9E9E9E') for c in sys_counts.index],
    autopct='%1.0f%%', startangle=90, textprops={'fontsize': 9})
axes[0].set_title('(a) System Scope')

# Workload type
def normalize_workload(s):
    s = str(s).strip()
    if not s or s == 'nan' or s == 'Unknown': return 'Unknown'
    if 'Workflow' in s or 'DAG' in s: return 'Workflow/DAG'
    if 'Batch' in s: return 'Batch Jobs'
    if 'Container' in s: return 'Container'
    if 'DNN' in s or 'Training' in s: return 'DNN Training'
    return 'Other'

df['workload_norm'] = df['workload_type'].apply(normalize_workload)
wl_counts = df['workload_norm'].value_counts()
wl_colors = {'Workflow/DAG': '#42A5F5', 'Batch Jobs': '#66BB6A', 'Container': '#FFA726',
             'DNN Training': '#AB47BC', 'Other': '#9E9E9E', 'Unknown': '#BDBDBD'}
axes[1].pie(wl_counts.values, labels=wl_counts.index,
    colors=[wl_colors.get(c, '#9E9E9E') for c in wl_counts.index],
    autopct='%1.0f%%', startangle=90, textprops={'fontsize': 9})
axes[1].set_title('(b) Workload Type')
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'fig5_system_workload.pdf'))
plt.savefig(os.path.join(FIG_DIR, 'fig5_system_workload.png'))
plt.close()
print(f"  System: {dict(sys_counts)}")
print(f"  Workload: {dict(wl_counts)}")

# ============================================================
# FIGURE 6: Constraints Analysis
# ============================================================
print("\n--- Figure 6: Constraints ---")
con_cols = ['assignment','capacity','feature','precedence','communication']
# Handle duplicate column names - the constraint columns
# In the spreadsheet, 'deadline' and 'energy' appear twice (objectives + constraints)
# We need to distinguish them. Let's check the raw data

con_labels = ['Assignment\nUniqueness', 'Resource\nCapacity', 'Feature\nCompatibility',
              'Precedence\nOrdering', 'Communication\nCost']
con_counts = []
for col in con_cols:
    count = (df[col] == 'Y').sum()
    con_counts.append(count)

fig, ax = plt.subplots(figsize=(8, 4))
bar_colors = ['#E91E63' if c > 50 else '#F48FB1' if c > 20 else '#FCE4EC' for c in con_counts]
bars = ax.bar(range(len(con_cols)), con_counts, color=bar_colors, edgecolor='black', linewidth=0.5)
ax.set_xticks(range(len(con_cols)))
ax.set_xticklabels(con_labels, fontsize=8)
ax.set_ylabel('Number of Papers')
ax.set_title(f'Constraints Modeled in Included Studies (N={len(df)})')
for bar, val in zip(bars, con_counts):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, str(val),
            ha='center', fontsize=9, fontweight='bold')
ax.grid(axis='y', alpha=0.3)
plt.savefig(os.path.join(FIG_DIR, 'fig6_constraints.pdf'))
plt.savefig(os.path.join(FIG_DIR, 'fig6_constraints.png'))
plt.close()
print(f"  Constraints: {dict(zip(con_cols, con_counts))}")

# ============================================================
# FIGURE 7: Mapping vs Scheduling Focus
# ============================================================
print("\n--- Figure 7: Mapping vs Scheduling ---")
ms_counts = df['mapping_scheduling'].value_counts()
fig, ax = plt.subplots(figsize=(6, 4))
ms_colors = {'Joint': '#4CAF50', 'Scheduling-only': '#2196F3', 'Mapping-only': '#FF9800',
             'Unknown': '#9E9E9E', 'None': '#BDBDBD'}
colors_list = [ms_colors.get(str(c).strip(), '#9E9E9E') for c in ms_counts.index]
ax.pie(ms_counts.values, labels=ms_counts.index, colors=colors_list,
       autopct='%1.0f%%', startangle=90, textprops={'fontsize': 9})
ax.set_title('Mapping vs Scheduling Focus')
plt.savefig(os.path.join(FIG_DIR, 'fig7_mapping_scheduling.pdf'))
plt.savefig(os.path.join(FIG_DIR, 'fig7_mapping_scheduling.png'))
plt.close()
print(f"  Mapping/Scheduling: {dict(ms_counts)}")

# ============================================================
# FIGURE 8: Specific Methods - Top 20 most used
# ============================================================
print("\n--- Figure 8: Specific Methods ---")
method_counter = Counter()
for methods_str in df['specific_method'].dropna():
    for m in str(methods_str).split(','):
        m = m.strip()
        if m and m != 'nan' and m != 'Unknown' and len(m) < 30:
            method_counter[m] += 1

top_methods = method_counter.most_common(20)
if top_methods:
    fig, ax = plt.subplots(figsize=(10, 6))
    names = [m[0] for m in top_methods]
    counts = [m[1] for m in top_methods]
    y_pos = range(len(names))
    bars = ax.barh(y_pos, counts, color=plt.cm.viridis(np.linspace(0.3, 0.9, len(names))),
                   edgecolor='black', linewidth=0.3)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=8)
    ax.set_xlabel('Frequency')
    ax.set_title('Top 20 Most Frequently Used Methods/Algorithms')
    for bar, val in zip(bars, counts):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                str(val), va='center', fontsize=8)
    ax.invert_yaxis()
    ax.grid(axis='x', alpha=0.3)
    plt.savefig(os.path.join(FIG_DIR, 'fig8_top_methods.pdf'))
    plt.savefig(os.path.join(FIG_DIR, 'fig8_top_methods.png'))
    plt.close()
    print(f"  Top methods: {top_methods[:10]}")

# ============================================================
# FIGURE 9: Evaluation Methods
# ============================================================
print("\n--- Figure 9: Evaluation Methods ---")
def normalize_eval(s):
    s = str(s).strip()
    if not s or s == 'nan' or s == 'Unknown': return 'Unknown'
    types = set()
    if 'Simulat' in s or 'simulat' in s: types.add('Simulation')
    if 'Real' in s or 'real' in s: types.add('Real-system')
    if 'Trace' in s or 'trace' in s: types.add('Trace-based')
    if not types: return 'Unknown'
    return '/'.join(sorted(types))

df['eval_norm'] = df['eval_type'].apply(normalize_eval)
eval_counts = df['eval_norm'].value_counts()
fig, ax = plt.subplots(figsize=(7, 4))
eval_colors = {'Simulation': '#42A5F5', 'Real-system': '#66BB6A', 'Trace-based': '#FFA726',
               'Simulation/Real-system': '#AB47BC', 'Simulation/Trace-based': '#EF5350',
               'Unknown': '#9E9E9E'}
ec = [eval_colors.get(c, '#9E9E9E') for c in eval_counts.index]
bars = ax.bar(range(len(eval_counts)), eval_counts.values, color=ec, edgecolor='black', linewidth=0.5)
ax.set_xticks(range(len(eval_counts)))
ax.set_xticklabels(eval_counts.index, rotation=30, ha='right', fontsize=8)
ax.set_ylabel('Number of Papers')
ax.set_title('Evaluation Methods Used')
for bar, val in zip(bars, eval_counts.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, str(val),
            ha='center', fontsize=9)
ax.grid(axis='y', alpha=0.3)
plt.savefig(os.path.join(FIG_DIR, 'fig9_evaluation.pdf'))
plt.savefig(os.path.join(FIG_DIR, 'fig9_evaluation.png'))
plt.close()
print(f"  Evaluation: {dict(eval_counts)}")

# ============================================================
# FIGURE 10: Scalability - Max Tasks by Solver Class
# ============================================================
print("\n--- Figure 10: Scalability ---")
df['max_tasks_num'] = pd.to_numeric(df['max_tasks'], errors='coerce')
scale_df = df[df['max_tasks_num'].notna() & (df['max_tasks_num'] > 0)]
if len(scale_df) > 10:
    fig, ax = plt.subplots(figsize=(8, 5))
    for solver in ['Heuristic','Metaheuristic','ML/AI','Exact','Hybrid']:
        mask = scale_df['solver_norm'] == solver
        if mask.sum() > 0:
            subset = scale_df[mask]
            ax.scatter(subset['year'], subset['max_tasks_num'],
                      label=f'{solver} (n={mask.sum()})',
                      color=colors_map.get(solver, '#9E9E9E'), alpha=0.7, s=50, edgecolors='black', linewidth=0.3)
    ax.set_xlabel('Publication Year')
    ax.set_ylabel('Max Tasks Evaluated (log scale)')
    ax.set_yscale('log')
    ax.set_title('Scalability: Maximum Problem Size by Solver Class')
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    plt.savefig(os.path.join(FIG_DIR, 'fig10_scalability.pdf'))
    plt.savefig(os.path.join(FIG_DIR, 'fig10_scalability.png'))
    plt.close()
    print(f"  Scalability data: {len(scale_df)} papers with max_tasks data")

# ============================================================
# FIGURE 11: Solver Class vs Objectives Heatmap
# ============================================================
print("\n--- Figure 11: Solver-Objective Heatmap ---")
solver_obj = pd.DataFrame()
for solver in ['Exact','Heuristic','Metaheuristic','ML/AI','Hybrid']:
    mask = df['solver_norm'] == solver
    row = {}
    for obj in obj_cols:
        row[obj] = (df.loc[mask, obj] == 'Y').sum()
    solver_obj[solver] = pd.Series(row)

if not solver_obj.empty:
    fig, ax = plt.subplots(figsize=(10, 5))
    im = ax.imshow(solver_obj.values, cmap='YlOrRd', aspect='auto')
    ax.set_xticks(range(len(solver_obj.columns)))
    ax.set_xticklabels(solver_obj.columns, fontsize=9)
    ax.set_yticks(range(len(solver_obj.index)))
    ax.set_yticklabels([l.replace('\n',' ') for l in obj_labels], fontsize=9)
    for i in range(len(solver_obj.index)):
        for j in range(len(solver_obj.columns)):
            val = solver_obj.iloc[i, j]
            ax.text(j, i, str(val), ha='center', va='center', fontsize=9,
                    color='white' if val > solver_obj.values.max()*0.6 else 'black')
    ax.set_title('Solver Class vs Optimization Objectives')
    fig.colorbar(im, ax=ax, label='Number of Papers')
    plt.savefig(os.path.join(FIG_DIR, 'fig11_solver_objective_heatmap.pdf'))
    plt.savefig(os.path.join(FIG_DIR, 'fig11_solver_objective_heatmap.png'))
    plt.close()
    print(f"  Heatmap generated")

# ============================================================
# FIGURE 12: ML/AI Trend Over Time
# ============================================================
print("\n--- Figure 12: ML/AI Trend ---")
ml_by_year = df.groupby('year')['solver_norm'].apply(lambda x: (x == 'ML/AI').sum())
total_by_year = df.groupby('year').size()
ml_pct = (ml_by_year / total_by_year * 100).fillna(0)

fig, ax1 = plt.subplots(figsize=(8, 4))
ax2 = ax1.twinx()
ax1.bar(ml_by_year.index, ml_by_year.values, color='#4CAF50', alpha=0.7, label='ML/AI papers')
ax2.plot(ml_pct.index, ml_pct.values, 'ro-', label='ML/AI %', linewidth=2)
ax1.set_xlabel('Year')
ax1.set_ylabel('Number of ML/AI Papers', color='#4CAF50')
ax2.set_ylabel('Percentage of ML/AI (%)', color='red')
ax1.set_title('Rise of ML/AI-based Scheduling Methods')
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')
ax1.grid(alpha=0.3)
plt.savefig(os.path.join(FIG_DIR, 'fig12_ml_trend.pdf'))
plt.savefig(os.path.join(FIG_DIR, 'fig12_ml_trend.png'))
plt.close()
print(f"  ML/AI by year: {dict(ml_by_year)}")
print(f"  ML/AI % by year: {dict(ml_pct.round(1))}")

# ============================================================
# TABLE: Summary Statistics for Paper
# ============================================================
print("\n\n=== SUMMARY STATISTICS FOR PAPER ===")
print(f"Total papers included: {len(df)}")
print(f"Year range: {df['year'].min()}-{df['year'].max()}")
print(f"\nPapers by year:")
for y in sorted(df['year'].unique()):
    print(f"  {y}: {(df['year']==y).sum()}")

print(f"\nSolver class distribution:")
for cls, cnt in df['solver_norm'].value_counts().items():
    print(f"  {cls}: {cnt} ({100*cnt/len(df):.1f}%)")

print(f"\nObjective frequency:")
for col, label in zip(obj_cols, obj_labels):
    cnt = (df[col] == 'Y').sum()
    print(f"  {label.replace(chr(10),' ')}: {cnt} ({100*cnt/len(df):.1f}%)")

print(f"\nSystem scope:")
for s, cnt in df['system_norm'].value_counts().items():
    print(f"  {s}: {cnt} ({100*cnt/len(df):.1f}%)")

print(f"\nWorkload type:")
for w, cnt in df['workload_norm'].value_counts().items():
    print(f"  {w}: {cnt} ({100*cnt/len(df):.1f}%)")

print(f"\nMapping/Scheduling:")
for m, cnt in df['mapping_scheduling'].value_counts().items():
    print(f"  {m}: {cnt} ({100*cnt/len(df):.1f}%)")

print(f"\nHeterogeneity:")
for h, cnt in df['heterogeneity'].value_counts().items():
    print(f"  {h}: {cnt} ({100*cnt/len(df):.1f}%)")

print(f"\nDynamic vs Static:")
for d, cnt in df['dynamic_workload'].value_counts().items():
    print(f"  {d}: {cnt} ({100*cnt/len(df):.1f}%)")

# Key findings for the paper
print(f"\n=== KEY FINDINGS ===")
ml_count = (df['solver_norm'] == 'ML/AI').sum()
ml_recent = df[(df['solver_norm'] == 'ML/AI') & (df['year'] >= 2023)].shape[0]
total_recent = df[df['year'] >= 2023].shape[0]
print(f"1. ML/AI approaches: {ml_count}/{len(df)} ({100*ml_count/len(df):.0f}%) overall, {ml_recent}/{total_recent} ({100*ml_recent/total_recent:.0f}%) since 2023")

makespan_only = df[(df['makespan']=='Y') & (df['single_multi_obj']=='Single')].shape[0]
print(f"2. Makespan-only papers: {makespan_only}")

no_real = df[df['eval_norm'] == 'Simulation'].shape[0]
real = df[df['eval_norm'].str.contains('Real', na=False)].shape[0]
print(f"3. Simulation-only evaluation: {no_real} ({100*no_real/len(df):.0f}%); Real-system: {real} ({100*real/len(df):.0f}%)")

joint = (df['mapping_scheduling'] == 'Joint').sum()
print(f"4. Joint mapping+scheduling: {joint}/{len(df)} ({100*joint/len(df):.0f}%)")

hetero = (df['heterogeneity'] == 'Hetero').sum()
print(f"5. Heterogeneous systems: {hetero}/{len(df)} ({100*hetero/len(df):.0f}%)")

print(f"\n=== FIGURES SAVED ===")
for f in sorted(os.listdir(FIG_DIR)):
    print(f"  {f}")
