import logging
from datetime import datetime
from datetime import timedelta
from typing import List

from aiohttp import ClientResponseError
from aiohttp import web

from rates.config import config
from rates.models import Currency
from rates.models import Rate
from rates.models import User
from rates.models import db
from rates.util import hash_password
from rates.util import request
from rates.util import timestamp_to_date
from rates.util import verify_password

LAST_TEN_DAYS = 10
TIME_FRAME_1_HOUR = '1h'
PAGE_LIMIT = 2


async def create_base_user(user_name: str, user_password: str):
    """ Create user if where are no one exists """
    user = await User.query.gino.first()
    if not user:
        await User.create(
            name=user_name,
            password_hash=hash_password(user_password)
        )


async def check_user_auth(user_name: str, user_password: str):
    """ Check that user with given name and password exists """
    user = await User.query.where(
        User.name == user_name
    ).gino.first()
    if not user or not verify_password(user.password_hash, user_password):
        raise web.HTTPForbidden()


async def get_rate_info(currency_id: int) -> (Rate, float):
    """ Get last currency rate and average volume of 10 days """
    last_10_days = datetime.today() - timedelta(days=10)

    # check that such currency exists
    currency = await Currency.query.where(
        Currency.id == currency_id
    ).gino.first()
    if not currency:
        raise web.HTTPNotFound()

    rate = await get_last_rate(currency_id)
    rate_avg_volume = await db.select([db.func.avg(Rate.volume).filter(
        Rate.currency_id == currency_id,
        Rate.date >= last_10_days
    )]).gino.scalar()
    return rate, rate_avg_volume


async def get_currencies(page_number: int) -> List[Currency]:
    """ Get list of available currencies with pagination """
    query = Currency.query.limit(PAGE_LIMIT).offset(PAGE_LIMIT * page_number)
    return await query.gino.all()


async def get_or_create_currencies(
        currencies_names: List[str]
) -> List[Currency]:
    currencies = []
    for currency_name in currencies_names:
        currency = await Currency.query.where(
            Currency.name == currency_name
        ).gino.first()
        if not currency:
            # check that currency with such name exists
            currency_url = config['currency_url_format'].format(currency_name)
            if await request(currency_url):
                currency = await Currency.create(name=currency_name)
        currencies.append(currency)
    return currencies


async def add_currency_rates(currency: Currency):
    rate_url = config['rate_url_format'].format(
        TIME_FRAME_1_HOUR, currency.name
    )

    # if we already got currency rates,
    # let's just get from foreign api only latest missing data
    rate = await get_last_rate(currency.id)
    try:
        if rate:
            rate_url = f'{rate_url}/last'
            data = await request(rate_url)
            timestamp, _, close, _, _, volume = data
            await create_rate(
                currency_id=currency.id, date=timestamp_to_date(timestamp),
                rate=close, volume=volume
            )
        else:
            rate_url = f'{rate_url}/hist?limit=500'
            data = await request(rate_url)
            for item in data:
                timestamp, _, close, _, _, volume = item
                await create_rate(
                    currency_id=currency.id, date=timestamp_to_date(timestamp),
                    rate=close, volume=volume
                )
    except ClientResponseError:
        logging.error(f'There is a trouble with {rate_url}')


async def create_rate(currency_id, date, rate, volume) -> Rate:
    return await Rate.create(
        currency_id=currency_id, date=date, rate=rate, volume=volume
    )


async def get_last_rate(currency_id: int) -> Rate:
    return await Rate.load(
        parent=Currency.on(Rate.currency_id == Currency.id)).query.where(
        Rate.currency_id == currency_id
    ).order_by(Rate.date.desc()).gino.first()
