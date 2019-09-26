import requests


class MyRequest(object):

    def __init__(self, data):
        self.method = data.get('request_type').strip()
        self.url = data.get('request_url').strip()
        self.params = {}
        for dic in data.get('request_params'):
            self.params[dic['key']] = dic['value']
        self.headers = {}
        for dic in data.get('header_params'):
            self.headers[dic['key']] = dic['value']

    def start(self):
        if self.method == 'get':
            response = requests.request(self.method, self.url, headers=self.headers, params=self.params, timeout=30)
        else:
            response = requests.request(self.method, self.url, headers=self.headers, data=self.params, timeout=30)

        return response
