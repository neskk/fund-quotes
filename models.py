#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

import peewee
from flask_admin.contrib.peewee import ModelView

from datetime import datetime, timedelta

log = logging.getLogger(__name__)


###############################################################################
# Custom field types
# https://docs.peewee-orm.com/en/latest/peewee/models.html#field-types-table
###############################################################################
class Utf8mb4CharField(peewee.CharField):
    def __init__(self, max_length=191, *args, **kwargs):
        self.max_length = max_length
        super(peewee.CharField, self).__init__(*args, **kwargs)


class UBigIntegerField(peewee.BigIntegerField):
    field_type = 'bigint unsigned'


class UIntegerField(peewee.IntegerField):
    field_type = 'int unsigned'


class USmallIntegerField(peewee.SmallIntegerField):
    field_type = 'smallint unsigned'


# https://github.com/coleifer/peewee/issues/630
class IntEnumField(peewee.SmallIntegerField):
    """	Unsigned integer representation field for Enum """
    field_type = 'smallint unsigned'

    def __init__(self, choices, *args, **kwargs):
        super(peewee.SmallIntegerField, self).__init__(*args, **kwargs)
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
class BaseModel(peewee.Model):
    @classmethod
    def database(cls):
        return cls._meta.database

    @classmethod
    def get_all(cls):
        return [m for m in cls.select().dicts()]

    @classmethod
    def get_random(cls, limit=1):
        return cls.select().order_by(peewee.fn.Rand()).limit(limit)


class Fund(BaseModel):
    id = peewee.AutoField()
    name = Utf8mb4CharField(index=True, null=True, max_length=200)
    bank = Utf8mb4CharField(index=True, null=True, max_length=100)
    start_date = peewee.DateTimeField(null=True)
    created = peewee.DateTimeField(index=True, default=datetime.utcnow)
    modified = peewee.DateTimeField(index=True, default=datetime.utcnow)


class Quote(BaseModel):
    id = peewee.BigAutoField()
    fund = peewee.ForeignKeyField(Fund, backref='quotes', on_delete='CASCADE')
    value = peewee.FloatField(null=False)
    date = peewee.DateField(index=True, default=datetime.today)
    modified = peewee.DateTimeField(index=True, default=datetime.utcnow)

    @staticmethod
    def get_latest(fund):
        query = (Quote
                 .select()
                 .where(Quote.fund == fund)
                 .order_by(Quote.date.desc()))
        return query.first()

    @staticmethod
    def get_by_fund(fund):
        query = (Quote
                 .select()
                 .where(Quote.fund == fund)
                 .order_by(Quote.date.asc()))
        return query


class DBConfig(BaseModel):
    """ Database versioning model """
    key = Utf8mb4CharField(null=False, max_length=64, unique=True)
    val = Utf8mb4CharField(null=True, max_length=64)
    modified = peewee.DateTimeField(index=True, default=datetime.utcnow)

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


###############################################################################
# Flask-Admin Model Views
# https://flask-admin.readthedocs.io/en/latest/introduction/
# https://github.com/flask-admin/flask-admin/tree/master/examples/peewee
# https://flask-admin.readthedocs.io/en/latest/api/mod_contrib_peewee/#module-flask_admin.contrib.peewee
###############################################################################
class FundAdmin(ModelView):
    # CRUD
    can_create = False
    can_edit = False
    can_delete = False

    # Show modals instead of separate page
    create_modal = True
    edit_modal = True

    # Remove columns from the list view
    column_exclude_list = ['created']

    # Inline edit
    column_editable_list = []

    # List of columns that can be sorted
    column_sortable_list = ['bank', 'name']

    # Full text search
    column_searchable_list = ['name']

    # Column filters
    # Warning: can not use filters on custom field types
    column_filters = []
