[![Pylint](https://github.com/tjtoml/nagios-haproxy-backend/actions/workflows/pylint.yml/badge.svg)](https://github.com/tjtoml/nagios-haproxy-backend/actions/workflows/pylint.yml)
# nagios-haproxy-backend  

## Description
[Nagios](https://www.nagios.org) check for a haproxy frontend using the built-in stats interface. Written in `python3` to utilize the built-in [`haproxy`](https://www.haproxy.org/) HTTP stats interface. Simply checks the number of backends that are passing the `haproxy` health checks against expected values. 

## Usage
Create a stats frontend in `haproxy.cfg`:
```HAproxy
frontend stats
    bind 0.0.0.0:8443 
    stats enable
    stats uri /stats
    stats refresh 10s
# consult the haproxy documentation - you probably don't want this open to the world!
```

