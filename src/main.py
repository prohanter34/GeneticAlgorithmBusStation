import sys
import time

from PyQt5 import QtCore
from PyQt5.QtGui import QColor
from algorithms import GeneticAlgorithm, EnumerationAlgorithm
from objects import BaseDriver
from PyQt5.QtWidgets import (QApplication, QWidget, QCheckBox,
                             QTabWidget, QVBoxLayout, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QLabel)


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Bus Station")
        self.setGeometry(300, 300, 100, 500)

        self.main_vbox = QVBoxLayout(self)

        self.gbox = QHBoxLayout(self)
        self.main_vbox.addLayout(self.gbox)

        self.vbox11 = QVBoxLayout()
        self.gbox.addLayout(self.vbox11)
        self.drivers_count = QLabel("Кол-во автобусов: ")
        self.vbox11.addWidget(self.drivers_count)

        self.vbox12 = QVBoxLayout()
        self.gbox.addLayout(self.vbox12)
        self.drivers_count_input = QLineEdit("5")
        self.vbox12.addWidget(self.drivers_count_input)

        self.vbox21 = QVBoxLayout()
        self.gbox.addLayout(self.vbox21)
        self.weekdays_pool = QLabel("Поток в будние: ")
        self.weekend_pool = QLabel("Поток в выходные: ")
        self.vbox21.addWidget(self.weekdays_pool)
        self.vbox21.addWidget(self.weekend_pool)

        self.vbox22 = QVBoxLayout()
        self.gbox.addLayout(self.vbox22)
        self.weekdays_pool_input = QLineEdit("2000")
        self.weekend_pool_input = QLineEdit("2000")
        self.vbox22.addWidget(self.weekdays_pool_input)
        self.vbox22.addWidget(self.weekend_pool_input)

        self.vbox31 = QVBoxLayout()
        self.gbox.addLayout(self.vbox31)
        self.population_label = QLabel("Кол-во индивидов в популяции: ")
        self.epoch_label = QLabel("Кол-во эпох: ")
        self.vbox31.addWidget(self.population_label)
        self.vbox31.addWidget(self.epoch_label)

        self.vbox32 = QVBoxLayout()
        self.gbox.addLayout(self.vbox32)
        self.population_input = QLineEdit("50")
        self.epoch_input = QLineEdit("4")
        self.vbox32.addWidget(self.population_input)
        self.vbox32.addWidget(self.epoch_input)

        self.vbox41 = QVBoxLayout()
        self.gbox.addLayout(self.vbox41)
        self.k_mutation_label = QLabel("Коэфф. мутации: ")
        self.k_selection_label = QLabel("Коэфф. селекции: ")
        self.vbox41.addWidget(self.k_mutation_label)
        self.vbox41.addWidget(self.k_selection_label)

        self.vbox42 = QVBoxLayout()
        self.gbox.addLayout(self.vbox42)
        self.k_mutation_input = QLineEdit("0.1")
        self.k_selection_input = QLineEdit("0.3")
        self.vbox42.addWidget(self.k_mutation_input)
        self.vbox42.addWidget(self.k_selection_input)

        self.gbox2 = QHBoxLayout(self)
        self.main_vbox.addLayout(self.gbox2)

        self.vbox51 = QVBoxLayout()
        self.gbox2.addLayout(self.vbox51)
        self.pass_cost_lable = QLabel("Стоимость проезда: ")
        self.driver_cost_label = QLabel("Стоимость дневного водителя и автобуса в месяц: ")
        self.driver_cost_label2 = QLabel("Стоимость ночного водителя и автобуса в месяц: ")
        self.vbox51.addWidget(self.pass_cost_lable)
        self.vbox51.addWidget(self.driver_cost_label)
        self.vbox51.addWidget(self.driver_cost_label2)

        self.vbox52 = QVBoxLayout()
        self.gbox2.addLayout(self.vbox52)
        self.pass_cost_input = QLineEdit("50")
        self.driver_cost_input = QLineEdit("50000")
        self.driver_cost_input2 = QLineEdit("35000")
        self.vbox52.addWidget(self.pass_cost_input)
        self.vbox52.addWidget(self.driver_cost_input)
        self.vbox52.addWidget(self.driver_cost_input2)

        self.gbox3 = QHBoxLayout(self)
        self.gbox3.setContentsMargins(500, 20, 500, 10)
        self.main_vbox.addLayout(self.gbox3)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self._count_times)
        self.ok_button.setFixedSize(QtCore.QSize(40, 25))
        self.switch_alg = QCheckBox("Перебором (не эффективно)")
        self.gbox3.addWidget(self.ok_button)
        self.gbox3.addWidget(self.switch_alg)

        self.gbox4 = QHBoxLayout(self)
        self.gbox4.setContentsMargins(500, 0, 500, 10)
        self.main_vbox.addLayout(self.gbox4)
        self.alg_time_label = QLabel("Время выполнения: -")
        self.gbox4.addWidget(self.alg_time_label)

        self.gbox_table = QHBoxLayout()
        self.main_vbox.addLayout(self.gbox_table)

        self.main_table = QTableWidget()
        self.gbox_table.addWidget(self.main_table)

        self.main_table.setColumnCount(3)
        self.main_table.setColumnWidth(1, 150)
        self.main_table.setColumnWidth(2, 200)
        self.main_table.setHorizontalHeaderLabels(["Тип водителя", "Эффективность", "Время выхода на работу"])

        self.tabs = None

    def _create_days_tabs(self, bs):

        if self.tabs is not None:
            self.gbox_table.removeWidget(self.tabs)

        self.tabs = QTabWidget()

        self.gbox_table.addWidget(self.tabs)

        self.tabs_tables = []
        weekdays = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

        for driver in bs.drivers:
            for i in range(1, len(driver.driving_times)):
                if driver.driving_times[i] // 10000 == driver.driving_times[i - 1] // 10000:
                    if driver.driving_times[i] % 10000 < driver.driving_times[i - 1] % 10000:
                        driver.driving_times[i - 1] -= 10000

        timeTable = []
        for i in range(len(bs.drivers)):
            driver_arr = [[], [], [], [], [], [], []]
            for j in range(len(bs.drivers[i].driving_times)):
                day_number = bs.drivers[i].driving_times[j] // 10000
                hours = (bs.drivers[i].driving_times[j] - (day_number * 10000)) // 60
                minutes = bs.drivers[i].driving_times[j] - hours * 60 - day_number * 10000
                hours = (hours) % 24
                str_minutes = "0" + str(minutes) if len(str(minutes)) == 1 else str(minutes)
                driver_arr[day_number - 1].append(str(hours) + ":" + str_minutes)
            timeTable.append(driver_arr)

        for day_ind in range(len(weekdays)):
            tab = QWidget()
            layout = QVBoxLayout()
            tab.setLayout(layout)
            day_table = QTableWidget()
            self.tabs_tables.append(day_table)
            self.tabs_tables.append(day_table)
            day_table.setColumnCount(int(self.drivers_count_input.text()))
            day_table.setRowCount(100)
            day_table.setHorizontalHeaderLabels([str(i + 1) for i in range(int(self.drivers_count_input.text()))])

            for driver_ind in range(len(timeTable)):
                for t_ind in range(len(timeTable[driver_ind][day_ind])):
                    day_table.setItem(t_ind, driver_ind, QTableWidgetItem(timeTable[driver_ind][day_ind][t_ind]))

            layout.addWidget(day_table)
            self.tabs.addTab(tab, weekdays[day_ind])

    def _count_times(self):

        t = time.time()

        min_points = int(self.driver_cost_input.text()) / int(self.pass_cost_input.text())
        min_points2 = int(self.driver_cost_input2.text()) / int(self.pass_cost_input.text())

        self._init_alg()
        bs = self.genetic_alg.count_timetable()
        for driver in bs.drivers:
            print(driver.driving_times)
        self.main_table.setRowCount(len(bs.drivers))
        for i in range(len(bs.drivers)):

            points = bs.drivers[i].points
            color = "black"
            if isinstance(bs.drivers[i], BaseDriver):
                if points < min_points:
                    color = "gray"
            else:
                if points < min_points2:
                    color = "gray"

            item = QTableWidgetItem(str(points))
            item.setForeground(QColor(color))
            self.main_table.setItem(i, 1, item)


            driver_type = "Дневной" if isinstance(bs.drivers[i], BaseDriver) else "Ночной"
            item = QTableWidgetItem(driver_type)
            item.setForeground(QColor(color))
            self.main_table.setItem(i, 0, item)

            delta = bs.drivers[i].time_delta_timer.start_time
            delta = (delta // 5) * 5
            hours = delta // 60
            minutes = delta - hours * 60
            hours = (hours % 24)
            str_minutes = "0" + str(minutes) if len(str(minutes)) == 1 else str(minutes)
            item = QTableWidgetItem(str(hours) + ":" + str_minutes)
            item.setForeground(QColor(color))
            self.main_table.setItem(i, 2, item)

        self.gbox_table.addWidget(self.main_table)

        self._create_days_tabs(bs)

        alg_time = round(time.time() - t, 2)
        minutes = alg_time // 60
        minutes_str = str(minutes) + " мин. " if minutes > 0 else ""
        seconds = alg_time - minutes * 60
        seconds_str = str(round(seconds, 2)) + " сек. "
        self.alg_time_label.setText("Время выполнения: " + str(minutes_str) + str(seconds_str))

    def _init_alg(self):

        args = [int(self.drivers_count_input.text()),
                int(self.weekdays_pool_input.text()), int(self.weekend_pool_input.text()),
                int(self.population_input.text()), int(self.epoch_input.text()),
                float(self.k_mutation_input.text()), float(self.k_selection_input.text())]

        if self.switch_alg.isChecked():
            self.genetic_alg = EnumerationAlgorithm(*args)
        else:
            self.genetic_alg = GeneticAlgorithm(*args)


app = QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec_())
