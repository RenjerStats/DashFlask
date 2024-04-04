import sys
sys.path.append("..")

from flask import Flask

from config import Config
from .dashboards.dash1 import create_dash1
from .dashboards.dash2 import create_dash2
from .dashboards.dash3 import create_dash3

from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

from .parser import create_dirs, update_central_bank_rate, update_inflation_rate, update_currency_exchange_rate, \
    update_shares_rate
import asyncio


def create_app():
    server = Flask(__name__)
    server.config.from_object(Config)

    create_dirs()
    # update_central_bank_rate()
    # update_inflation_rate()
    # update_currency_exchange_rate()
    # asyncio.run(update_shares_rate())

    app1 = create_dash1(requests_pathname_prefix="/dash1/")
    app2 = create_dash2(requests_pathname_prefix="/dash2/")
    app3 = create_dash3(requests_pathname_prefix="/dash3/")

    application = DispatcherMiddleware(server, {"/dash1": app1.server, "/dash2": app2.server, "/dash3": app3.server})

    with server.app_context():
        from . import routes
        return application


def run(app):
    run_simple('localhost', 0000, app)
