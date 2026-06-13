import sst
from sst.merlin.base import *
from sst.merlin.endpoint import *
from sst.merlin.interface import *
from sst.merlin.topology import *
from sst.ember import *


PlatformDefinition.setCurrentPlatform("firefly-defaults")

### Configure PolarFly topology  ###
q = 25  
topo = topoPolarFly(q=q)
topo.network_name = "polarfly_network"
topo.hosts_per_router = 1 
topo.total_radix = q + 1
topo.algorithm = "UGAL"
topo.link_latency = "20ns"

# Calculate topology size
total_routers = q*q + q + 1  
required_nodes = 651
hosts_per_router = (required_nodes + total_routers - 1) // total_routers
actual_nodes = total_routers * hosts_per_router

print(f"PolarFly Configuration:")
print(f"- q parameter: {q}")
print(f"- Total routers: {total_routers}")
print(f"- Hosts per router: {hosts_per_router}")



topo.hosts_per_router = hosts_per_router
topo.total_routers = total_routers
topo.total_endnodes = actual_nodes

# Set up the router 
router = hr_router()
router.link_bw = "12GB/s"     
router.flit_size = "16B"       
router.xbar_bw = "20GB/s"      
router.input_latency = "30ns" 
router.output_latency = "30ns"
router.input_buf_size = "16kB" 
router.output_buf_size = "16kB"
router.num_vns = 1     
router.xbar_arb = "merlin.xbar_arb_lru" 
topo.router = router

# Set up the network interface 
networkif = ReorderLinkControl()
networkif.link_bw = "12GB/s"        
networkif.input_buf_size = "16kB"  
networkif.output_buf_size = "16kB" 

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
    ep.network_interface = networkif
    ep.addMotif("Init")
    ep.addMotif(f"{job['pattern']} {job['params']}")
    ep.addMotif("Fini")
    ep.nic.nic2host_lat = "100ns"
    system.allocateNodes(ep, "linear")
    endpoints.append(ep)

system.build()

# Statistics configuration
sst.setStatisticLoadLevel(9)
sst.setStatisticOutput("sst.statOutputCSV", {
    "filepath": "polarfly_stats.csv",
    "separator": ", "
})

# Explicitly enable critical statistics
sst.enableAllStatisticsForComponentType("merlin.hr_router")
sst.enableAllStatisticsForComponentType("merlin.link_control")
sst.enableAllStatisticsForComponentType("ember.nic")

sst.enableAllStatisticsForComponentType("merlin.polarfly")

print("\n=== Job Configuration ===")
print(f"Total jobs: {len(jobs)}")
print(f"Total ranks: {sum(job['size'] for job in jobs)}")
for i, job in enumerate(jobs):
    print(f"Job {i+1}: {job['size']} ranks, {job['pattern']} ({job['params']})")