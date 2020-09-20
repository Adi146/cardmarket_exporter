from prometheus_client.core import GaugeMetricFamily
from mkmsdk.mkm import Mkm
from mkmsdk.api_map import _API_MAP

class WantsListCollector(object):
    def __init__(self):
        self.cardMarket = Mkm(_API_MAP["2.0"]["api"], _API_MAP["2.0"]["api_root"])

    def collect(self):
        wants_list_response = self.cardMarket.wants_list.get_all_wants_list()
        wants_list_json = wants_list_response.json()

        count_gauge = GaugeMetricFamily('wants_list_single_count', 'Count of cards on a wants list', labels=['list'])
        price_gauge = GaugeMetricFamily('wants_list_total_price', 'Total price of wants list', labels=['list'])
        price_single_gauge = GaugeMetricFamily('wants_list_single_price', 'Price of single card on wants list', labels=['list', 'card', 'count'])

        for wants_list in wants_list_json['wantslist']:
            id = wants_list['idWantslist']
            name = wants_list['name']

            total_count = 0
            total_price = 0
            single_prices = []

            wants_list_items_response = self.cardMarket.wants_list.get_wants_list(wants=id)
            wants_list_items_json = wants_list_items_response.json()
            for wants_list_item in wants_list_items_json['wantslist']['item']:
                total_count += wants_list_item['count']
                total_price += wants_list_item['count'] * wants_list_item['fromPrice']
                single_prices.append(
                    {
                        'name': wants_list_item['product']['enName'] if 'product' in wants_list_item else wants_list_item['metaproduct']['enName'],
                        'count': wants_list_item['count'],
                        'price': wants_list_item['fromPrice']
                    }
                )

            count_gauge.add_metric([name], total_count)
            price_gauge.add_metric([name], total_price)
            for item in single_prices:
                price_single_gauge.add_metric([name, item['name'], str(item['count'])], item['price'])

        yield count_gauge
        yield price_gauge
        yield price_single_gauge

