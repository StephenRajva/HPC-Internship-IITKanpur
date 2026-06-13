import sst

from sst.merlin.base import *
from sst.merlin.endpoint import *
from sst.merlin.interface import *
from sst.merlin.topology import *

from sst.ember import *

PlatformDefinition.setCurrentPlatform("firefly-defaults")

### Setup the topology ###
topo = topoDragonFly()
topo.hosts_per_router = 2   
topo.routers_per_group = 4 
topo.num_groups = 4         
topo.intergroup_links = 2    
topo.algorithm = ["ugal"]   
topo.link_latency = "20ns"

# Set up the router
router = hr_router()
router.link_bw = "4GB/s"
router.flit_size = "8B"
router.xbar_bw = "6GB/s"
router.input_latency = "20ns"
router.output_latency = "20ns"
router.input_buf_size = "4kB"
router.output_buf_size = "4kB"
router.num_vns = 1           
router.xbar_arb = "merlin.xbar_arb_lru"

topo.router = router

# set up the network interface
networkif = ReorderLinkControl()
networkif.link_bw = "4GB/s"
networkif.input_buf_size = "4kB"
networkif.output_buf_size = "4kB"

# Create the System object
system = System()
system.setTopology(topo)

# --- Define Multiple Ember MPI Jobs ---

# Job 1: Allreduce on 16 ranks
# This job will use global ranks 1-16
num_mpi_ranks_job1 = 16
ep1 = EmberMPIJob(0, num_mpi_ranks_job1) 
ep1.network_interface = networkif

ep1.addMotif("Init")
ep1.addMotif("Allreduce messageSize=1024") 
ep1.addMotif("Fini")

ep1.nic.nic2host_lat = "100ns"

# Job 2: Alltoall on 16 ranks
# This job will use global ranks 17-32
num_mpi_ranks_job2 = 16
ep2 = EmberMPIJob(17, num_mpi_ranks_job2) 
ep2.network_interface = networkif

ep2.addMotif("Init")
ep2.addMotif("Alltoall messageSize=512") 
ep2.addMotif("Fini")

ep2.nic.nic2host_lat = "100ns"


system.allocateNodes(ep1, "linear") 
system.allocateNodes(ep2, "linear") 

system.build()

### Statistics Configuration ###
sst.setStatisticLoadLevel(10) 
sst.setStatisticOutput("sst.statOutputCSV")
sst.setStatisticOutputOptions({
    "filepath": "dragonfly_multi_job_stats.csv", 
    "separator": ", "
})
sst.enableAllStatisticsForComponentType("merlin.hr_router")
sst.enableAllStatisticsForComponentType("merlin.link_control")
sst.enableAllStatisticsForComponentType("ember.nic")
