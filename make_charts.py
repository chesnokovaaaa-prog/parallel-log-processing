import matplotlib.pyplot as plt

# Данные из наших реальных тестов для файла 5M
variants = ['Multiprocessing\n(8 воркеров)', 'Baseline\n(1 поток)', 'Pandas\n(Chunksize)', 'Threading\n(8 потоков)']
times = [6.65, 18.32, 47.40, 51.84]
memory = [741.99, 576.94, 475.73, 580.00]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# График времени
colors1 = ['#2ecc71', '#3498db', '#e67e22', '#e74c3c']
bars1 = ax1.bar(variants, times, color=colors1, edgecolor='black', width=0.6)
ax1.set_title('Время выполнения на 5 млн строк (меньше = лучше)', fontsize=12, fontweight='bold', pad=15)
ax1.set_ylabel('Секунды', fontsize=11)
ax1.grid(axis='y', linestyle='--', alpha=0.7)
ax1.bar_label(bars1, fmt='%.2f сек', padding=3, fontweight='bold')

# График памяти
colors2 = ['#e74c3c', '#3498db', '#2ecc71', '#34495e']
bars2 = ax2.bar(variants, memory, color=colors2, edgecolor='black', width=0.6)
ax2.set_title('Пиковая память на 5 млн строк (меньше = лучше)', fontsize=12, fontweight='bold', pad=15)
ax2.set_ylabel('Мегабайты (МБ)', fontsize=11)
ax2.grid(axis='y', linestyle='--', alpha=0.7)
ax2.bar_label(bars2, fmt='%.1f МБ', padding=3, fontweight='bold')

plt.tight_layout()
plt.savefig('performance_charts.png', dpi=300)
print("Успех: График сохранен в файл performance_charts.png")
