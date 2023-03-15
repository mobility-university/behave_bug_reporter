# behave_bug_reporter

showcase on how to report bugs with behave automatically including all necessary details which might be needed to process the bug.

## What to do first
_(In our environment.py)_
### before_scenario
Check here if the context already contains an 'exception' variable, if not $\to$ initialize it as `None`.
We use this later to pass down the error that occured to other functions who need it.

### before_step
Here we have to implement our logging logic. First we save our old handler as `callback`, then we write our own that stores the error that occured in `context.exception` *(remember?)*.
After we implemented our logic, we call the old one inside our newly implemented function.
Finally we overwrite the `step.store_exception-context` with our method we've just written.

### after_scenario
Here is where the *fun* begins. Our scenario probably failed and we want to file a new report.
In that case we use our `BugReport` class *(more information later)* and retrieve our error-type and our traceback, create a new BugReport and save it in our list.

### after_all
In this method we call some function that creates a new bug-report ticket in azure (or similar) because *after all* (get it?) That is what we were trying to achieve all along.


## Bugreport Class

Our Bugreport-Class takes care of all the formatting, data-storage and so on.
We use the package `pystache` to format our data as html, and pystache makes that really easy. 

## report_bug
This method, who would've thought, reports our bugs.

# Toggle automation
Since this is a automated tool which, in theory, could produce bugreports every run we want to give it a mechanism to toggle it on/off.

## Turn it on
You have to explicitly tell the bugreporter to create bugreports. This can be done in any way you want as long as you have an environment-variable set: `CREATE_BUG_REPORT=True`.
**Careful, `True` has to begin with an uppercase letter**

### azure_pipeline.yml
In order for the creation of bugreports to work, you need to run your task as an `AzureCLI@2`-Task since we need the Azure-Credentials.

Here is an example of how we solved this in our project. For conconvenience sake I've marked all the variables you have to replace with `[brackets]`.

```bash
...

parameters:
  - name: should_create_bug_reports
    displayName: Should the pipeline create automated bugreports
    type: boolean
    default: false

...

- task: AzureCLI@2
    displayName: test specification
    inputs:
        azureSubscription: [YourSubscription]
        scriptType: bash
        scriptLocation: inlineScript
        inlineScript: |
        set -ex

        echo $(System.AccessToken) | az devops login --organization=https://dev.azure.com/[your_organisation]

        pip3 install -r requirements.txt
        az --version
        source .${{ environment }}_env


        # Export Secrets (yours, not these ones :D)
        export some_secret=SUPERSECRETKEY1
        export another_secret=SUPERSECRETKEY2

        # Settings for automated bugreports
        export CREATE_BUG_REPORT=$(CREATE_BUG_REPORT) # env

        if [[ ${{ parameters.should_create_bug_reports }} == 'True' ]]; then
            export CREATE_BUG_REPORT=True
        fi

        # Versions
        export SYSTEM_VERSION=0.1.0-SNAPSHOT

        if [[ ${{ parameters.debug_tests }} == 'True' ]]; then
            export verbose=true
        fi

        
        ./run_your_script
```

You can leave the settings for automated bugreports as they are or add some more conditions as to when you want reports created. Just remember, you have to explicitly say **True** in order for the bugreports being created.
