import requests

class RestClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def get(self, endpoint, headers=None, params=None):
        url = self.base_url + endpoint
        response = requests.get(url, headers=headers, params=params)
        return response

    def post(self, endpoint, headers=None,data=None, params=None, json=None,files=None):
        url = self.base_url + endpoint
        response = requests.post(url, headers=headers,data=data, params=params, json=json,files=files)
        return response

    def put(self, endpoint, headers=None, params=None, json=None):
        url = self.base_url + endpoint
        response = requests.put(url, headers=headers, params=params, json=json)
        return response

    def delete(self, endpoint, headers=None, params=None):
        url = self.base_url + endpoint
        response = requests.delete(url, headers=headers, params=params)
        return response
