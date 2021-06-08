# -*- coding: utf-8 -*-
#
#  TeachTime module "Config"
#  Created by LulzLoL231 at 09/09/20
#
import logging
from sys import platform


class Config(object):
    '''TeachTime config class.

    Args:
        db_name (str): TeachTime DB name.
        debug (bool): TeachTime debug mode.
        log_debug (bool): TeachTime logger debug level.

    Note:
        db_name: default is "teachtime.db".
        debug: default is False.
        log_debug: default is False.'''
    def __init__(self, db_name: str = '[REMOVED]', debug: bool = False, log_debug: bool = False):
        self.TG_TOKEN = '[REMOVED]'
        self.TG_TOKEN_BETA = '[REMOVED]'
        self.ADMIN_ID = 0
        self.KEY = b'[REMOVED]'
        self.BASE_DIR = '/home/lulz/TeachTime' if platform == 'linux' else 'C:\\Users\\lulz\\Documents\\python\\TeachTime'
        self.db_name = '/home/lulz/TeachTime/' + db_name if platform == 'linux' else db_name
        self.debug = debug
        self.log_debug = log_debug
        if log_debug or debug:
            logging.basicConfig(
                level=logging.DEBUG,
                format='[%(asctime)s] %(levelname)s | %(name)s | %(message)s')
        else:
            logging.basicConfig(
                level=logging.INFO,
                format='[%(asctime)s] %(levelname)s | %(name)s | %(message)s')

    def getTgToken(self) -> str:
        '''getTgToken: Returns TG_TOKEN_BETA if debug, else TG_TOKEN.

        Returns:
            str: Telegram bot token.'''
        if self.debug:
            return self.TG_TOKEN_BETA
        else:
            return self.TG_TOKEN
