import telebot
from telebot import types
from prettytable import PrettyTable
import webbrowser
import textwrap
import requests
import math
import json

bot = telebot.TeleBot("6360645906:AAEoP_l2HsgMzRZOxNx2p4CjoD5jnwqU21Q")

def get_basic_name(info):
    result = "%s %s.%s." %(info["surname"], info["name"][0], info["patronymic"][0])
    return result

def get_full_shedule(info, teacher = True):
    Shedule = PrettyTable()
    result = []
    lst = []
    if teacher:
        names = ["Название", "Преподаватель", "Место", "Комментарий"]
        jsonNames = ["name", "teacher", "location", "comment"]
    else:
        names = ["Название", "Место", "Комментарий"]
        jsonNames = ["name", "location", "comment"]
    for index in range(len(info)):
        Shedule.field_names = ["     Пара    ", "            %d            " %(info[index]["number"])]
        if info[index]["type"] != "":
            info[index]["name"] = "[%s] %s" %(info[index]["type"], info[index]["name"])
        for i in range(len(names)):
            lst = textwrap.wrap(info[index][jsonNames[i]], 25)
            place = math.ceil(len(lst)/2.0)-1
            for j in range(len(lst)):
                if j+1 == len(lst):
                    if place == j:
                        Shedule.add_row([names[i], lst[j]], divider=True)
                    else:
                        Shedule.add_row(["", lst[j]], divider=True)
                else:
                    if place == j:
                        Shedule.add_row([names[i], lst[j]])
                    else:
                        Shedule.add_row(["", lst[j]])
            if len(lst) == 0:
                Shedule.add_row([names[i], ""], divider=True)
        result.append("```\n%s```" %Shedule)
        Shedule.clear()
    return result


@bot.message_handler(commands=['start', 'help'])
def help(message):
    text = "Я помогу вам найти расписание! Если вы впервые пользуетесь мной - советую сначала зарегистрировать в Github, а затем зайти в свой /profile и настроить его!\n\n"\
        "*Изменить профиль*\n"\
        "/myprofile - информация пользователя\n"\
        "/setname - изменить имя\n"\
        "/setsurname - изменить фамилию\n"\
        "/setpatronymic - изменить отчество\n"\
        "/setgroup - изменить группу (только для студентов)\n"\
        "/unlinkgithub - отвязать аккаунт Github\n"\
        "/toadmin - открыть панель администратора (только для админов)\n\n"\
        "*Расписание занятий*"\
        "/nextlesson - где и когда начнется пара\n"\
        "/getshedule - расписание в определенную неделю и день\n"\
        "/sheduletoday - расписание на сегодня\n"\
        "/sheduletomorrow - расписание на завтра\n"\
        "/whereteacher - где находится учитель (только для студентов)\n"\
        "/wheregroup - где находится группа (только для преподавателей)\n"\
        "/addcomment - добавить комментарий к паре (только для преподавателей)"
    bot.send_message(message.from_user.id, text)

@bot.message_handler(commands=['profile'])
def profile(message):
    try:
        markup = types.InlineKeyboardMarkup()
        name = types.InlineKeyboardButton(text='Имя', callback_data='setname')
        surname = types.InlineKeyboardButton(text='Фамилия', callback_data='setsurname')
        patronymic = types.InlineKeyboardButton(text='Отчество', callback_data='setpatronymic')
        github = types.InlineKeyboardButton(text='Отвязать Github', callback_data='unlinkgithub')
        markup.row(name, surname, patronymic)
        info = json.loads(requests.get("http://localhost:8060/login?telegram_id=%s" %message.from_user.id).text)

        if info["recent_command"] == "UNAUTHORIZED":
            link = "http://localhost:8060/register?telegram_id=%d" %message.from_user.id
            text = "Упс! Кажется, вы еще не зарегистрированы. Чтобы зарегистрироваться - пожалуйста, перейдите по ссылке ниже:```\n%s```" %link
            bot.send_message(message.from_user.id, text, parse_mode='Markdown')
            return

        if info["surname"] == "":
            info["surname"] = "🚫"

        if info["name"] == "":
            info["name"] = "🚫"

        if info["patronymic"] == "":
            info["patronymic"] = "🚫"

        if info["group"] == "":
            info["group"] = "🚫"

        if info["role"] == "student":
            info["role"] = "студент"
            group = types.InlineKeyboardButton(text='Группа', callback_data='setgroup')
            markup.row(group, github)
            text = "*Ваш профиль*\n\n*Фамилия:* %s\n*Имя:* %s\n*Отчество:* %s\n*Группа:* %s\n*Статус:* %s" %(info["surname"], info["name"], info["patronymic"], info["group"], info["role"])

        if info["role"] == "teacher":
            info["role"] = "преподаватель"
            markup.add(github)
            text = "*Ваш профиль*\n\n*ФИО: *%s %s %s\n*Статус:* %s" %(info["surname"], info["name"], info["patronymic"], info["role"])

        if info["role"] == "admin":
            info["role"] = "администратор"
            group = types.InlineKeyboardButton(text='Группа', callback_data='setgroup')
            markup.row(group, github)
            admin = types.InlineKeyboardButton(text='Для администраторов', callback_data='toadmin', )
            markup.add(admin)
            text = "*Ваш профиль*\n\n*ФИО: *%s %s %s\n*Группа:* %s\n*Статус:* %s" %(info["surname"], info["name"], info["patronymic"], info["group"], info["role"])

        bot.send_message(message.from_user.id, text, reply_markup = markup, parse_mode='Markdown')
    except requests.ConnectionError:
        bot.send_message(message.from_user.id, "Нет соединения с сервером! Повторите попытку позже.")

@bot.message_handler(commands=['setname'])
def setname(message):
    try:
        markup = types.ReplyKeyboardRemove()
        info = json.loads(requests.get("http://localhost:8060/login?telegram_id=%s" %message.from_user.id).text)
        if info["recent_command"] == "UNAUTHORIZED":
            link = "http://localhost:8060/register?telegram_id=%d" %message.from_user.id
            text = "Упс! Кажется, вы еще не зарегистрированы. Чтобы зарегистрироваться - пожалуйста, перейдите по ссылке ниже:```\n%s```" %link
            bot.send_message(message.from_user.id, text, parse_mode='Markdown')
            return
        requests.get("http://localhost:8060/setuser?telegram_id=%d&recent_command=setname" %message.from_user.id)
        text = "Ок. Отправьте мне свое имя."
        bot.send_message(message.from_user.id, text, reply_markup = markup)
    except requests.ConnectionError:
        bot.send_message(message.from_user.id, "Нет соединения с сервером! Повторите попытку позже.")

