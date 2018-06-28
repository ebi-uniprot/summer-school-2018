import requests, sys

requestURL = "https://www.ebi.ac.uk/proteins/api/taxonomy/path/nodes?id=33090&depth=6&direction=BOTTOM&pageNumber=1&pageSize=200"

r = requests.get(requestURL, headers={ "Accept" : "application/json"})

if not r.ok:
  r.raise_for_status()
  sys.exit()

responseBody = r.text
print(responseBody)
