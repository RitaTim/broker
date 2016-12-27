# -*- coding: utf-8 -*-


class LogFormValidateError(Exception):
    """
        Ошибка при валидации форм логирования
    """
    def __init__(self, msg, errors):
        """
        :param msg: сообщение об ошибке
        :param errors: ошибки из формы
        """
        super(LogFormValidateError, self).__init__(msg)
        self.errors = errors
