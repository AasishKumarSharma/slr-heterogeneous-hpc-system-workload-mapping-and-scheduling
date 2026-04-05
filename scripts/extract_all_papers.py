#!/usr/bin/env python3
"""
SLR Paper Extraction Pipeline
Reads all PDFs from SLR_PaperCollection and Zotero, extracts structured data
with page references, and outputs to CSV for spreadsheet update.
"""
import os, re, csv, json, glob, sys
from collections import defaultdict

import fitz  # PyMuPDF

# Paths
BASE = "~/ETL_ReviewPapers"
SLR_COLLECTION = os.path.join(BASE, "SLR_PaperCollection")
ZOTERO = "~/zotero_collection/storage"
SLR_PAPERS = os.path.join(BASE, "SLR_Papers")
OUTPUT_CSV = os.path.join(BASE, "SLR_Extracted_From_PDFs.csv")
OUTPUT_JSON = os.path.join(BASE, "SLR_Extracted_From_PDFs.json")

# Keywords for extraction
SOLVER_KEYWORDS = {
    'Exact': [r'\bMILP\b', r'\bILP\b', r'integer\s+linear\s+program', r'mixed.integer',
              r'\bCP[-\s]?SAT\b', r'constraint\s+program', r'branch.and.bound', r'\bB&B\b',
              r'exact\s+method', r'exact\s+solution', r'exact\s+algorithm', r'optimal\s+solution\s+guarantee',
              r'\bGurobi\b', r'\bCPLEX\b', r'linear\s+program', r'\bLP\b.*relax'],
    'Heuristic': [r'\bHEFT\b', r'\bCPOP\b', r'heterogeneous\s+earliest\s+finish',
                  r'\bPEFT\b', r'\bMPEFT\b', r'list.schedul', r'earliest\s+finish\s+time',
                  r'priority.based', r'\bEFT\b', r'greedy', r'\bOLB\b', r'min.min', r'max.min',
                  r'sufferage', r'round.robin', r'\bFCFS\b', r'first.come', r'backfill',
                  r'level.based', r'critical\s+path', r'upward\s+rank', r'downward\s+rank',
                  r'\bIPPTS\b', r'\bHSV\b', r'\bDLS\b', r'\bETF\b', r'\bMCP\b',
                  r'insertion.based', r'look.ahead', r'\bLotaru\b'],
    'Metaheuristic': [r'genetic\s+algorithm', r'\bGA\b', r'\bNSGA', r'particle\s+swarm', r'\bPSO\b',
                      r'ant\s+colony', r'\bACO\b', r'simulated\s+annealing', r'\bSA\b',
                      r'differential\s+evolution', r'\bDE\b', r'tabu\s+search', r'\bTS\b',
                      r'memetic', r'\bMA\b', r'evolutionary', r'\bEA\b', r'\bMOEA',
                      r'firefly', r'\bFA\b', r'bat\s+algorithm', r'cuckoo', r'whale',
                      r'grey\s+wolf', r'\bGWO\b', r'harmony\s+search', r'bee\s+colony', r'\bABC\b',
                      r'cat\s+swarm', r'\bCSO\b', r'Jaya', r'dragonfly', r'flower\s+pollinat',
                      r'multi.objective.*optim', r'pareto', r'meta.heuristic', r'metaheuristic',
                      r'population.based', r'nature.inspired', r'\bHBA\b', r'hybrid\s+bat'],
    'ML/AI': [r'reinforcement\s+learn', r'\bRL\b', r'deep\s+reinforcement', r'\bDRL\b',
              r'deep\s+learn', r'\bDL\b', r'neural\s+network', r'\bNN\b', r'\bDNN\b', r'\bCNN\b',
              r'\bGNN\b', r'graph\s+neural', r'\bRNN\b', r'\bLSTM\b', r'transformer',
              r'machine\s+learn', r'\bML\b', r'Q.learning', r'\bDQN\b', r'\bPPO\b', r'\bA3C\b',
              r'actor.critic', r'policy\s+gradient', r'attention\s+mechanism',
              r'random\s+forest', r'support\s+vector', r'\bSVM\b', r'backpropagation',
              r'hyper.heuristic', r'genetic\s+program'],
    'Quantum': [r'quantum', r'\bQUBO\b', r'\bVQE\b', r'\bQAOA\b', r'quantum\s+anneal',
                r'D.Wave', r'\bNISQ\b']
}

