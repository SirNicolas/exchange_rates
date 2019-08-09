import json
import os

f = open(
    os.path.join(
        os.path.dirname(
            os.path.abspath(
                os.path.join(__file__, os.pardir)
            )
        ), 'settings.json'),
    'r'
)

config = json.load(f)
