from flask import Flask, Response, request
from flask_cors import CORS
import os
import json
from Tidesurf.data.constants.exchanges import Exchanges
from Tidesurf.config import Config
from Tidesurf.analytics.indicators.kindle import Kindle
from Tidesurf.analytics.indicators.volume import Volume
from Tidesurf.data.exchange.binance.binance_trade_loader import BinanceTradeGenerativeLoader
from Tidesurf.data.model.ui.i_olhc_data import IOHLCData
app = Flask(__name__)
CORS(app)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/ping")
def ping():
    return Response(json.dumps({"status": "ok"}), mimetype="application/json", status=200)


"""
url_params:
- exchange: str e.g.Binance
- symbol: str e.g. BTCUSD
- from_timestamp: int in millisecond
- to_timestamp: int in millisecond
- interval: int in seconds
"""
@app.route("/get_kindle")
def handle_get_kindle():
    exchange = request.args.get('exchange')
    symbol = request.args.get('symbol')
    from_timestamp = int(request.args.get('from_timestamp'))
    to_timestamp = int(request.args.get('to_timestamp'))
    interval = int(request.args.get('interval'))
    interval_in_milliseconds = interval * 1000
    if exchange == Exchanges.BINANCE:
        binance_loader = BinanceTradeGenerativeLoader(
            Config.HISTORICAL_RECORDS_LOCATION_MAP[Exchanges.BINANCE],
            symbol,
            from_timestamp
        )
        kindle = Kindle(interval, from_timestamp)
        volume = Volume(interval, from_timestamp)
        while binance_loader.has_next():
            data = binance_loader.next()
            if data[1] > to_timestamp:
                break
            kindle.append(data[1], data[2])
            volume.append(data[1], data[3])
        kindle.compute_and_append_residual()
        volume.compute_and_append_residual()
        kindle_list = kindle.get_indicator_values()
        volume_list = volume.get_indicator_values()
        cur_timestamp = from_timestamp
        res = []
        for i in range(len(kindle_list)):
            res.append(IOHLCData(cur_timestamp, kindle_list[i][0], kindle_list[i][1], kindle_list[i][2], kindle_list[i][3], volume_list[i]))
            cur_timestamp += interval_in_milliseconds
        return Response(json.dumps(res), mimetype="application/json", status=200)
    return Response(json.dumps({"error": "Exchange not found"}), mimetype="application/json", status=404)


@app.route("/populate_entry_trend")
def populate_entry_trend_handler():
    """
    Expect a dictionary of ticker -> value indicators
    request:
    {
        market: {
            "BTC-USD": [open, close, high, low, volume]
        },
        "position": {
            "BTC-USD": 30,
            ...
        }

    }

    response:

    """
    pass


@app.route("/populate_exit_trend")
def populate_exit_trend_handler():
    pass


if __name__ == "__main__":
    debug = os.environ.get("DEBUG_SERVER", "true") == "true"
    app.run("0.0.0.0", 9100, debug=debug)
