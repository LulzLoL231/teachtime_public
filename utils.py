# -*- coding: utf-8 -*-
#
#  TeachTime module "utilites".
#  Created by LulzLoL231 at 09/09/20
#
import locale
import datetime
import logging
import hmac
import hashlib
from sys import platform
from asyncio import sleep
from logging import getLogger

from aiogram import types, Dispatcher
from pymorphy2 import MorphAnalyzer

from config import Config


log = logging.getLogger('TeachTime Utilites')
if platform == 'linux':
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
else:
    locale.setlocale(locale.LC_ALL, 'ru')


def getGentLessonName(name: str) -> str:
    '''getGentLessonName returns gent lexema name.

    Args:
        name (str): lesson name.

    Returns:
        str: lesson name in gent lexema.
    '''
    return ' '.join([MorphAnalyzer().parse(i)[0].inflect({'gent'}).word for i in name.split()]).strip().capitalize()


def getAbltLexema(text: str) -> str:
    '''getAbltLexema: return ablt lexema text.

    Args:
        text (str): some text.

    Returns:
        str: text in ablt lexema.
    '''
    return ' '.join([MorphAnalyzer().parse(i)[0].inflect({'ablt'}).word for i in text.split()]).strip().capitalize()


def getNowDate() -> str:
    '''getNowDate: Returns date for now in ISO format (YYYY-MM-DD)

    Returns:
        str: date for now.
    '''
    date = str(datetime.datetime.now())
    log.debug(f'getNowDate - date: {date}')
    return date.split(' ')[0]


def getNowTime() -> str:
    '''getNowTime: Returns time for now in ISO format (HH:MM).

    Returns:
        str: time for now.
    '''
    time = str(datetime.datetime.now()).split(' ')[1].split(':')
    return time[0] + ':' + time[1]


def getNextDate(offset: int = 1) -> str:
    '''getNextDate: Returns next day date in ISO format (YYYY-MM-DD).

    Args:
        offset (int): offset days. Default is 1.

    Returns:
        str: next day date.
    '''
    now = datetime.datetime.now()
    log.debug(f'getNextDate - now: {str(now)}')
    td = now + datetime.timedelta(days=offset)
    log.debug(f'getNextDate - td: {str(td)}')
    return str(td).split(' ')[0]


def getDateObjFromStr(date: str) -> datetime.datetime:
    '''getDateObjFromStr: Retuns datetime object from date string in ISO format.

    Args:
        date (str): date string in ISO format.

    Returns:
        datetime.datetime: datetime object.
    '''
    return datetime.datetime.fromisoformat(date)


def isTime(time: str) -> bool:
    '''isTime: check if provided time is real time.

    Args:
        time (str): possible time var.

    Returns:
        bool: True or False.
    '''
    return True if len(time.split(':')) == 2 else False


def isDate(date: str) -> bool:
    '''isDate: check if provided date is real date.

    Args:
        date (str): possible date var.

    Returns:
        bool: True or False.
    '''
    return True if len(date.split('-')) == 3 else False


def isLessonPassed(lesson: dict) -> bool:
    '''isLessonPassed: return True if lesson is passed/visited, otherwise False.

    Args:
        lesson (dict): lesson dict.

    Returns:
        bool: True or False
    '''
    log = getLogger('TeachTime Utilites::isLessonPassed')
    log.debug(f'Args: Lesson: {str(lesson)}')
    if bool(lesson['visit']):
        log.debug(f'Lesson: {lesson["name"]} is visited. (True)')
        return True  # 'visited'
    else:
        if getDateObjFromStr(getNowDate() + ' ' + getNowTime()) >= getDateObjFromStr(lesson['date']+ ' ' + lesson['to']):
            log.debug(f'Lesson: {lesson["name"]} is ended. (True)')
            return True  # 'ended'
        else:
            if getDateObjFromStr(getNowDate() + ' ' + getNowTime()) < getDateObjFromStr(lesson['date'] + ' ' + lesson['from']):
                log.debug(f'Lesson: {lesson["name"]} not started yet. (False)')
                return False  # 'not started'
            else:
                log.debug(f'Lesson: {lesson["name"]} in progress. (False)')
                return False  # 'in-progress'
            return False
        return False


def getNotPassedLessons(lessons: list) -> list:
    '''getNotPassedLessons returns array with not passed lessons.

    Args:
        lessons (list): lessons array

    Returns:
        list: not passed lessons array.
    '''
    log.debug(f'Function "getNotPassedLessons" is called with args: Lessons: {str(lessons)}')
    not_passed = []
    for lesson in lessons:
        if isLessonPassed(lesson) is False:
            not_passed.append(lesson)
    return not_passed


