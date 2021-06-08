# -*- coding: utf-8 -*-
#
#  TeachTime execute script
#  Created by LulzLoL231 at 2020/09/14
#
from aiogram.utils.executor import start_polling

from misc import bot
from cmds_defaults import *
from cmds_private import *
from cmds_ench import *
from cmds_set_lessons import *
from cmds_show_lessons import *
from cmds_show_timetable import *
from cmds_set_timetables import *
from cmds_timer import *
from cmds_info import *


if __name__ == "__main__":
    start_polling(bot)
