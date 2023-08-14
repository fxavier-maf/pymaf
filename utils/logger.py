import logging

from .config import *

pkg_logger = logging.getLogger(PACKAGE_NAME)
# Create a file handler
file_handler = logging.FileHandler(f'{PACKAGE_NAME}.log')

# Create a console handler
console_handler = logging.StreamHandler()

# Set the log level for the handlers
file_handler.setLevel(logging.DEBUG)
console_handler.setLevel(logging.INFO)

# Create a formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
pkg_logger.addHandler(file_handler)
pkg_logger.addHandler(console_handler)