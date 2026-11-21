import logging

import requests
from certbot import configuration, errors
from certbot.plugins.dns_common import DNSAuthenticator
from tldextract import tldextract

logger = logging.getLogger(__name__)

BASE_URL = "https://api.neostrada.com/api"

class Authenticator(DNSAuthenticator):
    """DNS Authenticator for Neostrada"""

    description = "Obtain certificates using a DNS TXT record via Neostrada DNS API."

    def __init__(self, config: configuration.NamespaceConfig, name: str):
        super().__init__(config, name)
        self.credentials = None

    @classmethod
    def add_parser_arguments(cls, add, default_propagation_seconds=60):
        super().add_parser_arguments(add, default_propagation_seconds)
        add("credentials", help="Neostrada credentials INI file.")

    def _setup_credentials(self) -> None:
        self.credentials = self._configure_credentials(
            "credentials",
            "Neostrada credentials INI file",
            {
                "api_key": "Neostrada API key"
            }
        )

    def _perform(self, domain: str, validation_name: str, validation: str) -> None:
        logger.info("Domain:" + domain)
        logger.info("Validation name: " + validation_name)
        logger.info("Validation: " + validation)
        self._get_neostrada_client().add_txt_record(domain, validation_name, validation)

    def _cleanup(self, domain: str, validation_name: str, validation: str) -> None:
        self._get_neostrada_client().del_txt_record(domain, validation_name, validation)

    def _get_neostrada_client(self):
        return _NeostradaClient(self.credentials.conf('api_key'))


class _NeostradaClient:

    def __init__(self, api_key):
        logger.info("Initiated new Neostrada client")
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json", "Authorization": f"Bearer {api_key}"})
        self.tldextracter = tldextract.TLDExtract(suffix_list_urls=())

    @staticmethod
    def _handle_response(res: requests.Response):
        if res.status_code == 200:
            return res.json()
        elif res.status_code == 401:
            raise errors.PluginError("API key not authorized")
        elif res.status_code == 403:
            raise errors.PluginError("Exceeded API rate limits")
        else:
            logger.error(res.json())
            raise errors.PluginError("Something went wrong with Neostrada")

    def _get_domain_dns_id(self, domain: str) -> int:
        res = self.session.get(f"{BASE_URL}/domains")
        base_domain = self.tldextracter(domain).top_domain_under_public_suffix
        domains = self._handle_response(res)
        for d in domains["results"]:
            if d["description"] == base_domain:
                return d["dns_id"]
        raise errors.PluginError(f"Domain {base_domain} not found")

    def _get_dns_records(self, domain_id: int):
        res = self.session.get(f"{BASE_URL}/dns/{domain_id}")
        return self._handle_response(res)

    def add_txt_record(self, domain: str, record_name: str, record_content: str):
        domain_id = self._get_domain_dns_id(domain)
        record = {
            "name": record_name,
            "content": record_content,
            "type": "TXT"
        }
        res = self.session.post(f"{BASE_URL}/dns/add/{domain_id}", data=record)
        self._handle_response(res)

    def del_txt_record(self, domain: str, record_name: str, record_content: str):
        domain_id = self._get_domain_dns_id(domain)
        records = self._get_dns_records(domain_id)
        record_data = {
            "record_id": None
        }
        for record in records["results"]:
            if record["name"] == record_name and record["content"] == record_content:
                record_data["record_id"] = record["id"]
        if record_data["record_id"] is None:
            raise errors.PluginError(f"Could not find {record_name} DNS record with {record_content} value in Neostrada")
        res = self.session.delete(f"{BASE_URL}/dns/delete/{domain_id}", data=record_data)
        self._handle_response(res)

