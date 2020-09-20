import re
from mkmsdk.mkm import Mkm
from mkmsdk.api_map import _API_MAP
from .utils import analyzeArticles, getArticleGauges, checkForNextPage

class StockCollector(object):
    def __init__(self):
        self.cardMarket = Mkm(_API_MAP["2.0"]["api"], _API_MAP["2.0"]["api_root"])

    def collect(self):
        result_dict = {}

        stock_response = self.cardMarket.stock_management.get_stock_paginated(start=1)
        while stock_response is not None: 
            stock_json = stock_response.json()

            result_dict = analyzeArticles(
                json=stock_json,
                partial_result=result_dict
            )

            stock_response = checkForNextPage(stock_response, self.cardMarket.stock_management.get_stock_paginated)

        return getArticleGauges(
            result_dict=result_dict,
            main_name='stock'
        )