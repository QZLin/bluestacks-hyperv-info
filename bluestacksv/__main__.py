import argparse

import bluestacksv.probe_bluestacks_hyperv

parser = argparse.ArgumentParser()
parser.add_argument('--port', "-p", help='show port of bluestacks-hyper-v')

args = parser.parse_args()
result = bluestacksv.probe_bluestacks_hyperv.run(None, "")
print(result if result is None or len(result) != 1 else result[0])
