# -*- coding: utf-8 -*-
#
#  TeachTime commands group: set lessons
#  Created by LulzLoL231 at 2020/09/14
#
import os
import io
import tempfile

import aiohttp
import aiofiles
from pdf2image import convert_from_bytes as pdf
from aiogram import types
from aiogram.dispatcher import FSMContext

from misc import bot, log, db, conf
from utils import (
    check_id, check_cmd, parseLessons, getNowDate, getNextDate,
    getLessonsDaysKey, getNotPassedLessons, getLessonsTypesKey, getLessonsLength,
    getLessonsFromStateDict, isWeekend, getLessonsLengthKey, getStartKey,
    getVerifyKey, getDefaultTimeKey, getDefaultLessonsKey, getSendZamenaImagesKey
)
from states import SetTypesTimes, SetLessons


@bot.callback_query_handler(lambda m: m.data == 'sziTrue')
async def szi_query(query: types.CallbackQuery):
    log.debug('szi_query Called!')
    await query.answer('Отправляю...')
    await sendZamenaImages(query.message.chat.id)
    await query.message.delete()


@bot.callback_query_handler(lambda m: m.data == 'sziFalse')
async def noSzi_query(query: types.CallbackQuery):
    log.debug('noSzi_query Called!')
    await query.answer('Хорошо.')
    await query.message.delete()


@bot.callback_query_handler(lambda m: m.data == 'setLessons')
async def setLessons_query(query: types.CallbackQuery):
    await bot.bot.answer_callback_query(query.id)
    await bot.bot.edit_message_reply_markup(query.message.chat.id, query.message.message_id, types.InlineKeyboardMarkup())
    await setLessons_date(query.message, bot.current_state(chat=query.message.chat.id))


@bot.message_handler(lambda m: check_cmd(m, 'setLessons'))
@bot.message_handler(commands=('setLessons', 'sl'))
async def setLessons_date(msg: types.Message, state: FSMContext):
    log.info(f'Command "setLessons" from {msg.chat.mention} ({msg.from_user.id})')
    if await check_id(msg, conf):
        if isWeekend(getNowDate()):
            lessons = await db.getLessonsByDate(getNextDate())
            if lessons:
                await msg.answer('Сегодня выходной, и пары на завтра <b>установлены.</b>\n'
                                 f'Вот {parseLessons(lessons, getNextDate())}')
                await state.finish()
            else:
                await msg.answer('<b>Устанавливаем пары на завтра.</b>')
                await state.update_data(date=getNextDate())
                if await db.getTypesTimesByDate(getNextDate()):
                    await msg.answer('Пары стандартные?', reply_markup=getDefaultLessonsKey())
                    zam_msg = await msg.answer('<code>Получение замены...</code>')
                    await sendZamenaImages(zam_msg)
                    await SetLessons.wait_default.set()
                else:
                    await msg.answer('Время стандартное?', reply_markup=getDefaultTimeKey())
                    await SetLessons.wait_tt.set()
        else:
            lessons = await db.getLessonsByDate(getNowDate())
            if lessons:
                if isWeekend(getNextDate()):
                    monday_lessons = await db.getLessonsByDate(getNextDate(2))
                    if monday_lessons:
                        await msg.answer('Завтра <b>выходной</b>, а пары на <b>понедельник</b> уже установлены.')
                        await msg.answer(parseLessons(monday_lessons, getNextDate(2)))
                    else:
                        if msg.from_user == bot.bot.get_me():
                            await msg.edit_text('Завтра <b>выходной</b>, установим пары на <i>понедельник</i>.')
                        else:
                            await msg.answer('Завтра <b>выходной</b>, установим пары на <i>понедельник</i>.')
                        await state.update_data(date=getNextDate(2))
                        if await db.getTypesTimesByDate(getNextDate(2)):
                            await msg.answer('Пары стандартные?', reply_markup=getDefaultLessonsKey())
                            zam_msg = await msg.answer('<code>Получение замены...</code>')
                            await sendZamenaImages(zam_msg)
                            await SetLessons.wait_default.set()
                        else:
                            await msg.answer('Время стандартное?', reply_markup=getDefaultTimeKey())
                            await SetLessons.wait_tt.set()
                else:
                    await msg.answer('<b>Устанавливаем пары на завтра.</b>')
                    await state.update_data(date=getNextDate())
                    if await db.getTypesTimesByDate(getNextDate()):
                        await msg.answer('Пары стандартные?', reply_markup=getDefaultLessonsKey())
                        zam_msg = await msg.answer('<code>Получение замены...</code>')
                        await sendZamenaImages(zam_msg)
                        await SetLessons.wait_default.set()
                    else:
                        await msg.answer('Время стандартное?', reply_markup=getDefaultTimeKey())
                        await SetLessons.wait_tt.set()
            else:
                await msg.answer('<b>Устанавливаем пары.</b>')
                await msg.answer('Пары на сегодня или на завтра?', reply_markup=getLessonsDaysKey())
                await SetLessons.wait_date.set()