OBJECTIVE_KEYWORDS = {
    'makespan': [r'makespan', r'schedule\s+length', r'completion\s+time', r'total\s+execution\s+time',
                 r'minimize.*time', r'minimum.*time', r'earliest\s+finish', r'\bAFT\b'],
    'utilization': [r'resource\s+utiliz', r'resource\s+usage', r'CPU\s+utiliz', r'processor\s+utiliz',
                    r'utilization\s+rate', r'resource\s+efficiency'],
    'energy': [r'energy\s+consum', r'energy\s+efficien', r'energy\s+optim', r'energy.aware',
               r'power\s+consum', r'\bDVFS\b', r'energy\s+saving', r'green\s+computing',
               r'carbon', r'thermal', r'watt'],
    'cost': [r'monetary\s+cost', r'execution\s+cost', r'total\s+cost', r'budget',
             r'cloud\s+cost', r'pricing', r'pay.per.use', r'cost\s+optim', r'cost.effective',
             r'financial', r'dollar'],
    'load_balance': [r'load\s+balanc', r'workload\s+balanc', r'fair', r'fairness',
                     r'even\s+distribut', r'balanced\s+resource'],
    'throughput': [r'throughput', r'jobs\s+per\s+second', r'tasks\s+per\s+second',
                   r'processing\s+rate', r'bandwidth\s+utiliz'],
    'latency': [r'latency', r'response\s+time', r'turnaround\s+time', r'wait\s+time',
                r'queue\s+time', r'slowdown'],
    'deadline': [r'deadline', r'\bSLA\b', r'\bSLO\b', r'quality\s+of\s+service', r'\bQoS\b',
                 r'time\s+constraint', r'due\s+date'],
    'reliability': [r'reliabilit', r'fault\s+toler', r'failure\s+rate', r'availability',
                    r'resilien', r'robust', r'dependab'],
    'security': [r'security', r'privacy', r'trust', r'authentication', r'encryption']
}

CONSTRAINT_KEYWORDS = {
    'assignment': [r'one.task.*one.proc', r'assignment\s+constraint', r'each\s+task.*assigned',
                   r'unique\s+assignment', r'task\s+assign', r'one.to.one\s+map'],
    'capacity': [r'capacity\s+constraint', r'resource\s+limit', r'memory\s+limit',
                 r'CPU\s+limit', r'bandwidth\s+limit', r'slot\s+limit', r'core\s+limit',
                 r'resource\s+capacity', r'available\s+resources'],
    'feature': [r'feature\s+compatib', r'type\s+compatib', r'hardware\s+constraint',
                r'resource\s+type', r'eligible\s+resource', r'compatible\s+machine'],
    'precedence': [r'precedence', r'dependency\s+constraint', r'task\s+depend',
                   r'data\s+depend', r'order\s+constraint', r'topological'],
    'communication': [r'communication\s+cost', r'data\s+transfer', r'network\s+cost',
                      r'inter.machine', r'inter.processor', r'message\s+passing',
                      r'bandwidth', r'edge\s+weight.*communi'],
    'deadline_con': [r'deadline\s+constraint', r'time\s+constraint', r'SLA\s+constraint',
                     r'QoS\s+constraint', r'due\s+date\s+constraint'],
    'energy_con': [r'energy\s+constraint', r'energy\s+budget', r'power\s+budget',
                   r'energy\s+cap', r'power\s+limit']
}

