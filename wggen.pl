#!/usr/bin/perl
use strict;
use warnings;

#=======================================================================================================================
# Global definitions
#=======================================================================================================================
my $WG_BASE_PATH = "/etc/wireguard/";
my $WG_CLIENT_BASE_PATH = "/etc/wireguard/clients";

#=======================================================================================================================
# Main function and entrypoint
# args: @ARGV
# returns: ---
#=======================================================================================================================
sub main() {

    if (! -f "/usr/bin/wg") {
        die "wg command not found. Have you installed wireguard?";
    }

    my @opts = @ARGV;
    my %client_state;
    my @actual_clients = ();
    my $first = shift(@opts);
    my $second = shift(@opts);

    # check if we have an endpoint for the clients to connect to, if no then just die
    if ($first eq "--endpoint") {
        $client_state{'SERVER'}{'endpoint'} = $second;
    } else {
        die "Please specify an endpoint using --endpoint [endpoint address]:[port]";
    }

    my @clients = @opts;

    if (@clients < 1) {
        die "Need at least one client.";
    }

    # generate directories and server keypair, die on failure
    die "Failed to create base directory structure: $!" unless make_directory_structure();
    die "Failed to generate server keypair: $!" unless generate_server_keypair();

    # generate client keypairs, warn on failure
    foreach my $client (@clients) {
        if ($client eq "SERVER") {
            warn "WGGEN: Cannot create client $client\: Invalid client name";
        } else {
            if (generate_client_keypair($client) != 0) {
                push @actual_clients, $client;
            } else {
                warn "Failed to generate client keypair for $client\: $!";
            }
        }
    }

    # read server config and build client_state hash
    my @server_keys = read_server_keys();
    $client_state{'SERVER'}{'privatekey'} = $server_keys[0];
    $client_state{'SERVER'}{'publickey'}  = $server_keys[1];

    # read only from actual clients, to filter out the ones which couldn't be created
    my $client_counter = 100;
    foreach my $client (@actual_clients) {
        my @client_keys = read_client_keys($client);
        if (exists $client_state{$client}) {
            warn "Failed to add client $client to list of prepared clients: client already exists";
        } else {
            $client_state{$client}{'privatekey'} = $client_keys[0];
            $client_state{$client}{'publickey'} = $client_keys[1];
            $client_state{$client}{'presharedkey'} = $client_keys[2];
            $client_state{$client}{'host_addr'} = $client_counter;
            $client_counter++;
        }
    }

    # build configs
    die "Failed to create server config. To retry, delete /etc/wireguard and re-run the script." unless generate_server_config(\@actual_clients, \%client_state);
    foreach my $client (@actual_clients) {
        warn "Failed to create config for client $client, skipping" unless generate_client_config($client, \%client_state);
    }

    print("WGGEN: Wireguard configurations for @actual_clients generated.\n");
    return();
}

#=======================================================================================================================
# generate the basic directory structure
# args: ---
# returns: true/false
#=======================================================================================================================
sub make_directory_structure() {
    # check if the directories are missing and then create them
    if (! -d $WG_BASE_PATH) {
        print("WGGEN: WireGuard config directory missing, creating $WG_BASE_PATH\n");
        system("mkdir -p $WG_BASE_PATH")
    }
    if (! -d $WG_CLIENT_BASE_PATH) {
        print("WGGEN: WireGuard client config directory missing, creating $WG_CLIENT_BASE_PATH\n");
        system("mkdir -p $WG_CLIENT_BASE_PATH")
    }

    # check if the directories exist after creation and return true
    if (-d $WG_BASE_PATH && -d $WG_CLIENT_BASE_PATH) {
        return 1;
    }

    # return false if creating the directories failed
    return 0;
}

#=======================================================================================================================
# make the basic client directory
# args: client
# returns: true/false
#=======================================================================================================================
sub generate_client_keypair($) {
    my $client = shift();
    my $client_path = $WG_CLIENT_BASE_PATH . "/" . $client;

    # check if the client subdir already exists, if not create it
    if (! -d $client_path) {
        print("WGGEN: Client directory for client $client is missing, creating $client_path\n");
        system("mkdir -p $client_path");
    }

    # skip key generation if the keys already exist
    if (-f $client_path . "/privatekey" && -f $client_path . "/publickey" && -f $client_path . "/presharedkey") {
        print("WGGEN: Keys for client $client already exist. Skipping key generation\n");
        return 1;
    }

    # create keypairs
    print("WGGEN: Creating keypair for $client\n");
    system("umask 077; wg genkey | tee $client_path/privatekey | wg pubkey > $client_path/publickey");
    print("WGGEN: keypair for $client created\n");

    print("WGGEN: Creating preshared key for $client\n");
    system("umask 077; wg genpsk > $client_path/presharedkey");

    # check if all required files are present
    if (-f $client_path . "/privatekey" && -f $client_path . "/publickey" && -f $client_path . "/presharedkey") {
        return 1;
    }
    return 0;
}