@bot.message_handler(state=SetLessons.wait_default, content_types=types.ContentType.TEXT)
async def setLessons_default(msg: types.message, state: FSMContext):
    if msg.text not in SetLessons.available_default:
        await msg.reply('<b>Сука. Стандартные. Или. Нестандартные. Блядь!</b>')
        return
    data = await state.get_data()
    if msg.text == 'Стандартные':
        lessons = await db.getDefaultLessonsByDate(data['date'])
        lessons = await db.getLessonsWithTimeByDate(lessons, data['date'])
        await state.update_data(lessons=lessons)
        await msg.answer(parseLessons(lessons, data['date']))
        await msg.answer('Это верная информация? <i>(Да/Нет)</i>', reply_markup=getVerifyKey())
        await SetLessons.wait_verify.set()
    else:
        lessons = await db.getDefaultLessonsByDate(data['date'])
        lessons = await db.getLessonsWithTimeByDate(lessons, data['date'])
        await msg.answer('<b>Пары которые должны быть:</b>\n' + parseLessons(lessons, data['date']))
        await msg.answer('Сколько будет пар?', reply_markup=getLessonsLengthKey())
        await SetLessons.wait_lesson_types_length.set()


@bot.message_handler(state=SetLessons.wait_date, content_types=types.ContentType.TEXT)
async def setLessons_length(msg: types.Message, state: FSMContext):
    if msg.text not in SetLessons.available_dates:
        await msg.reply('<b>Выбери дату нормально, сука!</b>')
        return
    if msg.text == 'На сегодня':
        lessons = await db.getLessonsByDate(getNowDate())
        if lessons:
            await state.finish()
            if getNotPassedLessons(lessons):
                ev = await msg.answer('Пары на сегодня <b>уже установлены</b>.',
                                      reply_markup=getStartKey())
                await ev.answer(parseLessons(lessons, getNowDate()))
            else:
                await msg.answer('Пары на сегодня <b>уже установлены</b>, и более того, <b>закончились!</b>', reply_markup=getStartKey())
        else:
            await state.update_data(date=getNowDate())
            if await db.getTypesTimesByDate(getNowDate()):
                await msg.answer('Пары стандартные?', reply_markup=getDefaultLessonsKey())
                zam_msg = await msg.answer('<code>Получение замены...</code>')
                await sendZamenaImages(zam_msg)
                await SetLessons.wait_default.set()
            else:
                await msg.answer('Время стандартное?', reply_markup=getDefaultTimeKey())
                await SetLessons.wait_tt.set()
    else:
        lessons = await db.getLessonsByDate(getNextDate())
        if lessons:
            await state.finish()
            if getNotPassedLessons(lessons):
                ev = await msg.answer('Пары на завтра <b>уже установлены</b>.', reply_markup=getStartKey())
                await ev.answer(parseLessons(lessons, getNextDate()))
            else:
                await msg.answer('Пары на завтра <b>уже установлены</b>, но какого-то хуя указаны как уже пройденные! <b>Как так сука!?</b>')
        else:
            await state.update_data(date=getNextDate())
            if await db.getTypesTimesByDate(getNextDate()):
                await msg.answer('Пары стандартные?', reply_markup=getDefaultLessonsKey())
                zam_msg = await msg.answer('<code>Получение замены...</code>')
                await sendZamenaImages(zam_msg)
                await SetLessons.wait_default.set()
            else:
                await msg.answer('Время стандартное?', reply_markup=getDefaultTimeKey())
                await SetLessons.wait_tt.set()


