from enum import Enum
import json
import pystache
from subprocess import check_output


class SeverityLevel(Enum):
    LOW = "1 = low"
    MEDIUM = "2 = medium"
    HIGH = "3 = high"
    CRITICAL = "4 = critical"


class BugReport:
    def __init__(self, scenario, error_type, traceback, **kwargs) -> None:
        self.scenario = scenario
        self.error_type = error_type
        self.traceback = traceback
        self.versions = kwargs.get("versions", {})

    def prettify(self, template=None):
        if template is None:
            template = "<h3>Scenario: {{ scenario_name}}</h3>Error: {{ error_type }}<br>Log:<br><fontⶩcolor='red'>{{ traceback }}</font>"
        data = {
            "scenario_name": self.scenario.name,
            "error_type": self.error_type.__name__,
            "traceback": self.traceback,
        }
        return (
            pystache.render(template, **data)
            .replace(" ", "&nbsp;")
            .replace("\n", "<br>")
            .replace("ⶩ", " ")
        )

    def _create_list(self, list, template=None):
        """
        When providing a template make sure to use the 'steps' keyword to access all the data
        """
        if template is None:
            template = """<ul>{{#steps}}<li>{{.}}</li>{{/steps}}</ul>"""
        data = {
            "steps": list,
        }
        return pystache.render(template, **data)

    def repro_steps(self, template=None):
        return self._create_list(self.scenario.steps, template=template)

    def get_versions(self, template=None, seperator=" - "):
        return self._create_list(
            [f"{k}{seperator}{v}" for k, v in self.versions.items()], template=template
        )


def report_bug(bug: BugReport, severity: SeverityLevel, assignee="", tags=None):
    """This won't work btw, just an example"""  
    result = check_output(
        [
            "az",
            "boards",
            "work-item",
            "create",
            "--title",
            bug.scenario.name,
            "--assigned-to",
            assignee,
            "--type",
            "Bug",
            "--organization",
            "https://secret.azure.com/",
            "--project",
            "1234-5678-9012-3456",
            "--description",
            bug.prettify(),
            "--fields",
            f"Severity={severity.value}",
            f"Repro Steps={bug.repro_steps()}",
            f"System.Tags={';'.join(tags if tags else [])}",
            f"System Info={bug.versions()}",
        ]
    )
    result_string = result.decode()
    js = json.loads(result_string)
    bugreport_id = js["id"]
    print(
        f" - {bug.scenario.name} | {tags if tags else ''} > {f'https://www.watch_my_bugreport.com/{bugreport_id}'}"
    )
