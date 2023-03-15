import json
from enum import Enum
from subprocess import check_output

import pystache
from behave import model


class BugReport:
    def __init__(self, /, scenario, error_type, traceback, versions) -> None:
        self.scenario = scenario
        self.error_type = error_type
        self.traceback = traceback
        self.versions = versions

    def prettify(self, template=None):
        if template is None:
            template = "<h3>Scenario: {{ scenario_name }}</h3>Error: {{ error_type }}<br>Log:<br><fontⶩcolor='red'>{{ traceback }}</font>"
        return (
            pystache.render(
                template,
                scenario_name=self.scenario.name,
                error_type=self.error_type.__name__,
                traceback=self.traceback,
            )
            .replace(" ", "&nbsp;")
            .replace("\n", "<br>")
            .replace("ⶩ", " ")
        )

    def repro_steps(self, template=None):
        repro = []
        for step in self.scenario.steps:
            repro.append(f"<li>{step.keyword} {step.name}</li>")
            if step.table:
                repro.append(convert_table(step.table))

        repro.append("</html>")
        return create_list(content=repro, template=template)

    def get_versions(self, separator=" - "):
        return create_list(
            [f"{k}{separator}{v}" for k, v in self.versions.items()],
            template="{{#steps}}<li>{{.}}</li>{{/steps}}",
        )


def create_list(content, template=None):
    """
    Converts a behave.model.Table into a html table.
    When providing a template make sure to use the 'steps' keyword to access data
    >>> create_list(["A", "B"], template="{{#steps}}<li>{{.}}</li>{{/steps}}")
    '<li>A</li><li>B</li>'
    """
    if template is None:
        template = """{{#steps}}{{.}}{{/steps}}"""
    return (
        pystache.render(
            template,
            steps=content,
        )
        .replace("&lt;", "<")
        .replace("&gt;", ">")
    )


def convert_table(input_table: model.Table):
    """
    >>> convert_table(model.Table(headings=["A", "B"], rows=[["Q", "W"], ["E", "R"]]))
    '<table><tr><th>A</th><th>B</th></tr><tr><td>Q</td><td>W</td></tr><tr><td>E</td><td>R</td></tr></table>'
    """
    template = "<table><tr>{{#headings}}<th>{{.}}</th>{{/headings}}</tr>{{#rows}}<tr>{{#.}}<td>{{.}}</td>{{/.}}</tr>{{/rows}}</table>"
    return pystache.render(
        template,
        headings=input_table.headings,
        rows=[row.cells for row in input_table],
    )


def report_bug(
    bugreport: BugReport,
    severity="1 = low",
    assignee="",
    tags=None,
):
    """
    Report a bug to Azure DevOps
    bugreport: BugReport object containing the information about the error and where it occurred
    severity: SeverityLevel object containing the severity of the bug (LOW, MEDIUM, HIGH, CRITICAL)
        Convention: '1 = low', '2 = medium', etc.
    assignee: The person you want to associate the bugreport with (either name or email <- please use email ;))
    tags: List of tags to add to the bug report (Automated, Test, Foo, Bar, ...)
    """
    result = check_output(
        [
            "az",
            "boards",
            "work-item",
            "create",
            "--title",
            bugreport.scenario.name,
            "--assigned-to",
            assignee,
            "--type",
            "Bug",
            "--organization",
            "https://dev.azure.com/vwac/",
            "--project",
            "756288e9-a9e7-410e-ab1f-0a734e0e8145",
            "--description",
            bugreport.prettify(),
            "--fields",
            f"Severity={severity}",
            f"Repro Steps=<style>table, th, td {{ border: 1px solid black; border-collapse: collapse;}}</style>{bugreport.repro_steps()}",
            f"System.Tags={';'.join(tags if tags else [])}",
            f"System Info={bugreport.get_versions()}",
        ]
    )
    js = json.loads(result.decode())
    bugreport_id = js["id"]
    return f"https://dev.azure.com/vwac/Data%20Collection/_workitems/edit/{bugreport_id}/#/'"
