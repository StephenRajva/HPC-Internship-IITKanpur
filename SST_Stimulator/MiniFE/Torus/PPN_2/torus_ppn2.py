#!/usr/bin/env python
# =============================================================================
#  torus_ppn2.py  -  MiniFE on a Torus, PPN (ranks per node) = 2
# =============================================================================
#  Same study as torus_ppn1.py (topoTorus, wraparound links), but 2 hosts per
#  router so PPN = 2. The router grid / size label stays the same as PPN=1;
#  only host density (local_ports) and the job size double.
#
#        PPN = ranks / routers = (2 * num_routers) / num_routers = 2
#
#  USAGE:  export MESH_SHAPE="4x4"   (then) sst torus_ppn2.py
#  The runner run_torus_sweep_ppn2.sh loops over all shapes.
# =============================================================================

import sst, os
from sst.merlin.base import *
from sst.merlin.endpoint import *
from sst.merlin.interface import *
from sst.merlin.topology import *
from sst.ember import *

PPN              = 2
shape            = os.environ.get("MESH_SHAPE", "4x4")
nodes_per_router = PPN                              # local_ports = 2 hosts per router
out_dir          = os.environ.get("STATS_DIR", ".")

dims        = [int(x) for x in shape.lower().split("x")]
num_routers = 1
for d in dims:
    num_routers *= d
num_nodes = num_routers * nodes_per_router          # PPN=2 -> 2 hosts per router
num_ranks = num_nodes                               # one rank per host -> ranks == nodes
# PPN = num_ranks / num_routers = 2

PlatformDefinition.setCurrentPlatform("firefly-defaults")

topo              = topoTorus()
topo.shape        = shape
topo.local_ports  = nodes_per_router
topo.width        = "x".join(["1"] * len(dims))    # 1 link per dim (matches mesh study)
topo.link_latency = "25ns"

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

nic                 = ReorderLinkControl()
nic.link_bw         = "12GB/s"
nic.input_buf_size  = "16kB"
nic.output_buf_size = "16kB"

system = System()
system.setTopology(topo)

# MiniFE motifs (identical to the mesh + PPN=1 torus study so the comparison is fair)
motifs = [
    {"pattern": "Allreduce", "params": "iterations=92 count=1 compute=69ns"},
    {"pattern": "Bcast",     "params": "root=0 iterations=2 count=7 compute=1323ns"},
    {"pattern": "Reduce",    "params": "root=0 iterations=2 count=2 compute=450ns"},
    {"pattern": "Allgather", "params": "iterations=3 count=3 compute=243ns verify=0"},
    {"pattern": "Barrier",   "params": "iterations=99 compute=75ns"},
]
row_step  = dims[-1] if len(dims) >= 2 else 1
candidates = [1, row_step, num_nodes // 2, num_nodes - 1]
partners   = sorted({p for p in candidates if 0 < p < num_ranks})
for b in partners:
    motifs.append({"pattern": "PingPong",
                   "params": f"rank2={b} iterations=35 messageSize=256 compute=3ns"})

ep = EmberMPIJob(0, num_ranks)
ep.network_interface = nic
ep.addMotif("Init")
for m in motifs:
    ep.addMotif(f"{m['pattern']} {m['params']}")
ep.addMotif("Fini")
ep.nic.nic2host_lat = "100ns"

system.allocateNodes(ep, "linear")
system.build()

csv_path = os.path.join(out_dir, f"torus_{shape}_ppn{PPN}_nodes{num_nodes}_stats.csv")
sst.setStatisticLoadLevel(10)
sst.setStatisticOutput("sst.statOutputCSV", {"filepath": csv_path, "separator": ", "})
sst.enableAllStatisticsForComponentType("merlin.hr_router")
sst.enableAllStatisticsForComponentType("merlin.linkcontrol")
sst.enableAllStatisticsForComponentType("ember.EmberEngine", {"MotifLog": "1"})
sst.enableAllStatisticsForComponentType("ember.nic")

print("==================================================")
print(f" Topology          : Torus {shape}")
print(f" Routers           : {num_routers}")
print(f" Nodes per router  : {nodes_per_router}  (local_ports)")
print(f" Total nodes       : {num_nodes}")
print(f" Total MPI ranks   : {num_ranks}")
print(f" PPN (ranks/node)  : {num_ranks // num_routers}   <-- should be 2")
print(f" Stats CSV         : {csv_path}")
print("==================================================")