@bot.message_handler(state=SetLessons.wait_tt, content_types=types.ContentType.TEXT)
async def setLessons_tt(msg: types.Message, state: FSMContext):
    if msg.text not in SetTypesTimes.available_verify:
        await msg.reply('<b>Сука. Стандартное. Или. Нестандартное. Блядь!</b>')
        return
    data = await state.get_data()
    if msg.text == 'Стандартное':
        ev = await msg.answer('<b>Время установлено!</b>', reply_markup=getStartKey())
        if await db.setLessonsTypesTimes(data['date']) is not True:
            await ev.edit_text('<b>Непредвиденная ошибка!</b> Иди в логи сука!')
            await state.finish()
        else:
            await msg.answer('Пары стандартные?', reply_markup=getDefaultLessonsKey())
            await sendZamenaImages(msg.chat.id)
            await SetLessons.wait_default.set()
    else:
        await state.update_data(custom_tt=True)
        await msg.answer('Введи <b>время начала 1-ой пары</b> <code>(В формате: HH:MM)</code>.',
                         reply_markup=types.ReplyKeyboardRemove())
        await SetTypesTimes.wait_type1_start.set()


@bot.message_handler(state=SetLessons.wait_lesson_types_length, content_types=types.ContentType.TEXT)
async def setLessons_type(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    if 'length' not in data.keys():
        if msg.text not in SetLessons.available_length:
            await msg.reply('<b>Выбери колличество нормально, сука!</b>')
            return
        if msg.text == 'Одна':
            await state.update_data(length=1)
        elif msg.text == 'Две':
            await state.update_data(length=2)
        elif msg.text == 'Три':
            await state.update_data(length=3)
        elif msg.text == 'Четыре':
            await state.update_data(length=4)
    await setLessons_asktype(msg, state)


async def setLessons_asktype(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    log.debug(f'setLessons_asktype state data: {str(data)}')
    if getLessonsLength(data) == data['length']:
        await setLessons_verify(msg, state)
    else:
        await msg.answer('Какой парой будет пара?', reply_markup=getLessonsTypesKey())
        await SetLessons.wait_lesson_type.set()


@bot.message_handler(state=SetLessons.wait_lesson_type, content_types=types.ContentType.TEXT)
async def setLessons_name(msg: types.Message, state: FSMContext):
    if msg.text not in SetLessons.available_types:
        await msg.reply('<b>Выбери пару нормально, сука!</b>')
        return
    if msg.text == '1 пара':
        await state.update_data(lesson1_type=1)
        await SetLessons.wait_lesson1.set()
    elif msg.text == '2 пара':
        await state.update_data(lesson2_type=2)
        await SetLessons.wait_lesson2.set()
    elif msg.text == '3 пара':
        await state.update_data(lesson3_type=3)
        await SetLessons.wait_lesson3.set()
    elif msg.text == '4 пара':
        await state.update_data(lesson4_type=4)
        await SetLessons.wait_lesson4.set()
    key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    lessons = await db.getAllPossibleLessons()
    while len(lessons) != 0:
        if len(lessons) == 1:
            key.add(lessons.pop())
        else:
            key.add(lessons.pop(), lessons.pop())
    key.add('Другое')
    await msg.answer('Что за пара будет?', reply_markup=key)


@bot.message_handler(state=SetLessons.wait_lesson1, content_types=types.ContentType.TEXT)
async def setLessons_name1(msg: types.Message, state: FSMContext):
    if msg.text == 'Другое':
        await msg.answer('Введи название пары.', reply_markup=types.ReplyKeyboardRemove())
        await state.update_data(other_type=1)
        await SetLessons.wait_other.set()
    else:
        await state.update_data(lesson1=msg.text)
        await setLessons_asktype(msg, state)


@bot.message_handler(state=SetLessons.wait_lesson2, content_types=types.ContentType.TEXT)
async def setLessons_name2(msg: types.Message, state: FSMContext):
    if msg.text == 'Другое':
        await msg.answer('Введи название пары.', reply_markup=types.ReplyKeyboardRemove())
        await state.update_data(other_type=2)
        await SetLessons.wait_other.set()
    else:
        await state.update_data(lesson2=msg.text)
        await setLessons_asktype(msg, state)


@bot.message_handler(state=SetLessons.wait_lesson3, content_types=types.ContentType.TEXT)
async def setLessons_name3(msg: types.Message, state: FSMContext):
    if msg.text == 'Другое':
        await msg.answer('Введи название пары.', reply_markup=types.ReplyKeyboardRemove())
        await state.update_data(other_type=3)
        await SetLessons.wait_other.set()
    else:
        await state.update_data(lesson3=msg.text)
        await setLessons_asktype(msg, state)


@bot.message_handler(state=SetLessons.wait_lesson4, content_types=types.ContentType.TEXT)
async def setLessons_name4(msg: types.Message, state: FSMContext):
    if msg.text == 'Другое':
        await msg.answer('Введи название пары.', reply_markup=types.ReplyKeyboardRemove())
        await state.update_data(other_type=4)
        await SetLessons.wait_other.set()
    else:
        await state.update_data(lesson4=msg.text)
        await setLessons_asktype(msg, state)


@bot.message_handler(state=SetLessons.wait_other, content_types=types.ContentType.TEXT)
async def setLessons_other(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    other_type = data['other_type']
    if other_type == 1:
        await state.update_data(lesson1=msg.text)
        await setLessons_asktype(msg, state)
    elif other_type == 2:
        await state.update_data(lesson2=msg.text)
        await setLessons_asktype(msg, state)
    elif other_type == 3:
        await state.update_data(lesson3=msg.text)
        await setLessons_asktype(msg, state)
    elif other_type == 4:
        await state.update_data(lesson4=msg.text)
        await setLessons_asktype(msg, state)


async def setLessons_verify(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    lessons = getLessonsFromStateDict(data, await db.getTypesTimesByDate(data['date']))
    await msg.answer(parseLessons(lessons, data['date']))
    await msg.answer('Это верная информация? <i>(Да/Нет)</i>', reply_markup=getVerifyKey())
    await SetLessons.wait_verify.set()


@bot.message_handler(state=SetLessons.wait_verify, content_types=types.ContentType.TEXT)
async def setLessons_end(msg: types.Message, state: FSMContext):
    if msg.text not in SetLessons.available_verify:
        await msg.reply('<b>Сука. Да. Или. Нет. Блядь!</b>')
        return
    if msg.text == 'Да':
        data = await state.get_data()
        log.debug(f'setLessons_end data - {str(data)}')
        await state.finish()
        if 'lessons' not in data:
            lessons = getLessonsFromStateDict(data, await db.getTypesTimesByDate(data['date']))
        else:
            lessons = data['lessons']
        if lessons:
            for lesson in lessons:
                await db.addLesson(lesson['name'], lesson['type'], lesson['date'])
            await msg.answer('Пары <b>успешно установлены!</b>', reply_markup=getStartKey())
        else:
            await msg.answer('Возникла непредвидинная ошибка, иди в логи сука!', reply_markup=getStartKey())
    else:
        await state.finish()
        await msg.answer('Ну и иди нахуй, заново всё набирай... Или иди допиши эту функцию сука!', reply_markup=getStartKey())


async def sendZamenaQuery(chat_id: int) -> None:
    '''Sends zamena query to user.
    
    Args:
        chat_id (int): telegram chat id.
    '''
    await bot.bot.send_message(chat_id,
                               'Отправить замену?',
                               reply_markup=getSendZamenaImagesKey())


async def sendZamenaImages(msg: types.Message) -> None:
    '''Sends zamena images.

    Args:
        msg (types.Message): Telegram message.
    '''
    log.info(
        f'sendZamenaImages called with args: ({str(msg)})')
    await bot.bot.send_chat_action(msg.chat.id, types.ChatActions.UPLOAD_PHOTO)
    try:
        # TODO: Check ETag.
        async with aiohttp.ClientSession() as ses:
            async with ses.get('[REMOVED]') as resp:
                if resp.status == 200:
                    file = await resp.read()
    except Exception as e:
        log.error(
            f'sendZamenaImages Download Error: {str(e)}.')
        await msg.edit_text('<code>Ошибка при получении замены.</code>')
    else:
        await ses.close()
        try:
            images = pdf(file, 100)
        except Exception as e:
            log.error(
                f'sendZamenaImage Parse PDF Error: {str(e)}.')
            await msg.edit_text('<code>Ошибка при получении замены.</code>')
        else:
            log.info(
                f'sendZamenaImage Found {str(len(images))} images in zamena.')
            log.info(f'images: {str(images)}')
            saved = []
            for num, img in enumerate(images):
                buf = io.BytesIO()
                img.save(buf, 'JPEG')
                saved.append(io.BytesIO(buf.getvalue()))
            log.info(f'saved length: {str(len(saved))}')
            if len(saved) == 1:
                await msg.delete()
                await msg.answer_photo(types.InputFile(saved[0]), caption='Замена')
            else:
                media = types.MediaGroup()
                for num, img in enumerate(saved):
                    media.attach_photo(types.InputFile(img), caption=f'Замена {str(num + 1)} страница.')
                await msg.delete()
                await msg.answer_media_group(media)
            for buf in saved:
                buf.close()