@bot.message_handler(commands=['setsurname'])
def setsurname(message):
    try:
        markup = types.ReplyKeyboardRemove()
        info = json.loads(requests.get("http://localhost:8060/login?telegram_id=%s" %message.from_user.id).text)
        if info["recent_command"] == "UNAUTHORIZED":
            link = "http://localhost:8060/register?telegram_id=%d" %message.from_user.id
            text = "Упс! Кажется, вы еще не зарегистрированы. Чтобы зарегистрироваться - пожалуйста, перейдите по ссылке ниже:```\n%s```" %link
            bot.send_message(message.from_user.id, text, parse_mode='Markdown')
            return
        requests.get("http://localhost:8060/setuser?telegram_id=%d&recent_command=setsurname" %message.from_user.id)
        text = "Ок. Отправьте мне свою фамилию."
        bot.send_message(message.from_user.id, text, reply_markup=markup)
    except requests.ConnectionError:
        bot.send_message(message.from_user.id, "Нет соединения с сервером! Повторите попытку позже.")

@bot.message_handler(commands=['setpatronymic'])
def setpatronymic(message):
    try:
        markup = types.ReplyKeyboardRemove()
        info = json.loads(requests.get("http://localhost:8060/login?telegram_id=%s" %message.from_user.id).text)
        if info["recent_command"] == "UNAUTHORIZED":
            link = "http://localhost:8060/register?telegram_id=%d" %message.from_user.id
            text = "Упс! Кажется, вы еще не зарегистрированы. Чтобы зарегистрироваться - пожалуйста, перейдите по ссылке ниже:```\n%s```" %link
            bot.send_message(message.from_user.id, text, parse_mode='Markdown')
            return
        requests.get("http://localhost:8060/setuser?telegram_id=%d&recent_command=setpatronymic" %message.from_user.id)
        text = "Ок. Отправьте мне свое отчество."
        bot.send_message(message.from_user.id, text, reply_markup=markup)
    except requests.ConnectionError:
        bot.send_message(message.from_user.id, "Нет соединения с сервером! Повторите попытку позже.")

@bot.message_handler(commands=['setgroup'])
def setgroup(message):
    try:
        info = json.loads(requests.get("http://localhost:8060/login?telegram_id=%s" %message.from_user.id).text)
        if info["recent_command"] == "UNAUTHORIZED":
            link = "http://localhost:8060/register?telegram_id=%d" %message.from_user.id
            text = "Упс! Кажется, вы еще не зарегистрированы. Чтобы зарегистрироваться - пожалуйста, перейдите по ссылке ниже:```\n%s```" %link
            bot.send_message(message.from_user.id, text, parse_mode='Markdown')
            return
        if info["role"] != "teacher":
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            button1 = types.KeyboardButton('ПИ-б-о-231(1)')
            button2 = types.KeyboardButton('ПИ-б-о-231(2)')
            button3 = types.KeyboardButton('ПИ-б-о-232(1)')
            button4 = types.KeyboardButton('ПИ-б-о-232(2)')
            button5 = types.KeyboardButton('ПИ-б-о-233(1)')
            button6 = types.KeyboardButton('ПИ-б-о-233(2)')
            button7 = types.KeyboardButton('ИВТ-б-о-231(1)')
            button8 = types.KeyboardButton('ИВТ-б-о-231(2)')
            button9 = types.KeyboardButton('ИВТ-б-о-232(1)')
            button10 = types.KeyboardButton('ИВТ-б-о-232(2)')
            markup.row(button1, button2)
            markup.row(button3, button4)
            markup.row(button5, button6)
            markup.row(button7, button8)
            markup.row(button9, button10)
            requests.get("http://localhost:8060/setuser?telegram_id=%d&recent_command=setgroup" %message.from_user.id)
            text = "Ок. Выберите вашу группу."
        else:
            markup = types.ReplyKeyboardRemove()
            text = "Извините, но вы не можете изменить свою группу."
        bot.send_message(message.from_user.id, text, reply_markup=markup)
    except requests.ConnectionError:
        bot.send_message(message.from_user.id, "Нет соединения с сервером! Повторите попытку позже.")

@bot.message_handler(commands=['unlinkgithub'])
def unlinkgithub(message):
    try:
        markup = types.ReplyKeyboardRemove()
        info = json.loads(requests.get("http://localhost:8060/login?telegram_id=%s" %message.from_user.id).text)
        if info["recent_command"] == "UNAUTHORIZED":
            link = "http://localhost:8060/register?telegram_id=%d" %message.from_user.id
            text = "Упс! Кажется, вы еще не зарегистрированы. Чтобы зарегистрироваться - пожалуйста, перейдите по ссылке ниже:```\n%s```" %link
            bot.send_message(message.from_user.id, text, parse_mode='Markdown')
            return
        requests.get("http://localhost:8060/setuser?telegram_id=%d&recent_command=unlinkgithub" %message.from_user.id)
        text = "Вы уверены, что хотите отвязать свой Github от аккаунта? Вы сможете привязать его снова в любой момент.\n\nОтправьте \"Да, отвяжите мой Github.\", чтобы отвязать его."
        bot.send_message(message.from_user.id, text, reply_markup=markup)
    except requests.ConnectionError:
        bot.send_message(message.from_user.id, "Нет соединения с сервером! Повторите попытку позже.")

@bot.message_handler(commands=['toadmin'])
def toadmin(message):
    try:
        markup = types.ReplyKeyboardRemove()
        info = json.loads(requests.get("http://localhost:8060/login?telegram_id=%s" %message.from_user.id).text)
        if info["recent_command"] == "UNAUTHORIZED":
            link = "http://localhost:8060/register?telegram_id=%d" %message.from_user.id
            text = "Упс! Кажется, вы еще не зарегистрированы. Чтобы зарегистрироваться - пожалуйста, перейдите по ссылке ниже:```\n%s```" %link
            bot.send_message(message.from_user.id, text, parse_mode='Markdown')
            return
        if info["role"] == "admin":
            text = "Чтобы открыть панель администратора - перейдите по ссылке ниже"
            link = "http://localhost:8040"
            bot.send_message(message.from_user.id, "%s:```\n%s```" %(text, link), reply_markup=markup, parse_mode='Markdown')
        else:
            text = "Извините, но вы не имеете доступа к панели администратора."
        bot.send_message(message.from_user.id, text, reply_markup=markup)
    except requests.ConnectionError:
        bot.send_message(message.from_user.id, "Нет соединения с сервером! Повторите попытку позже.")

