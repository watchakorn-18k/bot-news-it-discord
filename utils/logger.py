from logging import FileHandler, StreamHandler, getLogger, Formatter, DEBUG
from io import TextIOWrapper, BytesIO
from sys import stdout
from datetime import datetime

FORMAT = '[%(asctime)s] [%(levelname)s]: %(message)s'
NOW = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
LOGGER_LEVEL = DEBUG

logger = getLogger('main')
handler = StreamHandler(stdout)
file_handler = FileHandler(f'logs/{NOW}_main_log.log', 'w+', 'utf-8')

logger.setLevel(LOGGER_LEVEL)
handler.setFormatter(Formatter(FORMAT))

logger.addHandler(handler)
logger.addHandler(file_handler)

nextcord_logger = getLogger('nextcord')
nextcord_logger.setLevel(LOGGER_LEVEL)
nextcord_handler = StreamHandler(TextIOWrapper(BytesIO(), 'utf-8'))
nextcord_file_handler = FileHandler(f'logs/{NOW}_nextcord_log.log', 'w+', 'utf-8')

nextcord_handler.setFormatter(Formatter(FORMAT))
nextcord_logger.addHandler(nextcord_handler)
nextcord_logger.addHandler(nextcord_file_handler)