def allLessonsPassed(lessons: list) -> bool:
    '''allLessonsPassed if any lesson in array is NOT passed, returns False

    Args:
        lessons (list): lessons array

    Returns:
        bool: True or False
    '''
    not_passed = getNotPassedLessons(lessons)
    if not_passed:
        return False
    return True


def getWeektypenameByWeektype(weektype: int) -> str:
    '''getWeektypenameByWeektype: return weektype name by weektype.

    Args:
        weektype (int): weektype.

    Returns:
        str: weektype name.
    '''
    return 'Числителю' if weektype == 0 else 'Знаменателю'


def parseLessons(array: list, date: str) -> str:
    '''parseLessons: Parse array with lessons and return telegram message content with it.

    Args:
        array (list): lessons array.
        date (str): lessons date.

    Returns:
        str: telegram message content.
    '''
    weektype = getWeektypenameByWeektype(getWeektypeByDate(date))
    date = getDateName(getDateObjFromStr(date))
    cnt = f'Пары на {date}\n<i>Учимся по <b>{weektype}</b></i>\n'
    sep = '\n'
    lesson_template = '<b>{} пара: {}</b>\nС: <code>{}</code> До: <code>{}</code>'
    ended_lesson_template = '<s><b>{} пара: {}</b></s>\n<s>С: {} До: {}</s>'
    for i in array:
        if isLessonPassed(i):
            cnt += ended_lesson_template.format(i['type'], i['name'], i['from'], i['to']) + sep
        else:
            cnt += lesson_template.format(i['type'], i['name'], i['from'], i['to']) + sep
    log.debug(f'parseLessons result: {str(cnt)}')
    return cnt


def getVKProfileURI(vk_id: str) -> str:
    '''getVKProfileURI: returns VK profile URI like "https://vk.com/id<ID>"

    Args:
        vk_id (str): VK profile ID

    Returns:
        str: VK profile URI
    '''
    return f'https://vk.com/id{vk_id}'


def parseTimes(times: dict) -> str:
    '''parseTimes: Parse dict with lessons_types times and return telegram message content with it.

    Args:
        times (dict): lessons_types times dict.

    Returns:
        str: telegram message content.
    '''
    date = getDateName(getDateObjFromStr(times["date"]))
    cnt = f'Расписание на {date}\n'
    sep = '\n'
    type_template = '<b>{} пара:</b> С: <code>{}</code> До: <code>{}</code>'
    cnt += type_template.format('1', times['start1'], times['end1']) + sep
    cnt += type_template.format('2', times['start2'], times['end2']) + sep
    cnt += type_template.format('3', times['start3'], times['end3']) + sep
    cnt += type_template.format('4', times['start4'], times['end4'])
    log.debug(f'parseTimes result: {str(cnt)}')
    return cnt


def getDateName(date: datetime.datetime) -> str:
    '''getDateName: returns date name from datetime object.

    Args:
        date (datetime): datetime object.

    Returns:
        str: date name.
    '''
    return date.strftime('%d %b %Y (%A)')


def getStudentYears(date: datetime.datetime) -> int:
    '''getStudentYears: returns student years.

    Args:
        date (datetime): datetime object.

    Returns:
        int: student years.
    '''
    return int((datetime.datetime.now() - date).days / 360)


def parseMobile(mobile: str) -> str:
    '''parseMobile: returns parsed mobile number at format: +7 (999) 000-00-00

    Args:
        mobile (str): mobile number.

    Returns:
        str: parsed mobile number.
    '''
    return f'+{mobile[0]} ({mobile[1:4]}) {mobile[4:7]}-{mobile[7:9]}-{mobile[9:11]}'


def parseStudent(student: dict) -> str:
    '''parseStudent: returns parsed student info to text message.

    Args:
        student (dict): student info.

    Returns:
        str: text ready for send.
    '''
    cnt = '<b>Студент: <i>'
    sep = '\n'
    if student['last_name']:
        cnt += student['last_name']
        if student['first_name']:
            cnt += ' ' + student['first_name']
            if student['second_name']:
                cnt += ' ' + student['second_name']
            if student['alias']:
                cnt += ' ' + f'({student["alias"]})</i></b>' + sep
            else:
                cnt += '</i></b>' + sep
    if student['dob']:
        date = datetime.datetime.fromisoformat(student['dob'])
        cnt += f'Дата рождения: {getDateName(date)} [{getStudentYears(date)}]' + sep
    if student['mobile']:
        mobile = parseMobile(student['mobile'])
        cnt += f'Мобильный: {mobile}' + sep
    if student['vk_id']:
        vk_uri = getVKProfileURI(student['vk_id'])
        cnt += f'VK: {vk_uri}' + sep
    if student['father_mobile']:
        father_mobile = parseMobile(student['father_mobile'])
        cnt += f'Отец: {father_mobile}' + sep
    if student['mother_mobile']:
        mother_mobile = parseMobile(student['mother_mobile'])
        cnt += f'Мать: {mother_mobile}' + sep
    if student['address']:
        cnt += f'Домашний адрес: {student["address"]}' + sep
    if student['aux_info']:
        cnt += f'Доп. Инфо.: <b>{student["aux_info"]}</b>' + sep
    premium = bool(student['premium'])
    if premium:
        cnt += '<b><i>Учится на платной основе.</i></b>' + sep
    else:
        cnt += '<b><i>Учится на бюджетной основе.</i></b>'
    return cnt