@bot.message_handler(commands=['nextlesson'])
def nextlesson(message):
    try :
        markup = types.ReplyKeyboardRemove()
        info = json.loads(requests.get("http://localhost:8060/login?telegram_id=%s" %message.from_user.id).text)
        if info["recent_command"] == "UNAUTHORIZED":
            link = "http://localhost:8060/register?telegram_id=%d" %message.from_user.id
            text = "Упс! Кажется, вы еще не зарегистрированы. Чтобы зарегистрироваться - пожалуйста, перейдите по ссылке ниже:```\n%s```" %link
            bot.send_message(message.from_user.id, text, parse_mode='Markdown')
            return
        if info["role"] == "teacher":
            if info["name"] != "" and info["surname"] != "" and info["patronymic"] != "":
                answer = json.loads(requests.get("http://localhost:8050/getshedule?command=nextlesson&fullname=%s" %get_basic_name(info)).text)
                if answer["type"] == "":
                    text = "Сегодня больше нет пар!"
                    bot.send_message(message.from_user.id, text, reply_markup=markup)
                else:
                    lst = []
                    lst.append(answer)
                    shedule = get_full_shedule(lst, False)
                    text = "*Следующая пара будет в %s:%s*\n%s" %(answer["hours"], answer["minutes"], shedule[0])
                    bot.send_message(message.from_user.id, text, reply_markup=markup, parse_mode='Markdown')
            else:
                markup = types.ReplyKeyboardRemove()
                text = "Мне необходимо знать ваше имя, фамилию и отчество. Пожалуйста, заполните свои данные. /profile"
                bot.send_message(message.from_user.id, text, reply_markup=markup)
        else:
            if info["group"] != "":
                answer = json.loads(requests.get("http://localhost:8050/getshedule?command=nextlesson&group=%s" %info["group"]).text)
                if answer["type"] == "":
                    text = "Сегодня больше нет пар!"
                    bot.send_message(message.from_user.id, text, reply_markup=markup)
                else:
                    lst = []
                    lst.append(answer)
                    shedule = get_full_shedule(lst)
                    text = "*Следующая пара будет в %s:%s*\n%s" %(answer["hours"], answer["minutes"], shedule[0])
                    bot.send_message(message.from_user.id, text, reply_markup=markup, parse_mode='Markdown')
            else:
                markup = types.ReplyKeyboardRemove()
                text = "Мне необходимо знать вашу группу. Пожалуйста, задайте ее в соответствующей команде. /setgroup"
                bot.send_message(message.from_user.id, text, reply_markup=markup)
    except requests.ConnectionError:
        bot.send_message(message.from_user.id, "Нет соединения с сервером! Повторите попытку позже.")

@bot.message_handler(commands=['getshedule'])
def getshedule(message):
    try :
        info = json.loads(requests.get("http://localhost:8060/login?telegram_id=%s" %message.from_user.id).text)
        if info["recent_command"] == "UNAUTHORIZED":
            link = "http://localhost:8060/register?telegram_id=%d" %message.from_user.id
            text = "Упс! Кажется, вы еще не зарегистрированы. Чтобы зарегистрироваться - пожалуйста, перейдите по ссылке ниже:```\n%s```" %link
            bot.send_message(message.from_user.id, text, parse_mode='Markdown')
            return
        if info["role"] == "teacher" and info["name"] != "" and info["surname"] != "" and info["patronymic"] != "" or info["role"] != "teacher" and info["group"] != "":
            markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            button1 = types.KeyboardButton('Четная')
            button2 = types.KeyboardButton('Текущая')
            button3 = types.KeyboardButton('Нечетная')
            markup.row(button1, button2, button3)
            requests.get("http://localhost:8060/setuser?telegram_id=%d&recent_command=getshedule" %message.from_user.id)
            text = "Выберите тип недели, либо \"Текущая\" для выбора текущего типа недели."
            bot.send_message(message.from_user.id, text, reply_markup=markup)
        elif info["role"] != "teacher" and info["group"] == "":
            markup = types.ReplyKeyboardRemove()
            text = "Мне необходимо знать вашу группу. Пожалуйста, задайте ее в соответствующей команде. /setgroup"
            bot.send_message(message.from_user.id, text, reply_markup=markup)
        else:
            markup = types.ReplyKeyboardRemove()
            text = "Мне необходимо знать ваше имя, фамилию и отчество. Пожалуйста, заполните свои данные. /profile"
            bot.send_message(message.from_user.id, text, reply_markup=markup)
    except requests.ConnectionError:
        bot.send_message(message.from_user.id, "Нет соединения с сервером! Повторите попытку позже.")

@bot.message_handler(commands=['sheduletoday'])
def sheduletoday(message):
    try :
        markup = types.ReplyKeyboardRemove()
        info = json.loads(requests.get("http://localhost:8060/login?telegram_id=%s" %message.from_user.id).text)
        if info["recent_command"] == "UNAUTHORIZED":
            link = "http://localhost:8060/register?telegram_id=%d" %message.from_user.id
            text = "Упс! Кажется, вы еще не зарегистрированы. Чтобы зарегистрироваться - пожалуйста, перейдите по ссылке ниже:```\n%s```" %link
            bot.send_message(message.from_user.id, text, parse_mode='Markdown')
            return
        if info["role"] == "teacher":
            if info["name"] != "" and info["surname"] != "" and info["patronymic"] != "":
                answer = json.loads(requests.get("http://localhost:8050/getshedule?command=sheduletoday&fullname=%s" %get_basic_name(info)).text)
                shedule = get_full_shedule(answer, False)
            else:
                markup = types.ReplyKeyboardRemove()
                text = "Мне необходимо знать ваше имя, фамилию и отчество. Пожалуйста, заполните свои данные. /profile"
                bot.send_message(message.from_user.id, text, reply_markup=markup)
        else:
            if info["group"] != "":
                answer = json.loads(requests.get("http://localhost:8050/getshedule?command=sheduletoday&group=%s" %info["group"]).text)
                shedule = get_full_shedule(answer)
            else:
                markup = types.ReplyKeyboardRemove()
                text = "Мне необходимо знать вашу группу. Пожалуйста, задайте ее в соответствующей команде. /setgroup"
                bot.send_message(message.from_user.id, text, reply_markup=markup)
        requests.get("http://localhost:8060/setuser?telegram_id=%d&recent_command=none" %message.from_user.id)
        text = "*Расписание на сегодня*"
        bot.send_message(message.from_user.id, text, reply_markup=markup, parse_mode='Markdown')
        for lesson in shedule:
            bot.send_message(message.from_user.id, lesson, parse_mode='Markdown')
    except requests.ConnectionError:
        bot.send_message(message.from_user.id, "Нет соединения с сервером! Повторите попытку позже.")

