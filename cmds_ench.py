# -*- coding: utf-8 -*-
#
#  TeachTime commands: enhancements.
#  Created by LulzLoL231 at 2020/09/14
#
from aiogram import types
from aiogram.dispatcher import FSMContext

from misc import bot, log, db
from utils import (parsePractice, getNowDate, getPracticeKey,
                   getPracticeDefaultKey, getVerifyKey, getStartKey)
from states import Practice, SetTypesTimes


@bot.callback_query_handler(lambda m: m.data == 'ench:practice')
async def ench_practice(query: types.CallbackQuery):
    log.debug(f'query "ench_practice" from {query.message.chat.mention} ({query.message.chat.id}).')
    await query.answer()
    practice = await db.getPractice(date=getNowDate())
    await query.message.edit_text(parsePractice(practice))
    await query.message.edit_reply_markup(getPracticeKey(False))


@bot.callback_query_handler(lambda m: m.data == 'ench:practice:end')
async def ench_practice_end(query: types.CallbackQuery):
    await query.answer()
    practice = await db.getPractice(date=getNowDate())
    await db.endPractice(practice['start_date'], getNowDate())
    await query.message.edit_reply_markup(types.InlineKeyboardMarkup())
    practice_num = await db.getPracticeNum(practice)
    await query.message.edit_text(f'Практика #{str(practice_num)} - Закончилась!')


@bot.callback_query_handler(lambda m: m.data == 'ench:practice:start')
async def ench_practice_start(query: types.CallbackQuery):
    await query.answer()
    first_practice = await db.getPractice(rowid=0)
    if first_practice:
        cnt = 'Началась практика!\nВремя начала и конца уроков та-же что и в прошлый раз?'
        await query.message.edit_reply_markup(getPracticeDefaultKey('times'))
    else:
        cnt = 'Началась практика!\nВведи время начала урока <i>(формат: <b>HH:MM</b>)</i>'
        await Practice.wait_timeFrom.set()
        await query.message.edit_reply_markup(types.InlineKeyboardMarkup())
    await query.message.edit_text(cnt)


@bot.message_handler(state=Practice.wait_timeFrom)
async def ench_practice_timeFrom(msg: types.Message, state: FSMContext):
    if msg.text not in SetTypesTimes.available_times:
        await msg.reply('Время нормально введи.')
        return
    await state.update_data(timeFrom=msg.text)
    await Practice.wait_timeTo.set()
    await msg.answer('Введи время конца урока <i>(формат: <b>HH:MM</b>)</i>')


@bot.message_handler(state=Practice.wait_timeTo)
async def ench_practice_timeTo(msg: types.Message, state: FSMContext):
    if msg.text not in SetTypesTimes.available_times:
        await msg.reply('Время нормально введи.')
        return
    await state.update_data(timeTo=msg.text)
    await Practice.wait_teacherFullname.set()
    await msg.answer('Введи полное имя преподавателя <i>(формат: <b>Фамилия Имя Отчество</b>)</i>')


@bot.message_handler(state=Practice.wait_teacherFullname)
async def ench_practice_teacher(msg: types.Message, state: FSMContext):
    await state.update_data(teacher=msg.text)
    data = await state.get_data()
    cnt = f'Время практики: <b>с {data["timeFrom"]} до {data["timeTo"]}</b>\nПреподователь: <b>{data["teacher"]}</b>'
    cnt += '\n\nВсё верно?'
    await Practice.wait_verify.set()
    await msg.answer(cnt, reply_markup=getVerifyKey())


@bot.message_handler(state=Practice.wait_verify)
async def ench_practice_new_setup(msg: types.Message, state: FSMContext):
    if msg.text == 'Да':
        data = await state.get_data()
        await state.finish()
        last_practice = await db.getLastPractice()
        if last_practice:
            last_practice_num = await db.getPracticeNum(last_practice)
            await msg.answer(f'Практика #{str(last_practice_num + 1)} добавлена в БД.', reply_markup=getStartKey())
            last_practice['start_date'] = getNowDate()
            last_practice['status'] = 1
            last_practice['end_date'] = None
            last_practice['timeFrom'] = data['timeFrom']
            last_practice['timeTo'] = data['timeTo']
        else:
            await msg.answer('Практика #1 добавлена в БД.', reply_markup=getStartKey())
            last_practice = {'status': 1, 'start_date': getNowDate(), 'timeFrom': data['timeFrom'], 'timeTo': data['timeTo'], 'end_date': None}
        await db.startPractice(getNowDate(), data['timeFrom'], data['timeTo'], data['teacher'])
        await msg.answer(parsePractice(last_practice))


@bot.callback_query_handler(lambda m: m.data == 'ench:practice:times:yes')
async def ench_practice_default_times(query: types.CallbackQuery):
    await query.answer()
    await query.message.edit_text('А преподователь тот-же?')
    await query.message.edit_reply_markup(getPracticeDefaultKey('teacher'))


@bot.callback_query_handler(lambda m: m.data == 'ench:practice:teacher:yes')
async def ench_practice_default_teacher(query: types.CallbackQuery):
    await query.answer()
    last_practice = await db.getLastPractice()
    if last_practice:
        last_practice['start_date'] = getNowDate()
        last_practice['end_date'] = None
        last_practice['status'] = 1
        await query.message.edit_reply_markup(getPracticeDefaultKey('def_verify'))
        await query.message.edit_text(f'Всё верно?\n{parsePractice(last_practice)}')
    else:
        await query.message.edit_reply_markup(types.InlineKeyboardMarkup())
        await query.message.edit_text('<b>Ошибка</b>. Прошлая практика не найдена в БД.')


@bot.callback_query_handler(lambda m: m.data == 'ench:practice:def_verify:yes')
async def ench_practice_default_setup(query: types.CallbackQuery):
    last_practice = await db.getLastPractice()
    last_practice_num = await db.getPracticeNum(last_practice)
    await query.answer(f'Практика #{str(last_practice_num + 1)} добавлена в БД.')
    teacher = await db.getTeacherByLessonName('Практика')
    teacher_fullname = ' '.join(teacher.values())
    await db.startPractice(getNowDate(), last_practice['timeFrom'], last_practice['timeTo'], teacher_fullname)
    last_practice['start_date'] = getNowDate()
    last_practice['status'] = 1
    last_practice['end_date'] = None
    await query.message.edit_reply_markup(types.InlineKeyboardMarkup())
    await query.message.edit_text(parsePractice(last_practice))
