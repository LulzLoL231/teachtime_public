# -*- coding: utf-8 -*-
#
#  TeachTime commands: defaults.
#  Created by LulzLoL231 at 2020/09/14
#
from os import getcwd, chdir
from subprocess import check_output
from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, CommandHelp, CommandStart

from misc import bot, log, conf, keys
from utils import (check_id, check_cmd, getStartKey,
                   getEnchKey)


@bot.callback_query_handler(lambda m: m.data == 'no')
async def query_no(query: types.CallbackQuery):
    await query.answer()
    await query.message.edit_reply_markup(types.InlineKeyboardMarkup())
    await cmd_cancel(query.message)


@bot.message_handler(lambda m: check_cmd(m, 'ench'))
@bot.message_handler(commands=('ench',))
async def enhancement(msg: types.Message):
    '''enhancement: TeachTime enhancement's

    Args:
        msg (types.Message): telegram message.
    '''
    log.info(f'Command "enhancement" from {msg.chat.mention} ({msg.from_user.id})')
    if await check_id(msg, conf):
        await msg.answer('Дополнительные команды', reply_markup=getEnchKey())


@bot.message_handler(commands=('track_on',))
async def track_on(msg: types.Message):
    '''track_on: Enable keyboards current lesson track.

    Args:
        msg (types.Message): telegram message.
    '''
    log.info(f'Command "track_on" from {msg.chat.mention} ({msg.from_user.id})')
    if await check_id(msg, conf):
        await msg.answer('Отслеживание расписания: <b>Включено.</b>')
        await keys.loop()


@bot.message_handler(CommandStart())
async def start(msg: types.Message):
    '''start: Bot cmd. Authorize user.

    Args:
        msg (types.Message): Telegram message.
    '''
    log.info(f'Command "start" from {msg.chat.mention} ({msg.from_user.id})')
    ev = await msg.answer('<code>Ожидайте авторизации...</code>')
    if await check_id(ev, conf, True):
        await ev.delete()
        await ev.answer(f'<b>Доступ разрешен!</b> Привет, {msg.chat.first_name}!', reply_markup=getStartKey())


@bot.message_handler(lambda m: check_cmd(m, 'help'))
@bot.message_handler(CommandHelp())
async def help(msg: types.Message):
    '''help: Show to user help page.

    Args:
        msg (types.Message): Telegram message.
    '''
    log.info(f'Command "help" from {msg.chat.mention} ({msg.from_user.id})')
    if await check_id(msg, conf):
        await msg.answer('<b>Команды бота:</b>\n'
                         '/start - Запуск/Авторизация.\n'
                         '/getLessons - Посмотреть сегодняшние пары.\n'
                         '/getNextDayLessons - Посмотреть пары на завтра.\n'
                         '/setTypesTimes - Задать расписание.\n'
                         '/setLessons - Задать пары.\n'
                         '/help - Посмотреть команды бота.\n'
                         '/ver - Версия бота.')


@bot.message_handler(commands=('ver', 'version'))
async def cmd_version(msg: types.Message):
    log.info(f'Command "version" from {msg.chat.mention} ({msg.from_user.id})')
    if await check_id(msg, conf):
        base = getcwd()
        chdir(conf.BASE_DIR)
        commit_hash = check_output(['git', 'describe', '--always']).decode().strip()
        commit_datetime = check_output(['git', 'log', '-n', '1', '--pretty=tformat:%aI', '--date=short']).decode().strip().split('T')
        chdir(base)
        commit_date = commit_datetime[0]
        commit_time = commit_datetime[1].split('+')[0]
        cnt = f'<b>LulzNetwork TeachTime Bot</b>\n\n<b>Commit hash:</b> <i>{commit_hash}</i>\n<b>Commit date:</b> <i>{commit_date}</i>\n<b>Commit time: </b><i>{commit_time}</i>\n<b>Author:</b> @LulzLoL231'
        await msg.answer(cnt)


@bot.message_handler(commands='cancel', state='*')
@bot.message_handler(Text(equals='отмена', ignore_case=True), state='*')
@bot.message_handler(Text(equals='нет', ignore_case=True), state='*')
async def cmd_cancel(msg: types.Message, state: FSMContext = None):
    log.info(f'Command "cancel" from {msg.chat.mention} ({msg.from_user.id})')
    if await check_id(msg, conf):
        if state:
            await state.finish()
        await msg.answer('Хорошо.', reply_markup=getStartKey())
