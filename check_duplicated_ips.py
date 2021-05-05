import os
import configparser

PATH = "/etc/wireguard"


def main():
    ips = []
    files_to_check = []

    client_path = PATH + '/clients'
    for p in os.walk(client_path):
        for f in p[2]:
            if f.endswith(".conf"):
                files_to_check.append("{}/{}".format(p[0], f))

    for f in files_to_check:
        print("Checking file: {}".format(f))
        config = configparser.ConfigParser()
        config.read(f)
        ip = {'addr': config['Interface']['Address'], 'file': f}
        for oip in ips:
            if oip['addr'] == ip['addr']:
                print("Found duplicated IP ({}) in two conflicting files: {} and {}".format(ip['addr'],
                                                                                            ip['file'], oip['file']))
        else:
            ips.append(ip)


if __name__ == "__main__":
    main()
