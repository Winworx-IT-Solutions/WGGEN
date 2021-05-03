import sys


class Logger:
    @staticmethod
    def fatal(error):
        print("FATAL: {}".format(error))
        sys.exit()

    @staticmethod
    def error(error):
        print("ERROR: {}".format(error))

    @staticmethod
    def warn(error):
        print("WARN: {}".format(error))

    @staticmethod
    def info(error):
        print("INFO: {}".format(error))
