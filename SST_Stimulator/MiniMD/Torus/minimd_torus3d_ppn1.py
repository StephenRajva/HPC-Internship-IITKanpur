#!/usr/bin/env python
# =============================================================================
#  minimd_torus3d_ppn1.py  -  MiniMD on a 3D Torus, PPN (ranks per node) = 1
# =============================================================================
#  3D torus (wraparound links). PPN = ranks/nodes = size/(routers*local_ports).
#  We set size = nodes, so PPN is ALWAYS 1.
#
#  USAGE:  export MESH_SHAPE="4x4x4"   (then) sst minimd_torus3d_ppn1.py
#  The runner loops over all shapes.
# =============================================================================

import sst, os
from sst.merlin.base import *
from sst.merlin.endpoint import *
from sst.merlin.interface import *
from sst.merlin.topology import *
from sst.ember import *

PPN              = 1
shape            = os.environ.get("MESH_SHAPE", "2x2x4")
nodes_per_router = 1
out_dir          = os.environ.get("STATS_DIR", ".")

dims        = [int(x) for x in shape.lower().split("x")]
num_routers = 1
for d in dims:
    num_routers *= d
num_nodes = num_routers * nodes_per_router
num_ranks = num_nodes * PPN                      # PPN=1 -> ranks == nodes

PlatformDefinition.setCurrentPlatform("firefly-defaults")

topo              = topoTorus()
topo.shape        = shape
topo.local_ports  = nodes_per_router
topo.width        = "x".join(["1"] * len(dims))   # "1x1x1" for 3D
topo.link_latency = "25ns"

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

nic                 = ReorderLinkControl()
nic.link_bw         = "12GB/s"
nic.input_buf_size  = "16kB"
nic.output_buf_size = "16kB"

system = System()
system.setTopology(topo)

# MiniMD motifs (identical to your TAU-profiled run, so comparison is fair)
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

csv_path = os.path.join(out_dir, f"minimd_torus_{shape}_ppn{PPN}_nodes{num_nodes}_stats.csv")
sst.setStatisticLoadLevel(10)
sst.setStatisticOutput("sst.statOutputCSV", {"filepath": csv_path, "separator": ", "})
sst.enableAllStatisticsForComponentType("merlin.hr_router")
sst.enableAllStatisticsForComponentType("merlin.linkcontrol")
sst.enableAllStatisticsForComponentType("ember.EmberEngine", {"MotifLog": "1"})
sst.enableAllStatisticsForComponentType("ember.nic")

print("==================================================")
print(f" Topology          : 3D Torus {shape}")
print(f" Routers           : {num_routers}")
print(f" Total nodes       : {num_nodes}")
print(f" Total MPI ranks   : {num_ranks}")
print(f" PPN (ranks/node)  : {num_ranks // num_nodes}   <-- should be 1")
print(f" Stats CSV         : {csv_path}")
print("==================================================")
