# -*- coding: utf-8 -*-
#
#  TeachTime module "database".
#  Created by LulzLoL231 at 09/09/20
#
import logging
import typing

import aiosqlite

import config
import utils


class Database:
    '''TeachTime Database class

    Args:
        conf (config.Config): TeachTime config instance.
    '''
    def __init__(self, conf: config.Config):
        self.db_name = conf.db_name
        self.log = logging.getLogger('TeachTime Database')

    async def getLessonsWithTimeByDate(self, array: list, date: str) -> typing.Optional[typing.Union[list, None]]:
        '''getLessonsWithTimeByDate: returns array of lessons with setted time by date typestimes.

        Args:
            array (list): lessons array
            date (str): lessons date.

        Returns:
            typing.Optional[typing.Union[list, None]]: array with lesson or None if typestimes not setted.
        '''
        self.log.debug(f'called "getLessonsWithTimeByDate" with args - array: {str(list)}; date: {date}')
        typestimes = await self.getTypesTimesByDate(date)
        if typestimes:
            lesson_temp = {'name': None, 'type': None, 'from': None,
                           'to': None, 'date': date, 'visit': 0, 'info': None}
            lessons = []
            for i in array:
                lesson = lesson_temp.copy()
                lesson['name'] = i['name']
                lesson['type'] = i['type']
                lesson['from'] = typestimes[f'start{str(i["type"])}']
                lesson['to'] = typestimes[f'end{str(i["type"])}']
                if 'visit' in i.keys():
                    lesson['visit'] = i['visit']
                if 'info' in i.keys():
                    lesson['info'] = i['info']
                lessons.append(lesson)
            return lessons
        else:
            return None

    async def getAllPossibleLessons(self) -> list:
        '''getAllPossibleLessons: returns array with names for all possible lessons.

        Returns:
            list: array with names of lessons.
        '''
        lessons = []
        async with aiosqlite.connect(self.db_name) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT lesson_name FROM aliases') as cur:
                async for row in cur:
                    name = dict(row)['lesson_name']
                    lessons.append(name)
        return lessons

    async def getDefaultLessonsByDate(self, date: int) -> list:
        '''getDefaultLessonsByDate: returns array with default lessons by date.

        Args:
            date (str): date.

        Returns:
            list: array of lessons.
        '''
        self.log.debug(
            f'called "getDefaultLessonsByDate" with arg - date: {str(date)}')
        lessons = []
        weektype = utils.getWeektypeByDate(date)
        weekday = utils.getDateWeekday(date)
        async with aiosqlite.connect(self.db_name) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT name, type FROM default_lessons WHERE weekday=? AND week=?', (weekday, weektype)) as cur:
                async for row in cur:
                    lessons.append(dict(row))
        return lessons

    async def getLessonsByDate(self, date: str, parse: bool = False) -> list:
        '''getLessonsByDate: Returns array with lessons by provided date.

        Args:
            date (str): date in ISO format (YYYY-MM-DD).
            parse (bool): use isLessonPassed func at each lesson or not. Defaults to False.

        Returns:
            list: lessons array.
        '''
        self.log.debug(f'called "getLessonsByDate" with args: ({str(date)})')
        array = []
        async with aiosqlite.connect(self.db_name) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('SELECT * FROM lessons WHERE date=?', (date,)) as cur:
                async for row in cur:
                    lesson = dict(row)
                    if parse:
                        if utils.isLessonPassed(lesson) is False:
                            array.append(lesson)
                    else:
                        array.append(lesson)
        result = await self.getLessonsWithTimeByDate(array, date)
        return result

    async def visitLesson(self, lessonid: int, visit: int = 1) -> bool:
        '''visitLesson: Set True or False in visit for lesson.

        Args:
            lessonid (int): Lesson ID.
            visit (int): lesson visit state. Defaults in 1.

        Returns:
            bool: True if success.
        '''
        self.log.debug(f'called "visitLesson" with args: ({str(lessonid)}, {str(visit)})')
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('UPDATE lessons SET visit=? WHERE _rowid_=?', (visit, lessonid))
            await db.commit()
        return True

    async def addLesson(self, name: str, type: int, date: str) -> bool:
        '''addLesson: Add new lesson to DB.

        Args:
            name (str): Lesson name.
            type (int): Lesson type (0-6)
            date (str): Lesson date.

        Returns:
            bool: True if success.
        '''
        self.log.debug(f'called "addLesson" with args: ({str(name)}, {str(type)}, {str(date)})')
        lesson = (name, type, date, 0, None)
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('INSERT INTO lessons VALUES(?,?,?,?,?)', lesson)
            await db.commit()
        return True

    async def setLessonsTypesTimes(
            self, date: str = utils.getNextDate(),
            start1: str = '08:30', end1: str = '10:00',
            start2: str = '10:20', end2: str = '11:50',
            start3: str = '12:20', end3: str = '13:50',
            start4: str = '14:10', end4: str = '15:40') -> bool:
        '''setLessonsTypesTime: Set types times in DB.

        Args:
            date (str, optional): types date. Defaults to utils.getNextDate().
            start1 (str, optional): type 1 start time. Defaults to '08:30'.
            end1 (str, optional): type 1 end time. Defaults to '10:00'.
            start2 (str, optional): type 2 start time. Defaults to '10:20'.
            end2 (str, optional): type 2 end time. Defaults to '11:50'.
            start3 (str, optional): type 3 start time. Defaults to '12:20'.
            end3 (str, optional): type 3 end time. Defaults to '13:50'.
            start4 (str, optional): type 4 start time. Defaults to '14:10'.
            end4 (str, optional): type 4 end time. Defaults to '15:40'.

        Returns:
            bool: True if success.
        '''
        self.log.debug(
            f'called "setLessonsTypesTimes" with args: ({str(date)}, {str(start1)}, {str(end1)}, '
            f'{str(start2)}, {str(end2)}, {str(start3)}, {str(end3)}, {str(start4)}, {str(end4)})')
        types_times = (date, start1, end1, start2, end2, start3, end3, start4, end4)
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('INSERT INTO types_times VALUES(?,?,?,?,?,?,?,?,?)', types_times)
            await db.commit()
        return True

    async def getTimesForType(
            self, type: int,
            date: str = utils.getNextDate()) -> typing.Optional[typing.Union[tuple, None]]:
        '''getTimesForType: Retuns tuple with start and end times for provided type and date.

        Args:
            type (int): Lesson type (1-4).
            date (str, optional): Lesson date. Defaults to utils.getNextDate().

        Returns:
            typing.Optional[typing.Union[tuple, None]]: array with start and end times for type and date, or None if times not set.
        '''
        self.log.debug(f'called "getTimesForType" with args: ({str(type)}, {str(date)})')
        async with aiosqlite.connect(self.db_name) as db:
            db.row_factory = aiosqlite.Row
            req = (date,)
            times = await db.execute('SELECT * FROM types_times WHERE date=?', req)
            async for row in times:
                row = dict(row)
                self.log.debug(f'getTimesForType row: {str(row)}')
                if row:
                    return (row['start' + str(type)], row['end' + str(type)])
                else:
                    return None

    async def getTypesTimesByDate(self, date: str) -> typing.Optional[typing.Union[dict, None]]:
        '''getTypesTimesByDate: Returns dict with date and types times

        Args:
            date (str): types date.

        Returns:
            Optional[Union[dict, None]]: types times or None if types times not set for provided date.
        '''
        self.log.debug(f'called "getTypesTimesByDate" with args: ({str(date)})')
        async with aiosqlite.connect(self.db_name) as db:
            db.row_factory = aiosqlite.Row
            times = await db.execute('SELECT * FROM types_times WHERE date=?', (date,))
            times = await times.fetchone()
            if times:
                return dict(times)
            else:
                return None

    async def getLessonByAlias(self, alias: str) -> typing.Optional[typing.Union[str, None]]:
        '''getLessonByAlias: Returns lesson name by him alias.

        Args:
            alias (str): lesson alias.

        Returns:
            typing.Optional[typing.Union[str, None]]: lesson name or None if alias not found.
        '''
        self.log.debug(f'called "getLessonByAlias" with args: ({str(alias)})')
        async with aiosqlite.connect(self.db_name) as db:
            db.row_factory = aiosqlite.Row
            fetch = await db.execute('SELECT lesson_name FROM aliases WHERE alias=?', (alias,))
            lesson_name = await fetch.fetchone()
            if lesson_name:
                return dict(lesson_name)['lesson_name']
            else:
                return None

    async def getTeacherByLessonName(self, lesson_name: str) -> typing.Optional[typing.Union[dict, None]]:
        '''getTeacherByLessonName: Returns teacher info in dict by lesson name.

        Args:
            lesson_name (str): lesson name.

        Returns:
            typing.Optional[typing.Union[dict, None]]: dict with teacher info or None, if lesson_name not found.
        '''
        self.log.debug(f'called "getTeacherByLessonName" with args: ({str(lesson_name)})')
        async with aiosqlite.connect(self.db_name) as db:
            db.row_factory = aiosqlite.Row
            fetch = await db.execute('SELECT * FROM teachers WHERE lesson_name=?', (lesson_name,))
            teacher = await fetch.fetchone()
            if teacher:
                return dict(teacher)
            else:
                return None

    async def searchTeacher(self, data: str = None) -> typing.Optional[typing.Union[list, dict, None]]:
        '''searchTeacher: Returns teachers list or just teacher dict by some data.

        Args:
            data (str): teacher data. Defaults to None.

        Returns:
            typing.Optional[typing.Union[list, dict, None]]: Teachers list or just teacher dict or None if not found.
        '''
        if (data is None):
            self.log.debug('called "searchTeacher" with not args.')
            return None
        else:
            self.log.debug(f'called "searchTeacher" with arg: data: {str(data)}')
            async with aiosqlite.connect(self.db_name) as db:
                db.row_factory = aiosqlite.Row
                fetch = await db.execute('SELECT * FROM teachers WHERE '
                                         'last_name=? OR first_name=? OR '
                                         'second_name=? OR lesson_name=?',
                                         (data, data, data, data))
                teachers = []
                teacher = await fetch.fetchall()
                if teacher:
                    if len(teacher) > 1:
                        for i in teacher:
                            teachers.append(dict(i))
                        return teachers
                    else:
                        return dict(teacher[0])
                else:
                    lesson_name = await self.getLessonByAlias(data)
                    if lesson_name:
                        fetch = await db.execute('SELECT * FROM teachers '
                                                 'WHERE lesson_name=?',
                                                 (lesson_name,))
                        fetch = await fetch.fetchall()
                        if fetch:
                            teacher = fetch
                            if len(teacher) > 1:
                                for i in teacher:
                                    teachers.append(dict(i))
                                return teachers
                            else:
                                return dict(teacher[0])
                    return None

    async def searchStudent(self, data: str = None) -> typing.Optional[typing.Union[list, dict, None]]:
        '''searchStudent: returns students list or just student dict or None if not found.

        Args:
            data (str, optional): student data. Defaults to None.

        Returns:
            typing.Optional[typing.Union[list, dict, None]]: students list or student dict or None
        '''
        if (data is None):
            self.log.debug('called "searchStudent" with not args.')
            return None
        else:
            self.log.debug(f'called "searchStudent" with arg: data: {str(data)}')
            async with aiosqlite.connect(self.db_name) as db:
                db.row_factory = aiosqlite.Row
                fetch = await db.execute('SELECT * FROM students WHERE first_name=? OR alias=? '
                                         'OR last_name=? OR second_name=? OR mobile=?', (data, data, data, data, data))
                fetch = await fetch.fetchall()
                if fetch:
                    if len(fetch) > 1:
                        students = []
                        for i in fetch:
                            students.append(dict(i))
                        return students
                    else:
                        return dict(fetch[0])
                else:
                    return None

    async def getLessonID(self, lesson: dict) -> typing.Optional[typing.Union[int, None]]:
        '''getLessonID: returns lesson rowid.

        Args:
            lesson (dict): lesson dict.

        Returns:
            typing.Optional[typing.Union[int, None]]: lesson rowid in DB or None.
        '''
        self.log.debug(f'getLessonID called with arg - lesson: {str(lesson)}')
        async with aiosqlite.connect(self.db_name) as db:
            db.row_factory = aiosqlite.Row
            fetch = await db.execute('SELECT _rowid_ FROM lessons WHERE name=? AND date=?', (lesson['name'], lesson['date']))
            fetch = await fetch.fetchone()
            if fetch:
                return fetch['rowid']
            else:
                return None

    async def getLessonByID(self, lessonid: int) -> typing.Optional[typing.Union[dict, None]]:
        '''getLessonByID: returns lesson dict by his rowid.

        Args:
            lessonid (int): lesson rowid.

        Returns:
            typing.Optional[typing.Union[dict, None]]: lesson dict, or None.
        '''
        self.log.debug(f'getLessonByID called with arg - lessonid: {str(lessonid)}')
        async with aiosqlite.connect(self.db_name) as db:
            db.row_factory = aiosqlite.Row
            fetch = await db.execute('SELECT * FROM lessons WHERE _rowid_=?', (lessonid,))
            fetch = await fetch.fetchone()
            if fetch:
                return dict(fetch)
            else:
                return None

    async def addTeacher(self, full_name: str, lesson_name: str, verify: int = 1, op: str = 'Преподователь') -> bool:
        '''addTeacher: add new teacher to DB.

        Args:
            full_name (str): teacher full name.
            lesson_name (str): teacher lesson name
            verify (int, optional): teacher verified? Defaults to 1.
            op (str, optional): teacher as is. Defaults to 'Преподователь'.

        Returns:
            bool: True (always).
        '''
        self.log.debug(f'addTeacher called with args - full_name: {full_name}, lesson_name: {lesson_name}, verify: {str(verify)}, op: {op}')
        teacher_name = utils.parseTeacherName(full_name)
        if len(teacher_name.keys()) == 3:
            sql = 'INSERT INTO teachers VALUES(?, ?, ?, ?, ?, ?)'
            vars = (op, lesson_name, teacher_name['last_name'], teacher_name['first_name'], teacher_name['second_name'], verify)
        else:
            if teacher_name['first_name'] and teacher_name['second_name']:
                sql = 'INSERT INTO teachers (op, lesson_name, first_name, second_name, verify) VALUES (?,?,?,?,?)'
                vars = (op, lesson_name, teacher_name['first_name'], teacher_name['second_name'], verify)
            else:
                if teacher_name['first_name']:
                    sql = 'INSERT INTO teachers (op, lesson_name, first_name, verify) VALUES (?,?,?,?)'
                    vars = (op, lesson_name, teacher_name['first_name'])
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute(sql, vars)
            await db.commit()
        return True

    async def getPractice(self,
                          date: typing.Optional[typing.Union[str, None]] = None,
                          start_date: typing.Optional[typing.Union[str, None]] = None,
                          rowid: typing.Optional[typing.Union[int, None]] = None) -> typing.Optional[typing.Union[dict, None]]:
        '''getPractice: returns practice dict by provided start_date or current date.

        Args:
            date (typing.Optional[typing.Union[str, None]], optional): current date. Defaults to None.
            start_date (typing.Optional[typing.Union[str, None]], optional): practice start date. Defaults to None.
            rowid (typing.Optional[typing.Union[int, None]]): practice number.

        Returns:
            typing.Optional[typing.Union[dict, None]]: practice dict or None if not found.
        '''
        self.log.debug(f'getPractice called with args - date: {date}, start_date: {start_date}, rowid: {str(rowid)}.')
        async with aiosqlite.connect(self.db_name) as db:
            db.row_factory = aiosqlite.Row
            if rowid:
                cur = await db.execute('SELECT * FROM practices WHERE _rowid_=?', (rowid,))
                practice = await cur.fetchone()
                if practice:
                    return dict(practice)
                else:
                    return None
            if start_date:
                cur = await db.execute('SELECT * FROM practices WHERE start_date=?', (start_date,))
                practice = await cur.fetchone()
                if practice:
                    return dict(practice)
                else:
                    return None
            else:
                cur = await db.execute('SELECT * FROM practices')
                practices = []
                fetch = await cur.fetchall()
                for i in fetch:
                    practices.append(dict(i))
                if len(practices) == 0:
                    return None
                else:
                    current_date = utils.getDateObjFromStr(utils.getNowDate())
                    for practice in practices:
                        if utils.getDateObjFromStr(practice['start_date']) <= current_date:
                            date_list = utils.getDateList(utils.getDateObjFromStr(
                                practice['start_date']), current_date)
                            if current_date in date_list:
                                return dict(practice)
                        continue
                    return None

    async def getLastPractice(self) -> typing.Optional[typing.Union[dict, None]]:
        '''getLastPractice: returns last passed practice from DB.

        Returns:
            typing.Optional[typing.Union[dict, None]]: practice dict or None if not found.
        '''
        self.log.debug('getLastPractice is called.')
        async with aiosqlite.connect(self.db_name) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute('SELECT * FROM practices')
            fetch = await cur.fetchall()
            practices = []
            if fetch:
                for i in practices:
                    practices.append(dict(i))
                return practices[-1]
            else:
                return None

    async def getPracticeNum(self, practice: dict) -> typing.Optional[typing.Union[int, None]]:
        '''getPracticeNum: returns practice number.

        Args:
            practice (dict): practice dict.

        Returns:
            typing.Optional[int, None]: practice number or None if not found.
        '''
        self.log.debug(f'getPracticeNum called with arg - practice: {str(practice)}')
        async with aiosqlite.connect(self.db_name) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute('SELECT _rowid_ FROM practices WHERE start_date=?', (practice['start_date'],))
            fetch = await cur.fetchone()
            if fetch:
                return dict(fetch)['num']
            else:
                return None

    async def startPractice(self, date: str, timeFrom: str, timeTo: str, teacher: str, mode: bool = True) -> bool:
        '''startPractice: add practice to DB.

        Args:
            date (str): practice start date.
            timeFrom (str): practice lesson start time.
            timeTo (str): practice lesson end time.
            teacher (str): teacher full name.
            mode (bool): True or False. Defaults to True.

        Returns:
            bool: True (always).
        '''
        self.log.debug(
            f'startPractice is called with args - mode: {str(mode)}, date: {date}, timeFrom: {timeFrom}, timeTo: {timeTo}, teacher: {teacher}')
        await self.addTeacher(teacher, 'Практика')
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('INSERT INTO practices (status, start_date, timeFrom, timeTo) VALUES (?,?,?,?)', (int(mode), date, timeFrom, timeTo))
            await db.commit()
        return True

    async def endPractice(self, date: str, end_date: str) -> bool:
        '''endPractice: set practice mode to False by provided "date" vars.

        Args:
            date (str): practice start date.
            end_date (str): practice end date.

        Returns:
            bool: True (always).
        '''
        self.log.debug(
            f'setPracticeMode called with args - date: {date}, end_date: {end_date}')
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('UPDATE practices SET status=? AND end_date=? WHERE start_date=?', (0, end_date, date))
            await db.commit()
        return True
