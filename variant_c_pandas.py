import os
import time
import tracemalloc
import pandas as pd
import numpy as np

def run_pandas(filepath):
    if not os.path.exists(filepath):
        print(f"Файл {filepath} не найден!")
        return

    tracemalloc.start()
    start_time = time.perf_counter()
    
    final_codes = pd.Series(dtype='int64')
    final_ips = pd.Series(dtype='int64')
    final_paths_bytes = pd.Series(dtype='int64')
    total_bytes = 0
    total_rows = 0
    all_sizes = []
    
    chunk_iter = pd.read_csv(
        filepath, 
        sep=r'\s+', 
        header=None, 
        names=['ts', 'ip', 'method', 'path', 'code', 'size'],
        chunksize=200000,
        dtype={'code': str, 'size': int, 'ip': str, 'path': str},
        usecols=['ip', 'path', 'code', 'size']
    )
    
    for chunk in chunk_iter:
        codes_chunk = chunk['code'].value_counts()
        ips_chunk = chunk['ip'].value_counts()
        paths_chunk = chunk.groupby('path')['size'].sum()
        
        final_codes = final_codes.add(codes_chunk, fill_value=0)
        final_ips = final_ips.add(ips_chunk, fill_value=0)
        final_paths_bytes = final_paths_bytes.add(paths_chunk, fill_value=0)
        
        total_bytes += chunk['size'].sum()
        total_rows += len(chunk)
        all_sizes.append(chunk['size'].values)

    avg_size = total_bytes / max(1, total_rows)
    flat_sizes = np.concatenate(all_sizes) if all_sizes else np.array([])
    p95_size = np.percentile(flat_sizes, 95) if len(flat_sizes) > 0 else 0
    
    end_time = time.perf_counter()
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print(f"\n=== Результаты Pandas (Чанки по 200k) для {filepath} ===")
    print(f"Время выполнения: {end_time - start_time:.4f} сек")
    print(f"Пиковая память: {peak_memory / (1024 * 1024):.2f} МБ")

if __name__ == "__main__":
    run_pandas("data/access_100k.log")
    run_pandas("data/access_1m.log")
    run_pandas("data/access_5m.log")
