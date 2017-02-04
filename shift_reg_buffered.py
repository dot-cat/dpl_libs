import logging
import threading

from dpl.libs.abs_shift_reg import AbsShiftRegister

logger = logging.getLogger(__name__)


class ShiftRegBuffered(AbsShiftRegister):
    """
    ShiftRegBuffered - декоратор для сдвиговорого регистра.
    Содержит дополнительный буфер содержимого и дополнительные методы для работы с ним
    """
    def __init__(self, shift_reg_instance: AbsShiftRegister):
        super().__init__()
        self.buffer = 0x0  # Начальное состояние буфера
        self.lock_write = threading.Lock()  # Блокировка для записи из других потоков

        if not isinstance(shift_reg_instance, AbsShiftRegister):
            raise ValueError("shift_reg_instance must be an instance of AbsShiftRegister"
                             "or derived class")

        self.shift_reg = shift_reg_instance

    def check_bit_pos(self, bit_pos):
        if not isinstance(bit_pos, int):
            raise ValueError('Bit number must be an integer')

        if bit_pos < 0:
            raise ValueError('Bit number must be positive or zero')

        capacity = self.get_capacity()

        if bit_pos >= capacity:
            raise ValueError('Bit position can\'t be bigger than '
                             'register capacity ({0})'.format(capacity))

    def get_buf_bit(self, bit_pos):
        """
        Считывание значения бита из буфера
        :param bit_pos: номер бита, значение которого необхожимо считать
        :return: none
        """
        self.check_bit_pos(bit_pos)

        return (self.buffer >> bit_pos) & 1

    def set_buf_bit(self, bit_pos, value):
        """
        Установка значения бита в буфере.
        Требует выполнения write_current_state для применения изменений
        :param bit_pos: номер (позиция) бита
        :param value: значение бита в позиции bit_num
        :return: none
        """
        self.check_bit_pos(bit_pos)

        if value == 0:
            self.buffer &= ~(1 << bit_pos)
        elif value == 1:
            self.buffer |= (1 << bit_pos)
        else:
            raise ValueError('Value must be 1 or zero, True or False')
        return

    def write_buffer(self):
        """
        Записать текущее содержимое буфера в регистр
        :return: none
        """
        logger.debug("%s: write planned. Data: %s", self, bin(self.buffer))

        with self.lock_write:  # Блокируем запись из других потоков
            self.shift_reg.write_data(self.buffer)

        logger.debug("%s: write finished", self)

    def get_buffer(self):
        """
        Получение копии буфера
        :return: целочисленное значение - последовательность нулей и единиц
        """
        return self.buffer

    def write_data(self, data):
        """
        Непосредственная запись в регистр с обновлением буфера
        :param data: записываемые данные
        :return: none
        """
        self.buffer = data
        self.write_buffer()

    def get_capacity(self):
        return self.shift_reg.get_capacity()

    def clear(self):
        """
        Очистка содержимого регистра
        :return: none
        """
        self.buffer = 0
        return self.shift_reg.clear()
