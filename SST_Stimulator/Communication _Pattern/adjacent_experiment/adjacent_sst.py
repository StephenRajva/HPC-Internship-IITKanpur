import sst


cpu = sst.Component("cpu", "memHierarchy.standardCPU")

cpu.addParams({
    "clock" : "2GHz",
    "memFreq" : 4,
    "memSize" : "1KiB",
    "verbose" : 0,
    "maxOutstanding" : 16,
    "opCount" : 50000,
    "reqsPerIssue" : 2,
    "write_freq" : 40,
    "read_freq" : 60
})

iface = cpu.setSubComponent(
    "memory",
    "memHierarchy.standardInterface"
)


cache = sst.Component(
    "l1cache",
    "memHierarchy.Cache"
)

cache.addParams({
    "cache_frequency" : "2GHz",
    "cache_size" : "4KB",
    "associativity" : 4,
    "access_latency_cycles" : 5,
    "replacement_policy" : "lru",
    "coherence_protocol" : "MESI",
    "L1" : 1
})


memctrl = sst.Component(
    "memory",
    "memHierarchy.MemController"
)

memctrl.addParams({
    "clock" : "1GHz",
    "backing" : "none"
})

memory = memctrl.setSubComponent(
    "backend",
    "memHierarchy.simpleMem"
)

memory.addParams({
    "access_time" : "100ns",
    "mem_size" : "512MiB"
})


link_cpu_cache = sst.Link("link_cpu_cache")

link_cpu_cache.connect(
    (iface, "lowlink", "1ns"),
    (cache, "highlink", "1ns")
)

link_cache_mem = sst.Link("link_cache_mem")

link_cache_mem.connect(
    (cache, "lowlink", "5ns"),
    (memctrl, "highlink", "5ns")
)


sst.setStatisticLoadLevel(4)

sst.setStatisticOutput("sst.statOutputCSV")

sst.setStatisticOutputOptions({
    "filepath" : "adjacent_stats.csv",
    "separator" : ","
})

for comp in [cpu, cache, memctrl]:
    comp.enableAllStatistics()

