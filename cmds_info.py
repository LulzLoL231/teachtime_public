# -*- coding: utf-8 -*-
#
#  TeachTime commands: Lessons and teachers information.
#  Created by LulzLoL231 at 2020/09/14
#
from aiogram import types
from aiogram.dispatcher import FSMContext

from misc import bot, conf, db, log
from utils import (
    check_id, check_cmd, getStartKey,
    parseTeacher, parseStudent
)
from states import Search


@bot.message_handler(lambda m: check_cmd(m, 'search'))
@bot.message_handler(commands=('search', 's'))
async def search_peoples(msg: types.Message):
    '''search_peoples: Search info from DB.

    Args:
        msg (types.Message): Telegram message.
    '''
    log.info(f'Command "search" from {msg.chat.mention} ({msg.from_user.id})')
    if await check_id(msg, conf):
        await msg.answer('Введи что ты знаешь об субъекте\n'
                         '<i>(Фамилия, Имя, Отчество, Кличка, Предмет, Кто такой)</i>',
                         reply_markup=types.ReplyKeyboardRemove())
        await Search.wait_ctx.set()


@bot.message_handler(state=Search.wait_ctx)
async def search_final(msg: types.Message, state: FSMContext):
    await state.finish()
    data = msg.text
    ev = await msg.answer('<code>Идёт поиск...</code>')
    cnt = '\n\n'
    students = await db.searchStudent(data)
    if students:
        if type(students) is list:
            cnt = cnt.join([parseStudent(i) for i in students])
        else:
            cnt = parseStudent(students)
    else:
        teachers = await db.searchTeacher(data)
        if teachers:
            if type(teachers) is list:
                cnt = cnt.join([parseTeacher(i) for i in teachers])
            else:
                cnt = parseTeacher(teachers)
        else:
            cnt = 'Поиск <b>не дал результатов.</b>'
    await ev.delete()
    await msg.answer(cnt, reply_markup=getStartKey())