def parseTeacher(teacher: dict) -> str:
    '''parseTeacher: returns parsed teacher info, ready for sent.

    Args:
        teacher (dict): teacher info.

    Returns:
        str: parsed teacher info.
    '''
    cnt = ''
    sep = '\n'
    cnt += f'<b><i>{teacher["op"]}: {teacher["first_name"]} {teacher["second_name"]} '
    if teacher['last_name']:
        cnt += f'{teacher["last_name"]}</i></b>' + sep
    else:
        cnt += '</i></b>' + sep
    if teacher['op'] == 'Преподаватель':
        cnt += f'Преподаёт: <b>{teacher["lesson_name"]}</b>' + sep
    elif 'Преподаватель' in teacher['op']:
        op = teacher['op'].split('/')
        cnt += f'Преподаёт: <b>{teacher["lesson_name"]}</b>' + sep
        cnt += f'Является: <b>{getAbltLexema(op[1])}</b>' + sep
    else:
        cnt += f'Является: <b>{teacher["op"]}</b>' + sep
    cnt += f'Подтверждено: {"Да" if bool(teacher["verify"]) else "Нет"}'
    return cnt


def getLessonsLength(array: dict) -> int:
    '''getLessonsLength: returns length of lessons in array.

    Args:
        array (dict): lessons array.

    Returns:
        int: lessons length
    '''
    length = 0
    if 'lesson1' in array:
        length += 1
    if 'lesson2' in array:
        length += 1
    if 'lesson3' in array:
        length += 1
    if 'lesson4' in array:
        length += 1
    log.debug(f'getLessonsLength result: {str(length)}')
    return length


def getLessonsFromStateDict(lessons: dict, timetable: dict) -> list:
    '''getLessonFromDict: returns lessons array from state dict.

    Args:
        lesson (dict): state dict.
        timetable (dict): lesson types times.

    Returns:
        list: lessons array.
    '''
    log.debug(f'getLessonsFromStateDict args: ({str(lessons)}, {str(timetable)})')
    array = []
    lesson_template = {'name': None, 'type': None, 'from': None, 'to': None, 'date': None, 'visit': 0, 'info': None}
    if 'lesson1' in lessons:
        lesson = lesson_template.copy()
        lesson['name'] = lessons['lesson1']
        lesson['type'] = 1
        lesson['from'] = timetable['start1']
        lesson['to'] = timetable['end1']
        lesson['date'] = lessons['date']
        array.append(lesson)
    if 'lesson2' in lessons:
        lesson = lesson_template.copy()
        lesson['name'] = lessons['lesson2']
        lesson['type'] = 2
        lesson['from'] = timetable['start2']
        lesson['to'] = timetable['end2']
        lesson['date'] = lessons['date']
        array.append(lesson)
    if 'lesson3' in lessons:
        lesson = lesson_template.copy()
        lesson['name'] = lessons['lesson3']
        lesson['type'] = 3
        lesson['from'] = timetable['start3']
        lesson['to'] = timetable['end3']
        lesson['date'] = lessons['date']
        array.append(lesson)
    if 'lesson4' in lessons:
        lesson = lesson_template.copy()
        lesson['name'] = lessons['lesson4']
        lesson['type'] = 4
        lesson['from'] = timetable['start4']
        lesson['to'] = timetable['end4']
        lesson['date'] = lessons['date']
        array.append(lesson)
    log.debug(f'getLessonsFromStateDict result: {str(array)}')
    return array


def getDateWeekday(date: str = getNowDate()) -> int:
    '''getDateWeekday: returns iso weekday for provided date.

    Args:
        date (str): date string. Defaults to getNowDate().

    Returns:
        int: date iso weekday
    '''
    return getDateObjFromStr(date).isoweekday()


def isWeekend(date: str) -> bool:
    '''isWeekend returns True if today is weekend.

    Args:
        date (str): date in ISO format (YYYY-MM-DD).

    Returns:
        bool: today is weekend?
    '''
    return datetime.datetime.fromisoformat(date).isoweekday() == 7


def getLessonsTypesKey() -> types.ReplyKeyboardMarkup:
    '''getLessonsTypesKey returns lessons types keyboard.

    Returns:
        types.ReplyKeyboardMarkup: Reply keyboard instance.
    '''
    key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key.row('1 пара', '2 пара')
    key.row('3 пара', '4 пара')
    return key


