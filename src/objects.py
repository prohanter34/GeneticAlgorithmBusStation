import enum
import math


BUS_VALUE = 15


class Timer:

    def __init__(self, start_time, is_start=False):
        self.start_time = start_time
        if is_start:
            self.value = start_time
            self.is_out = False
        else:
            self.value = 0
            self.is_out = True

    def tick(self):
        self.value -= 5
        if self.value <= 0:
            self.is_out = True

    def reset(self):
        self.value = self.start_time
        self.is_out = False

    def set_start_time(self, start_time):
        self.start_time = start_time


class DriveStates(enum.Enum):

    driving = 0
    break_ing = 1
    switching = 2
    resting = 3


class Driver:

    state: int
    # Время всей работы
    work_timer: Timer
    # Время без работы
    resting_time: Timer
    # Время перерыва
    break_timer: Timer
    # Время заезда
    driving_timer: Timer
    # Время работы без отдыха
    driving_without_rest_timer: Timer
    one_station_timer: Timer
    time_delta_timer: Timer
    points: int = 0

    # Время выездов
    driving_times: [int]

    def __init__(self, driving_time, work_time, resting_time, switching_time, time_delta,
                 weekend_pool: [int], weekdays_pool: [int]):
        self.work_timer = Timer(work_time, True)
        self.resting_timer = Timer(resting_time, True)
        self.driving_timer = Timer(driving_time, True)
        self.switching_timer = Timer(switching_time, True)
        self.one_station_timer = Timer(30, False)
        self.time_delta_timer = Timer(time_delta, True)
        self.state = DriveStates.switching.value
        self.weekend_pool = weekend_pool
        self.weekdays_pool = weekdays_pool
        self.now_time = Timer(24*60 - 1, True)

        self.driving_times = []

    def tick(self, is_weekend: bool = False, is_recording: bool = False, weekday=None):
        if self.time_delta_timer.is_out:
            self.now_time.tick()
            if self.now_time.is_out:
                self.now_time.reset()

            if self.state == DriveStates.driving.value:
                self._driving(is_weekend, is_recording, weekday)

            elif self.state == DriveStates.resting.value:
                self.resting_timer.tick()
                if self.resting_timer.is_out:
                    self.resting_timer.reset()
                    self.state = DriveStates.switching.value

            elif self.state == DriveStates.switching.value:
                self.switching_timer.tick()
                self.work_timer.tick()
                if self.switching_timer.is_out:
                    self.switching_timer.reset()
                    if self.work_timer.value > self.work_timer.start_time / 2:
                        self.state = DriveStates.driving.value
                    else:
                        self.state = DriveStates.resting.value
                        self.work_timer.reset()

            elif self.state == DriveStates.break_ing.value:
                self.break_timer.tick()
                self.work_timer.tick()
                if self.break_timer.is_out:
                    self.break_timer.reset()
                    self.state = DriveStates.driving.value
        else:
            self.time_delta_timer.tick()

    def reset(self):
        self.points = 0
        self.work_timer.reset()
        self.resting_timer.reset()
        self.driving_timer.reset()
        self.switching_timer.reset()
        self.time_delta_timer.reset()
        self.state = DriveStates.switching.value
        self.now_time = Timer(24 * 60 - 1, True)

        self.driving_without_rest_timer.reset()
        self.break_timer.reset()

        self.driving_times = []

    def _record_start_driving(self, is_recording=False, weekday=None):
        if is_recording:

            t = self.time_delta_timer.start_time + self.work_timer.start_time - self.work_timer.value - 60
            if self.time_delta_timer.start_time > 1440:
                t -= 1440
            if 1440 > t > 1360:
                drive_time = (weekday - 1) * 10000 + t
            else:
                drive_time = weekday * 10000 + t

            self.driving_times.append(drive_time)

    def _driving(self, is_weekend: bool, is_recording: bool = False, weekday=None):
        pass

    def _add_points(self, is_weekend: bool):
        if self.one_station_timer.is_out:
            if is_weekend:
                index = self.now_time.value // 30
                if self.weekend_pool[index] >= BUS_VALUE:
                    self.weekend_pool[index] -= BUS_VALUE
                    self.points += BUS_VALUE
                else:
                    self.points += self.weekend_pool[index]
                    self.weekend_pool[index] = 0
            else:
                index = self.now_time.value // 30 - 1
                if self.weekdays_pool[index] >= BUS_VALUE:
                    self.weekdays_pool[index] -= BUS_VALUE
                    self.points += BUS_VALUE
                else:
                    self.points += self.weekdays_pool[index]
                    self.weekdays_pool[index] = 0
            self.one_station_timer.reset()


