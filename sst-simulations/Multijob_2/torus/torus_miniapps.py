import sst
from sst.merlin.base import *
from sst.merlin.endpoint import *
from sst.merlin.interface import *
from sst.merlin.topology import *
from sst.ember import *

PlatformDefinition.setCurrentPlatform("firefly-defaults")

# 2D Torus — 4x4 grid, 1 host per router = 16 nodes
topo = topoTorus()
topo.shape = "4x4"
topo.local_ports = 1
topo.width = "1x1"
topo.link_latency = "25ns"

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

nic = ReorderLinkControl()
nic.link_bw = "12GB/s"
nic.input_buf_size = "16kB"
nic.output_buf_size = "16kB"

system = System()
system.setTopology(topo)

# Job 1: MiniFE 8x8x8 (4 ranks)
print("=== Job 1: MiniFE 8x8x8 (4 ranks) ===")
ep1 = EmberMPIJob(0, 4)
ep1.network_interface = nic
ep1.addMotif("Init")
ep1.addMotif("Allreduce iterations=92 count=1 compute=69ns")
ep1.addMotif("Bcast root=0 iterations=2 count=7 compute=1323ns")
ep1.addMotif("Allgather iterations=3 count=3 compute=243ns verify=0")
ep1.addMotif("Barrier iterations=99 compute=75ns")
ep1.addMotif("PingPong rank2=1 iterations=35 messageSize=409 compute=3ns")
ep1.addMotif("PingPong rank2=2 iterations=35 messageSize=409 compute=3ns")
ep1.addMotif("Fini")
ep1.nic.nic2host_lat = "100ns"
system.allocateNodes(ep1, "linear")

# Job 2: MiniMD LJ (4 ranks)
print("=== Job 2: MiniMD LJ (4 ranks) ===")
ep2 = EmberMPIJob(4, 4)
ep2.network_interface = nic
ep2.addMotif("Init")
ep2.addMotif("PingPong rank2=1 iterations=325 messageSize=20510 compute=5ns")
ep2.addMotif("PingPong rank2=2 iterations=325 messageSize=9000 compute=5ns")
ep2.addMotif("Allreduce iterations=40 count=1 compute=2458ns")
ep2.addMotif("Barrier iterations=15 compute=1399ns")
ep2.addMotif("Fini")
ep2.nic.nic2host_lat = "100ns"
system.allocateNodes(ep2, "linear")

# Job 3: MiniFE 32x32x32 (4 ranks)
print("=== Job 3: MiniFE 32x32x32 (4 ranks) ===")
ep3 = EmberMPIJob(8, 4)
ep3.network_interface = nic
ep3.addMotif("Init")
ep3.addMotif("Allreduce iterations=100 count=1 compute=69ns")
ep3.addMotif("Bcast root=0 iterations=2 count=7 compute=1323ns")
ep3.addMotif("Allgather iterations=3 count=3 compute=243ns verify=0")
ep3.addMotif("Barrier iterations=100 compute=75ns")
ep3.addMotif("PingPong rank2=1 iterations=35 messageSize=4096 compute=3ns")
ep3.addMotif("Fini")
ep3.nic.nic2host_lat = "100ns"
system.allocateNodes(ep3, "linear")

# Job 4: MiniMD EAM (4 ranks)
print("=== Job 4: MiniMD EAM (4 ranks) ===")
ep4 = EmberMPIJob(12, 4)
ep4.network_interface = nic
ep4.addMotif("Init")
ep4.addMotif("PingPong rank2=1 iterations=325 messageSize=20510 compute=8ns")
ep4.addMotif("PingPong rank2=2 iterations=325 messageSize=9000 compute=8ns")
ep4.addMotif("Allreduce iterations=40 count=1 compute=4000ns")
ep4.addMotif("Barrier iterations=15 compute=2000ns")
ep4.addMotif("Fini")
ep4.nic.nic2host_lat = "100ns"
system.allocateNodes(ep4, "linear")

system.build()

sst.setStatisticLoadLevel(8)
sst.setStatisticOutput("sst.statOutputCSV", {
    "filepath": "torus_miniapps_stats.csv",
    "separator": ", "
})
sst.enableAllStatisticsForComponentType("merlin.hr_router")
sst.enableAllStatisticsForComponentType("merlin.linkcontrol")
sst.enableAllStatisticsForComponentType("ember.nic")

print(f"\nTopology: 4x4 Torus = 16 nodes")
print(f"Total ranks: 16 (4 jobs x 4 ranks)")
print(f"Jobs: MiniFE-small, MiniMD-LJ, MiniFE-large, MiniMD-EAM")