def getLessonsLengthKey() -> types.ReplyKeyboardMarkup:
    '''getLessonsLengthKey returns lessons length keyboard.

    Returns:
        types.ReplyKeyboardMarkup: reply keyboard instance.
    '''
    key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key.row('Одна', 'Две')
    key.row('Три', 'Четыре')
    return key


def getLessonsDaysKey() -> types.ReplyKeyboardMarkup:
    '''getLessonsDaysKey returns lessons days keyboard.

    Returns:
        types.ReplyKeyboardMarkup: Reply keyboard instance.
    '''
    key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key.row('На сегодня', 'На завтра')
    return key


def check_cmd(msg: types.Message, cmd: str) -> bool:
    '''check_cmd: Check if msg.text in cmd calls.

    Args:
        msg (types.Message): telegram message.
        cmd (str): bot command name.

    Returns:
        bool: msg.text in cmd calls?
    '''
    # TODO: use fuzzywuzzy?
    cmds = {
        'getLessons': ['get today lessons', 'какие пары сегодня', 'сегодняшние пары', 'пары', 'пары на сегодня'],
        'getNextDayLessons': ['get next day lessons', 'какие пары завтра', 'завтрашние пары', 'пары на завтра'],
        'setTypesTimes': ['set types times', 'установить время', 'times', 'установить расписание'],
        'setLessons': ['set lessons', 'установить пары'],
        'nextDateTimetable': ['next day timetable', 'расписание на завтра'],
        'todayTimetable': ['today timetable', 'расписание', 'расписание на сегодня'],
        'help': ['помощь', 'помогите', 'команды', 'кмд', 'cmd', 'cmds'],
        'timeron': ('timeron', 'notifyon', 'ton', 'non', 'включить уведомления', 'вкл таймер', 'включить таймер',
                    'вкл увед'),
        'timeroff': ('timeroff', 'notifyoff', 'toff', 'noff', 'выключить уведомления', 'выключить таймер', 'выкл таймер',
                     'выкл увед'),
        'timer': ('timer', 'notify', 't', 'n', 'таймер', 'уведомления', 'увед', 'пара', 'время'),
        'search': ('search', 's', 'поиск', 'найти'),
        'ench': ('доп', 'ench', 'дополнительно')
    }
    return msg.text.lower() in cmds[cmd]


async def check_id(msg: types.Message, conf: Config, start: bool = False) -> bool:
    '''check_id: Coroutine. Compare msg.chat.id with conf.ADMIN_ID.

    Args:
        msg (types.Message): Telegram message.
        conf (TeachTime.Config): TeachTime config instance.
        start (bool): Called from "start" cmd? Defaults to "False".

    Returns:
        bool.'''
    # TODO: Make users?
    if msg.chat.id == conf.ADMIN_ID:
        log.info(
            f'Access granted for {msg.chat.mention} ({msg.from_user.id}).')
        return True
    else:
        log.warning(
            f'Access denied for {msg.chat.mention} ({msg.from_user.id}).')
        if start:
            await msg.edit_text('<b>Доступ запрещён.</b>')
        else:
            await msg.answer('<b>Доступ запрещён.</b>')
        return False


def getPracticeDefaultKey(default_for: str = None) -> types.InlineKeyboardMarkup:
    '''getPracticeDefaultKey: returns inline keyboard for verify default vars for some action.

    Args:
        default_for (str, optional): Default action. Defaults to None.

    Returns:
        types.InlineKeyboardMarkup: telegram inline keyboard.
    '''
    key = types.InlineKeyboardMarkup()
    btn_yes = types.InlineKeyboardButton('Да', callback_data=f'ench:practice:{default_for}:yes')
    btn_no = types.InlineKeyboardButton('Нет', callback_data=f'ench:practice:{default_for}:no')
    key.add(btn_yes, btn_no)
    return key


def getSendZamenaImagesKey() -> types.InlineKeyboardMarkup:
    '''Returns inline keyboard with query of sendZamenaImages.

    Returns:
        types.InlineKeyboardMarkup: telegram inline keyboard.
    '''
    key = types.InlineKeyboardMarkup()
    btn_yes = types.InlineKeyboardButton(
        'Да', callback_data='sziTrue')
    btn_no = types.InlineKeyboardButton(
        'Нет', callback_data='sziFalse')
    key.add(btn_yes, btn_no)
    return key

def getEnchKey() -> types.InlineKeyboardMarkup:
    '''getEnchKey: returns enhancement's inline keyboard.

    Returns:
        types.InlineKeyboardMarkup: telegram inline keyboard.
    '''
    key = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton('Практика', callback_data='ench:practice')
    key.add(btn)
    return key


