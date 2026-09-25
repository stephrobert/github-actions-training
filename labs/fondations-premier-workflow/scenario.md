# The tests of a calculator nobody runs

## Situation

Your team has just taken over a small Python library, `src/calculator.py`, used
as a building block by other projects of the company. It ships with nine pytest
tests, under `tests/`, which all pass when someone remembers to run them. Last
week nobody did: a change to `divide` reached production with an unhandled
division by zero, and a test was catching it.

The repository has no workflow. The `challenge/work` directory holds the project
as it was delivered: the code, the tests, `requirements.txt`, `pytest.ini`, and
an `.actrc` that names the runner image for act. It is not a git repository yet;
act needs one to read the context (branch, commit), and a project without one
cannot have a pull request.

## Objective

Run the nine tests **on every push and every pull request**, so that a change
that breaks a test can no longer reach `main` without someone seeing it. From
this very first file, the workflow must follow the reflexes of the lesson
"Security: the basics": it only asks for the right to read the code, and every
action it uses is pinned to the full SHA of its commit, with its version as a
comment, and zizmor has nothing to report.

The workflow is right when act runs it on both events with a green job where
pytest announces its nine tests, and when the same command, on a copy of the
project where a function has been broken, turns the job red.

## Pointers

- The lesson says where GitHub looks for workflows, and what one is made of: a
  name, triggers, jobs. `act -l` lists what act understood from your files; a
  job missing there will never run.
- `act push` and `act pull_request` run the workflow for each of the two events.
  act ignores `branches:` filters, which is no reason to leave them out: on
  GitHub, they matter.
- The runner knows nothing about your project: every job starts on a fresh
  machine, and it is up to you to fetch the code and install Python there.
- An action is named `owner/repo@ref`. The current version of each action of
  the `actions` organisation is on its Releases page, and
  `gh api repos/<owner>/<repo>/commits/<tag> --jq .sha` gives the SHA of a tag.
- `zizmor --offline .github/workflows` reads your files the way the check will.

## Verify

```bash
dsoxlab check fondations-premier-workflow
```

Five checks, twenty points each. The first three run the workflow with act and
read what it produces; the other two read the YAML. The last check is the one
that matters: it breaks a function in a copy of the project and requires the
pipeline to say so.
