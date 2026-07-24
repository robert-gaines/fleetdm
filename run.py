from src.methods.methods import Methods
from src.methods.reports import Reports
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("-tkn", "--token", help="API Token")
args = parser.parse_args()

if args.token:
    m = Methods(args.token)
    m._check_authentication()
    r = Reports(parent=m)
    r._purge_directory('src/data/reports')
    r._export_reports()
    # r._get_reports()
    # r._compare_reports()
    # r._process_deltas()
