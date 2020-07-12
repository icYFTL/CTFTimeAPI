import logging


class IncorrectInput:
    def __init__(self, ip, data):
        logging.getLogger('api')
        logging.warning(f'Incorrect input data [{str(data)}] from {ip}')

    @staticmethod
    def message(context=""):
        return context or "Incorrect data passed."
