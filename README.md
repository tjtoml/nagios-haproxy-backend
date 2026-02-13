[![Pylint](https://github.com/tjtoml/nagios-haproxy-backend/actions/workflows/pylint.yml/badge.svg)](https://github.com/tjtoml/nagios-haproxy-backend/actions/workflows/pylint.yml)
# nagios-haproxy-backend  

## Description
[Nagios](https://www.nagios.org) check for a haproxy frontend using the built-in stats interface. Written in `python3` to utilize the built-in [`haproxy`](https://www.haproxy.org/) HTTP stats interface. Simply checks the number of backends that are passing the `haproxy` health checks against expected values. 

## Dependencies

`requests` - use your system package manager or `pip` to install.
```shell
dnf install python3-requests #RedHat family
pacman -S pacman-requests #Arch 
apt install python3-requests #Debian/Ubuntu family
pip3 install requests #pip
```

Create a stats frontend in `haproxy.cfg` that is accessible to the machine running the check:
```HAproxy
frontend stats
    bind 10.10.10.10:8443 
    stats enable
    stats uri /stats
    stats refresh 10s
# consult the haproxy documentation - you probably don't want this open to the world, but this should get you going.
```

## Usage
```shell
usage: check_haproxy_backend.py [-h] -U URL -B BACKEND [-T TIMEOUT] [-v] (-w WARN | -W WARN_PERCENTAGE) (-c CRIT |
                                -C CRIT_PERCENTAGE)

Nagios check script to check a haproxy backend via the http stats interface

options:
  -h, --help            show this help message and exit
  -U, --url URL         The URL of the haproxy stats interface. Must be accessible without authentication and allow csv
                        data (enabled by default). Example: http://1.2.3.4:8443/stats
  -B, --backend BACKEND
                        Which backend to check. Name must match exactly what is shown in the stats interface.
  -T, --timeout TIMEOUT
                        Timeout to pull the stats data in seconds. default is 10s.
  -v, --verbose         Show verbose error message
  -w, --warn WARN       If the number of backends up is less than this the check will result in a WARNING state.
  -W, --warn_percentage WARN_PERCENTAGE
                        If the percentage of backends up is less than this the check will result in a WARNING state.
  -c, --crit CRIT       If the number of backends is less than this check will result in a CRITICAL state.
  -C, --crit_percentage CRIT_PERCENTAGE
                        If the percentage of backends up is less than this check will result in a CRITICAL state.
```

The `warn`, `crit`, `crit_percentage`, and `warn_percentage` represent the *minimum* number of backend servers that `haproxy` reports in an `UP` state in order to pass the check - which will usually mean that the `CRITICAL` value will be less than the `WARNING` value. For example, consider a backend `example_backend` with 10 servers, 6 `UP` and 4 `DOWN`:  
  
`check_haproxy_backend.py --url=10.10.10.10:8443/stats --backend=example_backend --warn=6 --crit=5`  
  
will result in an OK state because the minimum of 6 for a `WARNING` condition is met.   
  
Changing the `warn` and `crit` flags:
`check_haproxy_backend.py --url=10.10.10.10:8443/stats --backend=example_backend --warn=7 --crit=6`  
  
will result in a `WARNING` state because the number of `UP` backend servers is less than the `warn` flag. 

The `crit` flag takes precedence over the `warn` flag:
`check_haproxy_backend.py --url=10.10.10.10:8443/stats --backend=example_backend --warn=6 --crit=8`  
  
will result in a `CRITICAL` because the number of `UP` backend servers is less than 8. 

The percentage flags work the same way. Only reccomended if you have a large number of backend servers.

## Contributing
Pull requests welcomed. 
