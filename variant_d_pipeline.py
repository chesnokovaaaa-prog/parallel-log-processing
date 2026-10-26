import os
import time
import tracemalloc
import heapq
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
import numpy as np

def process_line_chunk(lines):
    codes = Counter()
    ips = Counter()
    paths_bytes = Counter()
    total_bytes = 0
    sizes = []
    
    for line in lines:
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

def run_pipeline(filepath):
    if not os.path.exists(filepath):
        print(f"Файл {filepath} не найден!")
        return

    tracemalloc.start()
    start_time = time.perf_counter()
    
    n_workers = os.cpu_count() or 4
    chunk_size = 50000  # Оптимальный размер чанка строк
    
    chunks = []
    current_chunk = []
    
    # Читаем файл и группируем в чанки строк
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            current_chunk.append(line)
            if len(current_chunk) >= chunk_size:
                chunks.append(current_chunk)
                current_chunk = []
        if current_chunk:
            chunks.append(current_chunk)

    # Параллельно обрабатываем пулом процессов (Имитация Pipeline)
    with ProcessPoolExecutor(max_workers=n_workers) as ex:
        results = list(ex.map(process_line_chunk, chunks))
        
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
    
    print(f"\n=== Результаты Pipeline (Producer-Consumer) для {filepath} ===")
    print(f"Время выполнения: {end_time - start_time:.4f}延 сек")
    print(f"Пиковая память: {peak_memory / (1024 * 1024):.2f} МБ")

if __name__ == "__main__":
    run_pipeline("data/access_100k.log")
    run_pipeline("data/access_1m.log")
    run_pipeline("data/access_5m.log")
