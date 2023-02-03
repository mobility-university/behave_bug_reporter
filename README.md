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

## Important Notes:
If you would like to use this in your own pipeline or projects, make sure you export `CREATE_BUG_REPORT` into the system environment and set it either to `True` or `False` *(case sensitive)*. By default automated bug-creation is turned off.