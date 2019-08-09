from aiohttp import web

from rates.logic import get_currencies
from rates.logic import get_rate_info

routes = web.RouteTableDef()


@routes.get('/currencies')
async def get_all_currencies(request):
    page_number = int(request.query.get('page_number', 0))
    currencies = await get_currencies(page_number)
    return web.json_response([cur.to_dict() for cur in currencies])


@routes.get(r'/rate/{currency_id:\d+}')
async def get_rate(request):
    currency_id = int(request.match_info['currency_id'])
    rate, rate_volume = await get_rate_info(currency_id)
    return web.json_response(
        {
            "rate": rate.rate,
            "volume": rate_volume,
            "currency_pair": rate.parent.name
        }
    )
