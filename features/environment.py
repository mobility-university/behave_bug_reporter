from behave.model_core import Status
from itertools import chain


def after_scenario(context, scenario):
    if scenario.status != Status.failed:
        return
    
    with open('bug.txt', 'w') as file:
        file.write(f'Scenario: {scenario.name} failed\n\n')
        file.write('Steps:\n')
        for step in chain(scenario._background_steps or [], scenario.steps):
            file.write(f'  {step.step_type} {step.name}\n')
            if step.table:
                assert False, 'hey, implement me please'
            if step.text:
                file.write(f'"""\n{step.text}\n"""\n')
        if context.stdout_capture:
            file.write("\n\n")
            file.write('stdout:\n')
            file.write(context.stdout_capture.getvalue())
        if context.stderr_capture:
            file.write("\n\n")
            file.write('stderr:\n')
            file.write(context.stderr_capture.getvalue())
        if scenario.error_message:
            file.write("\n\n")
            file.write('error:\n')
            file.write(scenario.error_message.getvalue())