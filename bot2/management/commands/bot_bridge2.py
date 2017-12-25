#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from django.shortcuts import get_object_or_404
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
import telepot
import emoji
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup
from ... import models


class Command(BaseCommand):
    def handle(self, *args, **options):
        def on_chat_message(msg):
            # Get User data From User RealTime
            content_type, chat_type, chat_id = telepot.glance(msg)
            try:
                username = msg['from']['username']
            except ValueError:
                username = "Null"

            if content_type == "text":
                command = msg['text'].encode('utf-8')
            elif content_type == 'contact':
                command = msg['contact']['phone_number']
            else:
                command = 'Null'

            if not check_user_is(telegram_id=chat_id):
                add_user(telegram_id=chat_id, username=username)

            if type(return_user_state(chat_id)) is not None:
                user_state = return_user_state(chat_id)
            else:
                user_state = "Null"
                # End Of Get Data From User

            if user_state == "start":
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(
                            text=emoji.emojize(":closed_lock_with_key:", use_aliases=True),
                            callback_data='Question&1'), ],
                    ])
                bot.sendMessage(chat_id=chat_id, text=" سوالات را نمایش بده! ", reply_markup=keyboard)

        def on_callback_query(msg):
            query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
            state = return_user_state(from_id)
            try:
                username = msg['from']['username']
            except ValueError:
                username = "Null"

            if check_user_is(telegram_id=from_id):
                requested_query = query_data.split("&")
                if requested_query[0] == "Question":
                    q_num = int(requested_query[1])
                    q_text = get_question(q_num)
                    choices_keyboard = get_question_choices_keyboard(q_num)
                    bot.sendMessage(chat_id=from_id, text=q_text.text, reply_markup=choices_keyboard)
                    set_state(telegram_id=from_id, state_word="Answer&%s" % q_num)
                elif requested_query[0] == "Choice":
                    q_num_state = state.split("&")[1]
                    if "Answer" in state and requested_query[1] == q_num_state:
                        q_num = int(requested_query[1])
                        selected_choice = int(requested_query[2])
                        keyboard = InlineKeyboardMarkup(
                            inline_keyboard=[
                                [InlineKeyboardButton(
                                    text=emoji.emojize(":closed_lock_with_key:", use_aliases=True),
                                    callback_data='Question&%d' % (int(q_num) + 1)), ],
                            ])
                        if is_correct_answer(q_num=q_num, selected_choice=selected_choice):
                            current_score = get_current_score(telegram_id=from_id)
                            current_score += 1;
                            update_user_score(telegram_id=from_id, score=current_score)
                            bot.sendMessage(chat_id=from_id, text="Correct!", reply_markup=keyboard)
                        else:
                            bot.sendMessage(chat_id=from_id, text="Try Again!", reply_markup=keyboard)

                        set_state(telegram_id=from_id, state_word="Question&%d" % (int(q_num) + 1))
                    else:
                        bot.sendMessage(chat_id=from_id, text="You Can Not Answer to this Question!", reply_markup=None)

            else:
                add_user(telegram_id=from_id, username=username)

        bot = telepot.Bot('533976032:AAH2-D_PkkXuO65_ZTN0j3hYZs1LsyJYWlA')

        bot.message_loop({'chat': on_chat_message, 'callback_query': on_callback_query})
        print('I am listening ...')
        while 1:
            time.sleep(10)


def return_user_id(chat_id):
    try:
        user = models.UserQ.objects.get(telegram_id=chat_id)
        return user.id
    except ObjectDoesNotExist:
        user = None
        return user


def return_user_telegram_id(user_id):
    try:
        user = models.UserQ.objects.get(pk=user_id)
        return user.telegram_id
    except ObjectDoesNotExist:
        user = None
        return user


def update_user(telegram_id, username):
    try:
        entry = models.UserQ.objects.get(username=username)
        entry.telegram_id = telegram_id
        entry.time_left = str(int(time.time()))
        entry.save()
        return True
    except Exception as e:
        print
        e
        return False


def check_user_is(telegram_id):
    try:
        user = get_object_or_404(models.UserQ, telegram_id=telegram_id)
        return 1
    except Exception as e:
        print(e)
        return 0


def return_user_state(telegram_id):
    try:
        state = models.UserQ.objects.get(telegram_id=telegram_id)
        return state.state
    except ObjectDoesNotExist:
        state = None
        return state


def set_state(telegram_id, state_word):
    try:

        state = models.UserQ.objects.get(telegram_id=telegram_id)
        state.state = state_word
        state.save()
        return True
    except Exception as e:
        print(e)
        return False


def add_user(telegram_id, username):
    try:
        user = models.UserQ(telegram_id=telegram_id, username=username)
        user.save()
        return 1
    except Exception as e:
        print(e)
        return 0


def get_question(q_num):
    try:
        question = models.Question.objects.get(number=q_num)
        return question
    except ObjectDoesNotExist:
        return None


def get_choice(question):
    try:
        choice = models.Choices.objects.get(question=question)
        return choice
    except ObjectDoesNotExist:
        return None


def get_question_choices_keyboard(q_num):
    try:
        question = get_question(q_num)
        choices = models.Choices.objects.filter(question=question)
        all_choices = []
        for choice in choices:
            one_choice = []
            one_choice.append(
                InlineKeyboardButton(text=choice.text, callback_data="Choice&%s&%s" % (q_num, choice.number)))
            all_choices.append(one_choice)
        return InlineKeyboardMarkup(inline_keyboard=all_choices)
    except ObjectDoesNotExist:
        return None


def is_correct_answer(q_num, selected_choice):
    choice = models.Choices.objects.get(number=selected_choice)
    if choice.correct_for_question == q_num:
        return 1
    else:
        return 0


def get_current_score(telegram_id):
    try:
        user = models.UserQ.objects.get(telegram_id=telegram_id)
        return user.score
    except ObjectDoesNotExist:
        return None


def update_user_score(telegram_id, score):
    try:
        entry = models.UserQ.objects.get(telegram_id=telegram_id)
        entry.score = score
        entry.save()
        return True
    except Exception as e:
        print(e)
        return False