@bot.message_handler(commands=['sheduletomorrow'])
def sheduletoday(message):
    try :
        markup = types.ReplyKeyboardRemove()
        info = json.loads(requests.get("http://localhost:8060/login?telegram_id=%s" %message.from_user.id).text)
        if info["recent_command"] == "UNAUTHORIZED":
            link = "http://localhost:8060/register?telegram_id=%d" %message.from_user.id
            text = "Упс! Кажется, вы еще не зарегистрированы. Чтобы зарегистрироваться - пожалуйста, перейдите по ссылке ниже:```\n%s```" %link
            bot.send_message(message.from_user.id, text, parse_mode='Markdown')
            return
        if info["role"] == "teacher":
            if info["name"] != "" and info["surname"] != "" and info["patronymic"] != "":
                answer = json.loads(requests.get("http://localhost:8050/getshedule?command=sheduletomorrow&fullname=%s" %get_basic_name(info)).text)
                shedule = get_full_shedule(answer, False)
            else:
                markup = types.ReplyKeyboardRemove()
                text = "Мне необходимо знать ваше имя, фамилию и отчество. Пожалуйста, заполните свои данные. /profile"
                bot.send_message(message.from_user.id, text, reply_markup=markup)
        else:
            if info["group"] != "":
                answer = json.loads(requests.get("http://localhost:8050/getshedule?command=sheduletomorrow&group=%s" %info["group"]).text)
                shedule = get_full_shedule(answer)
            else:
                markup = types.ReplyKeyboardRemove()
                text = "Мне необходимо знать вашу группу. Пожалуйста, задайте ее в соответствующей команде. /setgroup"
                bot.send_message(message.from_user.id, text, reply_markup=markup)
        requests.get("http://localhost:8060/setuser?telegram_id=%d&recent_command=none" %message.from_user.id)
        text = "*Расписание на завтра*"
        bot.send_message(message.from_user.id, text, reply_markup=markup, parse_mode='Markdown')
        for lesson in shedule:
            bot.send_message(message.from_user.id, lesson, parse_mode='Markdown')
    except requests.ConnectionError:
        bot.send_message(message.from_user.id, "Нет соединения с сервером! Повторите попытку позже.")

@bot.message_handler(commands=['whereteacher'])
def whereteacher(message):
    try :
        info = json.loads(requests.get("http://localhost:8060/login?telegram_id=%s" %message.from_user.id).text)
        if info["recent_command"] == "UNAUTHORIZED":
            link = "http://localhost:8060/register?telegram_id=%d" %message.from_user.id
            text = "Упс! Кажется, вы еще не зарегистрированы. Чтобы зарегистрироваться - пожалуйста, перейдите по ссылке ниже:```\n%s```" %link
            bot.send_message(message.from_user.id, text, parse_mode='Markdown')
            return
        if info["role"] != "teacher":
            markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            button1 = types.KeyboardButton('Ахрамович Л.Н.')
            button2 = types.KeyboardButton('Вареник М.Ю.')
            button3 = types.KeyboardButton('Галушко В.И.')
            button4 = types.KeyboardButton('Горская И.Ю.')
            button5 = types.KeyboardButton('Епишкин И.В.')
            button6 = types.KeyboardButton('Ильина В.Ю.')
            button7 = types.KeyboardButton('Кислицина Н.Н.')
            button8 = types.KeyboardButton('Клименко Е.П.')
            button9 = types.KeyboardButton('Корниенко А.Ю.')
            button10 = types.KeyboardButton('Корнута А.А.')
            button11 = types.KeyboardButton('Крюков С.А.')
            button12 = types.KeyboardButton('Лейбенсон Ю.Т.')
            button13 = types.KeyboardButton('Мальцев В.А.')
            button14 = types.KeyboardButton('Марянин Б.Д.')
            button15 = types.KeyboardButton('Мельниченко Т.В.')
            button16 = types.KeyboardButton('Непомнящий А.А.')
            button17 = types.KeyboardButton('Рудницкая Л.И.')
            button18 = types.KeyboardButton('Руев В.Л.')
            button19 = types.KeyboardButton('Сагайдак О.И.')
            button20 = types.KeyboardButton('Смирнова С.И.')
            button21 = types.KeyboardButton('Томичева И.В.')
            button22 = types.KeyboardButton('Фабрина А.В.')
            button23 = types.KeyboardButton('Чабанов В.В.')
            button24 = types.KeyboardButton('Шестакова Е.С.')
            markup.row(button1, button2, button3)
            markup.row(button4, button5, button6)
            markup.row(button7, button8, button9)
            markup.row(button10, button11, button12)
            markup.row(button13, button14, button15)
            markup.row(button16, button17, button18)
            markup.row(button19, button20, button21)
            markup.row(button22, button23, button24)
            requests.get("http://localhost:8060/setuser?telegram_id=%d&recent_command=whereteacher" %message.from_user.id)
            text = "Выберите имя преподавателя, которого вы хотите найти."
            bot.send_message(message.from_user.id, text, reply_markup=markup)
        else:
            markup = types.ReplyKeyboardRemove()
            text = "Извините, но вы не можете искать преподавателей."
            bot.send_message(message.from_user.id, text, reply_markup=markup)
    except requests.ConnectionError:
        bot.send_message(message.from_user.id, "Нет соединения с сервером! Повторите попытку позже.")

