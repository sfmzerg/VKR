import sys
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QDateEdit, QFileDialog, QRadioButton, QButtonGroup, QMessageBox)
from PyQt5.QtCore import QDate
import os
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from pandas import ExcelWriter


"""

Дочерний класс, который реализует функционал приложения, обработку кнопок и так далее

"""
class Analyze(QMainWindow):

    """

    Инициализация начальных параметров

    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Analyzer')
        self.UI()
        self.init_signals()

    """
    
    Реализация пользовательского интерфейса
    
    """

    def UI(self):
        self.label = QLabel('Загрузите данные')
        self.data_loader = QPushButton('Загрузить данные')
        self.show_plot = QPushButton('Построить график, исходя из загруженных данных')
        self.analyze_data = QPushButton('Анализ загруженных данных')
        self.plot_second_show = QPushButton('Диаграмма по средним занчениям')
        self.data2 = QDateEdit()
        self.get_actual_values = QPushButton('Получить актуальный курс чешской кроны')
        self.starter = QDateEdit()
        self.tarter2 = QDateEdit()
        self.period_plot = QPushButton('Построить график по периодам')
        self.save_data = QPushButton('Сохранить результаты')
        self.local = QRadioButton('На компьютер локально')
        self.yandex_button = QRadioButton('На Яндекс.Диск')
        self.data_loader.setStyleSheet('QPushButton {background-color: #A3C1DA; color: red;}')
        self.show_plot.setStyleSheet('QPushButton {background-color: #A3C1DA; color: red;}')
        self.analyze_data.setStyleSheet('QPushButton {background-color: #A3C1DA; color: red;}')
        self.plot_second_show.setStyleSheet('QPushButton {background-color: #A3C1DA; color: red;}')
        self.get_actual_values.setStyleSheet('QPushButton {background-color: #A3C1DA; color: red;}')
        self.period_plot.setStyleSheet('QPushButton {background-color: #A3C1DA; color: red;}')
        self.save_data.setStyleSheet('QPushButton {background-color: #A3C1DA; color: red;}')
        self.local.setChecked(True)
        self.storage_group = QButtonGroup()
        self.storage_group.addButton(self.local)
        self.storage_group.addButton(self.yandex_button)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.data_loader)
        layout.addWidget(self.analyze_data)
        layout.addWidget(self.show_plot)
        layout.addWidget(self.plot_second_show)
        layout.addWidget(self.data2)
        layout.addWidget(self.get_actual_values)
        layout.addWidget(self.starter)
        layout.addWidget(self.tarter2)
        layout.addWidget(self.period_plot)
        layout.addWidget(self.local)
        layout.addWidget(self.yandex_button)
        layout.addWidget(self.save_data)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)


    """
    
    Привязываем обработчики к кнопкам, созданным ранее
    
    """
    def init_signals(self):
        self.plot_second_show.clicked.connect(self.plot_second)
        self.get_actual_values.clicked.connect(self.rate)
        self.period_plot.clicked.connect(self.plot2)
        self.save_data.clicked.connect(self.save)
        self.data_loader.clicked.connect(self.load)
        self.analyze_data.clicked.connect(self.analyze)
        self.show_plot.clicked.connect(self.plot_first)


    """
    
    Проводим анализ по min, max, годам
    
    """
    def analyze(self):
        if hasattr(self, 'df'):
            try:
                max_value = self.df['Value'].max()
                min_value = self.df['Value'].min()
                self.df['Year'] = pd.to_datetime(self.df['Date'], format="%d/%m/%Y").dt.year
                values = self.df.groupby('Year')['Value'].mean()

                text = f'Максимальное: {max_value}\n'
                text += f'Минимальное: {min_value}\n'
                text += 'Средние значения по годам:\n'
                for year, average_value in values.items():
                    text += f'{year}: {average_value}\n'
                self.label.setText(text)
            except Exception as e:
                self.label.setText(f'Ошибка: {e}')
        else:
            self.label.setText('Данные не загружены')


    """
    
    Подгружаем данные с 2018 по 2024 год(текущий) из Центробанка (с помощью ЦБ API)
    
    ID чешской кроны - R01760 (для другой валюты уточнить айди и поменять его значение)
    
    """

    def load(self):
        url = 'https://cbr.ru/scripts/XML_dynamic.asp?date_req1=21/05/2018&date_req2=20/05/2024&VAL_NM_RQ=R01760'
        response = requests.get(url)
        if response.status_code == 200:
            root_temp = ET.fromstring(response.content)
            data = []
            for record in root_temp.findall('Record'):
                date = record.attrib['Date']
                date_formatted = pd.to_datetime(date, dayfirst=True)  #
                value = float(record.find('Value').text.replace(',', '.'))
                data.append({'Date': date_formatted, 'Value': value})
            self.df = pd.DataFrame(data)
            min_date = self.df['Date'].min()
            max_date = self.df['Date'].max()
            self.data2.setMinimumDate(QDate(min_date.year, min_date.month, min_date.day))
            self.data2.setMaximumDate(QDate(max_date.year, max_date.month, max_date.day))
            self.starter.setMinimumDate(QDate(min_date.year, min_date.month, min_date.day))
            self.starter.setMaximumDate(QDate(max_date.year, max_date.month, max_date.day))
            self.tarter2.setMinimumDate(QDate(min_date.year, min_date.month, min_date.day))
            self.tarter2.setMaximumDate(QDate(max_date.year, max_date.month, max_date.day))
            self.label.setText('Данные загружены')
        else:
            self.label.setText('Ошибка')


    """
    
    Построение первого графика по заданию
    
    """

    def plot_first(self, save_path=None):
        if hasattr(self, 'df'):
            try:
                plt.figure()
                plt.plot(self.df['Date'], self.df['Value'], label='Курс')
                plt.xlabel('Дата')
                plt.ylabel('Курс')
                plt.title('Изменение курса за 7 лет')
                plt.grid(True)

                max_point = self.df.loc[self.df['Value'].idxmax()]
                min_point = self.df.loc[self.df['Value'].idxmin()]

                plt.scatter(max_point['Date'], max_point['Value'], color='orange', s=100, zorder=5,
                            label='Максимальное')
                plt.scatter(min_point['Date'], min_point['Value'], color='blue', s=100, zorder=5,
                            label='Минимальное')

                plt.annotate(f'Max: {max_point["Value"]}', xy=(max_point["Date"], max_point["Value"]),
                             xytext=(max_point["Date"], max_point["Value"] + 1),
                             arrowprops=dict(facecolor='black', shrink=0.05), fontsize=12, color='orange')
                plt.annotate(f'Min: {min_point["Value"]}', xy=(min_point["Date"], min_point["Value"]),
                             xytext=(min_point["Date"], min_point["Value"] - 1),
                             arrowprops=dict(facecolor='black', shrink=0.05), fontsize=12, color='blue')

                plt.legend()
                if save_path:
                    plt.savefig(save_path)
                else:
                    plt.show()
            except Exception as e:
                self.label.setText(f'Ошибка: {e}')
        else:
            self.label.setText('Данные не загружены')



    """
    
    Получить текущий курс чешской кроны (либо другой валюты, в зависимоти от ID)
    
    """


    def rate(self):
        if hasattr(self, 'df'):
            try:
                temp1 = self.data2.date().toString('dd/MM/yyyy')
                temp2 = self.df.loc[self.df['Date'] == temp1, 'Value'].values
                if len(temp2) > 0:
                    self.label.setText(f'Курс на {temp1}: {temp2[0]}')
                else:
                    self.label.setText('Данные не найдены')
            except Exception as e:
                self.label.setText(f'Ошибка: {e}')
        else:
            self.label.setText('Данные не загружены')



    """
    
    Построение второго графика по заданию
    
    """
    def plot_second(self, save_path=None):
        if hasattr(self, 'df'):
            try:
                self.df['Year'] = pd.to_datetime(self.df['Date'], format='%d/%m/%Y').dt.year
                average_values = self.df.groupby('Year')['Value'].mean()
                years = average_values.index
                values = average_values.values
                plt.figure()
                plt.bar(years, values)
                plt.xlabel('Год')
                plt.ylabel('Среднее значение')
                plt.title('Средние значения курса по годам за 7 лет')
                plt.grid(True)
                for i, value in enumerate(values):
                    plt.text(years[i], value, str(round(value, 2)), ha='center')
                if save_path:
                    plt.savefig(save_path)
                else:
                    plt.show()
            except Exception as e:
                self.label.setText(f'Ошибка: {e}')
        else:
            self.label.setText('Данные не загружены')


    """
    
    Построение третьего графика по заданию с изменением курса чешской кроны (либо другой валюты, в зависимости от ID)
    
    """

    def plot2(self):
        if hasattr(self, 'df'):
            try:
                date1 = self.starter.date().toString('yyyy-MM-dd')
                date2 = self.tarter2.date().toString('yyyy-MM-dd')
                date1 = pd.to_datetime(date1, format='%Y-%m-%d')
                date2 = pd.to_datetime(date2, format='%Y-%m-%d')
                self.df['Date'] = pd.to_datetime(self.df['Date'], format='%d/%m/%Y')
                filtered_df = self.df[(self.df['Date'] >= date1) & (self.df['Date'] <= date2)]

                if not filtered_df.empty:
                    plt.figure(figsize=(10, 5))
                    plt.plot(filtered_df["Date"], filtered_df["Value"], marker='s', linestyle='-', label='Курс')
                    plt.xlabel('Дата')
                    plt.ylabel('Курс')
                    plt.title(
                        f"Изменение курса за период с {date1.strftime('%d/%m/%Y')} по {date2.strftime('%d/%m/%Y')}")
                    plt.grid(True)
                    plt.legend()
                    plt.show()
                else:
                    self.label.setText('Данные не найдены')
            except Exception as e:
                self.label.setText(f'Ошибка: {e}')
        else:
            self.label.setText('Данные не загружены')


    """
    
    Сохранить данные, либо на Яндекс Диск, либо локально
    
    """

    def save(self):
        if hasattr(self, 'df'):
            try:
                path, _ = QFileDialog.getSaveFileName(self, 'Сохранить данные', '', 'Excel Files (*.xlsx)')
                if path:
                    with ExcelWriter(path) as writer:
                        self.df.to_excel(writer, 'Data', index=False)

                    path2 = f'{os.path.splitext(path)[0]}_plot.png'
                    path3 = f'{os.path.splitext(path)[0]}_diagram.png'
                    self.plot_first(save_path=path2)
                    self.plot_second(save_path=path3)

                    self.label.setText('Данные успешно сохранены')


                    token = 'y0_AgAAAABySPwTAAvCrgAAAAEEclgCAADuigppyt9AppykzWS5zuSJVRVeCg'

                    self.yandex(path, token)
                    self.yandex(path2, token)
                    self.yandex(path3, token)

                    self.label.setText('Данные сохранены')
                else:
                    self.label.setText('Сохранение отменено')
            except Exception as e:
                self.label.setText(f'Ошибка: {e}')
        else:
            self.label.setText('Данные не загружены')

    """
    
    Реализована работа с Яндекс API, чтобы сохранять графики на Яндекс Диск
    
    """

    def yandex(self, file_path, token):
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        upload = f'{url}?path={os.path.basename(file_path)}'
        headers_to_response = {'Authorization': f'OAuth {token}'}

        with open(file_path, 'rb') as file:
            response = requests.get(upload, headers=headers_to_response)
            response.raise_for_status()
            response_data = response.json()

            upload_response = requests.put(response_data['href'], data=file)
            upload_response.raise_for_status()


"""

Запуск приложения

"""

if __name__ == '__main__':
    app = QApplication(sys.argv)
    analyzer = Analyze()
    analyzer.show()
    sys.exit(app.exec_())

