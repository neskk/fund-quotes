#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import sys
from threading import Event, Thread

from utils import configure_logging
from config import Config
from db import Database

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
        self.db = Database()

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
        scrapper = CGD()
        scrapper.run()

    def stop(self):
        log.debug('Shutdown')


if __name__ == '__main__':
    args = Config.get_args()
    configure_logging(log, args.verbose, args.log_path, "-fund-quotes")

    app = App()
    app.start()
