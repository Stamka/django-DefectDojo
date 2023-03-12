import base64
import logging
import re
import html2text
from defusedxml import ElementTree as etree
from dojo.models import Endpoint, Finding
from junitparser import JUnitXml

logger = logging.getLogger(__name__)


class DastardlyParser(object):
    """
    The objective of this class is to parse an xml file generated by the burp tool.

    TODO Handle errors.
    TODO Test burp output version. Handle what happens if the parser doesn't support it.
    """

    def get_scan_types(self):
        return ["Dastardly Scan"]

    def get_label_for_scan_types(self, scan_type):
        return "Dastardly Scan"

    def get_description_for_scan_types(self, scan_type):
        return "When the Dastardly report is generated, the recommended option is Base64 encoding both the request and response fields. These fields will be processed and made available in the 'Finding View' page."

    def get_findings(self, filename, test):
        try:
            xml = JUnitXml.fromfile(filename)
        except:
            return []
        items = []
        for suite in xml:
    # handle suites
    #print("suite= ",suite)
            for case in suite:
                #print("caseName= ",case.name)
                if case.name == "No issues were identified":
                    continue
                for failure in case:
                    #title = case.name
                    #print("title=", title)
                    #host = failure.text[failure.text.find("Host: ") + 6: failure.text.find("\n\nPath")]
                    #print("Host=",host)
                    #severity = failure.text[failure.text.find("Severity: ") + 10: failure.text.find("\n\nConfidence")].capitalize()
                    #print("Severity=",severity)
                    if failure.text.find("Issue Remediation") > -1:
                        description_local = failure.text[failure.text.find("Issue Detail") + 13: failure.text.find("Issue Remediation")]
                        mitigation_local = failure.text[failure.text.find("Issue Remediation") + 18: failure.text.find("Evidence")]
                    else:
                        description_local = failure.text[failure.text.find("Issue Detail") + 13: failure.text.find("Remediation")]
                        mitigation_local = failure.text[failure.text.find("Remediation Detail") + 19: failure.text.find("Evidence")]
                    #print("Description=",description)
                    #print("Mitigation=",mitigation)
                    request_local = failure.text[failure.text.find("Request:") + 9: failure.text.find("Response:")]
                    response_local = failure.text[failure.text.find("Response:") + 10: failure.text.find("\nReferences")+1 or failure.text.find("Vulnerability Classifications")]
                    #print("Request=",request)
                    #print("Response=",response)
                    finding = Finding(
                        title=case.name,
                        test=test,
                        description=description_local,
                        severity=failure.text[failure.text.find("Severity: ") + 10: failure.text.find("\n\nConfidence")].capitalize(),
                        mitigation=mitigation_local,
                        static_finding=False,
                        dynamic_finding=True,
                        tags = ["DAST"]
                        #endpoints = suite.name
                        #references=item.get("cve_link"),
                        #date=find_date,
                    )
                    endpoint = Endpoint.from_uri(suite.name)
                    finding.unsaved_endpoints.append(endpoint)
                    finding.unsaved_request = request_local
                    finding.unsaved_response = response_local
                    items.append(finding)
        return items
        