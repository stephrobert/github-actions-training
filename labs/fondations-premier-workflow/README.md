# First workflow: the tests run on every push

Lab of the **fondations** module of the GitHub Actions course, lessons
"What is a workflow?" and "Security: the basics". It proves the first skill
of the course: writing a workflow that runs a project's tests on every push
and every pull request, with the security reflexes set from the first file.

What the lab proves, and what the former exercise did not: **the workflow is
run**, with act, and a broken test turns it red. A workflow that wrote
`run: echo pytest` passed the former check, which only read the YAML; it does
not pass this one.

| | |
|---|---|
| Target | your machine: act 0.2.89 and Docker, `ubuntu-24.04` runner image pinned by digest |
| Duration | about 30 minutes |
| Paired lessons | [What is a workflow?](https://blog.stephane-robert.info/docs/pipeline-cicd/github/fondations/workflow/), [Security: the basics](https://blog.stephane-robert.info/docs/pipeline-cicd/github/fondations/securite-bases/) |
| Playable with act | yes, entirely |

```bash
mise install                               # act, actionlint, zizmor, pinact
dsoxlab run   fondations-premier-workflow   # puts the project in challenge/work
dsoxlab check fondations-premier-workflow   # runs the workflow and grades
```

The tests read what act produces: the result of the jobs on `push` and on
`pull_request`, the lines written by pytest, and the verdict of a copy of the
project in which a function has been broken. Two static complements read the
YAML: the `permissions:` block and the pinning of actions by SHA, confirmed
offline by zizmor.

Validated by `scripts/valider-labs.py`: 0 before the work, 100 after the
trainer's solution, replayable, machine left intact. The verdict, with the act
version and the image digest, is in `validation-labs.json`.