def getDateList(start: datetime.datetime, end: datetime.datetime) -> list:
    '''getDateList: returns date range list.

    Args:
        start (datetime.datetime): start date.
        end (datetime.datetime): end date.

    Returns:
        list: date range list.
    '''
    numdays = (end - start).days
    date_list = []
    for i in range(0, numdays + 1):
        date_list.append(start + datetime.timedelta(days=i))
    return date_list


def parsePractice(practice: dict) -> str:
    '''parsePractice: returns content for telegram message about practice.

    Args:
        practice (dict): practice dict.

    Returns:
        str: text for telegram message.
    '''
    if practice is None:
        return 'Дополнительно:Практика\nПрактика: Ещё не начиналась.\n\nПрактика началась?'
    cnt = 'Дополнительно:Практика\nПрактика: '
    sep = '\n'
    cnt += '<b>Идёт</b>' if bool(practice['status']) else '<b>Не идёт</b>'
    if bool(practice['status']) is False:
        cnt += 'Практика закончилась?' if bool(practice['status']) else 'Практика началась?'
        return cnt
    cnt += sep + \
        f'Дата начала: <b>{getDateName(getDateObjFromStr(practice["start_date"]))}</b>'
    cnt += f'{sep}Урок с {practice["timeFrom"]} по ' + \
           f'{practice["timeTo"]}{sep + sep}' if bool(practice['status']) else sep + sep
    cnt += 'Практика закончилась?' if bool(practice['status']) else 'Практика началась?'
    return cnt


def parseTeacherName(fullname: str) -> dict:
    '''parseTeacherName: returns dict with first, second and last name from teacher fullname.

    Args:
        fullname (str): teacher full name.

    Returns:
        dict: first, second and last teacher name.
    '''
    array = fullname.split()
    if len(array) >= 2:
        return {'first_name': array[0], 'second_name': array[1]}
    elif len(array) == 3:
        return {'first_name': array[1], 'second_name': array[2], 'last_name': array[0]}
    else:
        return {'first_name': array[0]}


def getPracticeKey(status: bool) -> types.InlineKeyboardMarkup:
    '''getPracticeKey: returns practice on/off by provided status.

    Args:
        status (bool): practice status.

    Returns:
        types.InlineKeyboardMarkup: telegram inline keyboard.
    '''
    key = types.InlineKeyboardMarkup()
    if status:
        btn = types.InlineKeyboardButton('Закончилась',
                                         callback_data='ench:practice:end')
    else:
        btn = types.InlineKeyboardButton('Началась',
                                         callback_data='ench:practice:start')
    key.add(btn)
    return key


def getStartKey() -> types.ReplyKeyboardMarkup:
    '''getStartKey returns telegram reply keyboard with start keys.

    Returns:
        types.ReplyKeyboardMarkup: telegram reply keyboard.
    '''
    key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key.row('Пары на сегодня', 'Время')
    key.row('Пары на завтра', 'Установить пары')
    key.row('Поиск', 'Помощь')
    return key


def getLessonsSetKey() -> types.InlineKeyboardMarkup:
    '''getLessonsSetKey returns telegram inline keyboard with set lessons question keys.

    Returns:
        types.InlineKeyboardMarkup: telegram reply keyboard.
    '''
    key = types.InlineKeyboardMarkup(row_width=1)
    set = types.InlineKeyboardButton('Установить пары', callback_data='setLessons')
    no = types.InlineKeyboardButton('Не устанавливать пары', callback_data='no')
    key.add(set, no)
    return key


def getTimeSetKey() -> types.ReplyKeyboardMarkup:
    '''getTimeSetKey returns telegram reply keyboard with set timetable question keys.

    Returns:
        types.ReplyKeyboardMarkup: telegram reply keyboard.
    '''
    key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key.row('Нет', 'Установить время')
    return key


def getVerifyKey() -> types.ReplyKeyboardMarkup:
    '''getVerifyKey returns verify keyboard.

    Returns:
        types.ReplyKeyboardMarkup: telegram reply keyboard.
    '''
    key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key.row('Да', 'Нет')
    return key


def getDefaultTimeKey() -> types.ReplyKeyboardMarkup:
    '''getDefaultTimeKey returns default time keyboard.

    Returns:
        types.ReplyKeyboardMarkup: telegram reply keyboard.
    '''
    key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key.row('Стандартное', 'Нестандартное')
    return key


def getDefaultLessonsKey() -> types.ReplyKeyboardMarkup:
    '''getDefaultLessonsKey: returns default lessons verify keyboard.

    Returns:
        types.ReplyKeyboardMarkup: telegram reply keyboard.
    '''
    key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key.row('Стандартные', 'Нестандартные')
    return key


