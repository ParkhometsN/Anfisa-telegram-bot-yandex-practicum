# :::'###::::'##::: ##:'########:'####::'######:::::'###::::
# ::'## ##::: ###:: ##: ##.....::. ##::'##... ##:::'## ##:::
# :'##:. ##:: ####: ##: ##:::::::: ##:: ##:::..:::'##:. ##::
# '##:::. ##: ## ## ##: ######:::: ##::. ######::'##:::. ##:
#  #########: ##. ####: ##...::::: ##:::..... ##: #########:
#  ##.... ##: ##:. ###: ##:::::::: ##::'##::: ##: ##.... ##:
#  ##:::: ##: ##::. ##: ##:::::::'####:. ######:: ##:::: ##:
# ..:::::..::..::::..::..::::::::....:::......:::..:::::..::
import telebot
import datetime as dt
import pyfiglet
import time
from bs4 import BeautifulSoup as bf
import datetime
import csv
import schedule
banner = pyfiglet.figlet_format("404",font='banner3-D')
bann = pyfiglet.figlet_format("anfisa",font='banner3-D')
print(bann)
print("[+] Бот работает")
bot = telebot.TeleBot('8387358592:AAGDbX4Q9fWOfsVo-curjh5D7YvavtrtgPE')


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, 'Бот находится в разработке и не выполняет базовые функции')


@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row_width = 1
    markup.row('/start', '/help')
    bot.send_animation(message.chat.id, 'https://i.giphy.com/26gsuUjoEBmLrNBxC.gif')
    bot.send_message(message.chat.id, text=f'\
                                    \nПривет {message.from_user.first_name}!\
                                    \n➖➖➖➖➖➖➖➖➖➖➖➖\
                                    \n Я виртуальный помощник Анфиса!\
                                    \n для начала можете спросить как у меня дела😈\
                                    \n➖➖➖➖➖➖➖➖➖➖➖➖', reply_markup=markup)


def create_calendar(year, month):
    markup = telebot.types.InlineKeyboardMarkup()
    days_in_month = (datetime.date(year, month + 1, 1) - datetime.date(year, month, 1)).days
    # Создание кнопок для каждого дня месяца
    buttons = [telebot.types.InlineKeyboardButton(str(day),row_width=5, callback_data=f'select_day_{day}_{month}',) for day in range(1, days_in_month + 1)]
    markup.add(*buttons)
    # Добавление кнопки "Проверить напоминания"
    check_reminders_button = telebot.types.InlineKeyboardButton('Проверить напоминания', callback_data='check_reminders')
    markup.add(check_reminders_button)
    return markup


@bot.message_handler(commands=['kalendar'])
def start_command(message):
    now = datetime.datetime.now()
    calendar = create_calendar(now.year, now.month)
    bot.send_message(message.chat.id, 'Выберите день:', reply_markup=calendar)


@bot.callback_query_handler(func=lambda call: call.data.startswith('select_day_'))
def select_day_callback(call):
    selected_day, selected_month = map(int, call.data.split('_')[2:])
    bot.send_message(call.message.chat.id, f'Вы выбрали день {selected_day}. Введите текст:')
    bot.register_next_step_handler(call.message, select_month, selected_day, selected_month)


def select_month(message, selected_day, selected_month):
    reminder_text = message.text
    months = {
        'Январь': 1,
        'Февраль': 2,
        'Март': 3,
        'Апрель': 4,
        'Май': 5,
        'Июнь': 6,
        'Июль': 7,
        'Август': 8,
        'Сентябрь': 9,
        'Октябрь': 10,
        'Ноябрь': 11,
        'Декабрь': 12
    }
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=4)
    buttons = [telebot.types.InlineKeyboardButton(text=month) for month in months]
    keyboard.add(*buttons)
    bot.send_message(message.chat.id, 'Выберете месяц для отправки напоминания:',
                    reply_markup=keyboard)
    bot.register_next_step_handler(message, select_time, selected_day, selected_month, months, reminder_text)


