import math
import random
from objects import Station, Timer, PassengerFabric, BaseDriver, NightlyDriver


class StationPool:

    stations: [Station]
    cycleCount: int = 1
    cycleTimer: Timer
    is_active = True

    def __init__(self, stations: [Station], n: int, gen_weekend_pool, gen_weekdays_pool):
        self.stations = stations
        self.cycleTimer = Timer(24*60, True)
        self.n = n

        self.gen_weekdays_pool = gen_weekdays_pool
        self.gen_weekend_pool = gen_weekend_pool

    def tick(self, is_recording: bool = False, weekday=None):
        self.cycleTimer.tick()
        if self.cycleTimer.is_out:
            self.cycleCount += 1
            self.reset_pools()
            if self.cycleCount == 8:
                self.cycleCount = 1
                self.is_active = False
            self.cycleTimer.reset()
        if self.cycleCount > 5:
            is_weekend = True
        else:
            is_weekend = False
        for station in self.stations:
            station.tick(is_weekend, is_recording=is_recording, weekday=weekday)

    def selection(self, k: float):
        self.best_stations = []
        for _ in range(int(len(self.stations) * k)):
            best_points = 0
            best_station = None
            for station in self.stations:
                station_points = station.get_points()
                if station_points >= best_points:
                    best_station = station
                    best_points = station.get_points()
            self.best_stations.append(best_station)
            self.stations.remove(best_station)
        return self.best_stations

    def reset_pools(self):
        for st in self.stations:
            st.reset_pools(self.gen_weekend_pool(), self.gen_weekdays_pool())

    def mutation(self, p: float, k: int = 1):
        for st in self.stations:
            r_num = random.random()
            if r_num < p:
                r_num = math.ceil(random.random() * len(st.drivers) - 1)
                driver = st.drivers[r_num]
                if isinstance(driver, BaseDriver):
                    driver.time_delta = random.random() * 4*60 + 6*60
                else:
                    num = random.random() * 9*60 + 6*60
                    if random.random() > 0.5:
                        num += 24*60
                    driver.time_delta = num

    def crossing(self, best_stations):
        new_stations = []
        for i in range(len(self.best_stations)):
            new_individual_data = []
            num = int(random.random() * (self.n - 2))
            new_individual_data += self.best_stations[i].drivers[:num]
            new_individual_data += self.best_stations[i - 1].drivers[num:]
            best_driver = None
            best_points = 0
            for driver in self.best_stations[i].drivers:
                if driver.points > best_points:
                    best_driver = driver
                    best_points = driver.points
            if best_driver not in new_individual_data:
                new_individual_data.pop()
                new_individual_data.append(best_driver)

            best_driver = None
            best_points = 0

            for driver in self.best_stations[i - 1].drivers:
                if driver.points > best_points:
                    best_driver = driver
                    best_points = driver.points
            if best_driver not in new_individual_data:
                new_individual_data.pop()
                new_individual_data.append(best_driver)


            new_stations.append(Station(new_individual_data, best_stations[i].weekdays_pool,
                                        best_stations[i].weekend_pool))
        return new_stations

    def add_stations(self, stations: [Station]):
        for i in range(len(stations)):
            if len(self.stations) == 0:
                self.best_stations.pop()
            else:
                self.stations.pop()
        self.stations += self.best_stations
        self.stations += stations

    def get_best(self):
        best = self.selection(1)[0]
        self.stations += [best]
        return best


class TimetableAlgorithm:
    weekdays_volume: int
    weekend_volume: int
    drivers_count: int
    population_count: int
    epochs_count: int
    k_mutation: float
    k_selection: float

    passenger_fabric: PassengerFabric

    def __init__(self, drivers_count, weekdays_volume, weekend_volume,
                 population_count, epochs_count, k_mutation, k_selection):
        self.drivers_count = drivers_count
        self.weekdays_volume = weekdays_volume
        self.weekend_volume = weekend_volume
        self.population_count = population_count
        self.epochs_count = epochs_count
        self.k_mutation = k_mutation
        self.k_selection = k_selection

        self.passenger_fabric = PassengerFabric()

    def _gen_weekdays_pool(self):
        return self.passenger_fabric.gen_weekdays_pool(self.weekdays_volume, [8 * 60, 19 * 60], 1.5)

    def _gen_weekend_pool(self):
        return self.passenger_fabric.gen_weekend_pool(self.weekend_volume)