def getWeektypeByDate(date: str) -> int:
    '''getWeektypeByDate: returns week type by date.

    Args:
        date (str): date.

    Returns:
        int: week type.
    '''
    point = datetime.datetime.fromisoformat('2020-10-12')  # weektype: 0
    now = datetime.datetime.fromisoformat(date)
    td = now - point
    weeks = td.days // 7
    if weeks % 2:
        return 1
    else:
        return 0


def getSortedLessons(lessons: list) -> list:
    '''getSortedLessons sort lessons array by datetime.

    Args:
        lessons (list): lessons array.

    Returns:
        list: sorted lessons array.
    '''
    log.debug(f'getSortedLessons array: {str(lessons)}')

    sort = []
    les1 = None
    les2 = None
    les3 = None
    les4 = None
    for i in lessons:
        if i['type'] == 1:
            les1 = i
        elif i['type'] == 2:
            les2 = i
        elif i['type'] == 3:
            les3 = i
        elif i['type'] == 4:
            les4 = i
    if les1:
        sort.append(les1)
    if les2:
        sort.append(les2)
    if les3:
        sort.append(les3)
    if les4:
        sort.append(les4)
    return sort


def getWordAgreeNum(word: str, num: int) -> str:
    '''getWordAgreeNum: returns word what agreed with provided number.

    Args:
        word (str): base word.
        num (int): number.

    Returns:
        str: agreed word.
    '''
    return MorphAnalyzer().parse(word)[0].make_agree_with_number(num).word


