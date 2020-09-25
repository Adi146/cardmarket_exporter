import re
from prometheus_client.core import GaugeMetricFamily
from mkmsdk.mkm import Mkm
from mkmsdk.api_map import _API_MAP
from .utils import analyzeArticles, getArticleGauges, checkForNextPage

ORDER_ACTORS = ['seller', 'buyer']
ORDER_STATES = ['bought', 'paid', 'sent', 'received', 'lost', 'cancelled']

class OrderCollector(object):
    def __init__(self):
        self.cardMarket = Mkm(_API_MAP["2.0"]["api"], _API_MAP["2.0"]["api_root"])

    def collect(self):
        count_gauge = GaugeMetricFamily('cardmarket_order_count', 'Total count of orders', labels=['actor', 'orderState'])
        value_gauge = GaugeMetricFamily('cardmarket_order_value', 'Total value of orders', labels=['actor', 'orderState'])

        for actor in ORDER_ACTORS:
            for state in ORDER_STATES:
                order_count = 0
                order_value = 0
                order_article_result_dict = {}

                order_response = self.cardMarket.order_management.filter_order_paginated(actor=actor, state=state, start=1)
                while order_response is not None: 
                    order_json = order_response.json()

                    for order in order_json['order']:
                        order_count += 1
                        order_value += order['totalValue']
                        order_article_result_dict = analyzeArticles(
                            json=order,
                            partial_result=order_article_result_dict
                        )

                    order_response = checkForNextPage(order_response, self.cardMarket.order_management.filter_order_paginated, actor=actor, state=state)

                count_gauge.add_metric([actor, state], order_count)
                value_gauge.add_metric([actor, state], order_value)
                for gauge in getArticleGauges(
                    result_dict=order_article_result_dict, 
                    main_name='cardmarket_order_article', 
                    additional_labels={'actor': actor, 'orderState': state}
                ):
                    yield gauge

        yield count_gauge
        yield value_gauge