@bot.message_handler(commands=['wheregroup'])
def wheregroup(message):
    try :
        info = json.loads(requests.get("http://localhost:8060/login?telegram_id=%s" %message.from_user.id).text)
        if info["recent_command"] == "UNAUTHORIZED":
            link = "http://localhost:8060/register?telegram_id=%d" %message.from_user.id
            text = "Упс! Кажется, вы еще не зарегистрированы. Чтобы зарегистрироваться - пожалуйста, перейдите по ссылке ниже:```\n%s```" %link
            bot.send_message(message.from_user.id, text, parse_mode='Markdown')
            return
        if info["role"] != "student":
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            button1 = types.KeyboardButton('ПИ-б-о-231(1)')
            button2 = types.KeyboardButton('ПИ-б-о-231(2)')
            button3 = types.KeyboardButton('ПИ-б-о-232(1)')
            button4 = types.KeyboardButton('ПИ-б-о-232(2)')
            button5 = types.KeyboardButton('ПИ-б-о-233(1)')
            button6 = types.KeyboardButton('ПИ-б-о-233(2)')
            button7 = types.KeyboardButton('ИВТ-б-о-231(1)')
            button8 = types.KeyboardButton('ИВТ-б-о-231(2)')
            button9 = types.KeyboardButton('ИВТ-б-о-232(1)')
            button10 = types.KeyboardButton('ИВТ-б-о-232(2)')
            markup.row(button1, button2)
            markup.row(button3, button4)
            markup.row(button5, button6)
            markup.row(button7, button8)
            markup.row(button9, button10)
            requests.get("http://localhost:8060/setuser?telegram_id=%d&recent_command=wheregroup" %message.from_user.id)
            text = "Выберите название группы, которую вы хотите найти."
            bot.send_message(message.from_user.id, text, reply_markup=markup)
        else:
            markup = types.ReplyKeyboardRemove()
            text = "Извините, но вы не можете искать группы."
            bot.send_message(message.from_user.id, text, reply_markup=markup)
    except requests.ConnectionError:
        bot.send_message(message.from_user.id, "Нет соединения с сервером! Повторите попытку позже.")

@bot.message_handler(commands=['addcomment'])
def leavecomment(message):
    try :
        info = json.loads(requests.get("http://localhost:8060/login?telegram_id=%s" %message.from_user.id).text)
        if info["recent_command"] == "UNAUTHORIZED":
            link = "http://localhost:8060/register?telegram_id=%d" %message.from_user.id
            text = "Упс! Кажется, вы еще не зарегистрированы. Чтобы зарегистрироваться - пожалуйста, перейдите по ссылке ниже:```\n%s```" %link
            bot.send_message(message.from_user.id, text, parse_mode='Markdown')
            return
        if info["role"] != "student":
            if info["name"] != "" and info["surname"] != "" and info["patronymic"] != "":
                markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                button1 = types.KeyboardButton('ПИ-б-о-231(1)')
                button2 = types.KeyboardButton('ПИ-б-о-231(2)')
                button3 = types.KeyboardButton('ПИ-б-о-232(1)')
                button4 = types.KeyboardButton('ПИ-б-о-232(2)')
                button5 = types.KeyboardButton('ПИ-б-о-233(1)')
                button6 = types.KeyboardButton('ПИ-б-о-233(2)')
                button7 = types.KeyboardButton('ИВТ-б-о-231(1)')
                button8 = types.KeyboardButton('ИВТ-б-о-231(2)')
                button9 = types.KeyboardButton('ИВТ-б-о-232(1)')
                button10 = types.KeyboardButton('ИВТ-б-о-232(2)')
                markup.row(button1, button2)
                markup.row(button3, button4)
                markup.row(button5, button6)
                markup.row(button7, button8)
                markup.row(button9, button10)
                markup.row(button1, button2, button3)
                requests.get("http://localhost:8060/setuser?telegram_id=%d&recent_command=addcomment" %message.from_user.id)
                text = "Выберите название группы, комментарий к которой вы будете оставлять."
                bot.send_message(message.from_user.id, text, reply_markup=markup)
            else:
                markup = types.ReplyKeyboardRemove()
                text = "Нам необходимо знать ваши имя, фамилию и отчество. Пожалуйста, заполните свои данные. /profile"
                bot.send_message(message.from_user.id, text, reply_markup=markup)
        else:
            markup = types.ReplyKeyboardRemove()
            text = "Извините, но вы не можете оставлять комментарии."
            bot.send_message(message.from_user.id, text, reply_markup=markup)
    except requests.ConnectionError:
        bot.send_message(message.from_user.id, "Нет соединения с сервером! Повторите попытку позже.")

