from piawg import piawg
from pick import pick
from getpass import getpass
from datetime import datetime
import argparse

# Create parser
parser = argparse.ArgumentParser(description='Generate PIA config.')
parser.add_argument('--region', type=str, help='PIA region')
parser.add_argument('--username', type=str, help='PIA username')
parser.add_argument('--password', type=str, help='PIA password')
parser.add_argument('--output', type=str, help='Output file path')

# Parse arguments
args = parser.parse_args()

pia = piawg()

# Generate public and private key pair
pia.generate_keys()

# Select region
if args.region:
    pia.set_region(args.region)
    print("Selected '{}'".format(args.region))
else:
    title = 'Please choose a region: '
    options = sorted(list(pia.server_list.keys()))
    option, index = pick(options, title)
    pia.set_region(option)
    print("Selected '{}'".format(option))

# Get token
while True:
    username = args.username if args.username else input("\nEnter PIA username: ")
    password = args.password if args.password else getpass()
    if pia.get_token(username, password):
        print("Login successful!")
        break
    else:
        print("Error logging in, please try again...")

# Add key
status, response = pia.addkey()
if status:
    print("Added key to server!")
else:
    print("Error adding key to server")
    print(response)

# Build config
timestamp = int(datetime.now().timestamp())
location = pia.region.replace(' ', '-')
default_config_file = 'PIA-{}-{}.conf'.format(location, timestamp)
config_file = args.output if args.output else default_config_file
print("Saving configuration file {}".format(config_file))
with open(config_file, 'w') as file:
    file.write('[Interface]\n')
    file.write('Address = {}\n'.format(pia.connection['peer_ip']))
    file.write('PrivateKey = {}\n'.format(pia.privatekey))
    file.write('DNS = {},{}\n\n'.format(pia.connection['dns_servers'][0], pia.connection['dns_servers'][1]))
    file.write('[Peer]\n')
    file.write('PublicKey = {}\n'.format(pia.connection['server_key']))
    file.write('Endpoint = {}:1337\n'.format(pia.connection['server_ip']))
    file.write('AllowedIPs = 0.0.0.0/0\n')
    file.write('PersistentKeepalive = 25\n')
