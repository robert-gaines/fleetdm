from src.methods.methods import Methods
from typing import Optional
import pandas as pd
import requests
import logging
import urllib3
import yaml
import json
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s][%(levelname)s][%(message)s]') # noqa

logger = logging.getLogger(__name__)


class Reports(Methods):

    def __init__(self,
                 token: Optional[str] = None,  # noqa: UP045
                 parent: Optional[Methods] = None) -> None:  # noqa: UP045
        current_directory = os.getcwd()
        self.report_dir = f"{current_directory}/src/data/reports"
        self.deltas = []
        self.reports = []
        self.report_ids = []
        if parent is not None:
            self.session = parent.session
            self.headers = parent.headers
            self.url = parent.url
        else:
            super().__init__(token or "")

    def _sanitize_report(self, report) -> dict:
        superfluous_keys = ['created_at',
                            'updated_at',
                            'fleet_id',
                            'labels_include_any',
                            'labels_include_all'
                            ]
        for key in superfluous_keys:
            if key in report:
                del report[key]
        return report

    def _get_reports(self) -> None:
        response = self._execute_get_request("reports")
        if response:
            self.reports = [report for report in response['reports']]
            self.report_ids = [report['id'] for report in response['reports']]

    def _list_reports(self) -> None:
        response = self._execute_get_request("reports")
        if response:
            for report in response['reports']:
                id = report['id']
                name = report['name']
                platform = report['platform']
                logger.info(f"{id}:{name}:{platform}")

    def _export_reports(self) -> None:
        response = self._execute_get_request("reports")
        for report in response['reports']:
            platforms = report['platform'].split(',')
            filename = self._create_filename(report['name'])
            if len(platforms) > 1:
                self._export_data_to_file(
                    f"{self.report_dir}/multiple/{filename}",
                    report)
            if len(platforms) == 1:
                self._export_data_to_file(
                    f"{self.report_dir}/{platforms[0]}/{filename}",
                    report)

    def _compare_reports(self) -> None:
        ''' Compare definitions with remote values '''
        report_data = []
        for directory in os.listdir(self.report_dir):
            for file in os.listdir(f"{self.report_dir}/{directory}"):
                if file.endswith('.yaml'):
                    with open(
                            f"{self.report_dir}/{directory}/{file}", 'r')\
                                  as fobj:
                        data = yaml.safe_load(fobj)
                        report_data.append(data)
        logger.info(f"Ingested: {len(report_data)} local report definitions")
        self.deltas = [report for report in report_data
                       if report not in self.reports]

    def _process_updates(self) -> None:
        ''' Process local updates '''
        remote_reports = {}
        report_data = {}
        for directory in os.listdir(self.report_dir):
            for file in os.listdir(f"{self.report_dir}/{directory}"):
                if file.endswith('.yaml'):
                    with open(
                            f"{self.report_dir}/{directory}/{file}", 'r')\
                                    as fobj:
                        data = yaml.safe_load(fobj)
                        report_data[data['id']] = data
        if self.reports:
            for report in self.reports:
                remote_reports[report['id']] = report
        for report in report_data.keys():  # noqa: PLC0206, SIM118
            local_report = report_data[report]
            remote_report = remote_reports[report]
            if local_report != remote_report:
                modified_report = self._sanitize_report(local_report)
                modified_report = json.dumps(modified_report)
                result = self._execute_patch_request(f'reports/{report}',
                                                     modified_report)
                if result == 200:
                    logger.info(f"Updated: {report_data[report]['id']}")
                else:
                    logger.info(f"Failure: {report_data[report]['id']}")

    def _process_deltas(self) -> None:
        ''' Identify and submit new local reports '''
        for report in self.deltas:
            report = json.dumps(report)
            result = self._execute_post_request('reports', report)
            if result == 200:
                logger.info("Successfully created report")
            else:
                logger.error("Result creation failed")

    def _execute_report(self, report_id: str, host_ids: list) -> None:
        ''' Execute a live report for specific hosts '''
        payload = json.dumps({"host_ids": host_ids})
        response = \
            self._execute_post_request_return_data(f"reports/{report_id}/run",
                                                   payload)
        logger.info(response)

    def _delete_report(self, report_id: str) -> None:
        result = self._execute_delete_request(f'reports/id/{report_id}')
        if result == 200:
            self._purge_directory('src/data/reports')
            self._export_reports()
            logger.info(f"Removed: {report_id}")
        else:
            logger.error(f"Failed to remove: {report_id}")