@bot.message_handler(commands=['cancel'])
def cancel(message):
    try :
        markup = types.ReplyKeyboardRemove()
        info = json.loads(requests.get("http://localhost:8060/login?telegram_id=%s" %message.from_user.id).text)
        if info["recent_command"] == "UNAUTHORIZED":
            link = "http://localhost:8060/register?telegram_id=%d" %message.from_user.id
            text = "Упс! Кажется, вы еще не зарегистрированы. Чтобы зарегистрироваться - пожалуйста, перейдите по ссылке ниже:```\n%s```" %link
            bot.send_message(message.from_user.id, text, parse_mode='Markdown')
            return
        if info["recent_command"] != "":
            requests.get("http://localhost:8060/setuser?telegram_id=%d&recent_command=none" %message.from_user.id)
            text = "Команда %s была отменена. /help" %info["recent_command"]
            bot.send_message(message.from_user.id, text, reply_markup=markup)
        else:
            text = "Я все равно не был ничем занят, но ладно."
            bot.send_message(message.from_user.id, text, reply_markup=markup)
    except requests.ConnectionError:
        bot.send_message(message.from_user.id, "Я не могу отменить команду, пока нет соединения с сервером.\nЛибо кто-то вызвал на сервере ошибку.")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    try:
        info = json.loads(requests.get("http://localhost:8060/login?telegram_id=%d" %call.from_user.id).text)
        if info["recent_command"] == "UNAUTHORIZED":
            link = "http://localhost:8060/register?telegram_id=%d" %call.from_user.id
            text = "Упс! Кажется, вы еще не зарегистрированы. Чтобы зарегистрироваться - пожалуйста, перейдите по ссылке ниже:```\n%s```" %link
            bot.answer_callback_query(call.id, text="Упс! Кажется, вы еще не зарегистрированы.")
            bot.send_message(call.from_user.id, text, parse_mode='Markdown')
            return
    except requests.ConnectionError:
        bot.send_message(call.from_user.id, "Нет соединения с сервером! Операция экстренно отменяется.")
        return

    if call.data == 'setname':
        markup = types.ReplyKeyboardRemove()
        requests.get("http://localhost:8060/setuser?telegram_id=%d&recent_command=setname(inline)" %call.from_user.id)
        text = "Ок. Отправьте мне свое имя."
        bot.answer_callback_query(call.id, text=text)
        bot.send_message(call.from_user.id, text=text, reply_markup=markup)
    
    if call.data == 'setsurname':
        markup = types.ReplyKeyboardRemove()
        requests.get("http://localhost:8060/setuser?telegram_id=%d&recent_command=setsurname(inline)" %call.from_user.id)
        text = "Ок. Отправьте мне свою фамилию."
        bot.answer_callback_query(call.id, text=text)
        bot.send_message(call.from_user.id, text=text, reply_markup=markup)

    if call.data == 'setpatronymic':
        markup = types.ReplyKeyboardRemove()
        requests.get("http://localhost:8060/setuser?telegram_id=%d&recent_command=setpatronymic(inline)" %call.from_user.id)
        text = "Ок. Отправьте мне свое отчество."
        bot.answer_callback_query(call.id, text=text)
        bot.send_message(call.from_user.id, text=text, reply_markup=markup)

    if call.data == 'setgroup':
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        button1 = types.KeyboardButton('ПИ-б-о-231(1)')
        button2 = types.KeyboardButton('ПИ-б-о-231(2)')
        button3 = types.KeyboardButton('ПИ-б-о-232(1)')
        button4 = types.KeyboardButton('ПИ-б-о-232(2)')
        button5 = types.KeyboardButton('ПИ-б-о-233(1)')
        button6 = types.KeyboardButton('ПИ-б-о-233(2)')
        button7 = types.KeyboardButton('ИВТ-б-о-231(1)')
        button8 = types.KeyboardButton('ИВТ-б-о-231(2)')
        button9 = types.KeyboardButton('ИВТ-б-о-232(1)')
        button10 = types.KeyboardButton('ИВТ-б-о-232(2)')
        markup.row(button1, button2)
        markup.row(button3, button4)
        markup.row(button5, button6)
        markup.row(button7, button8)
        markup.row(button9, button10)
        requests.get("http://localhost:8060/setuser?telegram_id=%d&recent_command=setgroup(inline)" %call.from_user.id)
        text = "Ок. Выберите вашу группу."
        bot.answer_callback_query(call.id, text=text)
        bot.send_message(call.from_user.id, text=text, reply_markup=markup)

    if call.data == 'unlinkgithub':
        markup  = telebot.types.InlineKeyboardMarkup()
        untie = types.InlineKeyboardButton(text='Отвязать', callback_data='unlinkgithubsure')
        back = types.InlineKeyboardButton(text='Назад', callback_data='profile')
        markup.row(untie, back)
        text = "Сейчас ваш Github аккаунт связан с данным аккаунтом. Если вы хотите отвязать свой Github - нажмите кнопку ниже."
        bot.edit_message_text(message_id=call.message.message_id, text=text, chat_id=call.from_user.id, reply_markup=markup)

    if call.data == 'unlinkgithubsure':
        requests.get("http://localhost:8060/setuser?telegram_id=%d&github_id=%d" %(call.from_user.id, -1))
        text = "Вы успешно отвязали свой Github аккаунт.\nЕсли вы хотите привязать новый - зайдите в него на сайте https://github.com\n*Вы не сможете пользоваться командами, не привязав свой Github.* /help"
        bot.edit_message_text(message_id=call.message.message_id, text=text, chat_id=call.from_user.id, parse_mode='Markdown')

    if call.data == 'toadmin':
        markup = types.ReplyKeyboardRemove()
        text = "Чтобы открыть панель администратора - перейдите по ссылке ниже"
        link = "http://localhost:8040"
        bot.answer_callback_query(call.id, "%s." %text)
        bot.send_message(call.from_user.id, "%s:```\n%s```" %(text, link), reply_markup=markup, parse_mode='Markdown')

    if call.data == 'profile':
        markup = types.InlineKeyboardMarkup()
        name = types.InlineKeyboardButton(text='Имя', callback_data='setname')
        surname = types.InlineKeyboardButton(text='Фамилия', callback_data='setsurname')
        patronymic = types.InlineKeyboardButton(text='Отчество', callback_data='setpatronymic')
        github = types.InlineKeyboardButton(text='Отвязать Github', callback_data='unlinkgithub')
        markup.row(name, surname, patronymic)

        if info["surname"] == "":
            info["surname"] = "🚫"

        if info["name"] == "":
            info["name"] = "🚫"

        if info["patronymic"] == "":
            info["patronymic"] = "🚫"

        if info["group"] == "":
            info["group"] = "🚫"

        if info["role"] == "student":
            info["role"] = "студент"
            group = types.InlineKeyboardButton(text='Группа', callback_data='setgroup')
            markup.row(group, github)
            text = "*Ваш профиль*\n\n*Фамилия:* %s\n*Имя:* %s\n*Отчество:* %s\n*Группа:* %s\n*Статус:* %s" %(info["surname"], info["name"], info["patronymic"], info["group"], info["role"])

        if info["role"] == "teacher":
            info["role"] = "преподаватель"
            markup.add(github)
            text = "*Ваш профиль*\n\n*ФИО: *%s %s %s\n*Статус:* %s" %(info["surname"], info["name"], info["patronymic"], info["role"])

        if info["role"] == "admin":
            info["role"] = "администратор"
            group = types.InlineKeyboardButton(text='Группа', callback_data='setgroup')
            markup.row(group, github)
            admin = types.InlineKeyboardButton(text='Для администраторов', callback_data='toadmin')
            markup.add(admin)
            text = "*Ваш профиль*\n\n*ФИО: *%s %s %s\n*Группа:* %s\n*Статус:* %s" %(info["surname"], info["name"], info["patronymic"], info["group"], info["role"])

        bot.edit_message_text(message_id=call.message.message_id, text=text, chat_id=call.from_user.id, reply_markup=markup, parse_mode='Markdown')


