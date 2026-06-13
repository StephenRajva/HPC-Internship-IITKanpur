import sst
from sst.merlin.base import *
from sst.merlin.endpoint import *
from sst.merlin.interface import *
from sst.merlin.topology import *
from sst.ember import *


PlatformDefinition.setCurrentPlatform("firefly-defaults")

# Configure 2D Mesh topology for 1024 nodes
topo = topoMesh()
topo.shape = "32x32"         # 32x32 = 1024 routers
topo.local_ports = 1         # 1 host per router (1024 total nodes)
topo.width = "4x4"           # Link width in each dimension
topo.link_latency = "25ns"   # Inter-router link latency

# Router configuration
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

# Network interface 
nic = ReorderLinkControl()
nic.link_bw = "12GB/s"
nic.input_buf_size = "16kB"
nic.output_buf_size = "16kB"


# Create system
system = System()
system.setTopology(topo)

#  Job definitions 256 ranks
jobs = [
    {"size": 32, "start": 0, "pattern": "Allreduce", "params": "arg.count=2048 arg.iterations=20 arg.compute=50ns"},
    {"size": 60, "start": 32, "pattern": "Alltoall", "params": "arg.bytes=1024 arg.iterations=10 arg.compute=100ns"},
    {"size": 64, "start": 92, "pattern": "Barrier", "params": "arg.iterations=30"},
    {"size": 32, "start": 156, "pattern": "Scatter", "params": "arg.root=0 arg.count=4096 arg.iterations=5 arg.compute=150ns"},
    {"size": 66, "start": 188, "pattern": "Bcast", "params": "arg.root=0 arg.count=8192 arg.iterations=8 arg.compute=75ns"},
    {"size": 2, "start": 254, "pattern": "PingPong", "params": "arg.messageSize=1024 arg.iterations=15 arg.rank2=1"}
]

# Verify total ranks
total_ranks = sum(job["size"] for job in jobs)
if total_ranks != 256:
    print(f"Error: Total ranks ({total_ranks}) does not equal 256! Exiting.")
    exit(1)

# Create and assign jobs
endpoints = []
current_start_rank = 0
for job in jobs:
    ep = EmberMPIJob(current_start_rank, job["size"]) 
    ep.network_interface = nic
    
    
    ep.addMotif("Init")
    ep.addMotif(f"{job['pattern']} {job['params']}")
    ep.addMotif("Fini")
    
    ep.nic.nic2host_lat = "100ns"
    
    system.allocateNodes(ep, "random")
    endpoints.append(ep)
    current_start_rank += job["size"] 

system.build()

# Statistics configuration
sst.setStatisticLoadLevel(8)
sst.setStatisticOutput("sst.statOutputCSV", {
    "filepath": "mesh_stats.csv",
    "separator": ", "
})

sst.enableAllStatisticsForComponentType("merlin.hr_router")
sst.enableAllStatisticsForComponentType("merlin.linkcontrol")
sst.enableAllStatisticsForComponentType("ember.nic")

print("Simulation Configuration:")
print(f"- Topology: 2D {topo.shape} Mesh")
print(f"- Total routers: {32*32} = 1024")
print(f"- Total compute nodes: {1024}")
print(f"- Jobs configured: {len(jobs)} jobs with sizes: {', '.join(str(job['size']) for job in jobs)}")
print(f"- Total ranks: {total_ranks}")

