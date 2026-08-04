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


class Hosts(Methods):

    def __init__(self,
                 token: Optional[str] = None,  # noqa: UP045
                 parent: Optional[Methods] = None) -> None:  # noqa: UP045
        if parent is not None:
            self.session = parent.session
            self.headers = parent.headers
            self.url = parent.url
        else:
            super().__init__(token or "")

    def _list_hosts(self) -> None:
        '''List FleetDM Hosts'''
        response = self._execute_get_request('hosts')
        for record in response['hosts']:
            logger.info(
                f"{record['id']}:{record['platform']}:{record['hostname']}")

    def _get_host_ids_by_platform(self, platform: str) -> list:
        ''' Return host IDs by platform '''
        response = self._execute_get_request('hosts')
        if response:
            hosts = response['hosts']
            host_ids = [host['id'] for host in hosts
                        if host['platform'] == platform]
            return host_ids
        else:
            return []
