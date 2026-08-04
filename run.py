import token

from src.methods.methods import Methods
from src.methods.reports import Reports
from src.methods.hosts import Hosts
from argparse import ArgumentParser
import time

parser = ArgumentParser()
parser.add_argument("-tkn", "--token", help="API Token")
parser.add_argument("-lsr", "--list-reports", action='store_true', help="List Reports") # noqa
parser.add_argument("-crp", "--create-reports", action='store_true', help="Create Reports") # noqa
parser.add_argument("-exr", "--export-reports", action='store_true', help="Export Reports") # noqa
parser.add_argument("-urp", "--update-reports", action='store_true', help="Update Reports") # noqa
parser.add_argument("-erp", "--execute-report", help="Execute report")
parser.add_argument("-ptf", "--platform", help="--platform <platform>")
args = parser.parse_args()


def list_reports(token: str):  # noqa: F811
    m = Methods(token)
    m._check_authentication()
    r = Reports(parent=m)
    r._list_reports()


def create_reports(token: str):  # noqa: F811
    m = Methods(token)
    m._check_authentication()
    r = Reports(parent=m)
    r._get_reports()
    r._compare_reports()
    r._process_deltas()
    time.sleep(5)
    r._purge_directory('src/data/reports')
    r._export_reports()


def update_reports(token: str):  # noqa: F811
    m = Methods(token)
    m._check_authentication()
    r = Reports(parent=m)
    r._get_reports()
    r._process_updates()
    r._purge_directory('src/data/reports')
    r._export_reports()


def execute_report(token: str, report_id: str, platform: str):   # noqa: F811
    m = Methods(token)
    m._check_authentication()
    r = Reports(parent=m)
    h = Hosts(parent=m)
    ids = h._get_host_ids_by_platform(platform)
    r._execute_report(report_id, ids)


if args.token:
    """
    ToDo:
        - Delete
    """
    if args.list_reports:
        list_reports(args.token)
    if args.create_reports:
        create_reports(args.token)
    if args.update_reports:
        update_reports(args.token)
    if args.execute_report and args.platform:
        execute_report(args.token,
                       args.execute_report,
                       args.platform)
    # r._get_reports()
    # r._process_updates()
    # r._execute_report('31')
    # ids = h._get_host_ids_by_platform('windows')
    # r._execute_report('31', ids)
    # r._delete_report('48')