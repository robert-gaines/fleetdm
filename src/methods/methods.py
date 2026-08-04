import requests
import logging
import urllib3
import yaml
import os
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s][%(levelname)s][%(message)s]'
)

logger = logging.getLogger(__name__)


class YamlExporter:

    class IndentExporter(yaml.SafeDumper):
        def increase_indent(self, flow=False, indentless=False):
            '''Optimize yaml structure to appease the linter'''
            return super(YamlExporter.IndentExporter, self).increase_indent(flow,  # noqa
                                                                            False) # noqa

    def export_to_file(self, output_path: str, data: dict) -> str:
        ''' Export the query or alert to a yaml file '''
        with open(output_path, 'w', encoding='utf-8') as fobj:
            fobj.write('---\n')
            yaml.dump(
                data,
                fobj,
                sort_keys=False,
                default_flow_style=False,
                Dumper=YamlExporter.IndentExporter,
            )
        return output_path


class Methods:

    def __init__(self, token: str) -> None:
        current_directory = os.getcwd()
        configuration = \
            f"{current_directory}/src/configuration/configuration.yaml"
        self.session = requests.Session()
        if os.path.exists(configuration):
            with open(configuration, 'r') as fobj:
                data = yaml.safe_load(fobj)
                configuration = data['configuration']
                fqdn = configuration['fqdn']
                port = configuration['port']
            self.headers = {
                'Authorization': f"Bearer {token}"
            }
            self.url = f"https://{fqdn}:{port}/api/v1/fleet/"
        else:
            logger.error(
                "Failed to locate configuration file"
            )

    def _create_filename(self, input: str) -> str:
        try:
            res = re.sub(r'[^a-zA-Z0-9]', '_', input)
            res = res.lower() + '.yaml'
            res = res.replace('__', '_')
            return res
        except Exception:
            logger.exception("Exception raised")
            return ''

    def _export_data_to_file(self, output_path: str, data: dict) -> str:
        ''' Export dictionary formatted data to a yaml file '''
        exporter = YamlExporter()
        return exporter.export_to_file(output_path, data)

    def _purge_directory(self, path: str) -> None:
        ''' Export dictionary formatted data to a yaml file '''
        current_directory = os.getcwd()
        for directory in os.listdir(f"{current_directory}/{path}"):
            sub_dir = f"{current_directory}/{path}/{directory}"
            for file in os.listdir(sub_dir):
                if file.endswith('.yaml'):
                    os.remove(f"{sub_dir}/{file}")

    def _check_authentication(self) -> bool:
        try:
            response = self.session.get(url=f"{self.url}me",
                                        headers=self.headers,
                                        verify=False)
            if 'name' in response.json()['user']:
                logger.info(f"User: {response.json()['user']['name']}")
            return response.status_code == 200
        except requests.RequestException:
            logger.exception("Exception raised")
            return False

    def _execute_get_request(self, path: str) -> dict:
        try:
            response = self.session.get(url=f"{self.url}{path}",
                                        headers=self.headers,
                                        verify=False)
            return response.json()
        except requests.RequestException:
            logger.exception("Exception raised")
            return {}

    def _execute_post_request(self, path: str, payload: str) -> int:
        try:
            response = self.session.post(url=f"{self.url}{path}",
                                         headers=self.headers,
                                         data=payload,
                                         verify=False)
            return response.status_code
        except requests.RequestException:
            logger.exception("Exception raised")
            return 0

    def _execute_post_request_return_data(self, path: str, payload: str) -> dict:
        try:
            response = self.session.post(url=f"{self.url}{path}",
                                         headers=self.headers,
                                         data=payload,
                                         verify=False)
            return response.json()
        except requests.RequestException:
            logger.exception("Exception raised")
            return {}

    def _execute_patch_request(self, path: str, payload: str) -> int:
        try:
            response = self.session.patch(url=f"{self.url}{path}",
                                          headers=self.headers,
                                          data=payload,
                                          verify=False)
            return response.status_code
        except requests.RequestException:
            logger.exception("Exception raised")
            return 0

    def _execute_delete_request(self, path) -> int:
        try:
            response = self.session.delete(url=f"{self.url}{path}",
                                           headers=self.headers,
                                           verify=False)
            return response.status_code
        except requests.RequestException:
            logger.exception("Exception raised")
            return 0
