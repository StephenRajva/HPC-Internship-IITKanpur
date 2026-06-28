#!/usr/bin/env python
# =============================================================================
#  minimd_dfly_ppn2.py  -  MiniMD on a Dragonfly, PPN (ranks per node) = 2
# =============================================================================
#  Same group structure as minimd_dfly_ppn1.py, but hosts_per_router = 2,
#  so each router holds two nodes -> PPN = 2. Same "size" labels (4/16/64).
#      size  routers_per_group  num_groups  hosts/router  nodes
#        4          2               2            2          8
#       16          4               4            2         32
#       64          8               8            2        128
#  PPN = nodes / routers = (2 * rpg * groups) / (rpg * groups) = 2.
#
#  USAGE:  export DFLY_SIZE="16"   (then) sst minimd_dfly_ppn2.py
# =============================================================================
import sst, os
from sst.merlin.base import *
from sst.merlin.endpoint import *
from sst.merlin.interface import *
from sst.merlin.topology import *
from sst.ember import *

SIZE_TABLE = {            # size label -> (routers_per_group, num_groups)
    "4":  (2, 2),
    "16": (4, 4),
    "64": (8, 8),
}

size_label = os.environ.get("DFLY_SIZE", "16")
out_dir    = os.environ.get("STATS_DIR", ".")
if size_label not in SIZE_TABLE:
    raise SystemExit(f"DFLY_SIZE must be one of {list(SIZE_TABLE)}, got '{size_label}'")

hosts_per_router = 2                              # <-- PPN = 2
routers_per_group, num_groups = SIZE_TABLE[size_label]
num_routers = routers_per_group * num_groups
num_nodes   = hosts_per_router * routers_per_group * num_groups
num_ranks   = num_nodes                           # PPN = 2

PlatformDefinition.setCurrentPlatform("firefly-defaults")

topo                   = topoDragonFly()
topo.hosts_per_router  = hosts_per_router
topo.routers_per_group = routers_per_group
topo.num_groups        = num_groups
topo.intergroup_links  = 2
topo.link_latency      = "25ns"
topo.algorithm         = "minimal"

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

# MiniMD motifs (same as mesh/torus MiniMD runs -> fair comparison)
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

csv_path = os.path.join(out_dir, f"minimd_dragonfly_{size_label}_ppn{2}_nodes{num_nodes}_stats.csv")
sst.setStatisticLoadLevel(10)
sst.setStatisticOutput("sst.statOutputCSV", {"filepath": csv_path, "separator": ", "})
sst.enableAllStatisticsForComponentType("merlin.hr_router")
sst.enableAllStatisticsForComponentType("merlin.linkcontrol")
sst.enableAllStatisticsForComponentType("ember.EmberEngine", {"MotifLog": "1"})
sst.enableAllStatisticsForComponentType("ember.nic")

print("==================================================")
print(f" Topology          : Dragonfly (size {size_label}) - MiniMD")
print(f" hosts_per_router  : {hosts_per_router}")
print(f" routers_per_group : {routers_per_group}")
print(f" num_groups        : {num_groups}")
print(f" Total routers     : {num_routers}")
print(f" Total nodes       : {num_nodes}")
print(f" Total MPI ranks   : {num_ranks}")
print(f" PPN (ranks/node)  : {num_ranks // num_routers}   <-- should be 2")
print(f" Stats CSV         : {csv_path}")
print("==================================================")
