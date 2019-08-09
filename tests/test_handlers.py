import base64
from datetime import datetime
from datetime import timedelta

import pytest

from rates.app import make_app
from rates.config import config
from rates.models import Currency
from rates.models import Rate
from rates.models import User
from rates.models import db
from rates.util import hash_password

USER_PASSWORD = 'testtest'
USER_NAME = 'testtest'
user = {'name': USER_NAME, "password_hash": hash_password(USER_PASSWORD)}
first_currency = {'name': "tBTCUSD"}
second_currency = {'name': "tLTCUSD"}
third_currency = {'name': "qwe"}
fourth_currency = {'name': "wqe"}
fifth_currency = {'name': "wrt"}
rates = [
    {
        "date": datetime.now() - timedelta(days=20),
        "rate": 10003,
        "volume": 500
    },
    {
        "date": datetime.now() - timedelta(days=9),
        "rate": 900,
        "volume": 200
    },
    {
        "date": datetime.now() - timedelta(days=8),
        "rate": 800,
        "volume": 100
    },
    {
        "date": datetime.now() - timedelta(days=7),
        "rate": 700,
        "volume": 200
    },
    {
        "date": datetime.now() - timedelta(days=6),
        "rate": 600,
        "volume": 100
    },
    {
        "date": datetime.now() - timedelta(days=5),
        "rate": 500,
        "volume": 200
    },
    {
        "date": datetime.now() - timedelta(days=4),
        "rate": 400,
        "volume": 100
    },
    {
        "date": datetime.now() - timedelta(days=3),
        "rate": 300,
        "volume": 200
    },
    {
        "date": datetime.now() - timedelta(days=2),
        "rate": 200,
        "volume": 100
    }, {
        "date": datetime.now() - timedelta(days=1),
        "rate": 10001,
        "volume": 200
    }
    , {
        "date": datetime.now(),
        "rate": 100,
        "volume": 100
    }
]


@pytest.fixture(scope='function')
async def setup_db():
    await db.set_bind(
        f'postgresql://{config["dbconfig"]["host"]}/'
        f'{config["dbconfig"]["testdb"]}'
    )
    await db.gino.drop_all()
    await db.gino.create_all()
    await User.create(**user)
    first_cur = await Currency.create(**first_currency)
    second_cur = await Currency.create(**second_currency)
    await Currency.create(**third_currency)
    await Currency.create(**fourth_currency)
    await Currency.create(**fifth_currency)
    for rate in rates:
        await Rate.create(currency_id=first_cur.id, **rate)
        await Rate.create(currency_id=second_cur.id, **rate)


def gen_auth_header(user_name, user_pass):
    payload = base64.b64encode(f'{user_name}:{user_pass}'.encode()).decode()
    return {'Authorization': f'Basic {payload}'}


@pytest.fixture
async def fx_client(aiohttp_client, setup_db):
    app = make_app()
    client = await aiohttp_client(app)

    return client


async def test_not_authenticated(fx_client):
    """ Request without authentication header"""
    resp = await fx_client.get('/currencies')
    assert resp.status == 403

    resp = await fx_client.get('/rate/123')
    assert resp.status == 403


async def test_currency_not_found(fx_client):
    """ There is no rate with such currency id """
    resp = await fx_client.get(
        '/rate/100500',
        headers=gen_auth_header(USER_NAME, USER_PASSWORD),
    )
    assert resp.status == 404


async def test_get_currencies(fx_client):
    """ Successful get all currencies """
    resp = await fx_client.get(
        '/currencies',
        headers=gen_auth_header(USER_NAME, USER_PASSWORD),
    )
    assert resp.status == 200
    data = await resp.json()
    assert len(data) == 2
    assert data[0].keys() == {'id', 'name'}
    assert {d['name'] for d in data} == {'tBTCUSD', 'tLTCUSD'}


async def test_currencies_paging(fx_client):
    """ There limit of 2 items per page """
    resp = await fx_client.get(
        '/currencies?page_number=0',
        headers=gen_auth_header(USER_NAME, USER_PASSWORD),
    )
    assert resp.status == 200
    data = await resp.json()
    assert len(data) == 2

    resp = await fx_client.get(
        '/currencies?page_number=1',
        headers=gen_auth_header(USER_NAME, USER_PASSWORD),
    )
    assert resp.status == 200
    data = await resp.json()
    assert len(data) == 2

    resp = await fx_client.get(
        '/currencies?page_number=2',
        headers=gen_auth_header(USER_NAME, USER_PASSWORD),
    )
    assert resp.status == 200
    data = await resp.json()
    assert len(data) == 1


async def test_get_rate(fx_client):
    """ Successful get last rate """
    resp = await fx_client.get(
        f'/rate/{1}',
        headers=gen_auth_header(USER_NAME, USER_PASSWORD),
    )
    assert resp.status == 200
    data = await resp.json()
    assert data.keys() == {'currency_pair', 'rate', 'volume'}
    assert data['currency_pair'] == 'tBTCUSD'
    assert data['volume'] == 150  # avg volume of last 10 days
    assert data['rate'] == 100  # last rate
