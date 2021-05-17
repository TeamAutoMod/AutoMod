import argparse



class Arguments(argparse.ArgumentParser):
    def error(self, message):
        raise RuntimeError(message)