@bot.message_handler(content_types=['text'])
def message_handler(message):
    try:
        info = json.loads(requests.get("http://localhost:8060/login?telegram_id=%d" %message.from_user.id).text)
    except requests.ConnectionError:
        text = "Соединение с сервером было прервано, либо были заданы неверные параметры.\nПопробуйте еще раз. Если ситуация повторится - значит сервера отключены."
        bot.send_message(message.from_user.id, text)
        return
    
    if info["recent_command"] == "setname":
        markup = types.ReplyKeyboardRemove()
        requests.get("http://localhost:8060/setuser?telegram_id=%d&name=%s&recent_command=none" %(message.from_user.id, message.text))
        text = "Имя успешно изменено на *%s*! /help" %message.text
        bot.send_message(message.from_user.id, text, reply_markup=markup, parse_mode='Markdown')

    if info["recent_command"] == "setname(inline)":
        markup = types.InlineKeyboardMarkup()
        back = types.InlineKeyboardButton(text='Назад к профилю', callback_data='profile')
        markup.add(back)
        requests.get("http://localhost:8060/setuser?telegram_id=%d&name=%s&recent_command=none" %(message.from_user.id, message.text))
        text = "Имя успешно изменено на *%s*! /help" %message.text
        bot.send_message(message.from_user.id, text, reply_markup=markup, parse_mode='Markdown')

    if info["recent_command"] == "setsurname":
        markup = types.ReplyKeyboardRemove()
        requests.get("http://localhost:8060/setuser?telegram_id=%d&surname=%s&recent_command=none" %(message.from_user.id, message.text))
        text = "Фамилия успешно изменена на *%s*! /help" %message.text
        bot.send_message(message.from_user.id, text, reply_markup=markup, parse_mode='Markdown')

    if info["recent_command"] == "setsurname(inline)":
        markup = types.InlineKeyboardMarkup()
        back = types.InlineKeyboardButton(text='Назад к профилю', callback_data='profile')
        markup.add(back)
        requests.get("http://localhost:8060/setuser?telegram_id=%d&surname=%s&recent_command=none" %(message.from_user.id, message.text))
        text = "Фамилия успешно изменена на *%s*! /help" %message.text
        bot.send_message(message.from_user.id, text, reply_markup=markup, parse_mode='Markdown')

    if info["recent_command"] == "setpatronymic":
        markup = types.ReplyKeyboardRemove()
        requests.get("http://localhost:8060/setuser?telegram_id=%d&patronymic=%s&recent_command=none" %(message.from_user.id, message.text))
        text = "Отчество успешно изменено на *%s*! /help" %message.text
        bot.send_message(message.from_user.id, text, reply_markup=markup, parse_mode='Markdown')

    if info["recent_command"] == "setpatronymic(inline)":
        markup = types.InlineKeyboardMarkup()
        back = types.InlineKeyboardButton(text='Назад к профилю', callback_data='profile')
        markup.add(back)
        requests.get("http://localhost:8060/setuser?telegram_id=%d&patronymic=%s&recent_command=none" %(message.from_user.id, message.text))
        text = "Отчество успешно изменено на *%s*! /help" %message.text
        bot.send_message(message.from_user.id, text, reply_markup=markup, parse_mode='Markdown')

    if info["recent_command"] == "setgroup":
        markup  = telebot.types.ReplyKeyboardRemove()
        requests.get("http://localhost:8060/setuser?telegram_id=%d&group=%s&recent_command=none" %(message.from_user.id, message.text))
        text = "Группа успешно изменена на *%s*! /help" %message.text
        bot.send_message(message.from_user.id, text, reply_markup=markup, parse_mode='Markdown')

    if info["recent_command"] == "setgroup(inline)":
        markup = types.InlineKeyboardMarkup()
        back = types.InlineKeyboardButton(text='Назад к профилю', callback_data='profile')
        markup.add(back)
        requests.get("http://localhost:8060/setuser?telegram_id=%d&group=%s&recent_command=none" %(message.from_user.id, message.text))
        text = "Группа успешно изменена на *%s*! /help" %message.text
        bot.send_message(message.from_user.id, text, reply_markup=markup, parse_mode='Markdown')

    if info["recent_command"] == 'unlinkgithub':
        if message.text == "Да, отвяжите мой Github.":
            markup  = telebot.types.ReplyKeyboardRemove()
            requests.get("http://localhost:8060/setuser?telegram_id=%d&github_id=%d" %(message.from_user.id, -1))
            text = "Вы успешно отвязали свой Github аккаунт.\nЕсли вы хотите привязать новый - зайдите в него на сайте https://github.com\n*Вы не сможете пользоваться командами, не привязав свой Github.* /help"
            bot.send_message(message.from_user.id, text, reply_markup=markup, parse_mode='Markdown')

    if info["recent_command"] == "getshedule":
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        button1 = types.KeyboardButton('Понедельник')
        button2 = types.KeyboardButton('Вторник')
        button3 = types.KeyboardButton('Среда')
        button4 = types.KeyboardButton('Четверг')
        button5 = types.KeyboardButton('Пятница')
        button6 = types.KeyboardButton('Суббота')
        button7 = types.KeyboardButton('Воскресенье')
        markup.add(button1, button2, button3, button4, button5, button6, button7)
        requests.get("http://localhost:8060/setuser?telegram_id=%d&recent_command=%s" %(message.from_user.id, "getsheduleRC" + message.text))
        text = "Отправьте день недели, расписание на который вы хотите узнать."
        bot.send_message(message.from_user.id, text, reply_markup=markup)

    if "RC" in info["recent_command"]:
        markup  = telebot.types.ReplyKeyboardRemove()
        if info["recent_command"].split("RC")[1] == "Четная":
            week = 0
        if info["recent_command"].split("RC")[1] == "Нечетная":
            week = 1
        if info["recent_command"].split("RC")[1] == "Текущая":
            week = -1
        if info["role"] == "teacher":
            answer = json.loads(requests.get("http://localhost:8050/getshedule?command=getshedule&fullname=%s&week=%d&day=%s" %(get_basic_name(info), week, message.text)).text)
            shedule = get_full_shedule(answer, False)
        else:
            answer = json.loads(requests.get("http://localhost:8050/getshedule?command=getshedule&group=%s&week=%d&day=%s" %(info["group"], week, message.text)).text)
            shedule = get_full_shedule(answer)
        requests.get("http://localhost:8060/setuser?telegram_id=%d&recent_command=none" %message.from_user.id)
        bot.send_message(message.from_user.id, "*Расписание на %s*" %(message.text.lower()), reply_markup=markup, parse_mode='Markdown')
        for lesson in shedule:
            bot.send_message(message.from_user.id, lesson, parse_mode='Markdown')

    if info["recent_command"] == "whereteacher":
        markup  = telebot.types.ReplyKeyboardRemove()
        answer = json.loads(requests.get("http://localhost:8050/getshedule?command=whereteacher&fullname=%s" %message.text).text)
        requests.get("http://localhost:8060/setuser?telegram_id=%d&recent_command=none" %message.from_user.id)
        lst = []
        lst.append(answer)
        shedule = get_full_shedule(lst, False)
        if answer["type"] != "":
            text = "*Преподаватель находится на паре:*\n%s" %(shedule[0])
        else:
            text = "Преподаватель сейчас не на паре!"
        bot.send_message(message.from_user.id, text, reply_markup=markup)

    if info["recent_command"] == "wheregroup":
        markup  = telebot.types.ReplyKeyboardRemove()
        answer = json.loads(requests.get("http://localhost:8050/getshedule?command=wheregroup&group=%s" %message.text).text)
        requests.get("http://localhost:8060/setuser?telegram_id=%d&recent_command=none" %message.from_user.id)
        lst = []
        lst.append(answer)
        shedule = get_full_shedule(lst)
        if answer["type"] != "":
            text = "*Группа находится на паре:*\n%s" %(shedule[0])
        else:
            text = "Группа сейчас не на паре!"
        bot.send_message(message.from_user.id, text, reply_markup=markup)

    if info["recent_command"] == "addcomment":
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        button1 = types.KeyboardButton('Четная')
        button2 = types.KeyboardButton('Текущая')
        button3 = types.KeyboardButton('Нечетная')
        markup.row(button1, button2, button3)
        requests.get("http://localhost:8060/login?telegram_id=%s" %message.from_user.id)
        requests.get("http://localhost:8060/setuser?telegram_id=%d&recent_command=%s" %(message.from_user.id, info["recent_command"] + "LC" + message.text))
        text = "Выберите тип недели, либо \"Текущая\" для выбора текущего типа недели."
        bot.send_message(message.from_user.id, text, reply_markup=markup)

    if "LC" in info["recent_command"] and "LC1" not in info["recent_command"]:
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        button1 = types.KeyboardButton('Понедельник')
        button2 = types.KeyboardButton('Вторник')
        button3 = types.KeyboardButton('Среда')
        button4 = types.KeyboardButton('Четверг')
        button5 = types.KeyboardButton('Пятница')
        button6 = types.KeyboardButton('Суббота')
        button7 = types.KeyboardButton('Воскресенье')
        markup.add(button1, button2, button3, button4, button5, button6, button7)
        requests.get("http://localhost:8060/setuser?telegram_id=%d&recent_command=%s" %(message.from_user.id, info["recent_command"] + "LC1" + message.text))
        text = "Выберите день недели."
        bot.send_message(message.from_user.id, text, reply_markup=markup)

    if "LC1" in info["recent_command"] and "LC2" not in info["recent_command"]:
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        button1 = types.KeyboardButton('1')
        button2 = types.KeyboardButton('2')
        button3 = types.KeyboardButton('3')
        button4 = types.KeyboardButton('4')
        button5 = types.KeyboardButton('5')
        button6 = types.KeyboardButton('6')
        button7 = types.KeyboardButton('7')
        markup.add(button1, button2, button3, button4, button5, button6, button7)
        requests.get("http://localhost:8060/setuser?telegram_id=%d&recent_command=%s" %(message.from_user.id, info["recent_command"] + "LC2" + message.text))
        text = "Выберите номер пары."
        bot.send_message(message.from_user.id, text, reply_markup=markup)

    if "LC2" in info["recent_command"] and "LC3" not in info["recent_command"]:
        markup  = telebot.types.ReplyKeyboardRemove()
        requests.get("http://localhost:8060/setuser?telegram_id=%d&recent_command=%s" %(message.from_user.id, info["recent_command"] + "LC3" + message.text))
        text = "Введите свой комментарий к паре. Он будет закреплен вместе с вашим именем, чтобы студенты знали, кто написал комментарий. "\
            "*Отправьте \"nul\", чтобы убрать существующий комментарий.*\n\n"\
            "Просьба использовать знаки \"\\n\" для перехода на следующую строку. Если хотя бы одна строка вашего комментария окажется слишком длинной - *таблица расписания будет отображаться некорректно!*"
        bot.send_message(message.from_user.id, text, reply_markup=markup, parse_mode='Markdown')

    if "LC3" in info["recent_command"]:
        markup  = telebot.types.ReplyKeyboardRemove()
        group = info["recent_command"].split("LC", 1)[1].split("LC1", 1)[0]
        weekString = info["recent_command"].split("LC", 1)[1].split("LC1", 1)[1].split("LC2", 1)[0]
        day = info["recent_command"].split("LC", 1)[1].split("LC1", 1)[1].split("LC2", 1)[1].split("LC3", 1)[0]
        number = info["recent_command"].split("LC", 1)[1].split("LC1", 1)[1].split("LC2", 1)[1].split("LC3", 1)[1]
        text = message.text
        if weekString == "Четная":
            week = 0
        if weekString == "Нечетная":
            week = 1
        if weekString == "Текущая":
            week = -1
        answer = json.loads(requests.get("http://localhost:8050/getshedule?command=addcomment&group=%s&fullname=%s&week=%d&day=%s&number=%s&text=%s" %(group, get_basic_name(info), week, day, number, text)).text)
        requests.get("http://localhost:8060/setuser?telegram_id=%d&recent_command=none" %message.from_user.id)
        lst = []
        lst.append(answer)
        shedule = get_full_shedule(lst, False)
        text = "*Результат выполнения команды*\n%s" %(shedule[0])
        bot.send_message(message.from_user.id, text, reply_markup=markup, parse_mode='Markdown')

bot.polling(none_stop=True, interval=0)