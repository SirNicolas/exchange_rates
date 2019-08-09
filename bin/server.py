import asyncio

from aiohttp import web

from rates.app import make_app
from rates.config import config
from rates.models import db


async def main():
    # connect to database
    await db.set_bind(
        f'postgresql://{config["dbconfig"]["host"]}/{config["dbconfig"]["db"]}'
    )


asyncio.get_event_loop().run_until_complete(main())

if __name__ == '__main__':
    web.run_app(make_app())