#=======================================================================================================================
# Generate a config file for each client
# args: client, client_state
# returns: true/false
#=======================================================================================================================
sub generate_client_config($$) {
    my $client = shift();
    my $client_state = shift();

    my $server_public_key    = $client_state->{'SERVER'}->{'publickey'};
    my $client_private_key   = $client_state->{$client}->{'privatekey'};
    my $client_preshared_key = $client_state->{$client}->{'presharedkey'};
    my $client_host_part     = $client_state->{$client}->{'host_addr'};
    my $server_endpoint      = $client_state->{'SERVER'}->{'endpoint'};

    chomp($server_public_key);
    chomp($client_private_key);
    chomp($client_preshared_key);
    chomp($client_host_part);
    chomp($server_endpoint);

    my $BASE_CLIENT_CONFIG = "[Interface]\nPrivateKey = $client_private_key\nAddress =192.168.254.$client_host_part/24\nDNS =\n\n[Peer] # wireguard server\nPublicKey = $server_public_key\nPresharedKey = $client_preshared_key\nAllowedIPs =\nEndpoint =$server_endpoint\nPersistentKeepalive = 20";

    # check if client config already exists
    if (-f $WG_CLIENT_BASE_PATH . "/" . $client . "/wg0-$client.conf" ) {
        print("WGGEN: Config for client $client already exists, skipping\n");
        return 1;
    }

    # write server config
    chomp($BASE_CLIENT_CONFIG);
    open(my $fh, ">", $WG_CLIENT_BASE_PATH . "/" . $client . "/wg0-$client.conf") or return 0;
        print $fh $BASE_CLIENT_CONFIG;
    close $fh or return 0;
    print("WGGEN: Client config for $client written\n");

    # check if client config was written successfully
    if (-f $WG_CLIENT_BASE_PATH . "/" . $client . "/wg0-$client.conf" ) {
        print("WGGEN: Config for client $client written\n");
        return 1;
    }

    return 0;
}

#=======================================================================================================================
# Generate the config file for the server
# args: client_state (data of ALL clients)
# returns: true/false
#=======================================================================================================================
sub generate_server_config($$) {
    my $clients = shift();
    my $client_state = shift();

    # create basic server config
    my $server_private_key = $client_state->{'SERVER'}->{'privatekey'};

    chomp($server_private_key);

    my $BASE_SERVER_CONFIG = "[Interface] # wireguard server\nAddress =192.168.254.1/24\nListenPort = 51820\nPrivateKey = $server_private_key\nPostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -A FORWARD -o wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o ens192 -j MASQUERADE\nPostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -D FORWARD -o wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o ens192 -j MASQUERADE\n";

    # append peer sections
    foreach my $client (@$clients) {
        my $client_public_key    = $client_state->{$client}->{'publickey'};
        my $client_preshared_key = $client_state->{$client}->{'presharedkey'};
        my $client_host_part     = $client_state->{$client}->{'host_addr'};

        chomp($client_public_key);
        chomp($client_preshared_key);
        chomp($client_host_part);

        my $CLIENT_SECTION = "\n[Peer] # $client\nPublicKey = $client_public_key\nPresharedKey = $client_preshared_key\nAllowedIPs = 192.168.254.$client_host_part/32\n";
        $BASE_SERVER_CONFIG = $BASE_SERVER_CONFIG . $CLIENT_SECTION;
    }

    # write server config
    chomp($BASE_SERVER_CONFIG);
    open(my $fh, ">", $WG_BASE_PATH . "/wg0.conf") or return 0;
        print $fh $BASE_SERVER_CONFIG;
    close $fh or return 0;
    print("WGGEN: Server config written\n");

    # return success
    return 1;
}

#=======================================================================================================================
# generate server keypair
# args: ---
# returns: true/false
#=======================================================================================================================
sub generate_server_keypair() {

    # check if server keys already exist
    if (-f $WG_BASE_PATH . "/privatekey" && -f $WG_BASE_PATH . "/publickey") {
        print("WGGEN: SERVER keypair already exists\n");
        return 1;
    }

    # create server keypair
    print("WGGEN: Creating SERVER keypair\n");
    system("umask 077; wg genkey | tee $WG_BASE_PATH/privatekey | wg pubkey > $WG_BASE_PATH/publickey");

    # check if creation was successful
    if (-f $WG_BASE_PATH . "/privatekey" && -f $WG_BASE_PATH . "/publickey") {
        print("WGGEN: Successfully created SERVER keypair\n");
        return 1;
    }

    return 0;
}

#=======================================================================================================================
# Read client data
# args: client name
# returns: array(privatekey, publickey, presharedkey)
#=======================================================================================================================
sub read_client_keys($) {
    my $client = shift();
    my $fh;
    my $private_key = undef;
    my $public_key = undef;
    my $preshared_key = undef;

    # read privatekey
    open($fh, "<", $WG_CLIENT_BASE_PATH . "/" . $client . "/privatekey") or return 0;
        while(<$fh>) {
            $private_key = $_;
        }
    close $fh;

    # read publickey
    open($fh, "<", $WG_CLIENT_BASE_PATH . "/" . $client . "/publickey") or return 0;
        while(<$fh>) {
            $public_key = $_;
        }
    close $fh;

    # read presharedkey
    open($fh, "<", $WG_CLIENT_BASE_PATH . "/" . $client . "/presharedkey") or return 0;
        while(<$fh>) {
            $preshared_key = $_;
        }
    close $fh;

    # check if reading the keys was successful
    if (defined $private_key && defined $public_key && defined $preshared_key) {
        return ($private_key, $public_key, $preshared_key);
    }

    return 0;

}

#=======================================================================================================================
# Read server data
# args: ---
# returns: array(privatekey, publickey)
#=======================================================================================================================
sub read_server_keys() {
    my $fh;
    my $private_key = undef;
    my $public_key = undef;

    # read privatekey
    open($fh, "<", $WG_BASE_PATH . "/privatekey") or return 0;
        while(<$fh>) {
            $private_key = $_;
        }
    close $fh;

    # read publickey
    open($fh, "<", $WG_BASE_PATH . "/publickey") or return 0;
        while(<$fh>) {
            $public_key = $_;
        }
    close $fh;

    # check if reading the keys was successful
    if (defined $private_key && defined $public_key) {
        return ($private_key, $public_key);
    }

    return 0;
}

#=======================================================================================================================
# call entrypoint
#=======================================================================================================================
main();