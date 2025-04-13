import requests

class HarvardDataverse:
    def __init__(self, dataset_id):
        self.dataset_id = dataset_id
        self.base_url = "https://dataverse.harvard.edu/api/datasets/"

    def fetch_data(self):
        url = f"{self.base_url}{self.dataset_id}/versions"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch data: {response.status_code} - {response.text}")
