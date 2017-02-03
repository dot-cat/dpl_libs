class AbsShiftRegister(object):
    def __init__(self):
        pass

    def get_capacity(self):
        raise NotImplementedError

    def clear(self):
        """
        Очистка содержимого регистра
        :return: none
        """
        raise NotImplementedError

    def write_data(self, data):
        """
        Запись данных во сдвиговый регистр
        :param data: 8 бит данных
            Например:
            0000 0000 0000 0001 - выдать единицу на пин A главного регистра
            0000 0000 0000 1001 - выдать единицу на пины A и D главного регистра
            0000 1001 0000 0000  - выдать единицу на пины A и D первого зависимого регистра
        :return: none
        """
        raise NotImplementedError
