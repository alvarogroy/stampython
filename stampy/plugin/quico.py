#!/usr/bin/env python
# encoding: utf-8
#
# Description: Plugin for processing Quico Jubilata strip requests
# Author: Pablo Iranzo Gomez (Pablo.Iranzo@gmail.com)

import datetime
import logging

import dateutil.parser
import requests
from lxml import html
from apscheduler.schedulers.background import BackgroundScheduler

import stampy.stampy
import stampy.plugin.stats
import stampy.plugin.config

sched = BackgroundScheduler()
sched.start()


def init():
    """
    Initializes module
    :return:
    """

    sched.add_job(quico, 'cron', id='quico', hour='10',
                  replace_existing=True)

    return


def run(message):  # do not edit this line
    """
    Executes plugin
    :param message: message to run against
    :return:
    """
    text = stampy.stampy.getmsgdetail(message)["text"]
    if text:
        if text.split()[0].lower() == "/quico":
            quicocommands(message=message)
        if stampy.plugin.config.config(key='owner') == stampy.stampy.getmsgdetail(message)["who_un"]:
            if text.split()[0].lower() == "triggerquico":
                quico()
    return


def help(message):  # do not edit this line
    """
    Returns help for plugin
    :param message: message to process
    :return: help text
    """
    commandtext = "Use `/quico <date>` to get Quico Jubilata's comic "
    commandtext += "strip for date or today (@quicostrip)\n\n"
    return commandtext


def quicocommands(message):
    """
    Searches for commands related to quico
    :param message: message to process
    :return:
    """

    logger = logging.getLogger(__name__)

    msgdetail = stampy.stampy.getmsgdetail(message)

    texto = msgdetail["text"]
    chat_id = msgdetail["chat_id"]
    message_id = msgdetail["message_id"]
    who_un = msgdetail["who_un"]

    logger.debug(msg="Command: %s by %s" % (texto, who_un))

    # We might be have been given no command, just /quico
    try:
        date = texto.split(' ')[1]
    except:
        date = ""

    try:
        # Parse date or if in error, use today
        date = dateutil.parser.parse(date)

        # Force checking if valid date
        day = date.day
        month = date.month
        year = date.year
        date = datetime.datetime(year=year, month=month, day=day)
    except:
        date = datetime.datetime.now()

    return quico(chat_id=chat_id, date=date, reply_to_message_id=message_id)


def quico(chat_id=-1001093624011, date=None, reply_to_message_id=""):
    """
    Sends quico strip for the date provided
    :param chat_id: chat to send image to
    :param date: date to get the strip from that day
    :param reply_to_message_id: Id of the message to send reply to
    :return:
    """
    # http://www.quicojubilata.com/quico-jubilata/2017-01-12

    logger = logging.getLogger(__name__)

    if not date:
        date = datetime.datetime.now()

    url = "http://www.quicojubilata.com/quico-jubilata/%s-%02d-%02d" % (date.year, date.month, date.day)

    # Ping chat ID to not have chat removed
    stampy.plugin.stats.pingchat(chat_id)

    logger.debug(msg="quico comic found")

    page = requests.get(url)
    tree = html.fromstring(page.content)

    try:
        imgsrc = "http://www.quicojubilata.com" + tree.xpath('//img[@class="img-responsive"]/@src')[0]
        imgtxt = tree.xpath('//h1[@class="js-quickedit-page-title page-header"]/span')[0].text + "\n" + url + " - @quicostrip"
        return stampy.stampy.sendimage(chat_id=chat_id, image=imgsrc, text=imgtxt, reply_to_message_id=reply_to_message_id)
    except:
        logger.debug(msg="No comic found yet")
        return
