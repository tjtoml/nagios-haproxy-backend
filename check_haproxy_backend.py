#! /usr/bin/env python3
""" Nagios check for a haproxy backend """
import sys
import argparse
import csv
import requests

# TODO: Implement authentication methods supported by haproxy
# TODO: Add option to disable strict SSL cert checking
# TODO: Add ability to connect to local unix socket for stats connection

def parse_arguments():
    """ Parses the arguments passed to the script. """
    parser = argparse.ArgumentParser(
        prog='check_haproxy_backend.py',
        description='''Nagios check script to check a haproxy backend via the
        http stats interface''')

    parser.add_argument('-U', '--url', required=True,
                        help='''The URL of the haproxy stats interface. Must be
                        accessible without authentication and allow
                        csv data (enabled by default).
                        Example: http://1.2.3.4:8443/stats ''')

    parser.add_argument('-B', '--backend', required=True,
                        help='''Which backend to check. Name must match exactly
                        what is shown in the stats interface.''')

    parser.add_argument('-T', '--timeout', type=int,
                        help='''Timeout to pull the stats data in seconds.
                        default is 10s.''',
                        nargs=1,
                        default=10)

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='''Show verbose error message''')

    warn_group = parser.add_mutually_exclusive_group(required=True)

    warn_group.add_argument('-w', '--warn', type=int,
                        help='''If the number of backends up is less than or
                            equal to this the check will result in a WARNING state.''')
    warn_group.add_argument('-W', '--warn_percentage', type=int,
                            help='''If the percentage of backends up is less
                            than or equal to this the check will result in a WARNING state.''')

    crit_group = parser.add_mutually_exclusive_group(required=True)

    crit_group.add_argument('-c', '--crit', type=int,
                        help='''If the number of backends is less than or equal
                            to this check will result in a CRITICAL state.''')
    crit_group.add_argument('-C', '--crit_percentage', type=int,
                            help='''If the percentage of backends up is less
                            than or equal to this check will result in a
                            CRITICAL state.''')

    parsed_args = parser.parse_args()

    return parsed_args

def get_status(args, number_of_backends, downed_backends):
    """ Gets the output and prints the status code"""
    backends_up = number_of_backends - downed_backends
    status_message = ""
    up_percent = round((backends_up / number_of_backends)*100)
    exit_code = 0

    if args.crit_percentage:
        if up_percent <= args.crit_percentage:
            status_message = ( status_message + args.backend + " has " +
            str(up_percent) + "% of backends up.")
            exit_code = 2

    if args.crit:
        if backends_up <= args.crit:
            status_message = (status_message + args.backend + " has " +
                              str(backends_up) + " backends up.")
            exit_code = 2

    if exit_code == 2:
        print("CRITICAL: " + status_message)
        sys.exit(exit_code)

    if args.warn_percentage:
        if up_percent <= args.warn_percentage:
            status_message = ( status_message + args.backend + " has " +
            str(up_percent) + "% of backends up.")
            exit_code = 1

    if args.warn:
        if backends_up <= args.warn:
            status_message = (status_message + args.backend + " has " +
                              str(backends_up) + " backends up.")
            exit_code = 1

    if exit_code == 1:
        print("WARNING: " + status_message)
        sys.exit(exit_code)

    print("OK: " + args.backend + " is up.")
    sys.exit(0)

def main():
    """ Checks a haproxy backend. """
    backend_to_check = []
    _args = parse_arguments()


    try:
        r = requests.get(_args.url + ";csv", stream=True, timeout=_args.timeout)
        lines = (line.decode('utf-8') for line in r.iter_lines())
        for row in csv.reader(lines):
            if row[0] == _args.backend:
                backend_to_check.append(row)
    except requests.exceptions.Timeout:
        print("UNKNOWN: Check of stats at" + _args.url + """ timed out. Check config!""")
        sys.exit(3)
    except requests.exceptions.ConnectionError as e:
        print("UNKNOWN: Error connecting to haproxy stats at " + _args.url +
             " - Check config!")
        if _args.verbose:
            print(e)
        sys.exit(3)
    except requests.exceptions.RequestException as e:
        print("UNKNOWN: an unexpected error occurred. " +
              "Pass -v or --verbose to see full traceback.")
        if _args.verbose:
            print(e)
        sys.exit(3)

    _number_of_backends = 0
    _downed_backends = 0

    if len(backend_to_check) == 0:
        print("UNKNOWN: No backend named " + _args.backend + """ found. Check config!""")
        sys.exit(3)

    for line in backend_to_check:
        if line[1] != "BACKEND":
            _number_of_backends += 1
            if line[17] != "UP":
                _downed_backends += 1


    get_status(_args, _number_of_backends, _downed_backends)

if __name__ == "__main__":
    main()
