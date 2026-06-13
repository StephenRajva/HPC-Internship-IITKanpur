# HPC Internship — IIT Kanpur SURGE Fellowship 2026

**Intern:** Stephen Raj V.A — Final-year CSBS, SRMIST Kattankulathur  
**Supervisor:** Prof. Preeti Malakar, Department of Computer Science & Engineering, IIT Kanpur  
**Program:** SURGE Fellowship 2026  
**Platform:** MacBook Air M-series (Apple Silicon ARM64), macOS Tahoe 25.3.0

---

## Overview

This repository documents work done during a summer research internship focused on **HPC network topology analysis** using:

- **MPI communication pattern profiling** with mpiP
- **SST (Structural Simulation Toolkit)** network simulations across four topologies
- **Real HPC mini-applications** (MiniFE, MiniMD) run inside SST

The core research question: *How do HPC network topologies (Dragonfly, Polarfly, 3D Torus, 3D Mesh) affect latency and scalability for different communication patterns?*

---

## Repository Structure

```
HPC-Internship-IITKanpur/
├── mpi-patterns/              # MPI C programs for 3 communication patterns
│   ├── mpi_adjacent.c         # Even→next odd rank (0→1, 2→3, …)
│   ├── mpi_halfshift.c        # First half → second half (0→P/2, …)
│   └── mpi_mirrored.c         # Mirror pairing (0→P-1, 1→P-2, …)
│
├── profiling-results/         # mpiP output files (.mpiP) for all patterns
│   ├── mpi_adjacent_prof.*
│   ├── mpi_halfshift_prof.*
│   └── mpi_mirrored_prof.*
│
├── visualization/             # Python analysis scripts (matplotlib/pandas)
│   ├── adjacent_analysis.py
│   ├── halfshift_analysis.py
│   ├── mirrored_analysis.py
│   ├── multijob_sst_analysis.py
│   └── multijob_2_analysis.py
│
├── sst-simulations/
│   ├── Singlejob_sst/         # Single-job simulations (1 app per run)
│   │   ├── Dragonfly_topology/ # 32 ranks, Allreduce, UGAL routing
│   │   ├── Mesh_topology/     # 4 ranks, Allreduce
│   │   ├── Polarfly_topology/ # 13 ranks, Allreduce
│   │   └── latency_comparison/
│   ├── MultiJob_sst/          # 2 simultaneous jobs (Allreduce + Alltoall)
│   │   ├── dragonfly_topo/    # 16 ranks each
│   │   └── mesh_topo/         # 2 ranks each
│   └── Multijob_2/            # 4 simultaneous jobs, all 4 topologies
│       ├── dragonfly/
│       ├── mesh/
│       ├── torus/
│       └── polarfly_topo/
│
└── miniapps/                  # Real HPC applications in SST
    ├── miniFE.x               # MiniFE binary (built on macOS ARM64)
    ├── MiniFE_simulation/     # SST simulation files for MiniFE
    │   ├── dragonfly/
    │   ├── torus/
    │   ├── mesh_topology/
    │   └── tau_profile_output/
    └── MiniMD_simulation/     # SST simulation files for MiniMD
        ├── torus/
        ├── mesh3D/
        └── tau_profile_output/
```

---

## Part 1 — MPI Communication Pattern Profiling

Three C programs send 1 KB messages in different pairing patterns across 4 MPI ranks, profiled with **mpiP**.

| Pattern   | Description                        | Ranks |
|-----------|------------------------------------|-------|
| Adjacent  | Even rank → next odd (0→1, 2→3)   | 4     |
| HalfShift | First half → second half (0→2, 1→3)| 4     |
| Mirrored  | Mirror pairs (0→3, 1→2)           | 4     |

### Build & Run

```bash
# Compile with MPICH + mpiP instrumentation
mpicc -o mpi_adjacent mpi_adjacent.c -L/path/to/mpiP/lib -lmpiP -lm -lbfd
mpirun -n 4 ./mpi_adjacent
```

### mpiP Profiling Results

| Pattern   | Send Latency | Recv Latency | Sender MPI% | Receiver MPI% |
|-----------|-------------|-------------|-------------|---------------|
| Adjacent  | 0.040 ms    | 0.260 ms    | 43.96%      | 95.59%        |
| HalfShift | 0.040 ms    | 0.373 ms    | 43.96%      | 91.87%        |
| Mirrored  | 0.040 ms    | 0.373 ms    | 43.96%      | 95.59%        |

**Key insight:** Send latency is identical across all patterns (~0.04 ms), while Recv latency varies (Adjacent is ~30% faster than HalfShift/Mirrored). Receivers spend 92–96% of their time in MPI calls, confirming they are fully communication-bound.

> **Note:** `Parent_Funct` shows `[unknown]` in mpiP reports due to a macOS limitation — `libiberty` is not available on macOS. This is not a code error.

---

## Part 2 — SST Single-Job Simulations

Single application runs across three topologies to measure collective latency.

### Setup

```bash
# SST built with OpenMPI on macOS ARM64
sst dragonfly_sst.py   # or mesh_sst.py / polarfly_sst.py.py
```

Each simulation models **Allreduce**, **Scatter**, **Broadcast**, and **Alltoall** collectives.

---

## Part 3 — SST Multi-Job Simulations

### MultiJob_sst — 2 Simultaneous Jobs

Two jobs (Allreduce + Alltoall) run concurrently on the same network fabric. Tests **interference** and **contention** between applications.

| Topology  | Config                       |
|-----------|------------------------------|
| Dragonfly | 2 jobs × 16 ranks            |
| Mesh      | 2 jobs × 2 ranks             |

### Multijob_2 — 4 Simultaneous Jobs, All 4 Topologies

