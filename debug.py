#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import sys
from threading import Event, Thread

from utils import configure_logging
from config import Config
from db import Database

from models import Quote, Fund
from datetime import datetime


from funds.ar import AR
from funds.cgd import CGD

log = logging.getLogger()


class App(Thread):

    __interrupt = Event()

    @staticmethod
    def interrupt():
        return App.__interrupt

    def __init__(self):
        Thread.__init__(self, name='main', daemon=False)
        self.args = Config.get_args()
        self.db = Database.get_db()

    def run(self):
        try:
            self.work()
        except (KeyboardInterrupt, SystemExit):
            log.info('Interrupted application.')
            pass
        except Exception as e:
            log.exception(e)
        finally:
            self.stop()

        sys.exit(0)

    def work(self):
        log.debug('Startup')
        debug()

    def stop(self):
        log.debug('Shutdown')


if __name__ == '__main__':
    args = Config.get_args()
    configure_logging(log, args.verbose, args.log_path, "-debug-fund-quotes")

    app = App()
    app.start()


def update_db(fund, date, value, created):
    quote = Quote.get_or_none(
        Quote.fund == fund,
        Quote.date == date,
    )

    if quote and quote.value == value:
        log.debug(f'Quote for {fund} on {date} already exists.')
        return

    if not quote:
        quote = Quote.create(fund=fund, date=date, value=value, modified=created)
        log.debug(f'Quote for {fund} on {date}: {quote.value}')
        return quote

    quote.value = value
    quote.modified = created
    quote.save()
    log.debug(f'Updated quote for {fund} on {date}: {quote.value}')
    return quote


def debug():
    Quote.database().connect()
    latest_quote = Quote.get_latest(fund=29)
    latest_quote.date
    Quote.database().close()


