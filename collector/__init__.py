import time
import prometheus_client
from prometheus_client.core import REGISTRY

from .account_collector import AccountCollector
from .stock_collector import StockCollector
from .order_collector import OrderCollector
from .wants_list_collector import WantsListCollector

def startHttpServer(collectors = [
    AccountCollector(),
    StockCollector(), 
    OrderCollector(),
    WantsListCollector()
]):
    prometheus_client.start_http_server(8000)
    for collector in collectors:
        REGISTRY.register(collector)
    while True:
        time.sleep(1) 