Four jobs run concurrently on Dragonfly, Polarfly, 3D Torus, and 3D Mesh.

**Original 4-topology comparison (collective latency):**

| Topology  | Allreduce  | Scatter   | Bcast     | Alltoall   | Total Sim Time |
|-----------|-----------|-----------|-----------|------------|----------------|
| Polarfly  | 4.304 µs  | 4.598 µs  | 5.954 µs  | 62.644 µs  | **75.3 µs** 🏆 |
| Dragonfly | 4.556 µs  | 4.657 µs  | 6.501 µs  | 77.565 µs  | 91.9 µs        |
| Torus     | 6.349 µs  | 7.609 µs  | 8.878 µs  | 88.865 µs  | 106.1 µs       |
| Mesh      | 12.786 µs | 8.805 µs  | 16.566 µs | 189.785 µs | 235.5 µs       |

**Polarfly wins overall**, with Dragonfly ~22% slower, Torus ~41% slower, and Mesh ~213% slower.

**MiniApps (MiniFE + MiniMD) on all 4 topologies:**

Each topology ran 4 concurrent jobs with real application communication traces.

---

## Part 4 — Real HPC Mini-Applications

### MiniFE — Finite Element Solver

MiniFE solves a 3D finite element problem using Conjugate Gradient (CG) iteration.

**Build on macOS ARM64:**
```bash
# Required fix: change tau_cxx.sh → mpicxx in Makefile
cd minife/ref/src
make
```

**Simulation results:**

| Grid Size  | CG Iterations | Convergence |
|------------|--------------|-------------|
| 8×8×8      | 20           | ✓           |
| 32×32×32   | 100          | ✓           |

**Communication profile:** 92 Allreduce + 35 PingPong (409 bytes) + 2 Bcast + 3 Allgather

**MiniFE latency across topologies:**

| Operation        | Dragonfly | Polarfly  | Torus     | Mesh      | Winner    |
|-----------------|-----------|-----------|-----------|-----------|-----------|
| Allreduce       | 3.486 µs  | 3.770 µs  | —         | 4.002 µs  | Dragonfly |
| Bcast           | 1.763 µs  | 1.763 µs  | —         | 1.762 µs  | Tie       |
| Allgather       | 3.662 µs  | 3.959 µs  | —         | 4.252 µs  | Dragonfly |

---

### MiniMD — Molecular Dynamics

MiniMD simulates atomic interactions using Lennard-Jones (LJ) and Embedded Atom Method (EAM) potentials.

**Build on macOS ARM64:**
```bash
# Required fix: patch openmp.h inclusion for Apple Clang
cd miniMD/ref
make
```

**Baseline performance (4 MPI processes, 131,072 atoms):**

| Force Model | Atom-steps/second | 
|-------------|-------------------|
| LJ          | 13.3 M/s          |
| EAM         | 6.98 M/s          |

**Communication profile:** 325 PingPong (20,510 bytes) + 40 Allreduce + 15 Barrier

**Scaling study (LJ, 131,072 atoms):**

| Processes | Performance    | Comm Time | Speedup    |
|-----------|---------------|-----------|------------|
| 2         | 7.08 M steps/s| 0.032 s   | 1.0×       |
| 4         | 13.05 M steps/s| 0.040 s  | 1.84×      |
| 8         | 12.27 M steps/s| 0.361 s  | ⚠️ bottleneck |

**Key finding:** At 8 processes, communication time jumped **9×** (0.040 s → 0.361 s), causing super-linear slowdown. This is consistent with halo-exchange overhead growing with the number of neighboring ranks.

**MiniMD latency across topologies:**

| Operation          | Dragonfly  | Polarfly   | Mesh       | Winner    |
|-------------------|-----------|-----------|-----------|-----------|
| PingPong (20 KB)  | 10.286 µs | 10.255 µs | 10.545 µs | Polarfly  |
| Allreduce (LJ)    | 5.825 µs  | 6.104 µs  | 6.331 µs  | Dragonfly |
| Allreduce (EAM)   | 7.367 µs  | 7.645 µs  | 7.873 µs  | Dragonfly |

---

## Summary of Key Findings

1. **Network topology matters.** Mesh is 3× slower than Polarfly for collective operations under multi-job workloads.

2. **Polarfly leads for synthetic collectives** (Alltoall, Scatter), while **Dragonfly leads for real-app collectives** (MiniFE Allreduce, MiniMD Allreduce) — suggesting Dragonfly's UGAL routing handles application-specific traffic patterns better.

3. **MPI receive is the bottleneck**, not send. Receivers spend 92–96% of time in MPI vs. ~44% for senders.

4. **MiniMD scaling hits a wall at 8 processes** due to halo-exchange explosion — communication time increases 9× while compute time drops only ~2×.

5. **Large messages (20 KB PingPong) favor Polarfly** over Dragonfly, suggesting topology effects are workload-dependent.

---

## Environment

| Component      | Details                                      |
|----------------|----------------------------------------------|
| Machine        | MacBook Air M-series (Apple Silicon ARM64)   |
| OS             | macOS Tahoe 25.3.0                           |
| MPI (SST)      | OpenMPI                                      |
| MPI (profiling)| MPICH + mpiP                                 |
| Simulator      | SST (Structural Simulation Toolkit)          |
| Profiler       | mpiP, TAU                                    |
| Languages      | C (MPI), Python (SST config + analysis)      |

---

## Acknowledgements

This work was carried out under the **SURGE Fellowship 2026** at IIT Kanpur, supervised by **Prof. Preeti Malakar**, Department of Computer Science & Engineering. The fellowship is supported by the Science and Engineering Research Board (SERB), Government of India.
