import sst

from sst.merlin.base import *
from sst.merlin.endpoint import *
from sst.merlin.interface import *
from sst.merlin.topology import *

from sst.ember import *

# Include the firefly defaults to get default parameters for NIC and network stack.
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

# Create the Ember MPI job
ep = EmberMPIJob(0, topo.getNumNodes())
ep.network_interface = networkif
ep.addMotif("Init")    
ep.addMotif("Allreduce") 
ep.addMotif("Fini")    
ep.nic.nic2host_lat = "100ns"

# Create the system object
system = System()
system.setTopology(topo)
system.allocateNodes(ep, "linear")
system.build()

### Statistics Configuration ###
sst.setStatisticLoadLevel(9)

sst.setStatisticOutput("sst.statOutputCSV")
sst.setStatisticOutputOptions({
    "filepath": "dragonfly.csv",
    "separator": ", "               
})

sst.enableAllStatisticsForComponentType("merlin.hr_router")
sst.enableAllStatisticsForComponentType("merlin.link_control")
sst.enableAllStatisticsForComponentType("ember.nic")
