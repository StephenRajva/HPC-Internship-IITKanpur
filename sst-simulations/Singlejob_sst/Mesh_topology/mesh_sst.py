import sst

from sst.merlin.base import *
from sst.merlin.endpoint import *
from sst.merlin.interface import *
from sst.merlin.topology import *

from sst.ember import *

PlatformDefinition.setCurrentPlatform("firefly-defaults")

### Setup the topology ###
topo = topoMesh()
topo.shape = "2x2"
topo.width = "1x1"
topo.local_ports = 1 
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
num_mpi_ranks = topo.getNumNodes()
ep = EmberMPIJob(0, num_mpi_ranks)
ep.network_interface = networkif 

ep.addMotif("Init")   
ep.addMotif("Allreduce messageSize=1024")
ep.addMotif("Fini")    

# Overwrite one of the defaults from firefly-defaults (NIC to host latency)
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
    "filepath": "mesh_stats.csv",
    "separator": ", "          
})
sst.enableAllStatisticsForComponentType("merlin.hr_router")
sst.enableAllStatisticsForComponentType("merlin.link_control")
sst.enableAllStatisticsForComponentType("ember.nic")
