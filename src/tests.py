from algorithms import GeneticAlgorithm
import time
from objects import PassengerFabric
import matplotlib.pyplot as plt


# Генерация потока пассажиров
fab = PassengerFabric()
weekdays = fab.gen_weekdays_pool(2000, [8 * 60, 19 * 60], 3)
weekend = fab.gen_weekend_pool(2000)
plt.bar([i for i in range(48)], weekdays)
plt.title("Поток в будние")
plt.show()
plt.bar([i for i in range(48)], weekend)
plt.ylim(0, 70)
plt.title("Поток в выходные")
plt.show()



# Зависимость времени выполнения ГА от n
ns = [n + 1 for n in range(1)]
times = []
for n in range(1):
    ga = GeneticAlgorithm(n + 1, 3000, 3000,
                 100, 10, 0.1, 0.3)
    t = time.time()
    ga.count_timetable()
    alg_time = time.time() - t
    times.append(alg_time)

plt.plot(ns, times)
plt.title("Время выполнения от n")
plt.show()