class BaseDriver(Driver):

    driving_without_rest_timer = Timer(60*4, True)
    break_timer = Timer(60, True)

    def _driving(self, is_weekend: bool, is_recording: bool = False, weekday=None):
        self._add_points(is_weekend)
        self.driving_timer.tick()
        self.driving_without_rest_timer.tick()
        self.work_timer.tick()
        self.one_station_timer.tick()
        if self.driving_timer.is_out:
            self.driving_timer.reset()
            self._record_start_driving(is_recording, weekday)
            if (self.driving_without_rest_timer.value >= self.driving_timer.start_time
                    and self.work_timer.value >= self.driving_timer.start_time):
                self.state = DriveStates.driving.value
            elif self.work_timer.value < self.driving_timer.start_time:
                self.state = DriveStates.switching.value
                self.driving_without_rest_timer.reset()
            elif self.driving_without_rest_timer.value < self.driving_timer.start_time:
                self.state = DriveStates.break_ing.value
                self.driving_without_rest_timer.reset()
            else:
                pass


class NightlyDriver(Driver):

    driving_without_rest_timer = Timer(2*60, True)
    break_timer = Timer(20, True)

    def _driving(self, is_weekend: bool, is_recording: bool = False, weekday=None):
        self._add_points(is_weekend)
        self.driving_timer.tick()
        self.driving_without_rest_timer.tick()
        self.work_timer.tick()
        self.one_station_timer.tick()
        if self.driving_timer.is_out:
            self.driving_timer.reset()
            self._record_start_driving(is_recording, weekday)
            if (self.driving_without_rest_timer.value >= self.driving_timer.start_time
                    and self.work_timer.value >= self.driving_timer.start_time):
                self.state = DriveStates.driving.value
            elif self.work_timer.value < self.driving_timer.start_time:
                self.state = DriveStates.switching.value
                self.driving_without_rest_timer.reset()
            elif self.driving_without_rest_timer.value < self.driving_timer.start_time:
                self.state = DriveStates.break_ing.value
                self.driving_without_rest_timer.reset()
            else:
                pass


class Station:

    drivers: [Driver]
    points: int = 0

    weekdays_pool: [int]
    weekend_pool: [int]

    def __init__(self, drivers: [Driver], weekdays_pool: [int], weekend_pool: [int]):
        self.drivers = drivers
        self.weekend_pool = weekend_pool
        self.weekdays_pool = weekdays_pool

    def tick(self, is_weekend: bool = False, is_recording: bool = False, weekday=None):
        for driver in self.drivers:
            driver.tick(is_weekend, is_recording=is_recording, weekday=weekday)

    def get_points(self):
        points = 0
        for driver in self.drivers:
            points += driver.points
        return points

    def reset_points(self):
        for driver in self.drivers:
            driver.reset()

    def reset_pools(self, weekend, weekdays):
        self.weekend_pool = weekend
        self.weekdays_pool = weekdays
        for driver in self.drivers:
            driver.weekend_pool = weekend
            driver.weekdays_pool = weekdays

    def reset_delta_timer(self):
        for driver in self.drivers:
            driver.time_delta_timer.reset()


class PassengerFabric:

    def gen_weekdays_pool(self, volume, hour_peeks: [int], peek_k):
        base_vol = math.floor(volume / (48 + len(hour_peeks) * (3 * peek_k / 2)))
        base_volume = math.floor(base_vol + base_vol*6/42)
        pool = [base_volume if i not in [7, 8, 9, 10, 11, 12] else 0 for i in range(48)]
        volume -= 48 * base_vol
        peek_vol = math.floor((volume / len(hour_peeks)) / 16)
        max_peek_vol = peek_vol * 3
        mid_peek_vol = peek_vol * 2
        min_peek_vol = peek_vol
        for i in range(len(hour_peeks)):
            peek_index = hour_peeks[i] // 30
            try:
                pool[peek_index-3] += min_peek_vol
                pool[peek_index-2] += min_peek_vol
                pool[peek_index-1] += mid_peek_vol
                pool[peek_index] += max_peek_vol
                pool[peek_index+1] += max_peek_vol
                pool[peek_index+2] += mid_peek_vol
                pool[peek_index+3] += min_peek_vol
                pool[peek_index+4] += min_peek_vol
            except:
                pass
        return pool

    def gen_weekend_pool(self, volume):

        return [math.floor(volume / 42) if i not in [7, 8, 9, 10, 11, 12] else 0 for i in range(48)]

