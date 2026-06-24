# PPN = 1 Mesh Scaling Study — Runbook

## What "PPN" means here (and where it lives in your code)

**PPN = Processes Per Node** = how many MPI ranks run on each compute node.

There is **no parameter literally called `ppn`** anywhere in your scripts. PPN is a
*derived* number you control indirectly:

```
PPN  =  total MPI ranks  /  total compute nodes
     =  job["size"]      /  (num_routers * local_ports)
```

So to **fix PPN = 1**, you make `job["size"]` equal to the number of nodes.

### Words in your code that relate to PPN
| Word in your script        | What it really means                          |
|----------------------------|-----------------------------------------------|
| `topo.local_ports`         | nodes attached to each router (= 1 in our study) |
| `topo.shape`               | the router grid, e.g. "4x4" = 16 routers      |
| `job["size"]`              | total MPI ranks (= "processes")               |
| `EmberMPIJob(0, size)`     | the job and its rank count                     |
| `system.allocateNodes(...)`| places ranks onto nodes                        |
| `nic` / `network_interface`| one NIC per node                               |

`local_ports` is the closest single knob to "nodes per router", and `job["size"]`
is the knob for "number of processes". PPN is the ratio of the two.

## Good news about your original files
Your 5 original meshes were **already PPN = 1** (e.g. mesh4x4: 16 routers × 1
local_port = 16 nodes, and job size = 16 → 16/16 = 1). So no big rewrite was needed.

## What I actually changed / fixed
1. **Made PPN = 1 explicit and automatic** — size is now computed from the shape, so
   it can never silently drift away from 1.
2. **Fixed `width`** — your files used `width="4x4"` (4 links between routers, a "fat"
   mesh) except mesh16x16 which used `"1x1"`. For a clean, comparable study every size
   now uses `width="1x1"` (one link per dimension = a standard mesh).
3. **Fixed PingPong partners** — the old `rank2=1,2,3` pairs only made sense for tiny
   meshes. Partners are now chosen so they always exist for the size being run.
4. **Per-size CSV names** — each run writes its own file, so results don't overwrite.

## How to run it

### Option A — one parameterized file + the sweep script (recommended)
```bash
cd "/Users/stephenrajva/Downloads/SST_Stimulator/MiniFE/Mesh"
chmod +x run_mesh_sweep.sh
./run_mesh_sweep.sh
```
This runs 2x2, 4x4, 8x8, 16x16, 32x32 one after another at PPN=1 and drops a CSV +
a log for each into the `results/` subfolder.

To run just one size by hand:
```bash
export MESH_SHAPE="8x8"
export STATS_DIR="./results"
sst mesh_ppn1.py
```

### Option B — the five separate files
```bash
cd "/Users/stephenrajva/Downloads/SST_Stimulator/MiniFE/Mesh/individual_files"
sst mesh2x2_ppn1.py
sst mesh4x4_ppn1.py
sst mesh8x8_ppn1.py
sst mesh16x16_ppn1.py
sst mesh32x32_ppn1.py
```

## How to confirm PPN really is 1
Each run prints a summary block. Look for this line:
```
 PPN (ranks/node)  : 1   <-- should be 1
```
If it ever shows something other than 1, the size and node count are out of sync.

## Node counts for reference
| Shape  | Routers | Nodes | Ranks | PPN |
|--------|---------|-------|-------|-----|
| 2x2    | 4       | 4     | 4     | 1   |
| 4x4    | 16      | 16    | 16    | 1   |
| 8x8    | 64      | 64    | 64    | 1   |
| 16x16  | 256     | 256   | 256   | 1   |
| 32x32  | 1024    | 1024  | 1024  | 1   |

## Analysing the results
Each `*_stats.csv` holds the router and NIC statistics. For a scaling study the
useful columns are usually the router `send_bit_count` / `output_port_stalls`
and the link-control send/receive byte counts. To compare across sizes, pull the
*total simulated time* and *peak/total bytes* per size and plot them against node
count. Share one finished CSV with me and I'll build a parser + scaling plot keyed
to its exact columns (I don't want to guess column names blind).
