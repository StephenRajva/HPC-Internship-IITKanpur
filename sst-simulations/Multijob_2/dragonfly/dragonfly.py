import sst
from sst.merlin.base import *
from sst.merlin.endpoint import *
from sst.merlin.interface import *
from sst.merlin.topology import *
from sst.ember import *

# Setup platform and topology
PlatformDefinition.setCurrentPlatform("firefly-defaults")

# Configure 512-node Dragonfly (16 groups, 8 routers/group, 4 hosts/router)
topo = topoDragonFly()
topo.hosts_per_router = 4
topo.routers_per_group = 8
topo.num_groups = 16
topo.intergroup_links = 4
topo.algorithm = ["ugal", "ugal"]
topo.link_latency = "25ns"

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

# Job definitions
jobs = [
    # Job 1: 16-rank Allreduce 
    {"size": 16, "start": 0, "pattern": "Allreduce", "params": "arg.count=512 arg.iterations=1 arg.compute=1"},
    # Job 2: 64-rank Alltoall 
    {"size": 64, "start": 16, "pattern": "Alltoall", "params": "arg.bytes=512 arg.iterations=1 arg.compute=1"},
    # Job 3: 32-rank Scatter 
    {"size": 32, "start": 80, "pattern": "Scatter", "params": "arg.root=0 arg.count=512 arg.iterations=1 arg.compute=1"},
    # Job 4: 64-rank Broadcast
    {"size": 64, "start": 112, "pattern": "Bcast", "params": "arg.root=0 arg.count=512 arg.iterations=1 arg.compute=1"}
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
    endpoints.append(ep)  # Keep track of endpoints

# Build the system
system.build()

# Statistics configuration
sst.setStatisticLoadLevel(8)
sst.setStatisticOutput("sst.statOutputCSV", {
    "filepath": "dragonfly_stats.csv",
    "separator": ", "
})

# Enable statistics for component types
sst.enableAllStatisticsForComponentType("merlin.hr_router")
sst.enableAllStatisticsForComponentType("merlin.linkcontrol")
sst.enableAllStatisticsForComponentType("ember.nic")


# Add debug outputS
print("Simulation configured with:")
print(f"- {len(jobs)} jobs")
print(f"- Total ranks: {sum(job['size'] for job in jobs)}")
print(f"- Dragonfly topology: {topo.num_groups} groups x {topo.routers_per_group} routers x {topo.hosts_per_router} hosts")