#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

from peewee import DatabaseProxy, DatabaseError, OperationalError
from playhouse.pool import PooledMySQLDatabase
from playhouse.migrate import migrate, MySQLMigrator

from config import Config
from models import Fund, Quote, DBConfig

log = logging.getLogger(__name__)


###############################################################################
# Database initialization
# https://docs.peewee-orm.com/en/latest/peewee/database.html#dynamically-defining-a-database
# https://docs.peewee-orm.com/en/latest/peewee/playhouse.html#database-url
# https://docs.peewee-orm.com/en/latest/peewee/database.html#setting-the-database-at-run-time
###############################################################################
class Database():
    BATCH_SIZE = 250  # TODO: move to Config argparse
    DB = DatabaseProxy()
    MODELS = [Fund, Quote, DBConfig]
    SCHEMA_VERSION = 1

    def __init__(self):
        """ Create a pooled connection to MySQL database """
        self.args = Config.get_args()

        log.info('Connecting to MySQL database on '
                 f'{self.args.db_host}:{self.args.db_port}...')

        # https://docs.peewee-orm.com/en/latest/peewee/playhouse.html#pool-apis
        database = PooledMySQLDatabase(
            self.args.db_name,
            host=self.args.db_host,
            port=self.args.db_port,
            user=self.args.db_user,
            password=self.args.db_pass,
            charset='utf8mb4',
            autoconnect=False,
            max_connections=self.args.db_max_conn,  # use None for unlimited
            stale_timeout=180,  # use None to disable
            timeout=10)  # 0 blocks indefinitely

        # Initialize DatabaseProxy
        self.DB.initialize(database)

        # Bind models to this database
        self.DB.bind(self.MODELS)

        try:
            self.DB.connect()
            self.verify_database_schema()
            self.verify_table_encoding()
        except OperationalError as e:
            log.error('Unable to connect to database: %s', e)
        except DatabaseError as e:
            log.exception('Failed to initalize database: %s', e)
        finally:
            self.DB.close()

    #  https://docs.peewee-orm.com/en/latest/peewee/api.html#Database.create_tables
    def create_tables(self):
        """ Create tables in the database (skips existing) """
        table_names = ', '.join([m.__name__ for m in self.MODELS])
        log.info('Creating database tables: %s', table_names)
        self.DB.create_tables(self.MODELS, safe=True)  # safe == if not exists
        # Create schema version key
        DBConfig.insert_schema_version(self.SCHEMA_VERSION)
        log.info('Database schema created.')

    #  https://docs.peewee-orm.com/en/latest/peewee/api.html#Database.drop_tables
    def drop_tables(self):
        """ Drop all the tables in the database """
        table_names = ', '.join([m.__name__ for m in self.MODELS])
        log.info('Dropping database tables: %s', table_names)
        self.DB.execute_sql('SET FOREIGN_KEY_CHECKS=0;')
        self.DB.drop_tables(self.MODELS, safe=True)
        self.DB.execute_sql('SET FOREIGN_KEY_CHECKS=1;')
        log.info('Database schema deleted.')

    # https://docs.peewee-orm.com/en/latest/peewee/playhouse.html#schema-migrations
    def migrate_database_schema(self, old_ver):
        """ Migrate database schema """
        log.info(f'Migrating schema v.{old_ver} to v.{self.SCHEMA_VERSION}.')
        migrator = MySQLMigrator(self.DB)

        if old_ver < 2:
            migrate(migrator.rename_table('db_config', 'db_config'))

        log.info('Schema migration complete.')

    def verify_database_schema(self):
        """ Verify if database is properly initialized """
        if not DBConfig.table_exists():
            self.create_tables()
            return

        DBConfig.init_lock()
        db_ver = DBConfig.get_schema_version()

        # Check if schema migration is required
        if db_ver < self.SCHEMA_VERSION:
            self.migrate_database_schema(db_ver)
            DBConfig.update_schema_version(self.SCHEMA_VERSION)
        elif db_ver > self.SCHEMA_VERSION:
            raise RuntimeError(
                f'Unsupported schema version: {db_ver} '
                f'(code requires: {self.SCHEMA_VERSION})')

    def verify_table_encoding(self):
        """ Verify if table collation is valid """
        change_tables = self.DB.execute_sql(
            'SELECT table_name FROM information_schema.tables WHERE '
            'table_collation != "utf8mb4_unicode_ci" '
            f'AND table_schema = "{self.args.db_name}";')

        tables = self.DB.execute_sql('SHOW tables;')

        if change_tables.rowcount > 0:
            log.info('Changing collation and charset on '
                     f'{change_tables.rowcount} tables.')

            if change_tables.rowcount == tables.rowcount:
                log.info('Changing whole database, this might a take while.')

            self.DB.execute_sql('SET FOREIGN_KEY_CHECKS=0;')
            for table in change_tables:
                log.debug('Changing collation and charset on '
                          f'table {table[0]}.')
                self.DB.execute_sql(
                    f'ALTER TABLE {table[0]} CONVERT TO '
                    'CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;')
            self.DB.execute_sql('SET FOREIGN_KEY_CHECKS=1;')

    def print_stats(self):
        in_use = len(self.DB._in_use)
        available = len(self.DB._connections)
        log.info('Database connections: '
                 f'{in_use} in use and {available} available.')
