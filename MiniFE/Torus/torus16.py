import sst
from sst.merlin.base import *
from sst.merlin.endpoint import *
from sst.merlin.interface import *
from sst.merlin.topology import *
from sst.ember import *

PlatformDefinition.setCurrentPlatform("firefly-defaults")

topo = topoTorus()
topo.shape = "4x4"
topo.local_ports = 1
topo.width = "4x4"
topo.link_latency = "25ns"

router = hr_router()
router.link_bw = "12GB/s"
router.flit_size = "16B"
router.xbar_bw = "20GB/s"
router.input_latency = "30ns"
router.output_latency = "30ns"
router.input_buf_size = "32kB"
router.output_buf_size = "32kB"
router.num_vns = 2
router.xbar_arb = "merlin.xbar_arb_lru"
topo.router = router

nic = ReorderLinkControl()
nic.link_bw = "12GB/s"
nic.input_buf_size = "16kB"
nic.output_buf_size = "16kB"

system = System()
system.setTopology(topo)

job = {
    "size": 16,
    "start": 0,
    "motifs": [
        {"pattern": "Allreduce", "params": "iterations=92 count=1 compute=69ns"},
        {"pattern": "Bcast", "params": "root=0 iterations=2 count=7 compute=1323ns"},
        {"pattern": "Reduce", "params": "root=0 iterations=2 count=2 compute=450ns"},
        {"pattern": "Allgather", "params": "iterations=3 count=3 compute=243ns verify=0"},
        {"pattern": "Barrier", "params": "iterations=99 compute=75ns"},

        {"pattern": "PingPong", "params": "rank2=1 iterations=35 messageSize=409 compute=3ns"},
        {"pattern": "PingPong", "params": "rank2=2 iterations=35 messageSize=409 compute=3ns"},
        {"pattern": "PingPong", "params": "rank2=3 iterations=35 messageSize=82 compute=3ns"},
        {"pattern": "PingPong", "params": "rank2=2 iterations=35 messageSize=82 compute=3ns"},
        {"pattern": "PingPong", "params": "rank2=3 iterations=35 messageSize=490 compute=3ns"},
        {"pattern": "PingPong", "params": "rank2=3 iterations=35 messageSize=490 compute=3ns"}
    ]
}

ep = EmberMPIJob(0, job["size"])
ep.network_interface = nic

ep.addMotif("Init")

for motif in job["motifs"]:
    ep.addMotif(f"{motif['pattern']} {motif['params']}")

ep.addMotif("Fini")

ep.nic.nic2host_lat = "100ns"

system.allocateNodes(ep, "linear")

system.build()

sst.setStatisticLoadLevel(10)

sst.setStatisticOutput("sst.statOutputCSV", {
	"filepath": "miniFE_communication_stats_torus16.csv",
	"separator": ", "
})

sst.enableAllStatisticsForComponentType("merlin.hr_router")
sst.enableAllStatisticsForComponentType("merlin.linkcontrol")

sst.enableAllStatisticsForComponentType("ember.EmberEngine", {
    "MotifLog": "1"
})

sst.enableAllStatisticsForComponentType("ember.nic")
