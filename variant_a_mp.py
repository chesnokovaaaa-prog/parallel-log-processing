import os
import time
import tracemalloc
import heapq
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
import numpy as np

# ---------- MAP: Обработка одного байтового диапазона ----------
def process_chunk(args):
    path, start, end = args
    codes = Counter()
    ips = Counter()
    paths_bytes = Counter()
    total_bytes = 0
    sizes = []
    
    with open(path, "rb") as f:
        f.seek(start)
        # Если мы не в самом начале файла — пропускаем "огрызок" строки,
        # так как его дочитает предыдущий воркер
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
                
            # В режиме "rb" строки считываются как bytes, поэтому используем префикс b''
            _, ip, _, p, code, size = parts
            codes[code] += 1
            ips[ip] += 1
            paths_bytes[p] += int(size)
            total_bytes += int(size)
            sizes.append(int(size))
            
    return codes, ips, paths_bytes, total_bytes, sizes

# ---------- Нарезка файла на диапазоны по байтовым границам ----------
def split_ranges(path, n_workers):
    size = os.path.getsize(path)
    step = size // n_workers
    ranges = []
    
    with open(path, "rb") as f:
        start = 0
        for i in range(n_workers):
            end = size if i == n_workers - 1 else start + step
            # Выравниваем end строго на конец строки (\n)
            if end < size:
                f.seek(end)
                f.readline()  # Дочитываем строку до конца
                end = f.tell()
            ranges.append((path, start, end))
            start = end
    return ranges

# ---------- REDUCE: Слияние результатов ----------
def run_multiprocessing(filepath):
    if not os.path.exists(filepath):
        print(f"Файл {filepath} не найден!")
        return

    tracemalloc.start()
    start_time = time.perf_counter()
    
    # Автоматически определяем количество ядер вашего процессора
    n_workers = os.cpu_count() or 4
    ranges = split_ranges(filepath, n_workers)
    
    # Запуск пула процессов
    with ProcessPoolExecutor(max_workers=n_workers) as ex:
        results = list(ex.map(process_chunk, ranges))
        
    # Слияние локальных словарей (Редукция)
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
        
    # Декодируем байты обратно в строки для вывода результатов
    codes_str = {k.decode('utf-8'): v for k, v in final_codes.items()}
    top_ips = heapq.nlargest(10, final_ips.items(), key=lambda x: x)
    top_ips_str = [(k.decode('utf-8'), v) for k, v in top_ips]
    
    top_paths = heapq.nlargest(10, final_paths_bytes.items(), key=lambda x: x)
    top_paths_str = [(k.decode('utf-8'), v) for k, v in top_paths]
    
    avg_size = final_total_bytes / max(1, sum(final_codes.values()))
    p95_size = np.percentile(final_all_sizes, 95) if final_all_sizes else 0
    
    end_time = time.perf_counter()
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    print(f"\n=== Результаты Multiprocessing ({n_workers} воркеров) для {filepath} ===")
    print("Коды ответов:", codes_str)
    print("Топ-10 IP:", top_ips_str)
    print("Топ-10 путей по трафику:", top_paths_str)
    print(f"Средний размер ответа: {avg_size:.1f} байт")
    print(f"p95 размера ответа: {p95_size:.1f} байт")
    print(f"Время выполнения: {end_time - start_time:.4f} сек")
    print(f"Пиковая память родительского процесса: {peak_memory / (1024 * 1024):.2f} МБ")

if __name__ == "__main__":
    # Прогоняем по всем трем файлам для сравнения
    run_multiprocessing("data/access_100k.log")
    run_multiprocessing("data/access_1m.log")
    run_multiprocessing("data/access_5m.log")
