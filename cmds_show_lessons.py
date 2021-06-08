# -*- coding: utf-8 -*-
#
#  TeachTime commands group: show lessons
#  Created by LulzLoL231 at 2020/09/14
#
from aiogram import types

from misc import bot, log, db, conf
from utils import (
    check_id, check_cmd, parseLessons,
    getNowDate, getNextDate, isWeekend,
    getLessonsSetKey, allLessonsPassed
)


@bot.message_handler(lambda m: check_cmd(m, 'getLessons'))
@bot.message_handler(commands=('getLessons', 'today', 'gtl'))
async def getLessons(msg: types.Message):
    '''getLessons: Show for user today lessons, or next day lessons if todays is gone.

    Args:
        msg (types.Message): Telegram message.
    '''
    if await check_id(msg, conf):
        log.info(
            f'Command "getLessons" from {msg.chat.mention} ({msg.from_user.id})')
        ev = await msg.answer('<code>Получаем пары на сегодня...</code>')
        today_lessons = await db.getLessonsByDate(getNowDate())
        log.debug(f'getLessons - today_lessons: {str(today_lessons)}')
        if today_lessons:
            if allLessonsPassed(today_lessons) is True:
                if isWeekend(getNextDate()):
                    monday_lessons = await db.getLessonsByDate(getNextDate(2))
                    if monday_lessons:
                        await ev.edit_text('На сегодня пары <b>закончились!</b> А завтра - <b>Выходной!</b> '
                                           'Вот пары на <b>понедельник</b>.')
                        await ev.answer(parseLessons(monday_lessons, getNextDate(2)))
                    else:
                        await ev.edit_text('На сегодня пары <b>закончились!</b> А завтра - <b>Выходной!</b>\n'
                                           'Пары на <b>понедельник</b> не установлены.')
                        await ev.edit_reply_markup(reply_markup=getLessonsSetKey())
                else:
                    next_day_lessons = await db.getLessonsByDate(getNextDate())
                    if next_day_lessons:
                        await ev.edit_text('На сегодня пары <b>закончились!</b>\n'
                                           'Вот пары на <b>завтра:</b>\n'
                                           f'{parseLessons(next_day_lessons, getNextDate())}')
                    else:
                        await ev.edit_text('На сегодня пары <b>закончились!</b>\n'
                                           'А на завтра пары <b>не установлены!</b>\n'
                                           'Пары на <b>понедельник</b> не установлены.')
                        await ev.edit_reply_markup(reply_markup=getLessonsSetKey())
            else:
                await ev.edit_text(parseLessons(today_lessons, getNowDate()))
        else:
            next_day_lessons = await db.getLessonsByDate(getNextDate())
            log.debug(f'getLessons - next_day_lessons: {str(next_day_lessons)}')
            if next_day_lessons:
                if isWeekend(getNowDate()):
                    await ev.edit_text('Сегодня <b>выходной.</b> '
                                       'Вот пары на завтра:\n'
                                       f'{parseLessons(next_day_lessons, getNextDate())}')
                else:
                    await ev.edit_text('На сегодня пары <b>кончились</b>, '
                                       'так что вот на <b>завтра:</b>\n'
                                       f'{parseLessons(next_day_lessons, getNextDate())}')
            else:
                if isWeekend(getNowDate()):
                    await ev.edit_text('Сегодня <b>выходной.</b>\nА пары на завтра <b>не установлены.</b>')
                    await ev.edit_reply_markup(reply_markup=getLessonsSetKey())
                else:
                    await ev.edit_text('Пары на сегодня <b>не установлены.</b>\n'
                                       'И на завтра <b>тоже.</b>')
                    await ev.edit_reply_markup(reply_markup=getLessonsSetKey())


@bot.message_handler(lambda m: check_cmd(m, 'getNextDayLessons'))
@bot.message_handler(commands=('getNextDayLessons', 'nextDay', 'gndl'))
async def getNextDayLessons(msg: types.Message):
    '''getNextDayLessons: Show for user next day lessons.

    Args:
        msg (types.Message): telegram message.
    '''
    if await check_id(msg, conf):
        log.debug(
            f'Command "getNextDayLessons" from {msg.chat.mention} ({msg.from_user.id})')
        ev = await msg.answer('<code>Получаем пары на завтра...</code>')
        next_day_lessons = await db.getLessonsByDate(getNextDate())
        if next_day_lessons:
            await ev.edit_text(parseLessons(next_day_lessons, getNextDate()))
        else:
            if isWeekend(getNextDate()):
                monday_lessons = await db.getLessonsByDate(getNextDate(2))
                if monday_lessons:
                    await ev.edit_text('Завтра <b>выходной</b>. Вот пары на <b>понедельник</b>.')
                    await ev.answer(parseLessons(monday_lessons, getNextDate(2)))
                else:
                    await ev.edit_text('Завтра <b>выходной</b>. Пары на <b>понедельник</b> не установлены.')
                    await ev.edit_reply_markup(reply_markup=getLessonsSetKey())
            else:
                await ev.edit_text('Пары на завтра <b>не установлены</b>!')
                await ev.edit_reply_markup(reply_markup=getLessonsSetKey())
