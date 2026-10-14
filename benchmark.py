import os, time, statistics, tracemalloc, json
from pathlib import Path
BASE=Path(__file__).parent
tracemalloc.start()
def norm(s): return set((s or "").lower().split())
def load_sections():
    out=[]
    for p in list((BASE/"protocols").glob("*.txt"))+list((BASE/"protocols").glob("*.md")):
        if p.name.lower()=="readme.txt": continue
        txt=p.read_text(encoding="utf-8",errors="ignore")
        for block in txt.split("\n\n"):
            if block.strip(): out.append((p.name,block.strip()))
    return out
sections=load_sections()
queries=["antenatal follow up","immunisation due","danger signs newborn","blood pressure follow-up","ORS fever management"]
times=[]
for q in queries*20:
    start=time.perf_counter()
    qt=norm(q)
    best=0
    for name,body in sections:
        bt=norm(body)
        best=max(best,len(qt&bt)/max(1,len(qt)))
    times.append((time.perf_counter()-start)*1000)
current,peak=tracemalloc.get_traced_memory()
print("Benchmark scope: Python retrieval baseline only; no AI model loaded.")
print("Protocol text sections:",len(sections))
print("Queries:",len(times))
print(f"Mean retrieval latency: {statistics.mean(times):.3f} ms")
print(f"P95 retrieval latency: {sorted(times)[int(.95*(len(times)-1))]:.3f} ms")
print(f"Python traced current memory: {current/1024/1024:.2f} MiB")
print(f"Python traced peak memory: {peak/1024/1024:.2f} MiB")
print("Model size: NOT MEASURED — no offline model connected.")
print("Use this only as a baseline; benchmark the supplied model on the target low-end device.")
