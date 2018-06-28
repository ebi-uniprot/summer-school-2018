import requests, sys
import json

def make_req(req_url):
    r = requests.get(req_url, headers={"Accept": "application/json"})

    if not r.ok:
        r.raise_for_status()
        sys.exit()

    jason_obj = json.loads(r.text)
    return jason_obj

class ResultsPageInfo:
    def __init__(self, json_obj):
        page_info = json_obj['pageInfo']  # 'pageInfo': {'totalRecords': 198929, 'currentPage': 1, 'resultsPerPage': 7}
        self.total_records = int(page_info['totalRecords'])
        self.cur_page = int(page_info['currentPage'])
        self.results_per_page = int(page_info['resultsPerPage'])

    def has_more_pages(self):
        return self.cur_page * self.results_per_page <= self.total_records
