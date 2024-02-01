import requests


class API:
    API_URL = "http://api:8000/"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json"
        })


    def verify_channel(self, channel_id: int):
        response = self.session.post(self.API_URL + 'channel/verify', json={
            'channel_id': channel_id
        })
        json_data = response.json()
        return json_data


    def get_channel_filters(self, channel_id: int):
        response = self.session.post(self.API_URL + 'channel/get_filters', json={
            'channel_id': channel_id
        })
        json_data = response.json()
        return json_data


    def delete_channel(self, channel_id: int):
        response = self.session.post(self.API_URL + 'channel/delete', json={
            'channel_id': channel_id
        })
        json_data = response.json()
        return json_data


    def update_channel_filters(self, channel_id: int, filters: dict):
        response = self.session.post(self.API_URL + 'channel/update_filters', json={
            'channel_id': channel_id,
            'filters': filters
        })
        json_data = response.json()
        return json_data


    def update_sports_filters(self, channel_id: int, sports: list):
        response = self.session.post(self.API_URL + 'channel/update_sports_filters', json={
            'channel_id': channel_id,
            'sports_data': sports
        })
        json_data = response.json()
        return json_data


    def get_channels(self):
        response = self.session.get(self.API_URL + 'data/channels')
        json_data = response.json()
        return json_data
