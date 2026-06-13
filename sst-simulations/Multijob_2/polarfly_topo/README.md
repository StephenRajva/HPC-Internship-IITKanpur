# SST PolarFly Multi-Job MPI Simulation

This project simulates multiple MPI communication jobs on a large-scale HPC system using the **Structural Simulation Toolkit (SST)** with the **PolarFly** topology.

---

## 🔧 Simulation Setup

- **Simulator**: SST (Structural Simulation Toolkit)
- **Topology**: PolarFly
- **Routing Algorithm**: UGAL
- **Total Routers**: 651 (based on `q=25`)
- **Host Configuration**:
  - Hosts per router: Auto-computed to cover 651 ranks
  - Actual nodes used: ≥ 651 (to ensure simulation scale ≥ 512-node system)

---

## 📦 Simulated MPI Jobs

| Job ID | Communication Pattern | No. of Ranks | Start Rank | Parameters |
|--------|------------------------|--------------|------------|------------|
| Job 1  | Allreduce              | 16           | 0          | `arg.count=512 arg.iterations=1` |
| Job 2  | Alltoall               | 64           | 16         | `arg.bytes=512 arg.iterations=1` |
| Job 3  | Scatter                | 32           | 80         | `arg.root=0 arg.count=512` |
| Job 4  | Broadcast (Bcast)      | 64           | 112        | `arg.root=0 arg.count=512` |

Each job includes:
- `Init` motif
- Core communication motif
- `Fini` motif

---

## 📊 Output Statistics & Plots

1. **Total Packets vs Hop Count per Job**
   - Shows packet volume across hop distances for each job.
   - Average hops per packet also plotted.

2. **Latency & Ranks Used**
   - Bar chart of ranks vs measured latency per job.
   - Helps compare performance based on job scale.

3. **Global Hop Count Distribution**
   - Summarizes total packets, min/max hops, and average hop per instance across all jobs.

---

## 📁 Output Files

- `polarfly_stats.csv` – SST-generated CSV with all enabled statistics.
- Plots:
  - `HopsPerJob.png`
  - `simulation_result.png`
  - `GlobalHopCountSummary.png`

---

## ✅ Task Objectives Covered

- Simulated 4 diverse MPI jobs ✅  
- Ranks varied between 16–64 ✅  
- Run on ≥512 nodes ✅  
- Plotted key metrics (hops, latency, packets) ✅  

---

## 📌 How to Run

Ensure SST is installed and Python simulation mode is enabled:

```bash
sst polarfly.py
