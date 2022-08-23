from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from utils.db_api.sqlite import Database
from data import config

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
<<<<<<< HEAD
db = Database(path_to_db='data/customer.db')
=======
db = Database(path_to_db="data/customer.db")
>>>>>>> 92a3aa76820dec9efde75530aaeef824966d78ab
