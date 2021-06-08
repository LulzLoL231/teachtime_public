# -*- coding: utf-8 -*-
#
#  TeachTime Telegram Bot.
#  Created by LulzLoL231 at 09/09/20
#
import logging
from os import environ

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import Config
from db import Database
from utils import BotKeyboards, Timer

if 'TT_ENVIRONMENT' in environ:
    if environ['TT_ENVIRONMENT'] == 'Debug':
        conf = Config(debug=True)
    elif environ['TT_ENVIRONMENT'] == 'Log_Debug':
        conf = Config(log_debug=True)
else:
    conf = Config(log_debug=True)
db = Database(conf)
log = logging.getLogger('TeachTime')
bot = Dispatcher(Bot(conf.getTgToken(), parse_mode='HTML'), storage=MemoryStorage())
timer = Timer(bot, conf, db)
keys = BotKeyboards(timer)
