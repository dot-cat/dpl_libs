import logging
import time
from collections import namedtuple

from dpl.libs.gpio_chooser import GPIO as GPIO

from dpl.libs.abs_shift_reg import AbsShiftRegister

LOGGER = logging.getLogger(__name__)

DELAY = 0.0


def pulse(pin):
    """
    Дергаем пин: подаем сначала ноль, потом - единицу, потом опять ноль
    :param pin: пин, который мы дергаем
    :return: none
    """
    GPIO.output(pin, GPIO.LOW)  # подаем на пин логичиеский 0
    time.sleep(DELAY)
    GPIO.output(pin, GPIO.HIGH)  # подаем на пин логичискую 1
    time.sleep(DELAY)
    GPIO.output(pin, GPIO.LOW)  # подаем на пин логичиеский 0


class ShiftRegGPIO(AbsShiftRegister):
    # Создаем новый класс с именем PortStruct и полями 'si', 'clk', 'rck', 'sclr'.
    # Класс - итерируемый, а также поддерживает обращение к элементам по индексу.
    # Подробнее - см. документацию namedtuple
    PortStruct = namedtuple('PortStruct', ['si', 'clk', 'rck', 'sclr'])

    def __setup_ports(self):
        """
        Установка всех портов на запись с обработкой ошибок
        :return: None
        """
        # Делаем обход всех портов
        for i in range(0, len(self.ports)):
            try:  # Пытаемся установить все порты на выход
                GPIO.setup(self.ports[i], GPIO.OUT)

            except:  # В случае ошибки...
                if i != 0:  # ...если хоть один пин уже установлен...
                    LOGGER.debug('Failed port setup. Cleaning up: %s', self.ports[0:i])
                    GPIO.cleanup(self.ports[0:i])  # ...очищаем все установленные порты...

                raise  # ...пробрасываем ошибку во внешний мир

    def __init__(self, si, sck, rck, sclr, num_of_slaves=0):  # обьявляем конструктор
        """
        Конструктор объекта
        :param si: номер пина для данных
        :param sck: номер пина для синхросигнала
        :param rck: номер пина для синхросигнала
        :param sclr: номер пина для очистки содержимого регистра
        :param num_of_slaves: количество зависимых сдвиговых регистров
        :return: None
        """
        super().__init__()

        # Контроль успешности выполнения конструктора. Зачем он нужен: http://bit.ly/2blHSL2
        self.__construction_finished = False

        LOGGER.debug("%s init started", self)

        if not isinstance(num_of_slaves, int):
            raise ValueError('num_of_slaves must be an integer')

        if num_of_slaves < 0:
            raise ValueError('num_of_slaves can\'t be negative')

        # Сохраняем номера портов
        self.ports = self.PortStruct(si, sck, rck, sclr)

        # Вычисляем разрядность сборки из регистров
        self.capacity = (num_of_slaves + 1) * 8

        # Устанавливаем все порты
        self.__setup_ports()

        LOGGER.debug("%s init finished", self)

        self.__construction_finished = True

        return

    def __del__(self):
        """
        Деструктор объекта: освобождение занятых ресурсов
        :return:
        """
        LOGGER.debug("%s destruction started", self)

        if self.__construction_finished:  # Если конструктор был выполнен успешно...
            self.clear()          # Очищаем содержимое регистра

            # Обновляем содержимое регистров хранения, выставлем все порты регистра в ноль
            pulse(self.ports.rck)
            self.set_zero()       # подаем на все пины нули

            # Освобождаем все занятые порты
            GPIO.cleanup(self.ports)

        LOGGER.debug("%s destruction finished", self)
        return

    def get_capacity(self):
        return self.capacity

    def set_zero(self):
        """
        Установка всех выводов в ноль
        :return: none
        """
        GPIO.output(self.ports, GPIO.LOW)  # Устанавливаем все пины в логический ноль
        return

    def clear(self):
        """
        Очистка содержимого регистра
        :return: none
        """
        GPIO.output(self.ports.sclr, GPIO.LOW)
        time.sleep(DELAY)
        GPIO.output(self.ports.sclr, GPIO.HIGH)
        return

    def write_data(self, data):
        """
        Запись данных во сдвиговый регистр
        :param data: 8*n бит данных
            Например:
            0000 0000 0000 0001 - выдать единицу на пин A главного регистра
            0000 0000 0000 1001 - выдать единицу на пины A и D главного регистра
            0000 1001 0000 0000  - выдать единицу на пины A и D первого зависимого регистра
        :return: none
        """
        if data >= (1 << self.capacity):
            raise ValueError(
                'Number of bits in data can\'t exceed {0} bits'.format(self.capacity)
            )

        # Очищаем содержимое регистра
        self.clear()

        # Маска для выборки старшего бита (most significant bit)
        msb_mask = 1 << (self.capacity - 1)

        for i in range(0, self.capacity):  # Обрабатываем 8*N битов
            if data & msb_mask:  # Проверяем старший бит, если он равен единице...
                GPIO.output(self.ports.si, GPIO.HIGH)  # ...то отправляем единицу в регистр
            else:
                GPIO.output(self.ports.si, GPIO.LOW)   # ...иначе отправляем ноль

            pulse(self.ports.clk)  # Выполняем сдвиг содержимого регистра

            data <<= 1  # Сдвигаем данные влево на один разряд

        pulse(self.ports.rck)  # Фиксируем значения
        return
