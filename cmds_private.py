# -*- coding: utf-8 -*-
#
#  TeachTime private commands
#  Created by LulzLoL231 at 2020/09/14
#
from datetime import datetime

from aiogram import types

from utils import check_id
from misc import bot, log, conf
from cmds_set_lessons import sendZamenaImages


@bot.message_handler(lambda m: m.text == '.id')
async def get_userid(msg: types.Message):
    '''get_userid: Bot private cmd. Show user his TG userID.

    Args:
        msg (types.Message): telegram message
    '''
    log.info(
        f'Private command "get_userid" from {msg.chat.mention} ({msg.from_user.id})')
    if await check_id(msg, conf):
        await msg.answer(f'<code>{str(msg.from_user.id)}</code>')


@bot.message_handler(lambda m: m.text == '.rm')
async def rm_key(msg: types.Message):
    '''rm_key: Bot private cmd. Deletes keyboard from user chat.

    Args:
        msg (types.Message): Telegram Message.
    '''
    log.info(
        f'Private command "rm_key" from {msg.chat.mention} ({msg.from_user.id})')
    if await check_id(msg, conf):
        await msg.answer('<code>Keyboard deleted.</code>', reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(lambda m: m.text == '.date')
async def get_date(msg: types.Message):
    '''get_date Bot private cmd. Returns server datetime.

    Args:
        msg (types.Message): telegram message.
    '''
    log.info(
        f'Private command "get_date" from {msg.chat.mention} ({msg.from_user.id})')
    if await check_id(msg, conf):
        await msg.answer(f'<code>{str(datetime.now())}</code>')


@bot.message_handler(lambda m: m.text == '.conf')
async def get_curr_conf(msg: types.Message):
    '''get_curr_conf: Bot private cmd. Returns bot current config.

    Args:
        msg (types.Message): Telegram message.
    '''
    log.info(
        f'Private command "get_curr_conf" from {msg.chat.mention} ({msg.from_user.id})')
    if await check_id(msg, conf):
        temp = '''<code>Time: {}
Debug: {}
Log_Debug: {}
DB path: {}
Admin ID: {}</code>'''
        await msg.answer(temp.format(str(datetime.now()), str(conf.debug), str(conf.log_debug),
                                     conf.db_name, str(conf.ADMIN_ID)))


@bot.message_handler(lambda m: m.text == '.send_zamena')
async def send_zamena(msg: types.Message):
    '''send_zamena: Bot private cmd. Sends zamena images.

    Args:
        msg (types.Message): Telegram message.
    '''
    log.info(f'Private command "send_zamena" from {msg.chat.mention} ({msg.from_user.id})')
    if await check_id(msg, conf):
        zam = await msg.answer('<code>Получение замены...</code>')
        dt_start = datetime.now()
        await sendZamenaImages(zam)
        dt_end = datetime.now()
        await msg.answer(f'<code>Time passed: {str((dt_end - dt_start).total_seconds())}</code>')
