# -*- coding: utf-8 -*-
#
#  TeachTime commands group: set timetable.
#  Created by LulzLoL231 at 2020/09/14
#
from aiogram import types
from aiogram.dispatcher import FSMContext

from misc import bot, db, conf
from utils import (
    check_id, check_cmd, getNowDate,
    parseTimes, getNextDate, getStartKey,
    getLessonsLengthKey
)
from states import SetTypesTimes, SetLessons


@bot.message_handler(lambda m: check_cmd(m, 'setTypesTimes'))
@bot.message_handler(commands=('setTypesTimes', 'times', 'stt'), state='*')
async def setTypesTimes_default(msg: types.Message):
    if await check_id(msg, conf):
        await msg.answer('<b>Устанавливаем расписание пар.</b>')
        key = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for i in SetTypesTimes.available_dates:
            key.add(i)
        await msg.answer('Ставим на сегодня или на завтра?', reply_markup=key)
        await SetTypesTimes.wait_types_date.set()


@bot.message_handler(state=SetTypesTimes.wait_types_date, content_types=types.ContentType.TEXT)
async def setTypesTimes_verify(msg: types.Message, state: FSMContext):
    if msg.text not in SetTypesTimes.available_dates:
        await msg.reply('Выбери дату нормально, сука!')
        return
    if msg.text == 'На сегодня':
        if await db.getTypesTimesByDate(getNowDate()):
            await state.finish()
            ev = await msg.answer('Расписание на сегодня <b>уже установлено.</b>', reply_markup=getStartKey())
            await ev.answer(parseTimes(await db.getTypesTimesByDate(getNowDate())))
        else:
            await state.update_data(date=getNowDate())
            key = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for i in SetTypesTimes.available_verify:
                key.add(i)
            await msg.answer('Расписание стандартное?', reply_markup=key)
            await SetTypesTimes.wait_types_default.set()
    else:
        if await db.getTypesTimesByDate(getNextDate()):
            await state.finish()
            ev = await msg.answer('Расписание на завтра <b>уже установлено.</b>', reply_markup=getStartKey())
            await ev.answer(parseTimes(await db.getTypesTimesByDate(getNextDate())))
        else:
            await state.update_data(date=getNextDate())
            key = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for i in SetTypesTimes.available_verify:
                key.add(i)
            await msg.answer('Расписание стандартное?', reply_markup=key)
            await SetTypesTimes.wait_types_default.set()


@bot.message_handler(state=SetTypesTimes.wait_types_default, content_types=types.ContentType.TEXT)
async def setTypesTimes_date(msg: types.Message, state: FSMContext):
    if msg.text not in SetTypesTimes.available_verify:
        await msg.reply('<b>Сука. Да. Или. Нет. Блядь!</b>')
        return
    if msg.text == 'Стандартное':
        ev = await msg.answer('<b>Расписание установлено!</b>', reply_markup=getStartKey())
        data = await state.get_data()
        await state.finish()
        if await db.setLessonsTypesTimes(data['date']) is not True:
            await ev.edit_text('<b>Непредвиденная ошибка!</b> Иди в логи сука!')
    else:
        await msg.answer('Введи <b>время начала 1-ой пары</b> <code>(В формате: HH:MM)</code>.', reply_markup=types.ReplyKeyboardRemove())
        await SetTypesTimes.wait_type1_start.set()


@bot.message_handler(state=SetTypesTimes.wait_type1_start, content_types=types.ContentType.TEXT)
async def setTypesTimes_type1_end(msg: types.Message, state: FSMContext):
    if msg.text not in SetTypesTimes.available_times:
        await msg.reply('Введи нормальное время, сука!')
        return
    await state.update_data(start1=msg.text)
    await SetTypesTimes.wait_type1_end.set()
    await msg.answer('Введи <b>время конца 1-ой пары</b> <code>(В формате: HH:MM)</code>.')


@bot.message_handler(state=SetTypesTimes.wait_type1_end, content_types=types.ContentType.TEXT)
async def setTypesTimes_type2_start(msg: types.Message, state: FSMContext):
    if msg.text not in SetTypesTimes.available_times:
        await msg.reply('Введи нормальное время, сука!')
        return
    await state.update_data(end1=msg.text)
    await SetTypesTimes.wait_type2_start.set()
    await msg.answer('Введи <b>время начала 2-ой пары</b> <code>(В формате: HH:MM)</code>.')


