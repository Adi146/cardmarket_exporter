from prometheus_client.core import GaugeMetricFamily
from mkmsdk.mkm import Mkm
from mkmsdk.api_map import _API_MAP

class AccountCollector(object):
    CREDIT_TYPES = ['totalBalance', 'moneyBalance', 'bonusBalance', 'unpaidAmount']

    def __init__(self):
        self.cardMarket = Mkm(_API_MAP["2.0"]["api"], _API_MAP["2.0"]["api_root"])

    def collect(self):
        credit_gauge = GaugeMetricFamily('cardmarket_account_credit', 'Current account credit for user', labels=['type'])
        unread_messages_gauge = GaugeMetricFamily('cardmarket_account_unread_messages', 'Current unread messages')
        on_vacation_gauge = GaugeMetricFamily('cardmarket_account_on_vacation', 'Current vacation state')

        account_response = self.cardMarket.account_management.account()
        account_json = account_response.json()

        for credit_type, value in account_json['account']['moneyDetails'].items():
            if credit_type in AccountCollector.CREDIT_TYPES:
                credit_gauge.add_metric([credit_type], value)

        unread_messages_gauge.add_metric([], account_json['account']['unreadMessages'])
        on_vacation_gauge.add_metric([], account_json['account']['onVacation'])

        yield credit_gauge
        yield unread_messages_gauge
        yield on_vacation_gauge