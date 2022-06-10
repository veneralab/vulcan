# Manhattan
# Copyright (c) 2021-2022 Venera, Inc. All Rights Reserved.
import os
import logging
import datetime

import dotenv
from cassandra.auth import PlainTextAuthProvider
from cassandra.cqlengine import columns, connection, management, models


dotenv.load_dotenv()
cloud = {'secure_connect_bundle': os.getcwd() + r'/private/cass-bundle.zip'}
auth_provider = PlainTextAuthProvider(
    os.getenv('CLIENT_ID'), os.getenv('CLIENT_SECRET')
)

BUCKET_SIZE = 1000 * 60 * 60 * 24 * 4


def connect():
    try:
        if os.getenv('SAFE', 'false') == 'true':
            connection.setup(
                None,
                'manhattan',
                cloud=cloud,
                auth_provider=auth_provider,
                connect_timeout=100,
                retry_connect=True,
            )
        else:
            connection.setup(
                None,
                'manhattan',
                connect_timeout=100,
                retry_connect=True,
                compression=False,
            )
    except:
        connect()


def _get_date():
    return datetime.datetime.now(datetime.timezone.utc)


class User(models.Model):
    """Users are the base entity of Manhattan."""
    id: int = columns.BigInt(primary_key=True, partition_key=True)
    email: str = columns.Text()
    password: str = columns.Text()
    name: str = columns.Text(index=True)
    screen_name: str = columns.Text()
    created_at: datetime.datetime | str = columns.DateTime(default=_get_date)
    icon_url: str = columns.Text()
    banner_url: str = columns.Text()
    flags: int = columns.Integer(default=0)
    analytic_flags: int = columns.BigInt(default=0)
    location: str = columns.Text(default='')
    about: str = columns.Text(default='')
    verified: bool = columns.Boolean(default=False)
    locale: str = columns.Text()


class UserPost(models.Model):
    """A Post created by a User."""
    id: int = columns.BigInt(primary_key=True)
    user_id: int = columns.BigInt()
    bucket_id: int = columns.Integer()


def gen_bucket(obj: int):
    timestamp = obj >> 22
    return timestamp // BUCKET_SIZE


def to_dict(model: models.Model) -> dict:
    dict_repr = dict(model)

    if 'id' in dict_repr:
        dict_repr['id'] = str(dict_repr['id'])


    if isinstance(model, User):
        dict_repr.pop('analytic_flags')
        dict_repr.pop('password')
        dict_repr['url'] = f'/{dict_repr["name"]}'

    return dict_repr


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    connect()
    management.sync_table(User)