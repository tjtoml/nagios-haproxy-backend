#! /usr/bin/env python3
import csv
import requests

url = "http://10.14.68.17:8443/stats;csv"
service = "RANCHER_SERVER_HTTPS_backend"
service_to_check = []
timeout = 10

with requests.get(url, stream=True) as r:
    lines = (line.decode('utf-8') for line in r.iter_lines())
    for row in csv.reader(lines):
        if row[0] == service:
            service_to_check.append(row)


number_of_backends = 0
downed_backends = 0

for line in service_to_check:
    if line[1] != "BACKEND":
        number_of_backends += 1
        if line[17] != "UP":
            downed_backends += 1


print("Number of backends: ", number_of_backends, "| downed: ",
      downed_backends)

