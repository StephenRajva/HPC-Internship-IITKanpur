import sst
from sst.merlin.base import *
from sst.merlin.endpoint import *
from sst.merlin.interface import *
from sst.merlin.topology import *
from sst.ember import *


PlatformDefinition.setCurrentPlatform("firefly-defaults")

# Configure 2D Torus topology (8x8 with 10 hosts per router)
topo = topoTorus()
topo.shape = "8x8"         # 8 routers in each dimension
topo.local_ports = 10         # 10 hosts per router
topo.width = "1x1"         # Link width in each dimension
topo.link_latency = "25ns"   # Inter-router link latency

# Router configuration 
router = hr_router()
router.link_bw = "12GB/s"
router.flit_size = "16B"
router.xbar_bw = "20GB/s"
router.input_latency = "30ns"
router.output_latency = "30ns"
router.input_buf_size = "16kB"
router.output_buf_size = "16kB"
router.num_vns = 2
router.xbar_arb = "merlin.xbar_arb_lru"
topo.router = router

# Network interface 
nic = ReorderLinkControl()
nic.link_bw = "12GB/s"
nic.input_buf_size = "16kB"
nic.output_buf_size = "16kB"

# Create system
system = System()
system.setTopology(topo)

# Job definitions (same as Dragonfly example)
jobs = [
    # Job 1: 16-rank Allreduce 
    {"size": 32, "start": 0, "pattern": "Allreduce", "params": "arg.count=512 arg.iterations=1 arg.compute=1"},
    # Job 2: 64-rank Alltoall 
    {"size": 64, "start": 32, "pattern": "Alltoall", "params": "arg.bytes=512 arg.iterations=1 arg.compute=1"},
    # Job 3: 32-rank Scatter 
    {"size": 128, "start": 96, "pattern": "Scatter", "params": "arg.root=0 arg.count=512 arg.iterations=1 arg.compute=1"},
    # Job 4: 64-rank Broadcast
    {"size": 256, "start": 224, "pattern": "Bcast", "params": "arg.root=0 arg.count=512 arg.iterations=1 arg.compute=1"}
]

# Create and assign jobs
endpoints = []
for job in jobs:
    ep = EmberMPIJob(job["start"], job["size"])
    ep.network_interface = nic
    ep.addMotif("Init")
    ep.addMotif(f"{job['pattern']} {job['params']}")
    ep.addMotif("Fini")
    ep.nic.nic2host_lat = "100ns"
    system.allocateNodes(ep, "random")
    endpoints.append(ep)

# Build the system
system.build()

# Statistics configuration
sst.setStatisticLoadLevel(8)
sst.setStatisticOutput("sst.statOutputCSV", {
    "filepath": "torus_stats.csv",
    "separator": ", "
})

# Enable statistics for key components
sst.enableAllStatisticsForComponentType("merlin.hr_router")
sst.enableAllStatisticsForComponentType("merlin.linkcontrol")
sst.enableAllStatisticsForComponentType("ember.nic")


print("Torus Simulation Configured:")
print(f"- Topology: 2D {topo.shape} Torus")
print(f"- Hosts per router: {topo.local_ports}")
print(f"- Total compute nodes: {8*8*topo.local_ports}")
print(f"- Jobs configured: {len(jobs)} jobs, {sum(job['size'] for job in jobs)} total ranks")