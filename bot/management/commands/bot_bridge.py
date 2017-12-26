#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from django.shortcuts import get_object_or_404
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
import telepot
import emoji
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from ... import models


class Command(BaseCommand):
    def handle(self, *args, **options):
        def on_chat_message(msg):
            # Get User data From User RealTime
            content_type, chat_type, chat_id = telepot.glance(msg)
            print(msg)
            try:
                username = msg['from']['username']
            except ValueError:
                username = "Null"

            if content_type == "text":
                command = msg['text'].encode('utf-8')
            elif content_type == 'contact':
                command = msg['contact']['phone_number']
                update_user_phone(telegram_id=chat_id, phone=command)
                bot.sendMessage(chat_id=chat_id, text="ممنون باهات تماس خواهم گرفت. ", reply_markup=None)
            else:
                command = 'Null'

            if type(return_user_state(chat_id)) is not None:
                user_state = return_user_state(chat_id)
            else:
                user_state = "Null"
                # End Of Get Data From User
            if not check_user_is(telegram_id=chat_id):
                add_user(telegram_id=chat_id, username=username)
            if (user_state == "start" or command == "/start") or (
                        user_state != "lock_level_1" and user_state != "lock_level_2" and user_state != "final"):
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(
                            text=emoji.emojize(":closed_lock_with_key:", use_aliases=True),
                            callback_data='lock_level_1'), ],
                    ])
                bot.sendMessage(chat_id=chat_id, text="سلام، خوش اومدی.می‌خوام معمایی رو برات مطرح کنم با حل این معما و فرستادن جواب درست برای من به مرحله بعد خواهی رفت. موفق باشی.راستی برای اینکه بتونی معما رو حل کنی با غرفه دانشگاه علم و صنعت رو خوب نگاه کنی.", reply_markup=keyboard)
            elif user_state == "lock_level_1":
                if command == "گره تبدیل":
                    bot.sendMessage(chat_id=chat_id, text=" عالیه. جواب درست بود حالا به این فایل صوتی که برات فرستادم دقت کن و رمزشو کشف کن و برای من بفرست تا به مرحله بعد راهنماییت کنم. ", reply_markup=None)
                    bot.sendAudio(chat_id=chat_id, audio=open('/var/harekatmellibot/bot/management/commands/morse.wav', 'r'), caption="Morse Me !!!")
                    set_state(telegram_id=chat_id, state_word="lock_level_2")
                else:
                    bot.sendMessage(chat_id=chat_id, text=" متاسفانه درست نیست، یکبار دیگه تلاش کن. ", reply_markup=None)

            elif user_state == "lock_level_2":
                if command.lower() == "CSSA":
                    bot.sendMessage(chat_id=chat_id, text=" خیلی خوب، حالا مرحله نهایی. ", reply_markup=None)
                    bot.sendMessage(chat_id=chat_id, text=" از این عدد باید استفاده کنی: ۹۴۲ ", reply_markup=None)
                    set_state(telegram_id=chat_id, state_word='final')
                    contact_keyboard = KeyboardButton(text='اشنراک شماره', resize=True,
                                                      request_contact=True)  # creating contact button object
                    custom_keyboard = [[contact_keyboard]]
                    reply_markup = ReplyKeyboardMarkup(keyboard=custom_keyboard)
                    bot.sendMessage(chat_id=chat_id, text=" شماره تلفنت رو هم برای من بفرست که بتونم باهات در تماس باشم فقط هم از طریق دکمه زیر شماره تلفن خودت رو با من به اشتراک بزار. ", reply_markup=reply_markup)
                else:
                    bot.sendMessage(chat_id=chat_id, text=" متاسفانه درست نیست، یکبار دیگه تلاش کن. ", reply_markup=None)

        def on_callback_query(msg):
            query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
            state = return_user_state(from_id)
            try:
                username = msg['from']['username']
            except ValueError:
                username = "Null"

            if check_user_is(telegram_id=from_id):
                if query_data == u'lock_level_1':
                    print state
                    if state == 'start':
                        set_state(telegram_id=from_id, state_word='lock_level_1')
                        bot.sendMessage(chat_id=from_id, text="در گذر حرکت از کدام نقوش هندسی در طراحی آن استفاده شد؟", reply_markup=None)
                    elif state == "final":
                        bot.sendMessage(chat_id=from_id, text="شما یک بار در بازی شرکت کرده‌اید.",
                                        reply_markup=None)


            else:
                add_user(telegram_id=from_id, username=username)

        bot = telepot.Bot('512062013:AAHw_M952tN3QZNmxG9F_niAaeuJdir8MxY')

        bot.message_loop({'chat': on_chat_message, 'callback_query': on_callback_query})
        print('I am listening ...')
        while 1:
            time.sleep(10)


def return_user_id(chat_id):
    try:
        user = models.User.objects.get(telegram_id=chat_id)
        return user.id
    except ObjectDoesNotExist:
        user = None
        return user


def return_user_telegram_id(user_id):
    try:
        user = models.User.objects.get(pk=user_id)
        return user.telegram_id
    except ObjectDoesNotExist:
        user = None
        return user


def check_user_is(telegram_id):
    try:
        user = get_object_or_404(models.User, telegram_id=telegram_id)
        return 1
    except Exception as e:
        print(e)
        return 0


def return_user_state(telegram_id):
    try:
        state = models.User.objects.get(telegram_id=telegram_id)
        return state.state
    except ObjectDoesNotExist:
        state = None
        return state


def set_state(telegram_id, state_word):
    try:

        state = models.User.objects.get(telegram_id=telegram_id)
        state.state = state_word
        state.save()
        return True
    except Exception as e:
        print(e)
        return False


def add_user(telegram_id, username):
    try:
        user = models.User(telegram_id=telegram_id, username=username)
        user.save()
        return 1
    except Exception as e:
        print(e)
        return 0


def update_user_phone(telegram_id, phone):
    try:
        entry = models.User.objects.get(telegram_id=telegram_id)
        entry.phone = phone
        entry.save()
        return True
    except Exception as e:
        print(e)
        return False
