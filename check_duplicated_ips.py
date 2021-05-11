import os
import configparser

PATH = "/etc/wireguard"


def main():
    ips = []
    dips = []
    files_to_check = []

    client_path = PATH + '/clients'
    for p in os.walk(client_path):
        for f in p[2]:
            if f.endswith(".conf"):
                files_to_check.append(f"{p[0]}/{f}")

    for f in files_to_check:
        print(f"Checking file: {f}")
        config = configparser.ConfigParser()
        config.read(f)
        ip = {'addr': config['Interface']['Address'], 'file': f}
        for oip in ips:
            if oip['addr'] == ip['addr']:
                dips.append([oip, ip])
                print(f"Found duplicated IP ({ip['addr']}) in two conflicting files: {ip['file']} and {oip['file']}")
        else:
            ips.append(ip)
    if dips:
        for dip in dips:
            print(dip)
        print(f"found a total of {len(dips)} duplicated IP's")


if __name__ == "__main__":
    main()
