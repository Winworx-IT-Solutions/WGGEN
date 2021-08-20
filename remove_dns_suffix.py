
import os
import argparse
import configparser

PATH = "/etc/wireguard/clients"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--peers', type=str, nargs="+", help='Peer names wich should have the DNS suffix removed', required=True)
    parser.add_argument('-c', '--count', type=int, help='Number of Configs for each Peer name', required=True)
    parser.add_argument('-s', '--suffix', type=str, help='DNS Suffix to remove', required=True)

    args = parser.parse_args()

    files = []
    for p in args.peers:
        for i in range(0,args.count):
            files.append(f"{PATH}/{p}-{i}/wg0-{p}-{i}.conf")


    print(f"INFO: Removing DNS-Suffix {args.suffix} from {len(files)} peer configs")

    for f in files:
        if not os.path.isfile(f):
            print(f"ERROR: Could not fine config file for {f}")
        c = configparser.ConfigParser()
        c.read(f)
        DNS = str(c.get('Interface', 'DNS'))
        nDNS = DNS.replace(f"{args.suffix}", "")
        c.set('Interface', 'DNS', nDNS)

        with open(f, 'w') as cf:
            c.write(cf)

        print(f"Changed DNS from {DNS} to {nDNS} in {f}")


if __name__ == "__main__":
    main();
