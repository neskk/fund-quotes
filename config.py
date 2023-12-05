#!/usr/bin/python
# -*- coding: utf-8 -*-

from enum import Enum
from hashlib import blake2b
from typing import Any
import os
import socket
import sys
import time

import configargparse
import pycountry

CWD = os.path.dirname(os.path.realpath(__file__))
APP_PATH = os.path.realpath(os.path.join(CWD, '..'))


class Config:
    """ Singleton class that parses and holds all the configuration arguments """
    __args = None
    __counter = 0

    @staticmethod
    def get_args():
        """ Static access method """
        if Config.__args is None:
            Config()
        return Config.__args

    def __init__(self):
        """ Parse config/CLI arguments and setup workspace """
        if Config.__args is not None:
            raise Exception('This class is a singleton!')

        Config.__args = get_args()
        self.__check_config()

    def __check_config(self):
        """ Validate configuration values """
        if self.__args.db_max_conn <= 5:
            raise RuntimeError('Database max connections must be greater than 5.')

        if self.__args.db_batch_size < 50:
            raise RuntimeError('Database batch size must be greater than 50.')

        hostname = socket.gethostname()
        signature = f'{hostname}-{time.time()}'

        hash = blake2b(signature.encode(), digest_size=10).hexdigest()
        setattr(self.__args, 'hash', hash)


###############################################################################
# ArgParse helper class to deal with Enums.
# https://stackoverflow.com/questions/43968006/support-for-enum-arguments-in-argparse
###############################################################################

class EnumAction(configargparse.Action):
    """
    ArgParse Action for handling Enum types
    """
    def __init__(self, **kwargs):
        # Pop off the type value
        enum_type = kwargs.pop('type', None)

        # Ensure an Enum subclass is provided
        if enum_type is None:
            raise ValueError('type must be assigned an Enum when using EnumAction')
        if not issubclass(enum_type, Enum):
            raise TypeError('type must be an Enum when using EnumAction')

        # Generate choices from the Enum
        kwargs.setdefault('choices', tuple(e.name for e in enum_type))

        super(EnumAction, self).__init__(**kwargs)

        self._enum = enum_type

    def __call__(self,
                 parser: configargparse.ArgumentParser,
                 namespace: configargparse.Namespace,
                 value: Any,
                 option_string: str = None):
        # Convert value back into an Enum
        if isinstance(value, str):
            value = self._enum[value]
            setattr(namespace, self.dest, value)
        elif value is None:
            msg = f'You need to pass a value after {option_string}!'
            raise configargparse.ArgumentTypeError(msg)
        else:
            # A pretty invalid choice message will be generated by argparse
            raise configargparse.ArgumentTypeError()


###############################################################################
# ConfigArgParse definitions for current application.
# The following code should have minimal dependencies.
# https://docs.python.org/3/library/argparse.html
# Note: If the 'type' keyword is used with the 'default' keyword,
# the type converter is only applied if the default is a string.
###############################################################################

