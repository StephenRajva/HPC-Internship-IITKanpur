import sst
from sst.merlin.base import *
from sst.merlin.endpoint import *
from sst.merlin.interface import *
from sst.merlin.topology import *
from sst.ember import *

# =====================================================================
#  Mesh 32x32  -  PPN (MPI ranks per node) FIXED at 1
#  nodes = 1024  (routers 1024 x local_ports 1)
#  ranks = 1024  -> ranks == nodes  => PPN = 1
# =====================================================================

PlatformDefinition.setCurrentPlatform("firefly-defaults")

topo              = topoMesh()
topo.shape        = "32x32"
topo.local_ports  = 1            # 1 node per router  (keeps PPN study clean)
topo.width        = "1x1"    # 1 link per dimension = standard mesh
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

# size == number of nodes  =>  PPN = 1
job = {
    "size": 1024,
    "start": 0,
    "motifs": [
        {"pattern": "Allreduce", "params": "iterations=92 count=1 compute=69ns"},
        {"pattern": "Bcast",     "params": "root=0 iterations=2 count=7 compute=1323ns"},
        {"pattern": "Reduce",    "params": "root=0 iterations=2 count=2 compute=450ns"},
        {"pattern": "Allgather", "params": "iterations=3 count=3 compute=243ns verify=0"},
        {"pattern": "Barrier",   "params": "iterations=99 compute=75ns"},
    ]
}

# representative PingPong partners that exist for this size (rank2 < size)
for b in [1, 32, 512, 1023]:
    job["motifs"].append(
        {"pattern": "PingPong", "params": f"rank2={b} iterations=35 messageSize=256 compute=3ns"}
    )

ep = EmberMPIJob(0, job["size"])
ep.network_interface = nic
ep.addMotif("Init")
for m in job["motifs"]:
    ep.addMotif(f"{m['pattern']} {m['params']}")
ep.addMotif("Fini")
ep.nic.nic2host_lat = "100ns"

system.allocateNodes(ep, "linear")
system.build()

sst.setStatisticLoadLevel(10)
sst.setStatisticOutput("sst.statOutputCSV", {
    "filepath": "mesh_32x32_ppn1_stats.csv",
    "separator": ", "
})

sst.enableAllStatisticsForComponentType("merlin.hr_router")
sst.enableAllStatisticsForComponentType("merlin.linkcontrol")
sst.enableAllStatisticsForComponentType("ember.EmberEngine", {"MotifLog": "1"})
sst.enableAllStatisticsForComponentType("ember.nic")