SYSTEM_KEYWORDS = {
    'HPC': [r'\bHPC\b', r'high.performance\s+comput', r'supercomput', r'cluster\s+comput',
            r'parallel\s+comput', r'data\s+center', r'datacenter'],
    'Cloud': [r'cloud\s+comput', r'\bIaaS\b', r'\bPaaS\b', r'virtual\s+machine', r'\bVM\b',
              r'multi.cloud', r'cloud\s+environment', r'cloud\s+platform', r'Amazon\s+EC2',
              r'AWS', r'Azure', r'Google\s+Cloud'],
    'Edge/Fog': [r'edge\s+comput', r'fog\s+comput', r'IoT', r'edge.cloud', r'fog.cloud',
                 r'\bMEC\b', r'mobile\s+edge'],
    'Hybrid': [r'hybrid\s+cloud', r'edge.cloud.*hybrid', r'fog.cloud.*hybrid',
               r'heterogeneous\s+landscape', r'compute\s+continuum', r'multi.tier']
}

WORKLOAD_KEYWORDS = {
    'Workflow/DAG': [r'workflow', r'\bDAG\b', r'directed\s+acyclic', r'task\s+graph',
                     r'scientific\s+workflow', r'Montage', r'CyberShake', r'Epigenomics',
                     r'SIPHT', r'LIGO', r'Inspiral'],
    'Batch': [r'batch\s+job', r'batch\s+process', r'job\s+schedul', r'batch\s+schedul',
              r'job\s+queue', r'workload\s+trace', r'PBS', r'SLURM'],
    'Container': [r'container', r'Kubernetes', r'\bK8s\b', r'Docker', r'microservice',
                  r'pod\s+schedul'],
    'DNN/Training': [r'DNN\s+training', r'deep\s+learning\s+train', r'model\s+parallel',
                     r'data\s+parallel', r'distributed\s+train']
}

EVAL_KEYWORDS = {
    'Simulation': [r'simulat', r'CloudSim', r'WorkflowSim', r'SimGrid', r'synthetic',
                   r'randomly\s+generated', r'random\s+DAG', r'random\s+graph'],
    'Real-system': [r'real\s+system', r'real\s+cluster', r'testbed', r'real\s+world\s+experiment',
                    r'deployed', r'production\s+system', r'physical\s+cluster',
                    r'real\s+hardware', r'Parallella'],
    'Trace-based': [r'trace.based', r'workload\s+trace', r'real\s+trace', r'Google\s+trace',
                    r'Alibaba\s+trace', r'SPEC', r'log\s+data']
}

def extract_text_from_pdf(pdf_path, max_pages=30):
    """Extract text from PDF with page numbers."""
    pages = {}
    try:
        doc = fitz.open(pdf_path)
        for i, page in enumerate(doc):
            if i >= max_pages:
                break
            text = page.get_text()
            if text.strip():
                pages[i+1] = text
        doc.close()
    except Exception as e:
        print(f"  ERROR reading {pdf_path}: {e}", file=sys.stderr)
    return pages

def search_patterns(text, patterns, case_insensitive=True):
    """Search for regex patterns in text, return matches with context."""
    flags = re.IGNORECASE if case_insensitive else 0
    matches = []
    for pat in patterns:
        for m in re.finditer(pat, text, flags):
            start = max(0, m.start() - 40)
            end = min(len(text), m.end() + 40)
            context = text[start:end].replace('\n', ' ').strip()
            matches.append((m.group(), context))
    return matches

def classify_with_pages(pages_dict, keyword_dict):
    """Classify text using keyword dict, return categories with page refs."""
    results = {}
    for category, patterns in keyword_dict.items():
        category_matches = []
        for page_num, text in pages_dict.items():
            matches = search_patterns(text, patterns)
            for match_text, context in matches:
                category_matches.append({
                    'page': page_num,
                    'match': match_text,
                    'context': context
                })
        if category_matches:
            results[category] = category_matches
    return results

