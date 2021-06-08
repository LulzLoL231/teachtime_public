# -*- coding: utf-8 -*-
#
#  TeachTime commands group: show timetable.
#  Created by LulzLoL231 at 2020/09/14
#
from aiogram import types

from misc import bot, log, db, conf
from utils import (
    check_id, check_cmd, parseTimes,
    getNowDate, getNextDate, isWeekend,
    getTimeSetKey
)


@bot.message_handler(lambda m: check_cmd(m, 'todayTimetable'))
@bot.message_handler(commands=('todayTimetable', 'tt'))
async def todayTimetable(msg: types.Message):
    log.info(
        f'Command "todayTimetable" from {msg.chat.mention} ({msg.from_user.id})')
    if await check_id(msg, conf):
        ev = await msg.answer('<code>Получаем сегодняшние расписание...</code>')
        timetable = await db.getTypesTimesByDate(getNowDate())
        if timetable:
            await ev.edit_text(parseTimes(timetable))
        else:
            if isWeekend(getNowDate()):
                nextday_timetable = await db.getTypesTimesByDate(getNextDate())
                if nextday_timetable:
                    await ev.edit_text('<b>Сегодня выходной</b>, '
                                       'так что вот расписание на завтра:\n'
                                       f'{parseTimes(nextday_timetable)}')
                else:

                    await ev.edit_text('<b>Сегодня выходной</b>, '
                                       'и расписание на завтра '
                                       '<b>не установлено.</b>')
                    await ev.answer('Установим?', reply_markup=getTimeSetKey())
            else:
                await ev.edit_text('Расписание на сегодня <b>не установлено!</b>')
                await ev.answer('Установим?', reply_markup=getTimeSetKey())


@bot.message_handler(lambda m: check_cmd(m, 'nextDateTimetable'))
@bot.message_handler(commands=('nextDateTimetable', 'ndt'))
async def nextDateTimetable(msg: types.Message):
    log.info(
        f'Command "nextDateTimetable" from {msg.chat.mention} ({msg.from_user.id})')
    if await check_id(msg, conf):
        ev = await msg.answer('<code>Получаем расписание на завтра...</code>')
        timetable = await db.getTypesTimesByDate(getNextDate())
        if timetable:
            await ev.edit_text(parseTimes(timetable))
        else:
            if isWeekend(getNextDate()):
                await ev.edit_text('<b>Завтра выходной</b>.')
            else:
                ev = await ev.edit_text('Расписание на завтра <b>не установлено.</b>')
                await ev.answer('Установим?', reply_markup=getTimeSetKey())
