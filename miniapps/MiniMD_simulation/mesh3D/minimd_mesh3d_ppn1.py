#!/usr/bin/env python
# =============================================================================
#  minimd_mesh3d_ppn1.py  -  MiniMD on a 3D mesh, PPN (ranks per node) = 1
# =============================================================================
#  Same idea as the MiniFE study, but:
#    * the topology is 3D  (shape like "4x4x4")
#    * the workload is the MiniMD pattern (neighbor halo exchange + collectives)
#
#  PPN = ranks / nodes = job_size / (routers * local_ports).
#  We set job_size = nodes, so PPN is ALWAYS 1.
#
#  USAGE (one shape per run, chosen with an environment variable):
#        export MESH_SHAPE="4x4x4"
#        sst minimd_mesh3d_ppn1.py
#  The runner script loops over all the shapes for you.
# =============================================================================

import sst
import os
from sst.merlin.base import *
from sst.merlin.endpoint import *
from sst.merlin.interface import *
from sst.merlin.topology import *
from sst.ember import *

# ---- parameters -------------------------------------------------------------
PPN              = 1
shape            = os.environ.get("MESH_SHAPE", "2x2x4")   # 3 numbers: XxYxZ
nodes_per_router = 1
out_dir          = os.environ.get("STATS_DIR", ".")

dims        = [int(x) for x in shape.lower().split("x")]
num_routers = 1
for d in dims:
    num_routers *= d
num_nodes = num_routers * nodes_per_router
num_ranks = num_nodes * PPN                      # PPN=1 -> ranks == nodes

PlatformDefinition.setCurrentPlatform("firefly-defaults")

# ---- topology (3D mesh) -----------------------------------------------------
topo              = topoMesh()
topo.shape        = shape
topo.local_ports  = nodes_per_router
topo.width        = "x".join(["1"] * len(dims))  # "1x1x1" for 3D
topo.link_latency = "20ns"

# ---- router -----------------------------------------------------------------
router                 = hr_router()
router.link_bw         = "12GB/s"
router.flit_size       = "16B"
router.xbar_bw         = "24GB/s"
router.input_latency   = "20ns"
router.output_latency  = "20ns"
router.input_buf_size  = "16kB"
router.output_buf_size = "16kB"
router.num_vns         = 2
router.xbar_arb        = "merlin.xbar_arb_lru"
topo.router = router

# ---- NIC --------------------------------------------------------------------
nic                 = ReorderLinkControl()
nic.link_bw         = "12GB/s"
nic.input_buf_size  = "16kB"
nic.output_buf_size = "16kB"

system = System()
system.setTopology(topo)

# ---- MiniMD workload (same motifs as your TAU-profiled run) -----------------
motifs = [
    {"pattern": "AllPingPong", "params": "iterations=325 messageSize=20510 computetime=476000"},
    {"pattern": "AllPingPong", "params": "iterations=325 messageSize=9000  computetime=476000"},
    {"pattern": "AllPingPong", "params": "iterations=325 messageSize=20510 computetime=476000"},
    {"pattern": "AllPingPong", "params": "iterations=325 messageSize=9000  computetime=476000"},
    {"pattern": "Allreduce",   "params": "count=1 iterations=40 compute=2451000"},
    {"pattern": "Barrier",     "params": "iterations=15 compute=1392000"},
]

ep = EmberMPIJob(0, num_ranks)
ep.network_interface = nic
ep.addMotif("Init")
for m in motifs:
    ep.addMotif(f"{m['pattern']} {m['params']}")
ep.addMotif("Fini")
ep.nic.nic2host_lat = "100ns"

system.allocateNodes(ep, "linear")
system.build()

# ---- statistics -> one CSV per shape ----------------------------------------
csv_path = os.path.join(out_dir, f"minimd_mesh_{shape}_ppn{PPN}_nodes{num_nodes}_stats.csv")

sst.setStatisticLoadLevel(10)
sst.setStatisticOutput("sst.statOutputCSV", {"filepath": csv_path, "separator": ", "})

sst.enableAllStatisticsForComponentType("merlin.hr_router")
sst.enableAllStatisticsForComponentType("merlin.linkcontrol")
sst.enableAllStatisticsForComponentType("ember.EmberEngine", {"MotifLog": "1"})
sst.enableAllStatisticsForComponentType("ember.nic")

# ---- summary print (verify PPN at a glance) ---------------------------------
print("==================================================")
print(f" Topology          : 3D Mesh {shape}")
print(f" Routers           : {num_routers}")
print(f" Total nodes       : {num_nodes}")
print(f" Total MPI ranks   : {num_ranks}")
print(f" PPN (ranks/node)  : {num_ranks // num_nodes}   <-- should be 1")
print(f" Stats CSV         : {csv_path}")
print("==================================================")
