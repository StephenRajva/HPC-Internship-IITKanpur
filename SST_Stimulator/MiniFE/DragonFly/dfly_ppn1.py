#!/usr/bin/env python
# =============================================================================
#  dfly_ppn1.py  -  MiniFE on a Dragonfly, PPN (ranks per node) = 1
# =============================================================================
#  Dragonfly node count = hosts_per_router * routers_per_group * num_groups.
#  To keep PPN = 1 we FIX hosts_per_router = 1, so each router holds one node,
#  and we grow the GROUP structure to reach the target size:
#
#      size  routers_per_group  num_groups  nodes
#        4          2               2         4
#       16          4               4        16
#       64          8               8        64
#
#  job["size"] = nodes  ->  PPN = nodes/nodes = 1.
#
#  USAGE:  export DFLY_SIZE="16"   (then) sst dfly_ppn1.py
#  The runner loops over all sizes.
# =============================================================================

import sst, os
from sst.merlin.base import *
from sst.merlin.endpoint import *
from sst.merlin.interface import *
from sst.merlin.topology import *
from sst.ember import *

# size label -> (routers_per_group, num_groups), all with hosts_per_router = 1
SIZE_TABLE = {
    "4":  (2, 2),
    "16": (4, 4),
    "64": (8, 8),
}

size_label = os.environ.get("DFLY_SIZE", "16")
out_dir    = os.environ.get("STATS_DIR", ".")
if size_label not in SIZE_TABLE:
    raise SystemExit(f"DFLY_SIZE must be one of {list(SIZE_TABLE)}, got '{size_label}'")

hosts_per_router      = 1                       # FIXED -> PPN = 1
routers_per_group, num_groups = SIZE_TABLE[size_label]
num_nodes = hosts_per_router * routers_per_group * num_groups
num_ranks = num_nodes                           # PPN = 1

PlatformDefinition.setCurrentPlatform("firefly-defaults")

topo                  = topoDragonFly()
topo.hosts_per_router = hosts_per_router
topo.routers_per_group = routers_per_group
topo.num_groups       = num_groups
topo.intergroup_links = 2                       # kept from your original configs
topo.link_latency     = "25ns"
topo.algorithm        = "minimal"

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

# MiniFE motifs (same collectives as mesh/torus so the comparison is fair)
motifs = [
    {"pattern": "Allreduce", "params": "iterations=92 count=1 compute=69ns"},
    {"pattern": "Bcast",     "params": "root=0 iterations=2 count=7 compute=1323ns"},
    {"pattern": "Reduce",    "params": "root=0 iterations=2 count=2 compute=450ns"},
    {"pattern": "Allgather", "params": "iterations=3 count=3 compute=243ns verify=0"},
    {"pattern": "Barrier",   "params": "iterations=99 compute=75ns"},
]
candidates = [1, num_nodes // 2, num_nodes - 1]
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

csv_path = os.path.join(out_dir, f"dragonfly_{size_label}_ppn1_nodes{num_nodes}_stats.csv")
sst.setStatisticLoadLevel(10)
sst.setStatisticOutput("sst.statOutputCSV", {"filepath": csv_path, "separator": ", "})
sst.enableAllStatisticsForComponentType("merlin.hr_router")
sst.enableAllStatisticsForComponentType("merlin.linkcontrol")
sst.enableAllStatisticsForComponentType("ember.EmberEngine", {"MotifLog": "1"})
sst.enableAllStatisticsForComponentType("ember.nic")

print("==================================================")
print(f" Topology          : Dragonfly (size {size_label})")
print(f" hosts_per_router  : {hosts_per_router}")
print(f" routers_per_group : {routers_per_group}")
print(f" num_groups        : {num_groups}")
print(f" Total nodes       : {num_nodes}")
print(f" Total MPI ranks   : {num_ranks}")
print(f" PPN (ranks/node)  : {num_ranks // num_nodes}   <-- should be 1")
print(f" Stats CSV         : {csv_path}")
print("==================================================")
