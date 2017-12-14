from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler
from bokeh.plotting import figure, curdoc, ColumnDataSource
from bokeh.models import DatetimeTickFormatter, NumeralTickFormatter
import numpy as np
from datetime import datetime
import logging

LOGGER = logging.getLogger(__name__)

LOGGER.info("HI")

pair = "BITF.BTC.USD"
num_levels = 10

source = ColumnDataSource(dict.fromkeys(
    ['datetime',
     'trade_price',
     'trade_size',
     'trade_aggressor'] +
    [part.format(i) for i in range(0, num_levels) for part in ['order_bid_{0}_price',
                                                               'order_ask_{0}_price',
                                                               'order_bid_{0}_qty',
                                                               'order_ask_{0}_qty',
                                                               'order_bid_{0}_scaled_qty',
                                                               'order_ask_{0}_scaled_qty']]), [])

fig = figure(title='Order Map')
fig.line(source=source, x='datetime', y='order_bid_0_price', color='green')
fig.line(source=source, x='datetime', y='order_ask_0_price', color='red')
fig.xaxis.formatter = DatetimeTickFormatter()
fig.xaxis.major_label_orientation = np.pi/4
fig.yaxis.formatter = NumeralTickFormatter('$0,0.00')


def test_update():
    new = dict.fromkeys(
        ['datetime', 'trade_price', 'trade_size', 'trade_aggressor'] + [part.format(i) for i in range(0, num_levels) for
                                                                        part in
                                                                        ['order_bid_{0}_price', 'order_ask_{0}_price',
                                                                         'order_bid_{0}_qty', 'order_ask_{0}_qty',
                                                                         'order_bid_{0}_scaled_qty',
                                                                         'order_ask_{0}_scaled_qty']])
    new['datetime'] = datetime.now()
    new['trade_price'] = 'NaN'
    new['trade_size'] = 'NaN'
    new['trade_aggressor'] = 'NaN'

    shift = (np.random.rand() - .5) / 10

    bid_prices = np.arange(100 + shift, 100 + shift - (num_levels * .01), -.01).tolist()
    ask_prices = np.arange(100.01 + shift, 100.01 + shift + (num_levels * .01), .01).tolist()
    bid_volumes = np.rand(10).tolist()
    ask_volumes = np.rand(10).tolist()
    max_volume = max(bid_volumes + ask_volumes)

    for i in range(0, num_levels):
        new['order_bid_{0}_price'.format(i)] = bid_prices[i]
        new['order_ask_{0}_price'.format(i)] = ask_prices[i]
        new['order_bid_{0}_qty'.format(i)] = bid_volumes[i]
        new['order_ask_{0}_qty'.format(i)] = ask_volumes[i]
        new['order_bid_{0}_scaled_qty'.format(i)] = bid_volumes[i] / max_volume
        new['order_ask_{0}_scaled_qty'.format(i)] = ask_volumes[i] / max_volume

    source.stream(new)


curdoc().add_root(fig)
curdoc().add_periodic_callback(test_update, 100)
