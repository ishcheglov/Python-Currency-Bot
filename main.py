import os
import telebot
from dotenv import load_dotenv, find_dotenv
from currency_converter import CurrencyConverter
from telebot import types

"""
Телеграмм бот с функцией конвертации валюты на основе currency_converter. Отработаны исключения, когда пользователь
вводит строку, отрицательные числа. Кнопки работают USD/EUR, EUR/USD, USD/GBP,есть кнопка с выбором валют. BOT_TOKEN 
засекречен с помощью библиотеки dotenv. Команда /start запуск конвертeра, команда /help дополнительная информация 
при запуске в начале и по рекомендации внутри программы. 
"""

if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
commands = ["start", "help"]

bot = telebot.TeleBot(BOT_TOKEN)
currency = CurrencyConverter()
amount = 0


@bot.message_handler(commands=["start"])
def start(message):  # Стартовая функция
    video = "currency_klip.mp4"
    file = open(f"video/{video}", "rb")
    bot.send_video(message.chat.id, file)

    bot.send_message(message.chat.id, f"<b><i> 👋 Привет, я чат бот, который может "
                                      f"конвертировать валюту.</i></b>", parse_mode="HTML")
    bot.send_message(message.chat.id, f"<b><i> Введите сумму.</i></b>", parse_mode="HTML")
    bot.send_message(message.chat.id, f"<b><i> После введения суммы и до конвертации валют "
                                      f"можете получить дополнительную информацию:  "
                                      f"/{commands[1]}.</i></b>", parse_mode="HTML")

    bot.register_next_step_handler(message, add_summa)


@bot.message_handler(commands=["help"])
def my_help(message):  # Информационная функция
    bot.send_message(message.chat.id, f"<b><i> Чат бот, который может конвертировать валюту.</i></b> \n\n"
                                      f"Для начала работы нужно ввести команду /{commands[0]}.\n"
                                      f"Появится приветственное сообщение и рекомендация ввести сумму.\n"
                                      f"Сумма должна быть числом больше нуля. \n"
                                      f"Становятся доступны кнопки выбора пары для конвертации валюты.\n"
                                      f"Есть варианты выбора или создать свою пару.\n"
                                      f"Получаем результат расчетов с точностью до 2 знаков после запятой.\n"
                                      f"Есть возможность повторного расчета при введении "
                                      f"новой суммы.", parse_mode="HTML")


def add_summa(message):  # Функция добавляет и обрабатывает данные пользователя.
    global amount
    try:
        amount = int(message.text.strip())

    except ValueError:
        bot.send_message(message.chat.id, "🆘 Неверный формат. Введите сумму")
        bot.register_next_step_handler(message, add_summa)

    if amount < 0 and amount != str:
        bot.send_message(message.chat.id, "🆘 Число должно быть больше нуля. Введите сумму")
        bot.register_next_step_handler(message, add_summa)

    elif amount > 0 and amount != str:
        marcup = types.InlineKeyboardMarkup(row_width=2)
        button1 = types.InlineKeyboardButton("USD/EUR", callback_data="usd/eur")
        button2 = types.InlineKeyboardButton("EUR/USD", callback_data="eur/usd")
        button3 = types.InlineKeyboardButton("USD/GBP", callback_data="usd/gbp")
        button4 = types.InlineKeyboardButton("Выбор валют", callback_data="if")
        marcup.add(button1, button2, button3, button4)
        bot.send_message(message.chat.id, f"<b><i> 👌 Выберите пару валют."
                                          f"</i></b>", reply_markup=marcup, parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: True)
def callback(call):  # Функция обрабатывает кнопку выбора пары валют.
    if call.data != "if":
        values = call.data.upper().split("/")
        result = currency.convert(amount, values[0], values[1])
        bot.send_message(call.message.chat.id, f"✅ {values[0]} >>> {values[1]}: {round(result, 2)}\n"
                                               f"Можете снова ввести сумму")
        bot.register_next_step_handler(call.message, add_summa)

    else:
        bot.send_message(call.message.chat.id, "Введите пару валют через слэш")
        bot.register_next_step_handler(call.message, my_values)


def my_values(message):  # Функция результата расчета конвертации валют.
    try:
        values = message.text.upper().split("/")
        result = currency.convert(amount, values[0], values[1])
        bot.send_message(message.chat.id, f"✅ {values[0]} >>> {values[1]}: {round(result, 2)}\n"
                                          f"Можете снова ввести сумму")
        bot.register_next_step_handler(message, add_summa)
    except Exception:
        bot.send_message(message.chat.id, "🆘 Неверный формат. Введите пару валют снова")
        bot.register_next_step_handler(message, my_values)


bot.polling(non_stop=True)
