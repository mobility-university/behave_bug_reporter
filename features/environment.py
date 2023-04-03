import os
import traceback

from behave.model_core import Status

from features.bug import BugReport, report_bug


def before_all(context):
    assert "generated_reports" not in dir(context)
    context.generated_reports = []


def before_scenario(context, scenario):
    assert "exception" not in dir(context)
    context.exception = None


def before_step(context, step):
    callback = step.store_exception_context

    def store_exception_context(exception):
        context.exception = dict(exception=exception, traceback=traceback.format_exc())
        callback(exception)

    step.store_exception_context = store_exception_context


def after_scenario(context, scenario):
    if scenario.status != Status.failed:
        return

    # Report Bug!
    if os.environ.get("CREATE_BUG_REPORT", "False") == "True":
        link = report_bug(
            BugReport(
                scenario=scenario,
                error_type=type(context.exception["exception"]),
                traceback=context.exception["traceback"],
                versions={
                    "youtube": "7.8.2",
                    "github": "1.2.3",
                },  # impl. your logic here!
            )
        )
        context.generated_reports.append(link)


def after_all(context):
    for report in context.generated_reports:
        print(report)
