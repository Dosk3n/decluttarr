import json
import urllib.request
import urllib.error

class SonarrApiCaller:
    def __init__(self, host, apikey):
        self.host = host
        self.apikey = apikey
        self.apiEndPoint = f"{self.host}/api/v3"

    def make_request(self, endpoint, method='GET', data=None):
        try:
            url = f"{self.apiEndPoint}/{endpoint}?apikey={self.apikey}"

            if method in ('POST', 'PUT') and data is not None:
                json_data = json.dumps(data).encode('utf-8')
                req = urllib.request.Request(url, data=json_data, method=method, headers={'Content-Type': 'application/json'})
            else:
                req = urllib.request.Request(url)

            with urllib.request.urlopen(req) as response:
                data = response.read()

                if response.getcode() == 200:
                    return json.loads(data.decode('utf-8'))
                else:
                    return False
        except urllib.error.URLError as e:
            error_msg = f"Error making API request: {e}"
            return error_msg

    def get_curr_commands(self):
        return self.make_request('command')

    def get_root_folders(self):
        return self.make_request('rootfolder')

    def get_series(self):
        return self.make_request('series')

    def get_series_by_id(self, series_id):
        return self.make_request(f'series/{series_id}')

    def update_series(self, series_json):
        return self.make_request('series', method='PUT', data=series_json)

    def series_search(self, series_id):
        data = {
            "name": "seriesSearch",
            "seriesId": int(series_id)
        }
        return self.make_request('command', method='POST', data=data)