def extract_numbers(pages_dict):
    """Extract task/resource counts from evaluation sections."""
    max_tasks = None
    max_resources = None
    task_refs = []
    resource_refs = []

    for page_num, text in pages_dict.items():
        # Look for task counts
        for m in re.finditer(r'(\d+)\s*(?:tasks?|nodes?|jobs?)', text, re.IGNORECASE):
            n = int(m.group(1))
            if 5 <= n <= 100000:
                task_refs.append((n, page_num, m.group()))
                if max_tasks is None or n > max_tasks:
                    max_tasks = n
        # Look for resource/processor counts
        for m in re.finditer(r'(\d+)\s*(?:processors?|machines?|resources?|VMs?|nodes?|servers?|cores?)', text, re.IGNORECASE):
            n = int(m.group(1))
            if 2 <= n <= 100000:
                resource_refs.append((n, page_num, m.group()))
                if max_resources is None or n > max_resources:
                    max_resources = n

    return max_tasks, max_resources, task_refs, resource_refs

def extract_specific_methods(pages_dict):
    """Extract specific algorithm/method names."""
    methods = set()
    method_patterns = [
        (r'\bHEFT\b', 'HEFT'), (r'\bCPOP\b', 'CPOP'), (r'\bPEFT\b', 'PEFT'),
        (r'\bMPEFT\b', 'MPEFT'), (r'\bIPPTS\b', 'IPPTS'), (r'\bDLS\b', 'DLS'),
        (r'\bEFT\b', 'EFT'), (r'\bOLB\b', 'OLB'), (r'\bMCT\b', 'MCT'),
        (r'\bMin-Min\b', 'Min-Min'), (r'\bMax-Min\b', 'Max-Min'),
        (r'\bNSGA-II\b', 'NSGA-II'), (r'\bNSGA-III\b', 'NSGA-III'),
        (r'\bMOEA/D\b', 'MOEA/D'), (r'\bSPEA2?\b', 'SPEA2'),
        (r'\bGA\b', 'GA'), (r'\bPSO\b', 'PSO'), (r'\bACO\b', 'ACO'),
        (r'\bSA\b', 'SA'), (r'\bDE\b', 'DE'), (r'\bGWO\b', 'GWO'),
        (r'\bABC\b', 'ABC'), (r'\bCSO\b', 'CSO'), (r'\bFA\b', 'FA'),
        (r'\bHBA\b', 'HBA'), (r'\bJaya\b', 'Jaya'),
        (r'\bDQN\b', 'DQN'), (r'\bPPO\b', 'PPO'), (r'\bA3C\b', 'A3C'),
        (r'\bA2C\b', 'A2C'), (r'\bDDPG\b', 'DDPG'), (r'\bSAC\b', 'SAC'),
        (r'Q-learning', 'Q-learning'), (r'\bGNN\b', 'GNN'),
        (r'\bMILP\b', 'MILP'), (r'\bCP-SAT\b', 'CP-SAT'),
        (r'\bGurobi\b', 'Gurobi'), (r'\bCPLEX\b', 'CPLEX'),
        (r'\bCloudSim\b', 'CloudSim'), (r'\bWorkflowSim\b', 'WorkflowSim'),
        (r'\bLotaru\b', 'Lotaru'), (r'\bDFMan\b', 'DFMan'),
    ]
    method_refs = []
    full_text = ' '.join(pages_dict.values())
    for pattern, name in method_patterns:
        if re.search(pattern, full_text, re.IGNORECASE):
            methods.add(name)
            # Find first occurrence page
            for pn, txt in pages_dict.items():
                if re.search(pattern, txt, re.IGNORECASE):
                    method_refs.append((name, pn))
                    break
    return methods, method_refs

def extract_benchmarks(pages_dict):
    """Extract benchmark/workflow names used in evaluation."""
    benchmarks = set()
    bench_patterns = [
        (r'Montage', 'Montage'), (r'CyberShake', 'CyberShake'),
        (r'Epigenomics', 'Epigenomics'), (r'SIPHT', 'SIPHT'),
        (r'LIGO', 'LIGO'), (r'Inspiral', 'Inspiral'),
        (r'random\s+DAG', 'Random DAG'), (r'random.*graph', 'Random Graph'),
        (r'CloudSim', 'CloudSim'), (r'WorkflowSim', 'WorkflowSim'),
        (r'SimGrid', 'SimGrid'), (r'Google\s+trace', 'Google Trace'),
        (r'Alibaba\s+trace', 'Alibaba Trace'), (r'STG', 'STG'),
        (r'Pegasus', 'Pegasus'), (r'SPEC', 'SPEC'),
    ]
    full_text = ' '.join(pages_dict.values())
    for pattern, name in bench_patterns:
        if re.search(pattern, full_text, re.IGNORECASE):
            benchmarks.add(name)
    return benchmarks

