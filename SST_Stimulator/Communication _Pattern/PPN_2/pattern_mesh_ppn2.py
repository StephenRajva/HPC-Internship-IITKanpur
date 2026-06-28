#!/usr/bin/env python
# =============================================================================
#  pattern_mesh_ppn2.py  -  Communication-pattern distance signature on a Mesh
#  PPN = 2.  Two hosts per router (local_ports=2), single job, linear allocation
#  (rank i -> node i), one PingPong between rank 0 and its pattern-partner.
#  Same router grid (shape) as the PPN=1 study; node/rank count doubles.
#
#    adjacent  -> rank 0 <-> rank 1      (nearest neighbour)
#    halfshift -> rank 0 <-> rank N/2    (half-way across)
#    mirrored  -> rank 0 <-> rank N-1    (opposite corner)
#
#  USAGE: export MESH_SHAPE="4x4"; export PATTERN="halfshift"; sst pattern_mesh_ppn2.py
# =============================================================================

import sst, os
from sst.merlin.base import *
from sst.merlin.endpoint import *
from sst.merlin.interface import *
from sst.merlin.topology import *
from sst.ember import *

PPN              = 2
shape            = os.environ.get("MESH_SHAPE", "4x4")
pattern          = os.environ.get("PATTERN", "adjacent").lower()
out_dir          = os.environ.get("STATS_DIR", ".")
nodes_per_router = PPN                       # local_ports = 2
msg_size = 256
iters    = 35

dims = [int(x) for x in shape.lower().split("x")]
num_routers = 1
for d in dims:
    num_routers *= d
N = num_routers * nodes_per_router           # nodes == ranks; PPN = N/num_routers = 2

if   pattern == "adjacent":  partner = 1
elif pattern == "halfshift": partner = N // 2
elif pattern == "mirrored":  partner = N - 1
else: raise SystemExit(f"Unknown PATTERN '{pattern}'")

# representative mesh distance (Manhattan) between node 0 and node `partner`.
# With 2 hosts per router, node id -> router id is nid // nodes_per_router;
# the geometric distance is measured between the two routers.
def coord(router_id):
    c, rem = [], router_id
    for d in dims:
        c.append(rem % d); rem //= d
    return c
def manhattan(a, b):
    return sum(abs(x - y) for x, y in zip(coord(a), coord(b)))
rep_hops = manhattan(0 // nodes_per_router, partner // nodes_per_router)

PlatformDefinition.setCurrentPlatform("firefly-defaults")

topo              = topoMesh()
topo.shape        = shape
topo.local_ports  = nodes_per_router
topo.width        = "x".join(["1"] * len(dims))
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

ep = EmberMPIJob(0, N)
ep.network_interface = nic
ep.addMotif("Init")
ep.addMotif(f"PingPong rank2={partner} messageSize={msg_size} iterations={iters} compute=3ns")
ep.addMotif("Fini")
ep.nic.nic2host_lat = "100ns"
system.allocateNodes(ep, "linear")
system.build()

csv_path = os.path.join(out_dir, f"{pattern}_mesh_{shape}_ppn2_nodes{N}_stats.csv")
sst.setStatisticLoadLevel(10)
sst.setStatisticOutput("sst.statOutputCSV", {"filepath": csv_path, "separator": ", "})
sst.enableAllStatisticsForComponentType("merlin.hr_router")
sst.enableAllStatisticsForComponentType("merlin.linkcontrol")
sst.enableAllStatisticsForComponentType("ember.EmberEngine", {"MotifLog": "1"})
sst.enableAllStatisticsForComponentType("ember.nic")

print("==================================================")
print(f" Pattern           : {pattern}")
print(f" Topology          : Mesh {shape}  ({num_routers} routers, {N} nodes, PPN=2)")
print(f" Exchange          : rank 0  <->  rank {partner}")
print(f" Representative hops: {rep_hops}  (Manhattan dist between routers)")
print(f" PPN (ranks/router): {N // num_routers}   <-- should be 2")
print(f" Stats CSV         : {csv_path}")
print("==================================================")
