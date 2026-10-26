import os
import time
import tracemalloc
import heapq
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import numpy as np

def process_chunk_thread(args):
    path, start, end = args
    codes = Counter()
    ips = Counter()
    paths_bytes = Counter()
    total_bytes = 0
    sizes = []
    
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        f.seek(start)
        if start != 0:
            f.readline()
            
        pos = f.tell()
        while pos < end:
            line = f.readline()
            if not line:
                break
            pos = f.tell()
            
            parts = line.split()
            if len(parts) != 6:
                continue
                
            _, ip, _, p, code, size = parts
            codes[code] += 1
            ips[ip] += 1
            paths_bytes[p] += int(size)
            total_bytes += int(size)
            sizes.append(int(size))
            
    return codes, ips, paths_bytes, total_bytes, sizes

def split_ranges(path, n_workers):
    size = os.path.getsize(path)
    step = size // n_workers
    ranges = []
    
    with open(path, "rb") as f:
        start = 0
        for i in range(n_workers):
            end = size if i == n_workers - 1 else start + step
            if end < size:
                f.seek(end)
                f.readline()
                end = f.tell()
            ranges.append((path, start, end))
            start = end
    return ranges

def run_threading(filepath):
    if not os.path.exists(filepath):
        print(f"Файл {filepath} не найден!")
        return

    tracemalloc.start()
    start_time = time.perf_counter()
    
    n_workers = os.cpu_count() or 4
    ranges = split_ranges(filepath, n_workers)
    
    with ThreadPoolExecutor(max_workers=n_workers) as ex:
        results = list(ex.map(process_chunk_thread, ranges))
        
    final_codes = Counter()
    final_ips = Counter()
    final_paths_bytes = Counter()
    final_total_bytes = 0
    final_all_sizes = []
    
    for c, i, p, t, s in results:
        final_codes.update(c)
        final_ips.update(i)
        final_paths_bytes.update(p)
        final_total_bytes += t
        final_all_sizes.extend(s)
        
    avg_size = final_total_bytes / max(1, sum(final_codes.values()))
    p95_size = np.percentile(final_all_sizes, 95) if final_all_sizes else 0
    
    end_time = time.perf_counter()
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print(f"\n=== Результаты Threading ({n_workers} потоков) для {filepath} ===")
    print(f"Время выполнения: {end_time - start_time:.4f} сек")
    print(f"Пиковая память: {peak_memory / (1024 * 1024):.2f} МБ")

if __name__ == "__main__":
    run_threading("data/access_100k.log")
    run_threading("data/access_1m.log")
    run_threading("data/access_5m.log")
