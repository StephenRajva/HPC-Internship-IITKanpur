#!/usr/bin/env python
# =============================================================================
#  mesh_ppn1.py  -  Mesh topology scaling study with PPN (ranks per node) = 1
# =============================================================================
#  PPN = "Processes Per Node" = number of MPI ranks placed on each compute node.
#
#  IMPORTANT: In SST there is NO parameter literally called "ppn".
#  PPN is a DERIVED number:
#
#        PPN = (number of MPI ranks)  /  (number of compute nodes)
#            =      job["size"]       /  (num_routers * local_ports)
#
#  To FIX PPN = 1 we simply make:   job size  ==  number of nodes.
#  This script computes that automatically, so PPN is guaranteed to be 1.
#
#  USAGE (one shape per run, chosen with an environment variable):
#        export MESH_SHAPE="4x4"        # router grid -> here 16 nodes
#        sst mesh_ppn1.py
#
#  The runner script run_mesh_sweep.sh loops over all the shapes for you.
# =============================================================================

import sst
import os
from sst.merlin.base import *
from sst.merlin.endpoint import *
from sst.merlin.interface import *
from sst.merlin.topology import *
from sst.ember import *

# -----------------------------------------------------------------------------
# 1. STUDY PARAMETERS  (the only things that change between runs)
# -----------------------------------------------------------------------------
PPN              = 1                                   # <-- FIXED at 1 (ranks per node)
shape            = os.environ.get("MESH_SHAPE", "4x4") # router grid, e.g. "2x2","8x8"
nodes_per_router = 1                                   # local_ports = 1 node per router
out_dir          = os.environ.get("STATS_DIR", ".")    # where to drop the CSV

# Work out how many routers / nodes / ranks this shape implies
dims        = [int(x) for x in shape.lower().split("x")]
num_routers = 1
for d in dims:
    num_routers *= d
num_nodes   = num_routers * nodes_per_router   # total compute nodes (endpoints)
num_ranks   = num_nodes * PPN                  # PPN=1  ->  ranks == nodes

# -----------------------------------------------------------------------------
# 2. PLATFORM + TOPOLOGY
# -----------------------------------------------------------------------------
PlatformDefinition.setCurrentPlatform("firefly-defaults")

topo               = topoMesh()
topo.shape         = shape
topo.local_ports   = nodes_per_router                  # nodes hanging off each router
topo.width         = "x".join(["1"] * len(dims))       # 1 link per dimension = clean mesh
topo.link_latency  = "25ns"

# -----------------------------------------------------------------------------
# 3. ROUTER
# -----------------------------------------------------------------------------
router                 = hr_router()
router.link_bw         = "12GB/s"
router.flit_size       = "16B"
router.xbar_bw         = "20GB/s"
router.input_latency   = "30ns"
router.output_latency  = "30ns"
router.input_buf_size  = "32kB"
router.output_buf_size = "32kB"
router.num_vns         = 2
router.xbar_arb        = "merlin.xbar_arb_lru"
topo.router = router

# -----------------------------------------------------------------------------
# 4. NETWORK INTERFACE (one NIC per node)
# -----------------------------------------------------------------------------
nic                 = ReorderLinkControl()
nic.link_bw         = "12GB/s"
nic.input_buf_size  = "16kB"
nic.output_buf_size = "16kB"

# -----------------------------------------------------------------------------
# 5. SYSTEM
# -----------------------------------------------------------------------------
system = System()
system.setTopology(topo)

# -----------------------------------------------------------------------------
# 6. WORKLOAD (MiniFE-style collectives + a few representative point-to-point)
# -----------------------------------------------------------------------------
motifs = [
    {"pattern": "Allreduce", "params": "iterations=92 count=1 compute=69ns"},
    {"pattern": "Bcast",     "params": "root=0 iterations=2 count=7 compute=1323ns"},
    {"pattern": "Reduce",    "params": "root=0 iterations=2 count=2 compute=450ns"},
    {"pattern": "Allgather", "params": "iterations=3 count=3 compute=243ns verify=0"},
    {"pattern": "Barrier",   "params": "iterations=99 compute=75ns"},
]

# Pick PingPong partners that ALWAYS exist for this size (rank2 must be < num_ranks).
# We sample a near neighbour, a one-row-down neighbour, the middle, and the far corner.
row_step  = dims[-1] if len(dims) >= 2 else 1
candidates = [1, row_step, num_nodes // 2, num_nodes - 1]
partners   = sorted({p for p in candidates if 0 < p < num_ranks})

for b in partners:
    motifs.append(
        {"pattern": "PingPong",
         "params": f"rank2={b} iterations=35 messageSize=256 compute=3ns"}
    )

# -----------------------------------------------------------------------------
# 7. BUILD THE JOB  (size == num_nodes  =>  PPN guaranteed = 1)
# -----------------------------------------------------------------------------
ep = EmberMPIJob(0, num_ranks)
ep.network_interface = nic
ep.addMotif("Init")
for m in motifs:
    ep.addMotif(f"{m['pattern']} {m['params']}")
ep.addMotif("Fini")
ep.nic.nic2host_lat = "100ns"

system.allocateNodes(ep, "linear")
system.build()

# -----------------------------------------------------------------------------
# 8. STATISTICS  ->  one CSV per shape
# -----------------------------------------------------------------------------
csv_path = os.path.join(out_dir, f"mesh_{shape}_ppn{PPN}_nodes{num_nodes}_stats.csv")

sst.setStatisticLoadLevel(10)
sst.setStatisticOutput("sst.statOutputCSV", {"filepath": csv_path, "separator": ", "})

sst.enableAllStatisticsForComponentType("merlin.hr_router")
sst.enableAllStatisticsForComponentType("merlin.linkcontrol")
sst.enableAllStatisticsForComponentType("ember.EmberEngine", {"MotifLog": "1"})
sst.enableAllStatisticsForComponentType("ember.nic")

# -----------------------------------------------------------------------------
# 9. CONFIG SUMMARY (prints to terminal so you can verify PPN at a glance)
# -----------------------------------------------------------------------------
print("==================================================")
print(f" Mesh shape        : {shape}")
print(f" Routers           : {num_routers}")
print(f" Nodes per router  : {nodes_per_router}  (local_ports)")
print(f" Total nodes       : {num_nodes}")
print(f" Total MPI ranks   : {num_ranks}")
print(f" PPN (ranks/node)  : {num_ranks // num_nodes}   <-- should be 1")
print(f" Stats CSV         : {csv_path}")
print("==================================================")
