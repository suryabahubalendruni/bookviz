from bokeh.plotting import figure, curdoc, ColumnDataSource
from bokeh.models.glyphs import Step
from bokeh.models.ranges import DataRange1d
from bokeh.models import DatetimeTickFormatter, NumeralTickFormatter
import numpy as np
from datetime import datetime, timedelta
import logging
import time

LOGGER = logging.getLogger(__name__)

LOGGER.info("HI")

pair = "BITF.BTC.USD"
num_levels = 5
window_width = timedelta(seconds=30).seconds * 1000
window_height = num_levels*2
x_range = DataRange1d(follow='end', follow_interval=window_width)
y_range = DataRange1d(follow='end', follow_interval=window_height, range_padding=1)
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
                                                               'order_ask_{0}_scaled_qty']], []))


fig = figure(title='Order Map', x_axis_type='datetime', x_range=x_range, y_range=y_range)
best_bid_glyph = Step(x='datetime', y='order_bid_0_price', line_width=2, line_color='green', mode='after')
best_ask_glyph = Step(x='datetime', y='order_ask_0_price', line_width=2, line_color='red', mode='after')
fig.add_glyph(source, best_bid_glyph)
fig.add_glyph(source, best_ask_glyph)
fig.circle_x(source=source, x='datetime', y='trade_price', color='trade_aggressor', size='trade_size')
for i in range(0, num_levels):
    fig.circle(source=source, x='datetime', y='order_bid_{0}_price'.format(i), fill_color='white', line_color='green',
               size='order_bid_{0}_scaled_qty'.format(i))
    fig.circle(source=source, x='datetime', y='order_ask_{0}_price'.format(i), fill_color='white', line_color='red',
               size='order_ask_{0}_scaled_qty'.format(i))

fig.xaxis.formatter = DatetimeTickFormatter(seconds=["%M:%S.%3n"])
fig.xaxis.major_label_orientation = np.pi/4
fig.yaxis.formatter = NumeralTickFormatter(format="$0,0.00")


def test_update():
    new = dict.fromkeys(
    ['datetime',
     'trade_price',
     'trade_size',
     'trade_aggressor'] +
    [part.format(i) for i in range(0, num_levels) for part in ['order_bid_{0}_price',
                                                               'order_ask_{0}_price',
                                                               'order_bid_{0}_qty',
                                                               'order_ask_{0}_qty',
                                                               'order_bid_{0}_scaled_qty',
                                                               'order_ask_{0}_scaled_qty']], [])

    for i in range(0, 3):
        time.sleep(np.random.rand()/5)
        new['datetime'] = new['datetime'] + [datetime.now()]
        shift = (np.random.rand() - .5) / 10
        bid_prices = np.arange(100+shift, 100+shift-(num_levels*.01), -.01).tolist()
        ask_prices = np.arange(100.05+shift, 100.05+shift+(num_levels*.01), .01).tolist()
        bid_volumes = np.random.rand(10).tolist()
        ask_volumes = np.random.rand(10).tolist()
        max_volume = max(bid_volumes+ask_volumes)

        for i in range(0, num_levels):
            new['order_bid_{0}_price'.format(i)] = new['order_bid_{0}_price'.format(i)] + [bid_prices[i]]
            new['order_ask_{0}_price'.format(i)] = new['order_ask_{0}_price'.format(i)] + [ask_prices[i]]
            new['order_bid_{0}_qty'.format(i)] = new['order_bid_{0}_qty'.format(i)] + [bid_volumes[i]]
            new['order_ask_{0}_qty'.format(i)] = new['order_ask_{0}_qty'.format(i)] + [ask_volumes[i]]
            new['order_bid_{0}_scaled_qty'.format(i)] = new['order_bid_{0}_scaled_qty'.format(i)] + [5*bid_volumes[
                i]/max_volume]
            new['order_ask_{0}_scaled_qty'.format(i)] = new['order_ask_{0}_scaled_qty'.format(i)]+ [5*ask_volumes[
                i]/max_volume]

        rand_trade = np.random.rand()
        if rand_trade > .8:
            new['trade_price'] = new['trade_price'] + [new['order_ask_0_price'][-1]]
            new['trade_size'] = new['trade_size'] + [5*np.random.rand()]
            new['trade_aggressor'] = new['trade_aggressor'] + ['green']
        elif rand_trade < .2:
            new['trade_price'] = new['trade_price'] + [new['order_bid_0_price'][-1]]
            new['trade_size'] = new['trade_size'] + [5*np.random.rand()]
            new['trade_aggressor'] = new['trade_aggressor'] + ['red']
        else:
            new['trade_price'] = new['trade_price'] + ['NaN']
            new['trade_size'] = new['trade_size'] + ['NaN']
            new['trade_aggressor'] = new['trade_aggressor'] + ['NaN']
    LOGGER.info("Best Bid: {0}, Best Ask: {0}".format(new['order_bid_0_price'][-1], new['order_ask_0_price'][-1]))
    source.stream(new)
    LOGGER.info("Streamed update.")


curdoc().add_root(fig)
curdoc().add_periodic_callback(test_update, 1000)
