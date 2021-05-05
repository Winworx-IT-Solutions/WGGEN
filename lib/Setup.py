import os
from lib.Utils import Logger
from lib.ServerTools import ServerTools


class Setup:
    @staticmethod
    def check_prerequisits():
        if not os.path.isfile("/usr/bin/wg"):
            Logger.fatal("wg command not found. Have you installed WireGuard?")
        if not os.path.isfile("/usr/bin/qrencode"):
            Logger.fatal("qrencode command not found. Have you installed qrencode?")
        if not os.getuid() == 0:
            Logger.fatal("This script needs to be run with Root-Privileges")

    @staticmethod
    def start(wg_base_path, wg_client_base_path):
        if not Setup.initialize_directory_structure(wg_base_path, wg_client_base_path):
            Logger.fatal("Failed to generate base directory structure")
        if not ServerTools.generate_server_keypair(wg_base_path):
            Logger.fatal("Failed to generate server keypair")

    @staticmethod
    def initialize_directory_structure(wg_base_path, wg_client_base_path):
        """
        Checks for required directories and attempts to create them if they are missing

        :return: True or False depending on if the creation of the directories was successful
        """
        # check and create base config dir
        if not os.path.isdir(wg_base_path):
            print("WGGEN: WireGuard config directory is missing, creating: {}".format(wg_base_path))
            try:
                os.makedirs(wg_base_path, exist_ok=True)
            except OSError:
                print("Failed to create WireGuard config directory: {}".format(wg_base_path))

        # check and create client config dir
        if not os.path.isdir(wg_client_base_path):
            print("WGGEN: WireGuard config client directory is missing, creating: {}".format(
                wg_client_base_path))
            try:
                os.makedirs(wg_client_base_path, exist_ok=True)
            except OSError:
                print("Failed to create WireGuard client config directory: {}".format(
                    wg_client_base_path))

        # check if we were able to create the config directories
        if os.path.isdir(wg_base_path) and os.path.isdir(wg_client_base_path):
            return True
        else:
            Logger.fatal("Could not create directory structure")
