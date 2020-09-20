import re
from prometheus_client.core import GaugeMetricFamily

COUNT_KEY = 'count'
PRICE_KEY = 'price'
DICT_INIT = {COUNT_KEY: 0, PRICE_KEY: 0}
CALCULATION_FUNCTIONS = {
        COUNT_KEY: lambda article: article['count'], 
        PRICE_KEY: lambda article: article['count'] * article['price']
    }

def analyzeArticles(json, partial_result = {}):
    if partial_result == {}:
        partial_result = {'total': {}, 'condition': {}, 'language': {}}

    analyzeArticlesByFunction(json, partial_result['total'], CALCULATION_FUNCTIONS, lambda article: '' )
    analyzeArticlesByFunction(json, partial_result['condition'], CALCULATION_FUNCTIONS, lambda article: article['condition'] if ('condition' in article) else None)
    analyzeArticlesByFunction(json, partial_result['language'], CALCULATION_FUNCTIONS, lambda article: article['language']['languageName'] if ('language' in article) else None)

    return partial_result

def analyzeArticlesByFunction(json, result_dict, calculation_functions, selection_function = None):
    write_dict = result_dict

    for article in json['article']:
        if selection_function is not None:
            attribute_value = selection_function(article)
            if attribute_value is None:
                continue
            else:
                if attribute_value not in result_dict:
                    result_dict[attribute_value] = {}
                write_dict = result_dict[attribute_value]

        for dict_key, calculation_function in calculation_functions.items():
            value = calculation_function(article)
            if dict_key not in write_dict:
                write_dict[dict_key] = 0
            write_dict[dict_key] += value

def getArticleGauges(result_dict, main_name, additional_labels = {}):
    for category_name, category_dict in result_dict.items():
        for calculation_type in CALCULATION_FUNCTIONS:
            gauge = GaugeMetricFamily(main_name + '_' + category_name + '_' + calculation_type, '', labels=[category_name] + list(additional_labels.keys()))
            for category, value_dict in category_dict.items():
                gauge.add_metric([category] + list(additional_labels.values()), value_dict[calculation_type])
            yield gauge

def checkForNextPage(response, func, *args, **kwargs):
    if response.status_code == 206:
        match = re.search(r'(\d+)-(\d+)/(\d+)', response.headers["Content-Range"])
        if int(match.group(2)) < int(match.group(3)):
            return func(start=int(match.group(2)) + 1, **kwargs)
    return None