import json
import urllib.request
import urllib.error

class TautulliApiHandler:
    def __init__(self, host, apikey):
        self.host = host
        self.apikey = apikey
        self.apiEndPoint = f"{self.host}/api/v2"

    def make_request(self, cmd, params=None):
        try:
            url = f"{self.apiEndPoint}?apikey={self.apikey}&cmd={cmd}"
            if params:
                for key, value in params.items():
                    url += f"&{key}={value}"

            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as response:
                data = response.read()

                if response.getcode() == 200:
                    return json.loads(data.decode('utf-8'))
                else:
                    return False
        except urllib.error.URLError as e:
            print(f"Error making API request: {e}")
            return False

    def get_activity(self):
        return self.make_request("get_activity")

    def get_history(self, **kwargs):
        params = {}
        for key, value in kwargs.items():
            if value is not None:
                params[key] = value
        return self.make_request("get_history", params=params)

    def terminate_session(self, sessionKey, message="SESSION TERMINATED"):
        params = {"session_key": sessionKey, "message": message}
        return self.make_request("terminate_session", params=params)

