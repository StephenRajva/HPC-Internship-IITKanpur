#!/usr/bin/env python
# =============================================================================
#  mesh_ppn2.py  -  Mesh topology scaling study with PPN (ranks per node) = 2
# =============================================================================
#  PPN = "Processes Per Node" = number of MPI ranks placed on each compute node.
#
#  In SST there is NO parameter literally called "ppn".  PPN is DERIVED:
#
#        PPN = (number of MPI ranks)  /  (number of compute nodes)
#            =      job["size"]       /  (num_routers * local_ports)
#
#  To FIX PPN = 2 we put 2 hosts on each router (local_ports = 2) and make the
#  job size = 2 * num_routers.  The "size" stays the same as the PPN=1 study
#  (same router grid / same node count), but each node now runs 2 ranks.
#
#  USAGE:
#        export MESH_SHAPE="4x4"        # router grid -> here 16 nodes, 32 ranks
#        sst mesh_ppn2.py
#  The runner script run_mesh_sweep_ppn2.sh loops over all the shapes.
# =============================================================================

import sst
import os
from sst.merlin.base import *
from sst.merlin.endpoint import *
from sst.merlin.interface import *
from sst.merlin.topology import *
from sst.ember import *

# -----------------------------------------------------------------------------
# 1. STUDY PARAMETERS
# -----------------------------------------------------------------------------
PPN              = 2                                    # <-- FIXED at 2 (ranks per node)
shape            = os.environ.get("MESH_SHAPE", "4x4")  # router grid, e.g. "2x2","8x8"
nodes_per_router = PPN                                  # local_ports = 2 nodes per router
out_dir          = os.environ.get("STATS_DIR", ".")     # where to drop the CSV

# Work out how many routers / nodes / ranks this shape implies
dims        = [int(x) for x in shape.lower().split("x")]
num_routers = 1
for d in dims:
    num_routers *= d
num_nodes   = num_routers * nodes_per_router   # PPN=2 -> 2 hosts per router
num_ranks   = num_nodes                        # one rank per host -> ranks == nodes
# NOTE: "size" (the router grid) is identical to PPN=1; only host density changed.
# PPN = num_ranks / num_routers = (2*num_routers)/num_routers = 2.

# -----------------------------------------------------------------------------
# 2. PLATFORM + TOPOLOGY
# -----------------------------------------------------------------------------
PlatformDefinition.setCurrentPlatform("firefly-defaults")

topo               = topoMesh()
topo.shape         = shape
topo.local_ports   = nodes_per_router                  # 2 nodes hanging off each router
topo.width         = "x".join(["1"] * len(dims))       # 1 link per dimension = clean mesh
topo.link_latency  = "25ns"

# -----------------------------------------------------------------------------
# 3. ROUTER  (identical to PPN=1 study)
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
# 4. NETWORK INTERFACE
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
# 6. WORKLOAD (identical MiniFE motif mix to the PPN=1 study)
# -----------------------------------------------------------------------------
motifs = [
    {"pattern": "Allreduce", "params": "iterations=92 count=1 compute=69ns"},
    {"pattern": "Bcast",     "params": "root=0 iterations=2 count=7 compute=1323ns"},
    {"pattern": "Reduce",    "params": "root=0 iterations=2 count=2 compute=450ns"},
    {"pattern": "Allgather", "params": "iterations=3 count=3 compute=243ns verify=0"},
    {"pattern": "Barrier",   "params": "iterations=99 compute=75ns"},
]

# PingPong partners must be < num_ranks (now 2x larger than PPN=1).
row_step  = dims[-1] if len(dims) >= 2 else 1
candidates = [1, row_step, num_nodes // 2, num_nodes - 1]
partners   = sorted({p for p in candidates if 0 < p < num_ranks})

for b in partners:
    motifs.append(
        {"pattern": "PingPong",
         "params": f"rank2={b} iterations=35 messageSize=256 compute=3ns"}
    )

# -----------------------------------------------------------------------------
# 7. BUILD THE JOB  (size == num_nodes == 2*num_routers  =>  PPN = 2)
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
# 8. STATISTICS  ->  one CSV per shape  (filename marks ppn2)
# -----------------------------------------------------------------------------
csv_path = os.path.join(out_dir, f"mesh_{shape}_ppn{PPN}_nodes{num_nodes}_stats.csv")

sst.setStatisticLoadLevel(10)
sst.setStatisticOutput("sst.statOutputCSV", {"filepath": csv_path, "separator": ", "})

sst.enableAllStatisticsForComponentType("merlin.hr_router")
sst.enableAllStatisticsForComponentType("merlin.linkcontrol")
sst.enableAllStatisticsForComponentType("ember.EmberEngine", {"MotifLog": "1"})
sst.enableAllStatisticsForComponentType("ember.nic")

# -----------------------------------------------------------------------------
# 9. CONFIG SUMMARY
# -----------------------------------------------------------------------------
print("==================================================")
print(f" Mesh shape        : {shape}")
print(f" Routers           : {num_routers}")
print(f" Nodes per router  : {nodes_per_router}  (local_ports)")
print(f" Total nodes       : {num_nodes}")
print(f" Total MPI ranks   : {num_ranks}")
print(f" PPN (ranks/node)  : {num_ranks // num_routers}   <-- should be 2")
print(f" Stats CSV         : {csv_path}")
print("==================================================")
