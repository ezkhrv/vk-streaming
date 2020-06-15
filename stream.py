import requests
import json

class Stream:
    OK_CODE = 200
    HEADERS = {'content-type': 'application/json'}
    def __init__(self, token):
        request_result = requests.get(
            f"https://api.vk.com/method/streaming.getServerUrl?access_token={token}&v=5.64")
        data = request_result.json()
        self.endpoint = data["response"]["endpoint"]
        self.key = data["response"]["key"]
        self.rules_url = f"https://{self.endpoint}/rules?key={self.key}"
        self.rule_number = 0

    def check_request_code(self, data):
        if data['code'] != self.OK_CODE:
            request_result = json.dumps(data, ensure_ascii=False)
            error_message = "Request returned code {data['code']}. Full request result: {request_result}"
            raise RuntimeError(error_message)

    def get_stream_url(self):
        return f"wss://{self.endpoint}/stream?key={self.key}"

    def get_rules(self):
        request_result = requests.get(self.rules_url)
        data = request_result.json()
        self.check_request_code(data)
        rules = data['rules'] if data['rules'] else []
        return rules

    def delete_rule(self, rule):
        request_result = requests.delete(self.rules_url, data=json.dumps(rule),
                                         headers=self.HEADERS)
        data = request_result.json()
        self.check_request_code(data)

    def add_rule(self, word):
        rule = {"rule": {"value": word, "tag": f"tag_{self.rule_number:03d}"}}
        request_result = requests.post(self.rules_url, data=json.dumps(rule), headers=self.HEADERS)
        data = request_result.json()
        self.check_request_code(data)
        self.rule_number += 1
