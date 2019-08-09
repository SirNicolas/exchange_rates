import asyncio

from rates.config import config
from rates.logic import add_currency_rates
from rates.logic import create_base_user
from rates.logic import get_or_create_currencies
from rates.models import db


async def main():
    # connect to database
    await db.set_bind(
        f'postgresql://{config["dbconfig"]["host"]}/{config["dbconfig"]["db"]}'
    )

    # create tables if they don't exist
    await db.gino.create_all()

    # create fist user
    await create_base_user(config['base_user']['name'],
                           config['base_user']['password'])

    # fill currencies
    currencies = await get_or_create_currencies(config["currency_pairs"])

    # fill currency rates
    for currency in currencies:
        await add_currency_rates(currency)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