def detect_mapping_scheduling(pages_dict):
    """Detect if paper addresses mapping, scheduling, or both."""
    full_text = ' '.join(pages_dict.values()).lower()
    has_mapping = bool(re.search(r'task.to.resource|task.to.processor|task.to.machine|resource\s+alloc|task\s+assign|task\s+map|mapping\s+problem|placement', full_text))
    has_scheduling = bool(re.search(r'schedul|execution\s+order|priority\s+queue|ready\s+list|time\s+slot|gantt', full_text))

    if has_mapping and has_scheduling:
        return 'Y', 'Y', 'Joint'
    elif has_mapping:
        return 'Y', 'N', 'Mapping-only'
    elif has_scheduling:
        return 'N', 'Y', 'Scheduling-only'
    return 'Unknown', 'Unknown', 'Unknown'

def detect_heterogeneity(pages_dict):
    """Detect heterogeneity type."""
    full_text = ' '.join(pages_dict.values()).lower()
    if re.search(r'heterogeneous', full_text):
        resource_types = set()
        if re.search(r'\bcpu\b|\bprocessor\b|\bcore\b', full_text): resource_types.add('CPU')
        if re.search(r'\bgpu\b|\bgraphics\s+process', full_text): resource_types.add('GPU')
        if re.search(r'\bfpga\b|\bfield.program', full_text): resource_types.add('FPGA')
        if re.search(r'\btpu\b', full_text): resource_types.add('TPU')
        if re.search(r'\bvm\b|\bvirtual\s+machine', full_text): resource_types.add('VM')
        if re.search(r'\bcontainer\b|\bpod\b', full_text): resource_types.add('Container')
        return 'Hetero', ', '.join(sorted(resource_types)) if resource_types else 'Unknown'
    elif re.search(r'homogeneous', full_text):
        return 'Homo', ''
    return 'Unknown', ''

def detect_dynamic(pages_dict):
    """Detect if workload is dynamic or static."""
    full_text = ' '.join(pages_dict.values()).lower()
    if re.search(r'dynamic\s+workload|dynamic\s+schedul|online\s+schedul|real.time\s+schedul|arrival\s+rate|streaming', full_text):
        return 'Dynamic'
    elif re.search(r'static\s+schedul|offline\s+schedul|predetermined|pre.defined\s+workflow', full_text):
        return 'Static'
    return 'Unknown'

def detect_task_dependencies(pages_dict):
    """Detect if task dependencies are modeled."""
    full_text = ' '.join(pages_dict.values()).lower()
    if re.search(r'task\s+depend|precedence|dag\b|directed\s+acyclic|workflow\s+graph|data\s+depend', full_text):
        return 'Y'
    return 'N'

