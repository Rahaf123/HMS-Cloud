 import logging


class Logger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Logger, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.logger = logging.getLogger('my_logger')
        self.logger.setLevel(logging.DEBUG)

        # Create a file handler and set the log level
        file_handler = logging.FileHandler('app.log')
        file_handler.setLevel(logging.DEBUG)

        # Create a log formatter and add it to the file handler
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # Add the file handler to the logger
        self.logger.addHandler(file_handler)

    def log(self, message):
        self.logger.debug(message)
