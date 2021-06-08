# -*- coding: utf-8 -*-
#
#  TeachTime module "states".
#  Created by LulzLoL231 at 09/10/20
#
from aiogram.dispatcher.filters.state import State, StatesGroup


class SetTypesTimes(StatesGroup):
    '''FSM States group for setup lesson_types times.'''
    wait_types_default = State()
    wait_types_date = State()
    wait_type1_start = State()
    wait_type1_end = State()
    wait_type2_start = State()
    wait_type2_end = State()
    wait_type3_start = State()
    wait_type3_end = State()
    wait_type4_start = State()
    wait_type4_end = State()
    wait_times_verify = State()
    available_verify = ['Стандартное', 'Нестандартное']
    available_dates = ['На сегодня', 'На завтра']
    available_times = [
        '08:30', '08:35', '08:40', '08:45', '08:50', '08:55',
        '09:00', '09:05', '09:10', '09:15', '09:20', '09:25', '09:30', '09:35', '09:40', '09:45', '09:50', '09:55',
        '10:00', '10:05', '10:10', '10:15', '10:20', '10:25', '10:30', '10:35', '10:40', '10:45', '10:50', '10:55',
        '11:00', '11:05', '11:10', '11:15', '11:20', '11:25', '11:30', '11:35', '11:40', '11:45', '11:50', '11:55',
        '12:00', '12:05', '12:10', '12:15', '12:20', '12:25', '12:30', '12:35', '12:40', '12:45', '12:50', '12:55',
        '13:00', '13:05', '13:10', '13:15', '13:20', '13:25', '13:30', '13:35', '13:40', '13:45', '13:50', '13:55',
        '14:00', '14:05', '14:10', '14:15', '14:20', '14:25', '14:30', '14:35', '14:40', '14:45', '14:50', '14:55',
        '15:00', '15:05', '15:10', '15:15', '15:20', '15:25', '15:30', '15:35', '15:40', '15:45', '15:50', '15:55',
    ]


class SetLessons(StatesGroup):
    wait_date = State()
    wait_tt = State()
    wait_default = State()
    wait_lesson_types_length = State()
    wait_lesson_type = State()
    wait_lesson1 = State()
    wait_lesson2 = State()
    wait_lesson3 = State()
    wait_lesson4 = State()
    wait_other = State()
    wait_verify = State()
    available_verify = ['Да', 'Нет']
    available_default = ['Стандартные', 'Нестандартные']
    available_dates = ['На сегодня', 'На завтра']
    available_types = ['1 пара', '2 пара', '3 пара', '4 пара']
    available_length = ['Одна', 'Две', 'Три', 'Четыре']


class Search(StatesGroup):
    wait_ctx = State()


class Practice(StatesGroup):
    wait_timeFrom = State()
    wait_timeTo = State()
    wait_teacherFullname = State()
    wait_verify = State()