def process_paper(pdf_path, paper_id=None):
    """Process a single paper and return structured extraction."""
    filename = os.path.basename(pdf_path)
    is_abstract = '_abstract_' in filename.lower() or 'abstract' in filename.lower()

    pages = extract_text_from_pdf(pdf_path, max_pages=30 if not is_abstract else 5)
    if not pages:
        return None

    full_text = ' '.join(pages.values())

    # System scope
    system_results = classify_with_pages(pages, SYSTEM_KEYWORDS)
    system_scope = '/'.join(sorted(system_results.keys())) if system_results else 'Unknown'
    system_refs = {k: [(m['page'], m['context'][:60]) for m in v[:2]] for k, v in system_results.items()}

    # Heterogeneity
    hetero, resource_types = detect_heterogeneity(pages)

    # Workload
    workload_results = classify_with_pages(pages, WORKLOAD_KEYWORDS)
    workload_type = '/'.join(sorted(workload_results.keys())) if workload_results else 'Unknown'

    # Task dependencies
    task_deps = detect_task_dependencies(pages)

    # Dynamic
    dynamic = detect_dynamic(pages)

    # Mapping/Scheduling
    addr_map, addr_sched, map_sched = detect_mapping_scheduling(pages)

    # Solver class
    solver_results = classify_with_pages(pages, SOLVER_KEYWORDS)
    solver_classes = sorted(solver_results.keys())
    solver_class = '/'.join(solver_classes) if solver_classes else 'Unknown'
    solver_refs = {k: [(m['page'], m['context'][:80]) for m in v[:3]] for k, v in solver_results.items()}

    # Specific methods
    methods, method_refs = extract_specific_methods(pages)

    # Objectives
    obj_results = classify_with_pages(pages, OBJECTIVE_KEYWORDS)
    obj_refs = {k: [(m['page'], m['context'][:80]) for m in v[:2]] for k, v in obj_results.items()}
    single_multi = 'Multi' if len(obj_results) > 1 else ('Single' if len(obj_results) == 1 else 'Unknown')

    # Constraints
    con_results = classify_with_pages(pages, CONSTRAINT_KEYWORDS)
    con_refs = {k: [(m['page'], m['context'][:80]) for m in v[:2]] for k, v in con_results.items()}

    # Evaluation
    eval_results = classify_with_pages(pages, EVAL_KEYWORDS)
    eval_type = '/'.join(sorted(eval_results.keys())) if eval_results else 'Unknown'

    # Numbers
    max_tasks, max_resources, task_refs_list, resource_refs_list = extract_numbers(pages)

    # Benchmarks
    benchmarks = extract_benchmarks(pages)

    # Algorithm strategy
    strategy = []
    if 'Heuristic' in solver_classes: strategy.append('Constructive/Priority')
    if 'Metaheuristic' in solver_classes: strategy.append('Population-based')
    if 'ML/AI' in solver_classes: strategy.append('Learning-based')
    if 'Exact' in solver_classes: strategy.append('Mathematical')
    if 'Quantum' in solver_classes: strategy.append('Quantum')

    # Hybrid approach
    hybrid = 'Y' if len(solver_classes) > 1 else 'N'

    # Confidence
    if is_abstract:
        confidence = 'low'
        extraction_source = 'abstract-pdf'
    else:
        page_count = len(pages)
        if page_count >= 8:
            confidence = 'high'
            extraction_source = 'full-text'
        elif page_count >= 4:
            confidence = 'medium'
            extraction_source = 'partial-text'
        else:
            confidence = 'low'
            extraction_source = 'abstract-pdf'

    # Compile all references for traceability
    all_refs = {
        'system': system_refs,
        'solver': solver_refs,
        'objectives': obj_refs,
        'constraints': con_refs,
        'methods': method_refs,
        'max_tasks_refs': [(n, p, t) for n, p, t in task_refs_list[-5:]] if task_refs_list else [],
        'max_resources_refs': [(n, p, t) for n, p, t in resource_refs_list[-5:]] if resource_refs_list else [],
    }

    return {
        'filename': filename,
        'paper_or_abstract': 'abstract' if is_abstract else 'paper',
        'num_pages_read': len(pages),
        'system_scope': system_scope,
        'heterogeneity': hetero,
        'resource_types': resource_types,
        'workload_type': workload_type,
        'task_dependencies': task_deps,
        'dynamic_workload': dynamic,
        'addresses_mapping': addr_map,
        'addresses_scheduling': addr_sched,
        'mapping_scheduling': map_sched,
        'solver_class': solver_class,
        'specific_method': ', '.join(sorted(methods)),
        'algorithm_strategy': ', '.join(strategy),
        'hybrid_approach': hybrid,
        'makespan': 'Y' if 'makespan' in obj_results else '',
        'utilization': 'Y' if 'utilization' in obj_results else '',
        'energy': 'Y' if 'energy' in obj_results else '',
        'cost': 'Y' if 'cost' in obj_results else '',
        'load_balance': 'Y' if 'load_balance' in obj_results else '',
        'throughput': 'Y' if 'throughput' in obj_results else '',
        'latency': 'Y' if 'latency' in obj_results else '',
        'deadline': 'Y' if 'deadline' in obj_results else '',
        'reliability': 'Y' if 'reliability' in obj_results else '',
        'security': 'Y' if 'security' in obj_results else '',
        'single_multi_obj': single_multi,
        'con_assignment': 'Y' if 'assignment' in con_results else '',
        'con_capacity': 'Y' if 'capacity' in con_results else '',
        'con_feature': 'Y' if 'feature' in con_results else '',
        'con_precedence': 'Y' if 'precedence' in con_results else '',
        'con_communication': 'Y' if 'communication' in con_results else '',
        'con_deadline': 'Y' if 'deadline_con' in con_results else '',
        'con_energy': 'Y' if 'energy_con' in con_results else '',
        'max_tasks': str(max_tasks) if max_tasks else '',
        'max_resources': str(max_resources) if max_resources else '',
        'eval_type': eval_type,
        'benchmark': ', '.join(sorted(benchmarks)),
        'reproducible': '',  # Needs manual check
        'extraction_source': extraction_source,
        'confidence': confidence,
        'references': json.dumps(all_refs, default=str),
    }

