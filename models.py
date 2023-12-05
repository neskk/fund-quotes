#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

from peewee import (
    fn, JOIN, Case, OperationalError, IntegrityError,
    Model, ModelSelect, ModelUpdate, ModelDelete, AutoField,
    ForeignKeyField, BigAutoField, DateTimeField, CharField,
    IntegerField, BigIntegerField, SmallIntegerField, FloatField)

from datetime import datetime, timedelta

log = logging.getLogger(__name__)


###############################################################################
# Custom field types
# https://docs.peewee-orm.com/en/latest/peewee/models.html#field-types-table
###############################################################################
class Utf8mb4CharField(CharField):
    def __init__(self, max_length=191, *args, **kwargs):
        self.max_length = max_length
        super(CharField, self).__init__(*args, **kwargs)


class UBigIntegerField(BigIntegerField):
    field_type = 'bigint unsigned'


class UIntegerField(IntegerField):
    field_type = 'int unsigned'


class USmallIntegerField(SmallIntegerField):
    field_type = 'smallint unsigned'


# https://github.com/coleifer/peewee/issues/630
class IntEnumField(SmallIntegerField):
    """	Unsigned integer representation field for Enum """
    field_type = 'smallint unsigned'

    def __init__(self, choices, *args, **kwargs):
        super(SmallIntegerField, self).__init__(*args, **kwargs)
        self.choices = choices

    def db_value(self, value):
        return value.value

    def python_value(self, value):
        return self.choices(value)


###############################################################################
# Database models
# https://docs.peewee-orm.com/en/latest/peewee/models.html#model-options-and-table-metadata
# https://docs.peewee-orm.com/en/latest/peewee/models.html#meta-primary-key
# https://docs.peewee-orm.com/en/latest/peewee/models.html#field-initialization-arguments
# Note: field attribute "default" is implemented purely in Python and "choices" are not validated.
###############################################################################
class BaseModel(Model):
    @classmethod
    def database(cls):
        return cls._meta.database

    @classmethod
    def get_all(cls):
        return [m for m in cls.select().dicts()]

    @classmethod
    def get_random(cls, limit=1):
        return cls.select().order_by(fn.Rand()).limit(limit)


class Fund(BaseModel):
    id = AutoField()
    name = Utf8mb4CharField(index=True, null=True, max_length=200)
    bank = Utf8mb4CharField(index=True, null=True, max_length=100)
    start_date = DateTimeField(null=True)
    created = DateTimeField(index=True, default=datetime.utcnow)
    modified = DateTimeField(index=True, default=datetime.utcnow)


class Quote(BaseModel):
    id = BigAutoField()
    fund = ForeignKeyField(Fund, backref='quotes', on_delete='CASCADE')
    value = FloatField(null=False)
    created = DateTimeField(index=True, default=datetime.utcnow)


class DBConfig(BaseModel):
    """ Database versioning model """
    key = Utf8mb4CharField(null=False, max_length=64, unique=True)
    val = Utf8mb4CharField(null=True, max_length=64)
    modified = DateTimeField(index=True, default=datetime.utcnow)

    class Meta:
        primary_key = False
        table_name = 'db_config'

    @staticmethod
    def get_schema_version() -> int:
        """ Get current schema version """
        db_ver = DBConfig.get(DBConfig.key == 'schema_version').val
        return int(db_ver)

    @staticmethod
    def insert_schema_version(schema_version):
        """ Insert current schema version """
        DBConfig.insert(
            key='schema_version',
            val=schema_version
        ).execute()

    @staticmethod
    def update_schema_version(schema_version):
        """ Update current schema version """
        with DBConfig.database().atomic():
            query = (DBConfig
                     .update(val=schema_version)
                     .where(DBConfig.key == 'schema_version'))
            query.execute()

    @staticmethod
    def init_lock():
        """ Initialize database lock """
        DBConfig.get_or_create(
            key='read_lock',
            defaults={'val': None})

    @staticmethod
    def lock_database(hash):
        """ Update database lock with local IP """
        conditions = (
            (DBConfig.key == 'read_lock') &
            (DBConfig.val.is_null(True)))

        query = (DBConfig
                 .update(val=hash, modified=datetime.utcnow())
                 .where(conditions))
        row_count = query.execute()

        if row_count == 1:
            return True

        log.debug('Failed to lock database.')
        max_lock = datetime.utcnow() - timedelta(seconds=10)
        conditions = (
            (DBConfig.key == 'read_lock') &
            (DBConfig.modified < max_lock))

        query = (DBConfig
                 .update(val=hash, modified=datetime.utcnow())
                 .where(conditions))

        row_count = query.execute()
        if row_count == 1:
            log.warning('Database locked forcibly.')
            return True

        return False

    @staticmethod
    def unlock_database(hash):
        """ Update database to clear lock """
        conditions = (
            (DBConfig.key == 'read_lock') &
            (DBConfig.val == hash))

        query = (DBConfig
                 .update(val=None, modified=datetime.utcnow())
                 .where(conditions))
        row_count = query.execute()

        if row_count == 1:
            return True

        log.debug('Failed to unlock database.')
        return False
