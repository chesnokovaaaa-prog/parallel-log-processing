import time
import tracemalloc
import heapq
from collections import Counter
import numpy as np
import os

def run_baseline(filepath):
    if not os.path.exists(filepath):
        print(f"Файл {filepath} не найден!")
        return

    # Запуск отслеживания памяти
    tracemalloc.start()
    start_time = time.perf_counter()
    
    codes = Counter()
    ips = Counter()
    paths_bytes = Counter()
    total_bytes = 0
    all_sizes = []
    
    # Построчное чтение (не загружает файл целиком в память)
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            if len(parts) != 6:
                continue
            
            # Структура: timestamp, ip, method, path, code, size
            _, ip, _, path, code, size_str = parts
            size = int(size_str)
            
            codes[code] += 1
            ips[ip] += 1
            paths_bytes[path] += size
            total_bytes += size
            all_sizes.append(size)
            
    # Сбор результатов агрегации
    top_ips = heapq.nlargest(10, ips.items(), key=lambda x: x[1])
    top_paths = heapq.nlargest(10, paths_bytes.items(), key=lambda x: x[1])
    avg_size = total_bytes / max(1, sum(codes.values()))
    p95_size = np.percentile(all_sizes, 95) if all_sizes else 0
    
    end_time = time.perf_counter()
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print(f"\n=== Результаты Baseline для {filepath} ===")
    print("Коды ответов:", dict(codes))
    print("Топ-10 IP:", top_ips)
    print("Топ-10 путей по трафику:", top_paths)
    print(f"Средний размер ответа: {avg_size:.1f} байт")
    print(f"p95 размера ответа: {p95_size:.1f} байт")
    print(f"Время выполнения: {end_time - start_time:.4f} сек")
    print(f"Пиковая память: {peak_memory / (1024 * 1024):.2f} МБ")

if __name__ == "__main__":
    run_baseline("data/access_100k.log")
    run_baseline("data/access_1m.log")
    run_baseline("data/access_5m.log")