def collect_all_pdfs():
    """Collect all PDF paths from both locations."""
    pdfs = {}

    # SLR_PaperCollection
    for f in sorted(glob.glob(os.path.join(SLR_COLLECTION, "*.pdf"))):
        pdfs[os.path.basename(f)] = f

    # SLR_Papers (previously downloaded)
    for f in sorted(glob.glob(os.path.join(SLR_PAPERS, "*.pdf"))):
        name = os.path.basename(f)
        if name not in pdfs:
            pdfs[name] = f

    # Zotero storage
    for folder in sorted(glob.glob(os.path.join(ZOTERO, "*"))):
        if os.path.isdir(folder):
            for f in glob.glob(os.path.join(folder, "*.pdf")):
                name = os.path.basename(f)
                if name not in pdfs:
                    pdfs[name] = f

    return pdfs

def main():
    print("Collecting PDFs...")
    pdfs = collect_all_pdfs()
    print(f"Found {len(pdfs)} unique PDFs")

    results = []
    errors = []

    for i, (name, path) in enumerate(sorted(pdfs.items())):
        print(f"[{i+1}/{len(pdfs)}] Processing: {name[:80]}...")
        try:
            result = process_paper(path)
            if result:
                results.append(result)
            else:
                errors.append((name, "No text extracted"))
        except Exception as e:
            errors.append((name, str(e)))
            print(f"  ERROR: {e}", file=sys.stderr)

    # Write CSV
    if results:
        fieldnames = list(results[0].keys())
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"\nSaved {len(results)} extractions to {OUTPUT_CSV}")

    # Write JSON (includes references for traceability)
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump({'extractions': results, 'errors': errors}, f, indent=2, default=str)
    print(f"Saved detailed JSON to {OUTPUT_JSON}")

    # Summary
    print(f"\n=== SUMMARY ===")
    print(f"Total PDFs found: {len(pdfs)}")
    print(f"Successfully extracted: {len(results)}")
    print(f"Errors: {len(errors)}")

    # Field fill rates
    for field in ['solver_class', 'makespan', 'energy', 'eval_type', 'max_tasks', 'confidence']:
        filled = sum(1 for r in results if r.get(field) and r[field] not in ['', 'Unknown'])
        print(f"  {field}: {filled}/{len(results)} ({100*filled/len(results):.0f}%)")

    if errors:
        print(f"\nErrors:")
        for name, err in errors[:10]:
            print(f"  {name[:60]}: {err}")

if __name__ == '__main__':
    main()
