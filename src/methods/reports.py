from src.methods.methods import Methods
from typing import Optional
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

    def _get_reports(self) -> None:
        response = self._execute_get_request("reports")
        if response:
            self.reports = [report for report in response['reports']]
            self.report_ids = [report['id'] for report in response['reports']]  

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

    def _process_deltas(self) -> None:
        for report in self.deltas:
            report = json.dumps(report)
            result = self._execute_post_request('reports', report)
            if result == 200:
                logger.info("Successfully created report")
            else:
                logger.error("Result creation failed")
    
