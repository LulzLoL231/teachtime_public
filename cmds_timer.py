# -*- coding: utf-8 -*-
#
#  TeachTime commands: notifications.
#  Created by LulzLoL231 at 2020/09/14
#
import logging
from random import choice

from aiogram import types

from misc import bot, conf, timer
from utils import (
    check_id, check_cmd, getLessonEt
)


log = logging.getLogger('TeachTime Timer')


def getRandomGood() -> str:
    '''getRandomGood: returns pseudorandom congrats text.

    Returns:
        str: congrats text.
    '''
    smile = ['Молодец!', 'Хорошая работа!', 'Красава!', 'Красавчик!', 'Респект!', 'NICE!', 'Awesome!']
    return choice(smile)


def getRandomAngry() -> str:
    '''getRandomAngry: returns pseudorandom angry text.

    Returns:
        str: angry text.
    '''
    angry = ['Долбаёб.', 'Дебил.', 'Дегенерат.', 'Уёбок', 'Долбоящер.', 'Тупой.', 'Идиот.']
    return choice(angry)


@bot.callback_query_handler(lambda m: m.data.startswith('visit:'))
async def visit_lesson(query: types.CallbackQuery):
    await bot.bot.answer_callback_query(query.id, getRandomGood())
    lessonid = await timer.getLessonIDFromLessonInfo(query.data)
    if lessonid:
        await timer.db.visitLesson(lessonid)
        await bot.bot.edit_message_reply_markup(query.message.chat.id, query.message.message_id, types.InlineKeyboardMarkup())
    else:
        log.debug(f'visitLesson error - lessonid: {str(lessonid)}')
        await bot.bot.send_message(query.from_user.id, 'Что-то пошло не так...')


@bot.callback_query_handler(lambda m: m.data == 'notvisited')
async def not_visit_lesson(query: types.CallbackQuery):
    await bot.bot.answer_callback_query(query.id, getRandomAngry())
    await bot.bot.edit_message_reply_markup(query.message.chat.id, query.message.message_id, types.InlineKeyboardMarkup())


def getNumWithSuffix(num: int) -> str:
    '''getNumWithSuffix: returns number with suffix.

    Args:
        num (int): number.

    Returns:
        str: number with suffix.
    '''
    if num == 3:
        return '3-ей'
    else:
        return f'{str(num)}-ой'


@bot.message_handler(regexp='Сейчас: ')
@bot.message_handler(lambda m: check_cmd(m, 'timer'))
@bot.message_handler(lambda m: check_cmd(m, 'timeron'))
@bot.message_handler(commands=('timer', 'notify', 't', 'n', 'timeron', 'notifyon', 'ton', 'non'))
async def timerstatus(msg: types.Message):
    if await check_id(msg, conf):
        log.info(
            f'Command "timerstatus" from {msg.chat.mention} ({msg.from_user.id})')
        if timer.work:
            if timer.lesson:
                lesson = await timer.getCurrentLesson()
                start_time = await timer.getLessonStartEt()
                if start_time.total_seconds() > 0:
                    await msg.answer(f'До начала <b>{getNumWithSuffix(lesson["type"])} пары {lesson["name"]}</b> '
                                     f'осталось <b>{getLessonEt(td=start_time)}</b>')
                else:
                    end_time = await timer.getLessonEndEt()
                    if end_time.total_seconds() > 0:
                        await msg.answer(f'До конца <b>{getNumWithSuffix(lesson["type"])} пары {lesson["name"]}</b> '
                                         f'осталось <b>{getLessonEt(td=end_time)}</b>')
            else:
                await msg.answer('На <b>сегодня</b> уроков <b>нету/кончились</b>.')
        else:
            ev = await msg.answer('Уведомления <b>выключены.</b> Идёт включение...')
            await ev.edit_text('Уведомления <b>включены!</b>')
            await timer.main()


@bot.message_handler(lambda m: check_cmd(m, 'timeroff'))
@bot.message_handler(commands=('timeroff', 'notifyoff', 'toff', 'noff'))
async def timeroff(msg: types.Message):
    if await check_id(msg, conf):
        log.info(f'Command "timeroff" from {msg.chat.mention} ({msg.from_user.id})')
        if timer.work:
            timer.work = False
            await msg.answer('Уведомления <b>выключены.</b>')
        else:
            await msg.answer('Уведомления <b>уже выключены!</b>')