@bot.message_handler(state=SetTypesTimes.wait_type2_start, content_types=types.ContentType.TEXT)
async def setTypesTimes_type2_end(msg: types.Message, state: FSMContext):
    if msg.text not in SetTypesTimes.available_times:
        await msg.reply('Введи нормальное время, сука!')
        return
    await state.update_data(start2=msg.text)
    await SetTypesTimes.wait_type2_end.set()
    await msg.answer('Введи <b>время конца 2-ой пары</b> <code>(В формате: HH:MM)</code>.')


@bot.message_handler(state=SetTypesTimes.wait_type2_end, content_types=types.ContentType.TEXT)
async def setTypesTimes_type3_start(msg: types.Message, state: FSMContext):
    if msg.text not in SetTypesTimes.available_times:
        await msg.reply('Введи нормальное время, сука!')
        return
    await state.update_data(end2=msg.text)
    await SetTypesTimes.wait_type3_start.set()
    await msg.answer('Введи <b>время начала 3-ой пары</b> <code>(В формате: HH:MM)</code>.')


@bot.message_handler(state=SetTypesTimes.wait_type3_start, content_types=types.ContentType.TEXT)
async def setTypesTimes_type3_end(msg: types.Message, state: FSMContext):
    if msg.text not in SetTypesTimes.available_times:
        await msg.reply('Введи нормальное время, сука!')
        return
    await state.update_data(start3=msg.text)
    await SetTypesTimes.wait_type3_end.set()
    await msg.answer('Введи <b>время конца 3-ой пары</b> <code>(В формате: HH:MM)</code>.')


@bot.message_handler(state=SetTypesTimes.wait_type3_end, content_types=types.ContentType.TEXT)
async def setTypesTimes_type4_start(msg: types.Message, state: FSMContext):
    if msg.text not in SetTypesTimes.available_times:
        await msg.reply('Введи нормальное время, сука!')
        return
    await state.update_data(end3=msg.text)
    await SetTypesTimes.wait_type4_start.set()
    await msg.answer('Введи <b>время начала 4-ой пары</b> <code>(В формате: HH:MM)</code>.')


@bot.message_handler(state=SetTypesTimes.wait_type4_start, content_types=types.ContentType.TEXT)
async def setTypesTimes_type4_end(msg: types.Message, state: FSMContext):
    if msg.text not in SetTypesTimes.available_times:
        await msg.reply('Введи нормальное время, сука!')
        return
    await state.update_data(start4=msg.text)
    await SetTypesTimes.wait_type4_end.set()
    await msg.answer('Введи <b>время конца 4-ой пары</b> <code>(В формате: HH:MM)</code>.')


@bot.message_handler(state=SetTypesTimes.wait_type4_end, content_types=types.ContentType.TEXT)
async def setTypesTimes_times_verify(msg: types.Message, state: FSMContext):
    if msg.text not in SetTypesTimes.available_times:
        await msg.reply('Введи нормальное время, сука!')
        return
    await state.update_data(end4=msg.text)
    await SetTypesTimes.wait_times_verify.set()
    key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in SetLessons.available_verify:
        key.add(i)
    await msg.answer(parseTimes(await state.get_data()))
    await msg.answer('Это верная информация? <i>(Да/Нет)</i>', reply_markup=key)


@bot.message_handler(state=SetTypesTimes.wait_times_verify, content_types=types.ContentType.TEXT)
async def setTypesTimes_finish(msg: types.Message, state: FSMContext):
    if msg.text not in SetLessons.available_verify:
        await msg.reply('<b>Сука. Да. Или. Нет. Блядь!</b>')
        return
    if msg.text == 'Да':
        data = await state.get_data()
        if await db.setLessonsTypesTimes(data['date'], data['start1'], data['end1'], data['start2'], data['end2'],
                                         data['start3'], data['end3'], data['start4'], data['end4']):
            data = await state.get_data()
            if 'custom_tt' in data.keys():
                await msg.answer('Новое время <b>успешно установлено!</b>')
                await msg.answer('Сколько будет пар?', reply_markup=getLessonsLengthKey())
                await SetLessons.wait_lesson_types_length.set()
            else:
                await msg.answer('Новое время <b>успешно установлено!</b>', reply_markup=getStartKey())
                await state.finish()
        else:
            await msg.answer('Возникла непредвидинная ошибка, иди в логи сука!', reply_markup=getStartKey())
            await state.finish()
    else:
        await msg.answer('Ну и иди нахуй, заново всё набирай... Или иди допиши эту функцию сука!',
                         reply_markup=getStartKey())
        await state.finish()