def get_args():
    default_config = []

    config_file = os.path.normpath(
        os.path.join(APP_PATH, 'config/config.ini'))

    if '-cf' not in sys.argv and '--config' not in sys.argv:
        default_config = [config_file]
    parser = configargparse.ArgParser(default_config_files=default_config)

    parser.add_argument('-cf', '--config',
                        is_config_file=True, help='Set configuration file.')
    parser.add_argument('-v', '--verbose',
                        help='Control verbosity level, e.g. -v or -vv.',
                        action='count',
                        default=0)
    parser.add_argument('--log-path',
                        help='Directory where log files are saved.',
                        default='logs',
                        type=str_path)
    parser.add_argument('--download-path',
                        help='Directory where downloaded files are saved.',
                        default='downloads',
                        type=str_path)
    parser.add_argument('-ua', '--user-agent',
                        help='Browser User-Agent used. Default: random',
                        choices=['random', 'chrome', 'firefox', 'safari'],
                        default='random')

    group = parser.add_argument_group('Database')
    group.add_argument('--db-name',
                       env_var='MYSQL_DATABASE',
                       help='Name of the database to be used.',
                       required=True)
    group.add_argument('--db-user',
                       env_var='MYSQL_USER',
                       help='Username for the database.',
                       required=True)
    group.add_argument('--db-pass',
                       env_var='MYSQL_PASSWORD',
                       help='Password for the database.',
                       required=True)
    group.add_argument('--db-host',
                       env_var='MYSQL_HOST',
                       help='IP or hostname for the database.',
                       default='127.0.0.1')
    group.add_argument('--db-port',
                       env_var='MYSQL_PORT',
                       help='Port for the database.',
                       type=int, default=3306)
    group.add_argument('--db-max-conn',
                       env_var='MYSQL_MAX_CONN',
                       help='Maximum number of connections to the database.',
                       type=int, default=20)
    group.add_argument('--db-batch-size',
                       env_var='MYSQL_BATCH_SIZE',
                       help='Maximum number of rows to update per batch.',
                       type=int, default=250)

    group = parser.add_argument_group('Scrapper')
    group.add_argument('-Sf', '--scrapper-frequency',
                       help='Scrap quotes very X hours. Default: 6.',
                       default=6,
                       type=int_hours)
    group.add_argument('-Sr', '--scrapper-retries',
                       help=('Maximum number of web request attempts. '
                             'Default: 5.'),
                       default=5,
                       type=int)
    group.add_argument('-Sbf', '--scrapper-backoff-factor',
                       help=('Time factor (in seconds) by which the delay '
                             'until next retry will increase. Default: 1.0.'),
                       default=1.0,
                       type=float_seconds)
    group.add_argument('-St', '--scrapper-timeout',
                       help='Connection timeout in seconds. Default: 5.',
                       default=10.0,
                       type=float_seconds)
    group.add_argument('-Sp', '--scrapper-proxy',
                       help=('Use this proxy for webpage scrapping. '
                             'Format: <proto>://[<user>:<pass>@]<ip>:<port> '
                             'Default: None.'),
                       default=None)

    args = parser.parse_args()

    if args.verbose:
        parser.print_values()

    # Helper attributes
    setattr(args, "app_path", APP_PATH)

    return args


def int_hours(arg: int):
    interval = int(arg)

    if interval <= 0:
        raise ValueError('Negative time interval specified!')

    return interval * 3600


def int_minutes(arg: int):
    interval = int(arg)

    if interval <= 0:
        raise ValueError('Negative time interval specified!')

    return interval * 60


def float_minutes(arg: float):
    interval = float(arg)

    if interval <= 0:
        raise ValueError('Negative time interval specified!')

    return interval * 60


def int_seconds(arg: int):
    interval = int(arg)

    if interval <= 0:
        raise ValueError('Negative time interval specified!')

    return interval


def float_seconds(arg: float):
    interval = float(arg)

    if interval <= 0:
        raise ValueError('Negative time interval specified!')

    return interval


def float_ratio(arg: float):
    ratio = float(arg)

    if ratio < 0:
        raise ValueError('Minimum percentage is 0.0!')

    if ratio > 1:
        raise ValueError('Maximum percentage is 1.0!')

    return ratio


def str_path(arg: str):
    if arg is None:
        raise ValueError('Empty path specified!')

    if os.path.isabs(arg):
        path = arg
    else:
        path = os.path.abspath(f'{APP_PATH}/{arg}')

    # Create directory if path not found
    if not os.path.exists(path):
        os.mkdir(path)
    return path


def str_disable(arg: str):
    if arg is None or arg.lower() in ['none', 'false']:
        return None

    return arg


def str_iso3166_1(arg: str):
    country = None
    if arg.isnumeric():
        country = pycountry.countries.get(numeric=arg)
    elif len(arg) == 2:
        country = pycountry.countries.get(alpha_2=arg)
    elif len(arg) == 3:
        country = pycountry.countries.get(alpha_3=arg)
    else:
        print(arg)
        msg = 'invalid ISO 3166-1 code format'
        raise configargparse.ArgumentTypeError(msg)

    if country is None:
        msg = f'"{arg}" unknown ISO 3166-1 code'
        raise configargparse.ArgumentTypeError(msg)

    return country.alpha_2