def select_time(message, selected_day, selected_month, months,reminder_text):
    try:
        selected_month = months[message.text]
        try:
            if selected_month > 0 and selected_month <= 12:
                keyboard = telebot.types.ReplyKeyboardRemove()
                bot.send_message(message.chat.id, 'Введите время (в формате HH:MM) для отправки напоминания:', reply_markup=keyboard)
                bot.register_next_step_handler(message, save_reminder, selected_day, selected_month, reminder_text)
            else:
                bot.send_message(message.chat.id, 'Неверный формат. Попробуйте еще раз.')
                bot.register_next_step_handler(message, select_month, selected_day, selected_month)
        except ValueError:
            bot.send_message(message.chat.id, 'Неверный формат. Попробуйте еще раз.')
            bot.register_next_step_handler(message, select_month, selected_day, selected_month)
    except KeyError:
        bot.send_message(message.chat.id, 'Неверный формат. Попробуйте еще раз.')
        bot.register_next_step_handler(message, select_month, selected_day, selected_month)
    except ValueError:
        bot.send_message(message.chat.id, 'Неверный формат. Попробуйте еще раз.')
        bot.register_next_step_handler(message, select_month, selected_day, selected_month)


def save_reminder(message, selected_day, selected_month, reminder_text):
    reminder_time = message.text
    with open('reminders.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([message.chat.id, message.from_user.first_name, selected_day, selected_month, reminder_time, reminder_text])
    # Запланировать отправку напоминания в выбранный день
    now = datetime.datetime.now()
    target_date = datetime.datetime(datetime.datetime.now().year, selected_month, selected_day)
    target_time = datetime.datetime.strptime(reminder_time, '%H:%M').time()
    target_datetime = datetime.datetime.combine(target_date, target_time)
    schedule.every().day.at(target_datetime.strftime('%H:%M')).do(send_reminder, message.chat.id, reminder_text)
    bot.send_message(message.chat.id, f'Напоминание на {selected_day} число {selected_month} месяца в {reminder_time}:\n\n{reminder_text}')
    while True:
        schedule.run_pending()
        time.sleep(1)
def send_reminder(chat_id, reminder_text):
    bot.send_message(chat_id, f'Напоминание:\n\n{reminder_text}')
@bot.callback_query_handler(func=lambda call: call.data == 'check_reminders')
def check_reminders_callback(call):
    reminders = get_future_reminders(call.message.chat.id)
    if reminders:
        reminders_text = '\n\n'.join(
            [f'{reminder.date.strftime("%d.%m.%Y")} в {reminder.time}: {reminder.text}' for reminder in reminders])
        bot.send_message(call.message.chat.id, f'Будущие напоминания:\n\n{reminders_text}')
    else:
        bot.send_message(call.message.chat.id, 'У вас пока нет будущих напоминаний')
def get_future_reminders(chat_id):
    now = datetime.datetime.now()
    reminders = []
    with open('reminders.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            user_id, user_name, day, month, time, text = row[0], row[1], int(row[2]), int(row[3]), row[4], row[5]
            target_date = datetime.datetime(datetime.datetime.now().year, int(month), int(day))
            target_time = datetime.datetime.strptime(time, '%H:%M')
            target_datetime = datetime.datetime.combine(target_date, target_time.time())
            if target_datetime > now and user_id == str(chat_id):
                reminders.append(Reminder(target_date, target_time, text))
    return reminders
class Reminder:
    def __init__(self, date, time, text):
        self.date = date
        self.time = time
        self.text = text
@bot.message_handler(func=lambda message: True)
def handle_question(message):
    try:
        if message.text:
            question = message.text.lower()
            if "погода в" in question:
                if 'питере' in question:
                    city = 'Cанкт-Петербург'
                    answer = f'В Санкт-Петербурге\n{get_weather(city)}'
                elif 'москве' in question:
                    city = 'Москва'
                    answer = f'В Москве\n{get_weather(city)}'
                elif 'краснодар' in question or 'армавире' in question or 'армавир' in question:
                    city = 'краснодар'
                    answer = f'В {message.text}\n{get_weather_krasnodar(message)}'
                else:
                    city = question.split()[-1]
                    answer = f'Я не знаю погоды в {city}'
            elif 'привет' in question or 'Привет' in question:
                answer = start(message)
            elif 'Календарь' in question or 'календарь' in question:
                return start_command(message)
            elif 'погода' in question or "Сказать погоду" in question:
                city = "Москва"
                answer = f'В Москве\
                \n {get_weather(city)}\
                \n Для выбора города просто спросите "Погода в ...'
            elif "время в" in question or "сколько время в" in question:
                if 'питере' == question.split()[2] or 'питере' == question.split()[1] or 'питере' == question.split()[0]:
                    city = 'Санкт-Петербург'
                    answer = f'{get_time(city)}'
                elif 'москве' == question.split()[2] or 'москве' == question.split()[1] or 'москве' == question.split()[0]:
                    city = 'Москва'
                    answer = get_time(city)
                else:
                    city = question.split()[2]
                    answer = get_time(city)
            elif "время" in question or "сколько время" in question:
                city = "Москва"
                answer = f'\
                    \n{get_time(city)}\
                \n Для выбора города просто \
                \nспросите "Время в ...'
            elif 'как дела' in question or 'как дела?' in question or 'как у тебя дела?' in question:
                bot.send_animation(message.chat.id, "https://i.giphy.com/media/dANWlKmK8q0lT7v9k1/giphy.mp4",)
                answer = f'Все отлично! Рассказать что я умею)?'
            elif 'да' in question or 'конечно' in question or 'Да' in question or 'Давай' in question:
                return yourself(message)
            elif 'как' in question or 'как делать' in question or 'как сделать' in question:
                ser = question
                url = 'https://www.youtube.com/results?search_query=' + '+'.join(ser.split(' '))
                answer = f'Вот что мне удалось найти в интернете {url}'
            elif 'таймер' in question:
                return set_timer(message)
            elif 'курс' in question:
                return money(message)
            elif 'что ты еще умеешь?' in question or 'что ты еще умеешь' in question:
                try:
                    return battun_for_skils(message)
                except telebot.apihelper.ApiTelegramException:
                    return bot.send_message(message.chat.id, text='ERROR 403')
            elif 'игра' in question:
                answer = bot.answer_callback_query(message.chat.id, text='В данный момент это не доступно')
            else:
                user_query = str(question)
                url = 'https://yandex.ru/search/?text=' + '%20'.join(user_query.split(' '))
                answer = f'Вот что мне удалось найти в интернете {url}'
            bot.reply_to(message, answer)
    except telebot.apihelper.ApiTelegramException:
        return bot.send_message(message.chat.id, text='402 недоступно')
@bot.message_handler(commands=['change_city'])
def change_city(message):
    global city
    city = message.text.split()[1]
    bot.send_message(message.chat.id, f'Город изменен на {city}')
UTC_OFFSET = {
    'Москва': 3,
    'Санкт-Петербург': 3,
    'новосибирск': 7,
    'Новосибирск': 7
}
def download(message):
    bot.answer_callback_query(message.chat.id, text=f'заргузка 🙄')
def answers_for_skils(call):
    try:
        if call.data == 'butt1':
            download(call.message)
            set_timer(call.message)
        elif call.data == 'butt2':
            try:
                return get_time(city)
            except NameError:
                return bot.answer_callback_query(call.id, text=f'кнопка не доступна, но можете написать "время"')
        elif call.data == 'butt3':
            try:
                return bot.send_message(call, text=f'{get_weather(city)}')
            except NameError:
                return bot.answer_callback_query(call.id, text=f'кнопка не доступна, но можете написать "погода"')
        elif call.data == 'butt4':
            return bot.answer_callback_query(call.id, text='В данный момент это не доступно')
        else:
            bot.answer_callback_query(call.id, text='Ошибка!')
    except telebot.apihelper.ApiTelegramException:
        return bot.send_message(call.message.chat.id, text='ERROR 400')
def get_time(city):
    if city in UTC_OFFSET:
        offset = UTC_OFFSET[city]
        city_time = dt.datetime.utcnow() + dt.timedelta(hours=offset)
        f_time = city_time.strftime("%H:%M")
        return f'В городе {city}\
            \n➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖\
            \nсейчас {f_time} ⏳'
    else:
        return f'К сожалению, я не знаю времени в городе {city}'

def yourself(message):
    bot.send_animation(message.chat.id,'https://i.giphy.com/media/n7IyB6qZOFFCgFGGkT/giphy.mp4')
    bot.send_message(message.chat.id, text="Вот что я могу:\
                                \n・ поставить таймер ⏱️\
                                \n・ рассказать про погоду 🌤️\
                                \n・ вести ваш календарь 🗓\
                                \n・ рассказать про настоящий курс 💲\
                                \n➤ Но если я чего - то не знаю, я обращусь к ресурсам в интернете ☺️\
                                            ")
    battun_for_skils(message)


import requests

def get_weather(city):
    url = f'http://wttr.in/{city}'
    weather_parameters = {
        'format': 2,
        'M': ''
    }
    request_headers = {
        'Accept-Language': 'ru'
    }
    try:
        response = requests.get(url, params=weather_parameters, headers=request_headers)
    except requests.ConnectionError:
        return '<сетевая ошибка>'
    if response.status_code == 200:
        return response.text
    else:
        return '<ошибка на сервере погоды>'

def get_weather_krasnodar(message):
    url = f'https://wttr.in/краснодар'
    weather_parameters = {
        'format': 2,
        'M': ''
    }
    request_headers = {
        'Accept-Language': 'ru'
    }
    try:
        response = requests.get(url, params=weather_parameters, headers=request_headers)
    except requests.ConnectionError:
        return '<сетевая ошибка>'
    if response.status_code == 200:
        return response.text
    else:
        return '<ошибка на сервере погоды>'
def set_timer(message):
    try:
        keyboard = telebot.types.InlineKeyboardMarkup()
        button_5sec = telebot.types.InlineKeyboardButton(text='5 сек', callback_data='5')
        button_5min = telebot.types.InlineKeyboardButton(text='5 мин', callback_data='300')
        button_10min = telebot.types.InlineKeyboardButton(text='10 мин', callback_data='600')
        button_30min = telebot.types.InlineKeyboardButton(text='30 мин', callback_data='1800')
        button_60min = telebot.types.InlineKeyboardButton(text='60 мин', callback_data='3600')
        keyboard.row(button_5sec)
        keyboard.row(button_5min, button_10min)
        keyboard.row(button_30min, button_60min)
        bot.send_message(message.chat.id, 'Выберите время:', reply_markup=keyboard)
    except telebot.apihelper.ApiTelegramException:
        return f'ERROR try one more later\
            \n {bann}'
stop_timer = False


def start_timer(duration, chat_id):
    global stop_timer
    keyboard = telebot.types.InlineKeyboardMarkup()
    button_stop = telebot.types.InlineKeyboardButton(text='Отмена ❌', callback_data='stop')
    keyboard.add(button_stop)
    message = bot.send_message(chat_id, text=f'Таймер на {duration // 60} минут {duration % 60} секунд установлен ✅', reply_markup=keyboard)
    for i in range(duration, 0, -1):
        if stop_timer:
            stop_timer = False
            bot.send_message(chat_id, text='Таймер отменен ❌')
            return
        bot.edit_message_text(chat_id=chat_id, message_id=message.message_id, text=f'Осталось {i // 60} минут {i % 60} секунд',reply_markup=keyboard)
        time.sleep(1)
    bot.send_animation(chat_id, 'https://i.giphy.com/media/4YXUhN0154lr6gNXpy/giphy.mp4')
    bot.send_message(chat_id, 'Время вышло!')

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    try:
        global stop_timer  # Объявляем, что используем глобальную переменную stop_timer
        if call.data == 'stop':
            stop_timer = True
        elif call.data.isdigit():
            duration = int(call.data)
            start_timer(duration, call.message.chat.id)
        else:
            return answers_for_skils(call) or bot.answer_callback_query(call.id, text='Ошибка! Пожалуйста, выберите время из предложенных вариантов')
    except telebot.apihelper.ApiTelegramException:
        return f'ERROR try one more later\n {bann}'
# def play(message):
#     bot.send_message(message.chat.id, "У вас есть 3 попытки правильно ответить")
#     import random
#     correct = 0
#     mistakes = 0
#     answered_messages = set()
#     while mistakes < 3:
#         a = random.randrange(1, 100)
#         b = random.randrange(1, 100)
#         answer = a + b
#         bot.send_message(message.chat.id, f"{a} + {b} = ")
#         answer_message = None
#         while answer_message is None:
#             updates = bot.get_updates()
#             for update in updates:
#                 if update.message and update.message.text and update.message.text not in answered_messages:
#                     answer_message = update.message
#                     answered_messages.add(answer_message.text)
#                     break
#         if answer_message:
#             user_answer = answer_message.text
#             if int(user_answer) == answer:
#                 correct += 1
#                 bot.send_message(message.chat.id, 'Правильно!')
#             else:
#                 mistakes += 1
#                 bot.send_message(message.chat.id, f'Не правильно! Правильный ответ - {answer}')
#         else:
#             bot.send_message(message.chat.id, 'Пожалуйста, введите ответ')
#     bot.send_message(message.chat.id, f'Игра окончена! Правильных ответов - {correct}, неправильных ответов - {mistakes}')
def money(message):
    try:
        loading_message = bot.send_message(message.chat.id, '⏳ Загрузка...')
        response = requests.get("http://www.finmarket.ru/currency/rates/")
        src = response.text
        soup = bf(src, "lxml")
        new_response = requests.get("https://technewsleader.com/predictions/ru/bitcoin-price-prediction-2023")
        new_src = new_response.text
        new_soup = bf(new_src, "lxml")
        bitcoin = new_soup.find("div", class_="price-set")
        try:
            usd_money = soup.find("div", class_='value')
            USD_print = soup.find("div", class_='change red')
            if float(USD_print.text.replace(',', '.')) < 0:
                smile1 = "💵"
            else:
                smile1 = '💵'
            euro_money = soup.find("div", class_='fintool_button', id="ft_52170").find(class_="value")
            euro_print = soup.find("div", class_='fintool_button', id="ft_52170").find(class_="change red")
            if float(euro_print.text.replace(',', '.')) < 0:
                smile = "💶"
            else:
                smile = '💶'
            bot.edit_message_text(chat_id=loading_message.chat.id, message_id=loading_message.id,
                                text=f'💵USD - {usd_money.text}, {USD_print.text}{smile1}\
                                                    \n➖➖➖➖➖➖➖➖➖➖➖➖\
                                                    \n💶EUR - {euro_money.text}, {euro_print.text}{smile}\
                                                    \n➖➖➖➖➖➖➖➖➖➖➖➖\
                                                    \n🌐BITCOIN    {bitcoin.text}')
        except AttributeError:
            usd_money = soup.find("div", class_='value')
            USD_print = soup.find("div", class_='change green')
            if float(USD_print.text.replace(',', '.')) < 0:
                smile1 = "📈"
            else:
                smile1 = '📉'
            euro_money = soup.find("div", class_='fintool_button', id="ft_52170").find(class_="value")
            euro_print = soup.find("div", class_='fintool_button', id="ft_52170").find(class_="change green")
            if float(euro_print.text.replace(',', '.')) < 0:
                smile = "📈"
            else:
                smile = '📉'
            bot.edit_message_text(chat_id=loading_message.chat.id, message_id=loading_message.id,
                                text=f'💵USD - {usd_money.text}, {USD_print.text}{smile1}\
                                                    \n➖➖➖➖➖➖➖➖➖➖➖➖\
                                                    \n💶EUR - {euro_money.text}, {euro_print.text}{smile}\
                                                    \n➖➖➖➖➖➖➖➖➖➖➖➖\
                                                    \n🌐BITCOIN    {bitcoin.text}')
    except requests.ConnectionError:
        bot.send_message(message.chat.id, text=f'Error 404 is not definded')


def battun_for_skils(message):
    try:
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        butt1 = telebot.types.InlineKeyboardButton(text='Таймер', callback_data='butt1')
        butt3 = telebot.types.InlineKeyboardButton(text='Погода', callback_data='butt3')
        butt4 = telebot.types.InlineKeyboardButton(text='Курс', callback_data='butt4')
        butt5 = telebot.types.InlineKeyboardButton(text='Календарь', callback_data='butt5')
        keyboard.add(butt1, butt3, butt4, butt5)
        bot.send_message(message.chat.id, f'Вот что я пока умею:', reply_markup=keyboard)
    except telebot.apihelper.ApiTelegramException:
        return bot.send_message(message.chat.id, text='ERROR 401')

bot.polling()