def getLessonEt(start_time: datetime.datetime = None, td: datetime.timedelta = None) -> str:
    '''getLessonEt: returns str with estimated time before lesson start.

    Args:
        start_time (datetime.datetime): lesson start time. Defaults is None.
        td (datetime.timedelta): custom timedelta. Defaults is None.

    Returns:
        str: string with estimated time.
    '''
    if td is None:
        td = start_time - datetime.datetime.now()
    secs = int(td.total_seconds() % 60)
    mins = int((td.total_seconds() % 3600) // 60)
    hours = int(td.total_seconds() // 3600)
    log.debug(f'getLessonEt - start_time: {str(start_time)}; td: {str(td)}')
    log.debug(f'getLessonEt - secs: {str(secs)}; mins: {str(mins)}; hours: {str(hours)}')
    if mins:
        if hours:
            return f'{str(hours)} {getWordAgreeNum("час", hours)}, {str(mins)} {getWordAgreeNum("минута", mins)} и {str(secs)} {getWordAgreeNum("секунда", secs)}'
        else:
            return f'{str(mins)} {getWordAgreeNum("минута", mins)} и {str(secs)} {getWordAgreeNum("секунда", secs)}'
    else:
        if hours:
            return f'{str(hours)} {getWordAgreeNum("час", hours)} и {str(secs)} {getWordAgreeNum("секунда", secs)}'
        else:
            return f'{str(secs)} {getWordAgreeNum("секунда", secs)}'


def getLessonVisitInlineMarkup(callback_data: str) -> types.InlineKeyboardMarkup:
    '''getLessonVisitInlineMarkup: returns lesson visit inline markup.

    Args:
        callback_data (str): lesson encrypted info.

    Returns:
        types.InlineKeyboardMarkup: telegram inline markup.
    '''
    key = types.InlineKeyboardMarkup()
    key.add(types.InlineKeyboardButton('Я был!', callback_data=callback_data),
            types.InlineKeyboardButton('Я не был.', callback_data='notvisited'))
    return key


def getEditLessonsInlineMarkup(callback_data: str) -> types.InlineKeyboardMarkup:
    '''getEditLessonsInlineMarkup: returns inline keyboard for edit setted lessons.

    Args:
        callback_data (str): callback data.

    Returns:
        types.InlineKeyboardMarkup: Telegram Inline keyboard.
    '''
    key = types.InlineKeyboardMarkup()
    key.add(types.InlineKeyboardButton('Изменить пары', callback_data=callback_data))
    key.add(types.InlineKeyboardButton('Не изменять', callback_data='no'))
    return key


def getWhatEditLessonsInlineMarkup() -> types.InlineKeyboardMarkup:
    '''getWhatEditLessonsInlineMarkup: return inline keyboard for edit setted lessons.

    Returns:
        types.InlineKeyboardMarkup: Telegram Inline keyboard.
    '''
    key = types.InlineKeyboardMarkup()
    key.add(types.InlineKeyboardButton('Пары', callback_data='sl_editLessons'))
    key.add(types.InlineKeyboardButton('Время', callback_data='sl_editTimes'))
    return key


class BotKeyboards:
    '''BotKeyboards: TeachTime bot keyboards class.

       Args:
          timer (Timer): TeachTime timer instance.
    '''
    def __init__(self, timer):
        self.log = getLogger('TeachTime BotKeyboards')
        self.timer = timer
        self.current_lesson = None

    def set_lesson(self, lesson) -> bool:
        '''set_lesson: asign provided lesson as self.current_lesson

        Args:
            lesson (dict or None): lesson dict

        Returns:
            bool: always True.
        '''
        self.log.debug(f'set_lesson - Lesson: {str(lesson)}')
        self.current_lesson = lesson
        return True

    def get_lesson_name(self) -> str:
        '''get_lesson: returns self.current_lesson.

        Returns:
            str: lesson name.
        '''
        if self.current_lesson:
            self.log.debug(f'get_lesson_name - Current Lesson: {self.current_lesson["name"]}')
            return self.current_lesson['name']
        else:
            self.log.debug('get_lesson_name - Current Lesson: None')
            return 'Ничего'

    async def loop(self):
        '''loop: class main loop.
        '''
        while True:
            await sleep(10)
            self.log.debug(f'loop - timer.work: {str(self.timer.work)}, timer.lesson: {str(self.timer.lesson)}')
            if self.timer.work:
                self.set_lesson(self.timer.lesson)
            else:
                self.set_lesson(None)

    def getStartKey(self) -> types.ReplyKeyboardMarkup:
        '''getStartKey returns telegram reply keyboard with start keys.

           Returns:
              types.ReplyKeyboardMarkup: telegram reply keyboard.
        '''
        lesson = self.get_lesson_name()
        key = types.ReplyKeyboardMarkup(resize_keyboard=True)
        key.row('Пары на сегодня', f'Сейчас: {lesson}')
        key.row('Пары на завтра', 'Установить пары')
        key.row('Установить время', 'Помощь')
        self.log.debug(f'getStartKey - keyboard returned with lesson: {lesson}')
        return key


class Timer:
    '''Timer: TeachTime notifications timer class.

       Args:
            bot (Dispatcher): aiogram Dispatcher instance.
            conf (Config): TeachTime config instance.
            db (Database): TeachTime database instance.
    '''

    def __init__(self, bot: Dispatcher, conf: Config, db):
        self.WAIT_GET_LESSONS = 10  # every 10 sec.
        self.FIRST_LESSON_ALERT = 600  # notify 10 minutes before the start
        self.SECOND_LESSON_ALERT = 120  # notify 2 minutes before the start
        self.lessons = None  # lessons array in current loop
        self.lesson = None  # lesson dict from lessons array
        self.past_lesson = None  # passed lesson dict
        self.work = False  # timer is working
        self.bot = bot
        self.conf = conf
        self.db = db
        self.log = getLogger('TeachTime Timer')

    async def main(self):
        self.log.info('Timer is started up.')
        self.work = True
        while True and self.work:
            temp = await self.db.getLessonsByDate(getNowDate())
            self.log.debug(f'Timer loop! Temp: {str(temp)}')
            if temp:
                self.lessons = getSortedLessons(getNotPassedLessons(temp))
                if self.lessons and self.work:
                    self.log.info('Recived new lessons.')
                    self.log.debug(f'lessons: {str(self.lessons)}')
                    for lesson in self.lessons:
                        if self.work is False:
                            continue
                        if self.past_lesson:
                            lesson_info = await self.signLessonInfo(self.past_lesson)
                            await self.bot.bot.send_message(self.conf.ADMIN_ID,
                                                            f'{self.past_lesson["type"]} пара: '
                                                            f'<b>{self.past_lesson["name"]}</b> - '
                                                            '<i>закончилась!</i>',
                                                            reply_markup=getLessonVisitInlineMarkup(lesson_info))
                        self.lesson = lesson
                        lesson_time = getDateObjFromStr(lesson['date'] + ' ' + lesson['from'])
                        alert1 = ((lesson_time - datetime.timedelta(seconds=self.FIRST_LESSON_ALERT)) - datetime.datetime.now())
                        self.log.info(f'Lesson #{str(lesson["type"])} {lesson["name"]}: '
                                      f'Alert 1: {str(alert1.total_seconds())} sec')
                        if alert1.total_seconds() > 0:
                            if self.work:
                                await self.bot.bot.send_message(self.conf.ADMIN_ID,
                                                                f'{lesson["type"]} пара: '
                                                                f'<b>{lesson["name"]}</b>, '
                                                                f'начнётся <b>через {getLessonEt(lesson_time)}</b>')
                                await self.wait(alert1.total_seconds())
                        alert2 = ((lesson_time - datetime.timedelta(seconds=self.SECOND_LESSON_ALERT)) - datetime.datetime.now())
                        self.log.info(f'Lesson #{str(lesson["type"])} {lesson["name"]}: '
                                      f'Alert 2: {str(alert2.total_seconds())} sec')
                        if alert2.total_seconds() > 0:
                            if self.work:
                                await self.bot.bot.send_message(self.conf.ADMIN_ID,
                                                                f'{lesson["type"]} пара: '
                                                                f'<b>{lesson["name"]}</b>, '
                                                                f'начнётся <b>через {getLessonEt(lesson_time)}!</b>')
                                await self.wait(alert2.total_seconds())
                        lesson_end = (getDateObjFromStr(
                            lesson['date'] + ' ' + lesson['to']) - datetime.datetime.now())
                        if lesson_end.total_seconds() > 0 and self.work:
                            await self.bot.bot.send_message(self.conf.ADMIN_ID,
                                                            f'{lesson["type"]} пара: '
                                                            f'<b>{lesson["name"]}</b>, '
                                                            'началась, и закончится <b>через '
                                                            f'{getLessonEt(td=lesson_end)}.</b>')
                            await self.wait(lesson_end.total_seconds())
                        if await self.lessonInTT(self.lesson):
                            self.past_lesson = self.lesson
            if self.past_lesson and self.work:
                lesson_info = await self.signLessonInfo(self.past_lesson)
                await self.bot.bot.send_message(self.conf.ADMIN_ID,
                                                f'{self.past_lesson["type"]} пара: '
                                                f'<b>{self.past_lesson["name"]}</b> - '
                                                '<i>закончилась!</i>',
                                                reply_markup=getLessonVisitInlineMarkup(lesson_info))
                self.past_lesson = None
            self.past_lesson = None
            self.lesson = None
            await sleep(self.WAIT_GET_LESSONS)
            continue
        self.past_lesson = None
        self.lesson = None

    async def signLessonInfo(self, lesson: dict) -> str:
        '''encryptLessonInfo: returns signed lesson info.

        Args:
            lesson (dict): lesson dict.

        Returns:
            str: signed text.
        '''
        self.log.debug(f'signLessonInfo called with arg - lesson: {str(lesson)}')
        cnt = 'visit:{}'
        lessonid = await self.db.getLessonID(lesson)
        cnt = cnt.format(str(lessonid))
        sign = hmac.new(self.conf.KEY, cnt.encode(), hashlib.md5).hexdigest()
        cnt = cnt + f':{sign}'
        self.log.debug(f'signLessonInfo signed lesson info: {cnt}')
        return cnt

    async def getLessonIDFromLessonInfo(self, lesson_info: str) -> int:
        '''getLessonIDFromLessonInfo: returns lesson id fron signed lesson info.

        Args:
            lesson_info (str): signed lesson info.

        Returns:
            int: lesson id or None.
        '''
        self.log.debug(f'getLessonIDFromLessonInfo called with arg - lesson_info: {str(lesson_info)}')
        cnt = lesson_info.split(':')
        verify = hmac.new(self.conf.KEY, f'{cnt[0]}:{cnt[1]}'.encode(), hashlib.md5).hexdigest()
        self.log.debug(f'getLessonIDFromLessonInfo verify sign: {verify}')
        if cnt[2] == verify:
            self.log.debug('getLessonIDFromLessonInfo verify - OK!')
            return int(cnt[1])
        else:
            self.log.debug('getLessonIDFromLessonInfo verify - Fail.')
            return None

    async def lessonInTT(self, lesson: dict) -> bool:
        '''lessonInTT: check if lesson in timetable.

        Args:
            lesson (dict): lesson dict.

        Returns:
            bool: True or False
        '''
        if self.work:
            temp = await self.db.getLessonsByDate(lesson['date'])
            lessons = getSortedLessons(temp)
            return lesson in lessons

    async def wait(self, delay: int) -> bool:
        '''wait: coroutine that returns True, if is not interrupted, after a given time (in seconds).

        Args:
            delay (int): delay seconds.

        Returns:
            bool: True or False.
        '''
        self.log.debug(f'Timer for {str(delay)} seconds is started!')
        start_time = datetime.datetime.now()
        while True:
            if self.work:
                if await self.lessonInTT(self.lesson):
                    if start_time >= (datetime.datetime.now() - datetime.timedelta(seconds=delay)):
                        await sleep(10)
                        continue
                    else:
                        self.log.debug('Timer is timed out!')
                        break
                else:
                    self.log.debug('Timer has been interrupted because lesson not in timetable!')
                    return False
            else:
                self.log.debug('Timer has been interrupted!')
                return False
        return True

    async def getCurrentLesson(self):
        return self.lesson

    async def getLessonStartEt(self) -> datetime.timedelta:
        return (getDateObjFromStr(self.lesson['date'] + ' ' + self.lesson['from']) - datetime.datetime.now())

    async def getLessonEndEt(self) -> datetime.timedelta:
        return (getDateObjFromStr(self.lesson['date'] + ' ' + self.lesson['to']) - datetime.datetime.now())