class GeneticAlgorithm(TimetableAlgorithm):

    def count_timetable(self):
        # Случайным образом создаем станции в популяцию

        stations = []
        for i in range(self.population_count):

            weekdays_pool = self._gen_weekdays_pool()
            weekend_pool = self._gen_weekend_pool()

            drivers = []
            for j in range(self.drivers_count):
                num = random.random()
                if num > 0.5:
                    num = math.ceil(random.random() * 4*60 + 6*60)
                    driver = BaseDriver(work_time=9 * 60, driving_time=1 * 60, resting_time=15 * 60,
                                        switching_time=20, time_delta=num, weekend_pool=weekend_pool,
                                        weekdays_pool=weekdays_pool)
                else:
                    num = math.ceil(random.random() * 9*60 + 6*60)
                    if random.random() > 0.5:
                        num += 24 * 60
                    driver = NightlyDriver(work_time=12 * 60, driving_time=1 * 60, resting_time=36 * 60,
                                           switching_time=20, time_delta=num, weekend_pool=weekend_pool,
                                           weekdays_pool=weekdays_pool)
                drivers.append(driver)

            stations.append(Station(drivers, weekdays_pool, weekend_pool))
        station_pool = StationPool(stations, self.population_count, self._gen_weekend_pool, self._gen_weekdays_pool)

        # Генетический алгоритм
        for i in range(self.epochs_count):
            while station_pool.is_active:
                station_pool.tick()
            station_pool.is_active = True
            print(i)
            station_pool.mutation(self.k_mutation)
            best_stations = station_pool.selection(self.k_selection)
            new_stations = station_pool.crossing(best_stations)
            station_pool.add_stations(new_stations)
            for station in station_pool.stations:
                station.reset_points()
            for station in station_pool.best_stations:
                station.reset_points()
            for station in station_pool.stations:
                station.reset_delta_timer()

        # Лучшая сатнция
        bs = station_pool.get_best()
        st_pool = StationPool([bs], 1, self._gen_weekend_pool, self._gen_weekdays_pool)
        st_pool.reset_pools()
        while st_pool.is_active:
            st_pool.tick(is_recording=True, weekday=st_pool.cycleCount)

        print(bs.get_points())
        for i in bs.drivers:
            delta = i.time_delta_timer.start_time
            delta = (delta // 5) * 5
            if isinstance(i, NightlyDriver):
                print("Ночной водитель")
            else:
                print("Дневной водитель")
            print(str(delta // 60) + ":" + str(delta - (delta // 60) * 60))

        return bs


class EnumerationAlgorithm(GeneticAlgorithm):

    def count_timetable(self):

        data_arr = [0 for i in range(self.drivers_count)]

        best_station = None
        best_points = 0

        for i in range(156**self.drivers_count):

            weekend_pool = self._gen_weekend_pool()
            weekdays_pool = self._gen_weekdays_pool()

            for j in range(len(data_arr)):
                if data_arr[j] + 1 < 156:
                    data_arr[j] += 1
                    break
                else:
                    data_arr[j] = 0

            drivers = []

            for j in data_arr:
                if j < 12 * 4:
                    driver = BaseDriver(work_time=9 * 60, driving_time=1 * 60, resting_time=15 * 60,
                                        switching_time=20, time_delta=j*5 + 6*60, weekend_pool=weekend_pool,
                                        weekdays_pool=weekdays_pool)
                else:
                    time_delta = j*5 - 4*60
                    time_delta = time_delta + 6*60 if time_delta > 9*60 else time_delta - 9*60 + 24*60
                    driver = NightlyDriver(work_time=12 * 60, driving_time=1 * 60, resting_time=36 * 60,
                                           switching_time=20, time_delta=time_delta, weekend_pool=weekend_pool,
                                           weekdays_pool=weekdays_pool)
                drivers.append(driver)


            station = Station(drivers, weekdays_pool, weekend_pool)
            st_pool = StationPool([station], 1, self._gen_weekend_pool, self._gen_weekdays_pool)
            st_pool.reset_pools()
            while st_pool.is_active:
                st_pool.tick(weekday=st_pool.cycleCount)

            station = st_pool.stations[0]
            points = station.get_points()
            if points > best_points:
                best_station = station
                best_points = points

        best_station.reset_points()
        best_station.reset_pools(self._gen_weekend_pool(), self._gen_weekdays_pool())
        st_pool = StationPool([best_station], 1, self._gen_weekend_pool, self._gen_weekdays_pool)
        st_pool.reset_pools()
        while st_pool.is_active:
            st_pool.tick(is_recording=True, weekday=st_pool.cycleCount)

        best_station = st_pool.stations[0]

        return best_station

