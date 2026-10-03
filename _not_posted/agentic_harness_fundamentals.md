# Agentic Harness in Practice

Harness is a ... Each tool comes with its own harness.

But its very generic instructions that may not fit your project

Make it better, it affects your results, level of your interreptions to agent, token
usage.

## Building Blocks

Some general concepts

### Context

The general prompt, instructions buissnes context. Should be small, its expensive.

Global scope context. Conventions, practices.

Local scope -- not yet fully standarized, tool based

### Skills

On demand capabilities. agents read only the frontmaters on start. then use as per usage
guidance.

Minimal example of a skill:

```markdown
...

```

Example flavours of skills:

- wording - caveman, asdste100
- general approach - ponytail
- specific functions - paper tiger elephant risk assesment
- usage of tools - built into the packages

### Deterministic Tooling

There is many tools that asurre best modern practices.
Be aware of the environment and use it.

Example in Python - full type annotation coverage and a typechecker like pyrefly.

A riddle - what does this code do?

```python
def prepare_objects(data, preparer):
    objects = []
    for d in data:
        o = preparer(d)
    return objects

```

This is much more husssle but much more readable. Both for developers and for agents.

```python
import datetime as dt
from typing import Callable

type YieldCurve
type ParSwapQuote = tuple[dt.date, float]

def prepare_objects(
    data: list[ParSwapQuote],
    preparer Callable[[list[ParSwapQuote]], YieldCurve ]
):
    objects: list[YieldCurve] = []
    for d in data:
        o = preparer(d)
    return objects
```

## Putting on the Harness

Your milage may vary but this is the order I follow when setting up a project.

Most important word -- bootstrap. Make the agent help you put the harness on itself.

### Tooling

Deterministic tooling is the most reliable and highest ROI. If you are developing
software you should be aware of the tooling arounf technologies you use. But the
configuraiton can take time or be a hassle. Use pre-made templates or describe what you
need, and let the agent do it for you. If possible, add them to CI jobs, precommit
hooks, run as often as possible

### Context

Two most important things - what is the project trying to achive and that all
development must adhere to the quality standards put togheter above.

It's efficient if each task begin with a rediscovery what is being developed,
what is the current state etc. Don't overdoit. Context is the most expensive part.
Keep it concise and dense in information.

It can also contain style guides, conventions etc. But probabilistic models are not
relible in following those. Better to lean on the derteministing tooling and code
quality checks.

#### Published Skills

npx skills install

they may come with scripts, executables, tools so be wary
don't overdo it, 100s of skills make both agent and dev cofused
but less crucial than the context. Experiment, see what works.
There are thousands of them, new hype each week.

### Custom Skills

Most agentic tools include skill making skills in the defualt harness.
Just ask the agent to make a skill based on your description, read it, test it, iterate.
Add it to your repo, version, treat as integral part of the project

### Custom Tooling

Make your own bespoke tooling. You know best the charachter of the project.
What are the hidden conventions and practices you follow?
What invariants you need to assure?
What are the painpoints?

Spend half a day indentifying them, detailing and make the agent write a tool that
flags violations of that rule. Add it to your harness.

## Here Be Dragons

- Don't trust techbros. dont let the hype win
- dont expect a dark factory (yet). you shouldnt want that either.