def import_db():
    Quote.database().connect()

    lines = [
        '1,1,4.7642,"2023-12-04","2023-12-04 03:57:46"',
        '2,2,4.9696,"2023-12-04","2023-12-04 03:57:47"',
        '3,3,5.1122,"2023-12-04","2023-12-04 03:57:47"',
        '4,4,4.5391,"2023-12-04","2023-12-04 03:57:48"',
        '5,5,5.7421,"2023-12-04","2023-12-04 03:57:48"',
        '6,6,10.5837,"2023-12-04","2023-12-04 03:57:48"',
        '7,7,5.0395,"2023-12-04","2023-12-04 03:57:49"',
        '8,8,5.0649,"2023-12-04","2023-12-04 03:57:49"',
        '9,9,5.0954,"2023-12-04","2023-12-04 03:57:49"',
        '10,10,5.0849,"2023-12-04","2023-12-04 03:57:50"',
        '11,11,5.0795,"2023-12-04","2023-12-04 03:57:50"',
        '12,12,4.8924,"2023-12-04","2023-12-04 03:57:51"',
        '13,13,7.4095,"2023-12-04","2023-12-04 03:57:51"',
        '14,14,5.6654,"2023-12-04","2023-12-04 03:57:51"',
        '15,15,5.5868,"2023-12-04","2023-12-04 03:57:52"',
        '16,16,12.2954,"2023-12-04","2023-12-04 03:57:52"',
        '17,17,14.836,"2023-12-04","2023-12-04 03:57:53"',
        '18,18,8.556,"2023-12-04","2023-12-04 03:57:53"',
        '19,19,8.7262,"2023-12-04","2023-12-04 03:57:53"',
        '20,20,13.0418,"2023-12-04","2023-12-04 03:57:54"',
        '21,21,12.0775,"2023-12-04","2023-12-04 03:57:54"',
        '22,22,5.3195,"2023-12-04","2023-12-04 03:57:55"',
        '23,23,6.4563,"2023-12-04","2023-12-04 03:57:55"',
        '24,24,5.9038,"2023-12-04","2023-12-04 03:57:55"',
        '25,25,13.3288,"2023-12-04","2023-12-04 03:57:56"',
        '26,26,6.5335,"2023-12-04","2023-12-04 03:57:56"',
        '27,27,5.2764,"2023-12-04","2023-12-04 03:57:57"',
        '28,28,8.4163,"2023-12-04","2023-12-04 03:57:57"',
        '29,1,4.7641,"2023-12-04","2023-12-04 14:33:15"',
        '30,2,4.9693,"2023-12-04","2023-12-04 14:33:15"',
        '31,3,5.1115,"2023-12-04","2023-12-04 14:33:15"',
        '32,4,4.5404,"2023-12-04","2023-12-04 14:33:15"',
        '33,5,5.7433,"2023-12-04","2023-12-04 14:33:15"',
        '34,6,10.5837,"2023-12-04","2023-12-04 14:33:16"',
        '35,7,5.0399,"2023-12-04","2023-12-04 14:33:16"',
        '36,8,5.0653,"2023-12-04","2023-12-04 14:33:16"',
        '37,9,5.0957,"2023-12-04","2023-12-04 14:33:16"',
        '38,10,5.0853,"2023-12-04","2023-12-04 14:33:16"',
        '39,11,5.0805,"2023-12-04","2023-12-04 14:33:17"',
        '40,12,4.8922,"2023-12-04","2023-12-04 14:33:17"',
        '41,13,7.4088,"2023-12-04","2023-12-04 14:33:17"',
        '42,14,5.6647,"2023-12-04","2023-12-04 14:33:17"',
        '43,15,5.5869,"2023-12-04","2023-12-04 14:33:17"',
        '44,16,12.2929,"2023-12-04","2023-12-04 14:33:18"',
        '45,17,14.8334,"2023-12-04","2023-12-04 14:33:18"',
        '46,18,8.5548,"2023-12-04","2023-12-04 14:33:18"',
        '47,19,8.725,"2023-12-04","2023-12-04 14:33:19"',
        '48,20,13.0398,"2023-12-04","2023-12-04 14:33:19"',
        '49,21,12.0751,"2023-12-04","2023-12-04 14:33:19"',
        '50,22,5.3202,"2023-12-04","2023-12-04 14:33:20"',
        '51,23,6.4573,"2023-12-04","2023-12-04 14:33:20"',
        '52,24,5.9046,"2023-12-04","2023-12-04 14:33:20"',
        '53,25,13.3326,"2023-12-04","2023-12-04 14:33:20"',
        '54,26,6.5328,"2023-12-04","2023-12-04 14:33:20"',
        '55,27,5.277,"2023-12-04","2023-12-04 14:33:21"',
        '56,28,8.4163,"2023-12-04","2023-12-04 14:33:21"',
        '57,1,4.7641,"2023-12-05","2023-12-05 03:58:46"',
        '58,2,4.9693,"2023-12-05","2023-12-05 03:58:47"',
        '59,3,5.1115,"2023-12-05","2023-12-05 03:58:47"',
        '60,4,4.5404,"2023-12-05","2023-12-05 03:58:47"',
        '61,5,5.7433,"2023-12-05","2023-12-05 03:58:47"',
        '62,6,10.5837,"2023-12-05","2023-12-05 03:58:47"',
        '63,7,5.0399,"2023-12-05","2023-12-05 03:58:48"',
        '64,8,5.0653,"2023-12-05","2023-12-05 03:58:48"',
        '65,9,5.0957,"2023-12-05","2023-12-05 03:58:48"',
        '66,10,5.0853,"2023-12-05","2023-12-05 03:58:48"',
        '67,11,5.0805,"2023-12-05","2023-12-05 03:58:48"',
        '68,12,4.8922,"2023-12-05","2023-12-05 03:58:49"',
        '69,13,7.4088,"2023-12-05","2023-12-05 03:58:49"',
        '70,14,5.6647,"2023-12-05","2023-12-05 03:58:49"',
        '71,15,5.5869,"2023-12-05","2023-12-05 03:58:49"',
        '72,16,12.2929,"2023-12-05","2023-12-05 03:58:49"',
        '73,17,14.8334,"2023-12-05","2023-12-05 03:58:50"',
        '74,18,8.5548,"2023-12-05","2023-12-05 03:58:50"',
        '75,19,8.725,"2023-12-05","2023-12-05 03:58:50"',
        '76,20,13.0398,"2023-12-05","2023-12-05 03:58:50"',
        '77,21,12.0751,"2023-12-05","2023-12-05 03:58:50"',
        '78,22,5.3202,"2023-12-05","2023-12-05 03:58:51"',
        '79,23,6.4573,"2023-12-05","2023-12-05 03:58:51"',
        '80,24,5.9046,"2023-12-05","2023-12-05 03:58:51"',
        '81,25,13.3326,"2023-12-05","2023-12-05 03:58:51"',
        '82,26,6.5328,"2023-12-05","2023-12-05 03:58:51"',
        '83,27,5.277,"2023-12-05","2023-12-05 03:58:52"',
        '84,28,8.4176,"2023-12-05","2023-12-05 03:58:52"',
        '85,1,4.7834,"2023-12-05","2023-12-05 14:28:30"',
        '86,2,4.9937,"2023-12-05","2023-12-05 14:28:30"',
        '87,3,5.1402,"2023-12-05","2023-12-05 14:28:30"',
        '88,4,4.5485,"2023-12-05","2023-12-05 14:28:30"',
        '89,5,5.7649,"2023-12-05","2023-12-05 14:28:31"',
        '90,6,10.6684,"2023-12-05","2023-12-05 14:28:31"',
        '91,7,5.0532,"2023-12-05","2023-12-05 14:28:31"',
        '92,8,5.0805,"2023-12-05","2023-12-05 14:28:31"',
        '93,9,5.1131,"2023-12-05","2023-12-05 14:28:32"',
        '94,10,5.1029,"2023-12-05","2023-12-05 14:28:32"',
        '95,11,5.0985,"2023-12-05","2023-12-05 14:28:32"',
        '96,12,4.9128,"2023-12-05","2023-12-05 14:28:32"',
        '97,13,7.4456,"2023-12-05","2023-12-05 14:28:32"',
        '98,14,5.697,"2023-12-05","2023-12-05 14:28:33"',
        '99,15,5.6309,"2023-12-05","2023-12-05 14:28:33"',
        '100,16,12.5184,"2023-12-05","2023-12-05 14:28:33"',
        '101,17,15.0163,"2023-12-05","2023-12-05 14:28:33"',
        '102,18,8.647,"2023-12-05","2023-12-05 14:28:33"',
        '103,19,8.7814,"2023-12-05","2023-12-05 14:28:34"',
        '104,20,13.1455,"2023-12-05","2023-12-05 14:28:34"',
        '105,21,12.1989,"2023-12-05","2023-12-05 14:28:34"',
        '106,22,5.3296,"2023-12-05","2023-12-05 14:28:34"',
        '107,23,6.4936,"2023-12-05","2023-12-05 14:28:35"',
        '108,24,5.9142,"2023-12-05","2023-12-05 14:28:35"',
        '109,25,13.3905,"2023-12-05","2023-12-05 14:28:35"',
        '110,26,6.5625,"2023-12-05","2023-12-05 14:28:35"',
        '111,27,5.3093,"2023-12-05","2023-12-05 14:28:35"',
        '112,28,8.4176,"2023-12-05","2023-12-05 14:28:36"',
        '113,1,4.7955,"2023-12-06","2023-12-06 13:40:59"',
        '114,2,5.0094,"2023-12-06","2023-12-06 13:41:00"',
        '115,3,5.1596,"2023-12-06","2023-12-06 13:41:00"',
        '116,4,4.5526,"2023-12-06","2023-12-06 13:41:00"',
        '117,5,5.7759,"2023-12-06","2023-12-06 13:41:00"',
        '118,6,10.7722,"2023-12-06","2023-12-06 13:41:00"',
        '119,7,5.06,"2023-12-06","2023-12-06 13:41:01"',
        '120,8,5.088,"2023-12-06","2023-12-06 13:41:01"',
        '121,9,5.1218,"2023-12-06","2023-12-06 13:41:01"',
        '122,10,5.1119,"2023-12-06","2023-12-06 13:41:01"',
        '123,11,5.1075,"2023-12-06","2023-12-06 13:41:01"',
        '124,12,4.9248,"2023-12-06","2023-12-06 13:41:02"',
        '125,13,7.4688,"2023-12-06","2023-12-06 13:41:02"',
        '126,14,5.7189,"2023-12-06","2023-12-06 13:41:02"',
        '127,15,5.6601,"2023-12-06","2023-12-06 13:41:02"',
        '128,16,12.5724,"2023-12-06","2023-12-06 13:41:02"',
        '129,17,15.0789,"2023-12-06","2023-12-06 13:41:03"',
        '130,18,8.6272,"2023-12-06","2023-12-06 13:41:03"',
        '131,19,8.7838,"2023-12-06","2023-12-06 13:41:03"',
        '132,20,13.1912,"2023-12-06","2023-12-06 13:41:03"',
        '133,21,12.2756,"2023-12-06","2023-12-06 13:41:03"',
        '134,22,5.3348,"2023-12-06","2023-12-06 13:41:03"',
        '135,23,6.5164,"2023-12-06","2023-12-06 13:41:04"',
        '136,24,5.92,"2023-12-06","2023-12-06 13:41:04"',
        '137,25,13.4343,"2023-12-06","2023-12-06 13:41:04"',
        '138,26,6.5848,"2023-12-06","2023-12-06 13:41:04"',
        '139,27,5.3336,"2023-12-06","2023-12-06 13:41:04"',
        '140,28,8.4221,"2023-12-06","2023-12-06 13:41:05"',
        '141,1,4.7955,"2023-12-06","2023-12-06 23:52:30"',
        '142,2,5.0094,"2023-12-06","2023-12-06 23:52:30"',
        '143,3,5.1596,"2023-12-06","2023-12-06 23:52:30"',
        '144,4,4.5526,"2023-12-06","2023-12-06 23:52:31"',
        '145,5,5.7759,"2023-12-06","2023-12-06 23:52:31"',
        '146,6,10.7722,"2023-12-06","2023-12-06 23:52:31"',
        '147,7,5.06,"2023-12-06","2023-12-06 23:52:32"',
        '148,8,5.088,"2023-12-06","2023-12-06 23:52:32"',
        '149,9,5.1218,"2023-12-06","2023-12-06 23:52:32"',
        '150,10,5.1119,"2023-12-06","2023-12-06 23:52:32"',
        '151,11,5.1075,"2023-12-06","2023-12-06 23:52:32"',
        '152,12,4.9248,"2023-12-06","2023-12-06 23:52:33"',
        '153,13,7.4688,"2023-12-06","2023-12-06 23:52:33"',
        '154,14,5.7189,"2023-12-06","2023-12-06 23:52:33"',
        '155,15,5.6601,"2023-12-06","2023-12-06 23:52:33"',
        '156,16,12.5724,"2023-12-06","2023-12-06 23:52:33"',
        '157,17,15.0789,"2023-12-06","2023-12-06 23:52:33"',
        '158,18,8.6272,"2023-12-06","2023-12-06 23:52:34"',
        '159,19,8.7838,"2023-12-06","2023-12-06 23:52:34"',
        '160,20,13.1912,"2023-12-06","2023-12-06 23:52:34"',
        '161,21,12.2756,"2023-12-06","2023-12-06 23:52:34"',
        '162,22,5.3348,"2023-12-06","2023-12-06 23:52:34"',
        '163,23,6.5164,"2023-12-06","2023-12-06 23:52:35"',
        '164,24,5.92,"2023-12-06","2023-12-06 23:52:35"',
        '165,25,13.4343,"2023-12-06","2023-12-06 23:52:35"',
        '166,26,6.5848,"2023-12-06","2023-12-06 23:52:35"',
        '167,27,5.3336,"2023-12-06","2023-12-06 23:52:35"',
        '168,28,8.4185,"2023-12-06","2023-12-06 23:52:36"',
        '169,1,4.7955,"2023-12-07","2023-12-07 14:35:17"',
        '170,2,5.0094,"2023-12-07","2023-12-07 14:35:17"',
        '171,3,5.1596,"2023-12-07","2023-12-07 14:35:17"',
        '172,4,4.5526,"2023-12-07","2023-12-07 14:35:17"',
        '173,5,5.7759,"2023-12-07","2023-12-07 14:35:18"',
        '174,6,10.7722,"2023-12-07","2023-12-07 14:35:18"',
        '175,7,5.06,"2023-12-07","2023-12-07 14:35:18"',
        '176,8,5.088,"2023-12-07","2023-12-07 14:35:18"',
        '177,9,5.1218,"2023-12-07","2023-12-07 14:35:18"',
        '178,10,5.1119,"2023-12-07","2023-12-07 14:35:19"',
        '179,11,5.1075,"2023-12-07","2023-12-07 14:35:19"',
        '180,12,4.9248,"2023-12-07","2023-12-07 14:35:19"',
        '181,13,7.4688,"2023-12-07","2023-12-07 14:35:19"',
        '182,14,5.7189,"2023-12-07","2023-12-07 14:35:19"',
        '183,15,5.6601,"2023-12-07","2023-12-07 14:35:20"',
        '184,16,12.5724,"2023-12-07","2023-12-07 14:35:20"',
        '185,17,15.0789,"2023-12-07","2023-12-07 14:35:20"',
        '186,18,8.6272,"2023-12-07","2023-12-07 14:35:20"',
        '187,19,8.7838,"2023-12-07","2023-12-07 14:35:20"',
        '188,20,13.1912,"2023-12-07","2023-12-07 14:35:21"',
        '189,21,12.2756,"2023-12-07","2023-12-07 14:35:21"',
        '190,22,5.3348,"2023-12-07","2023-12-07 14:35:21"',
        '191,23,6.5164,"2023-12-07","2023-12-07 14:35:21"',
        '192,24,5.92,"2023-12-07","2023-12-07 14:35:21"',
        '193,25,13.4343,"2023-12-07","2023-12-07 14:35:22"',
        '194,26,6.5848,"2023-12-07","2023-12-07 14:35:22"',
        '195,27,5.3336,"2023-12-07","2023-12-07 14:35:22"',
        '196,28,8.4185,"2023-12-07","2023-12-07 14:35:22"',
        '197,1,4.8105,"2023-12-11","2023-12-11 14:35:41"',
        '198,2,5.0349,"2023-12-11","2023-12-11 14:35:41"',
        '199,3,5.1947,"2023-12-11","2023-12-11 14:35:41"',
        '200,4,4.5574,"2023-12-11","2023-12-11 14:35:41"',
        '201,5,5.7867,"2023-12-11","2023-12-11 14:35:41"',
        '202,6,10.8209,"2023-12-11","2023-12-11 14:35:42"',
        '203,7,5.0627,"2023-12-11","2023-12-11 14:35:42"',
        '204,8,5.0918,"2023-12-11","2023-12-11 14:35:42"',
        '205,9,5.1251,"2023-12-11","2023-12-11 14:35:42"',
        '206,10,5.1149,"2023-12-11","2023-12-11 14:35:42"',
        '207,11,5.1114,"2023-12-11","2023-12-11 14:35:43"',
        '208,12,4.9401,"2023-12-11","2023-12-11 14:35:43"',
        '209,13,7.5068,"2023-12-11","2023-12-11 14:35:43"',
        '210,14,5.7582,"2023-12-11","2023-12-11 14:35:43"',
        '211,15,5.6788,"2023-12-11","2023-12-11 14:35:43"',
        '212,16,12.5731,"2023-12-11","2023-12-11 14:35:44"',
        '213,17,14.9453,"2023-12-11","2023-12-11 14:35:44"',
        '214,18,8.6847,"2023-12-11","2023-12-11 14:35:44"',
        '215,19,8.7274,"2023-12-11","2023-12-11 14:35:44"',
        '216,20,13.2249,"2023-12-11","2023-12-11 14:35:44"',
        '217,21,12.3255,"2023-12-11","2023-12-11 14:35:45"',
        '218,22,5.3386,"2023-12-11","2023-12-11 14:35:45"',
        '219,23,6.5342,"2023-12-11","2023-12-11 14:35:45"',
        '220,24,5.9243,"2023-12-11","2023-12-11 14:35:45"',
        '221,25,13.4688,"2023-12-11","2023-12-11 14:35:45"',
        '222,26,6.615,"2023-12-11","2023-12-11 14:35:46"',
        '223,27,5.3492,"2023-12-11","2023-12-11 14:35:46"',
        '224,28,8.4207,"2023-12-11","2023-12-11 14:35:46"',
        '225,1,4.8105,"2023-12-12","2023-12-12 03:02:21"',
        '226,2,5.0349,"2023-12-12","2023-12-12 03:02:22"',
        '227,3,5.1947,"2023-12-12","2023-12-12 03:02:22"',
        '228,4,4.5574,"2023-12-12","2023-12-12 03:02:22"',
        '229,5,5.7867,"2023-12-12","2023-12-12 03:02:22"',
        '230,6,10.8209,"2023-12-12","2023-12-12 03:02:22"',
        '231,7,5.0627,"2023-12-12","2023-12-12 03:02:23"',
        '232,8,5.0918,"2023-12-12","2023-12-12 03:02:23"',
        '233,9,5.1251,"2023-12-12","2023-12-12 03:02:23"',
        '234,10,5.1149,"2023-12-12","2023-12-12 03:02:23"',
        '235,11,5.1114,"2023-12-12","2023-12-12 03:02:23"',
        '236,12,4.9401,"2023-12-12","2023-12-12 03:02:24"',
        '237,13,7.5068,"2023-12-12","2023-12-12 03:02:24"',
        '238,14,5.7582,"2023-12-12","2023-12-12 03:02:24"',
        '239,15,5.6788,"2023-12-12","2023-12-12 03:02:24"',
        '240,16,12.5731,"2023-12-12","2023-12-12 03:02:24"',
        '241,17,14.9453,"2023-12-12","2023-12-12 03:02:25"',
        '242,18,8.6847,"2023-12-12","2023-12-12 03:02:25"',
        '243,19,8.7274,"2023-12-12","2023-12-12 03:02:25"',
        '244,20,13.2249,"2023-12-12","2023-12-12 03:02:25"',
        '245,21,12.3255,"2023-12-12","2023-12-12 03:02:25"',
        '246,22,5.3386,"2023-12-12","2023-12-12 03:02:26"',
        '247,23,6.5342,"2023-12-12","2023-12-12 03:02:26"',
        '248,24,5.9243,"2023-12-12","2023-12-12 03:02:26"',
        '249,25,13.4688,"2023-12-12","2023-12-12 03:02:26"',
        '250,26,6.615,"2023-12-12","2023-12-12 03:02:26"',
        '251,27,5.3492,"2023-12-12","2023-12-12 03:02:27"',
        '252,28,8.4216,"2023-12-12","2023-12-12 03:02:27"',
        '253,29,4.9882,"2023-12-12","2023-12-12 03:02:28"',
    ]

    for line in lines:
        idx, fund_id, quote, date, created = line.split(',')
        date = datetime.strptime(date.replace('"', ''), '%Y-%m-%d')
        created = datetime.strptime(created.replace('"', ''), '%Y-%m-%d %H:%M:%S')
        quote = update_db(fund_id, date, quote, created)

    Quote.database().close()
