# Contributing to github-actions-training

**Language:** [English](./CONTRIBUTING.md) · [Français](./CONTRIBUTING.fr.md)

This repository is a **catalogue of labs** consumed by the
[`dsoxlab`](https://github.com/stephrobert/dsoxlab) CLI. Contributions are new
labs and fixes. The CLI lives in its own repository: do not add a runner, a
scoring system or hint handling here. If you hit a limit of the engine, open an
issue [in its repository](https://github.com/stephrobert/dsoxlab/issues)
rather than working around it locally.

## Setup

```bash
uv tool install dsoxlab        # the CLI, an external tool
git clone https://github.com/stephrobert/github-actions-training.git
cd github-actions-training
git switch develop             # never work on master
mise install                   # act, actionlint, zizmor, pinact, poutine, uv
dsoxlab doctor                 # check the environment
```

## Branches

`master` stays in its published state until the rebuilt catalogue is complete
and validated. Work happens on a **dedicated branch**, opened from `develop`,
and comes back to `develop` through a pull request. No automatic merge.

## The non-negotiable rule: a lab is proven both ways

A passing test proves nothing until you have seen **fail** what must fail. A
lab whose tests pass **before** the work measures nothing, and it is the
costliest defect of the field because it only shows this way.

```bash
python3 scripts/valider-labs.py --lab <id>
```

The validator chains dsoxlab commands: it sets the starting point
(`dsoxlab run`), checks that the score is **0**, lays down the reference
solution, checks that the score is **100**, resets, replays, then cleans up.
It refuses to run with any act version other than the one in `mise.toml`, and
records the date, the act version and the runner image digest in
`validation-labs.json`. A lab absent from that file is **deliverable**, not
**validated**.

The mechanical check says **nothing** about whether a lab is right, but it
refuses a non-compliant lab before a human reads it:

```bash
dsoxlab validate-structure
```

## Tests run the workflow, they do not re-read the YAML

The learner reaches the result by whatever path they like. The proof is
therefore **execution**: act runs the workflow, and the test reads what it
produced.

```python
# NO: re-reading what the learner wrote
assert "pytest" in Path(".github/workflows/ci.yml").read_text()

# YES: running the workflow and reading what it did
run = jouer_act(depot, "push")
assert run.job("test").result == "success"
```

Reading the YAML (actionlint, zizmor) complements the proof, it never
replaces it. The last test of a lab exercises **both sides**: what must be
refused is refused, what must pass passes. For a first workflow: a broken test
fails the pipeline, and the healthy suite makes it pass.

Before writing a test, ask one question: **would it be green if the learner
did nothing?** "The application has tests" or "act runs without error" would
be: they are not tests, they are assumptions of the starting point.

## What act does not run

`branches:` and `paths:` filters, `services:`, environments and approvals,
OIDC, attestations, rulesets, Scorecard, `concurrency`: these only exist on
GitHub. The lab about them is checked against the learner's repository, named
by `LAB_REPO=account/repo`, through the GitHub API. The measured table is in
[`docs/conception.md`](docs/conception.md) (French).

## Anatomy of a lab

```text
labs/<module>-<subject>/
├── lab.yaml, lab.fr.yaml       # the contract: section and level = course module,
│                               # doc_url = the paired lesson, runtime.fixtures = the starting point
├── scenario.md, .fr.md         # the situation and the goal, never a how-to
├── README.md, .fr.md           # the tutorial, on examples unrelated to the challenge
├── fixtures/                   # the starting point, copied into challenge/work by dsoxlab run
├── solution/                   # the reference solution, laid down for validation
└── challenge/
    ├── README.md, .fr.md       # the assignment: the requirements to meet
    ├── hints.yaml              # four base64 hints, bilingual, increasing cost
    └── tests/test_functional.py  # the proof, read by pytest (fixed name)
```

`dsoxlab new lab <id> --runtime shell` creates the skeleton. The identifier
follows `<module>-<subject>`, lowercase and in French, the course language:
`fondations-premier-workflow`. `section` and `level` repeat the identifier of
the module **in the blog course**, word for word: this is what answers the
question that drives this repository, "how many skills of the course can I
demonstrate?".

`doc_url` points to the lesson the lab proves. A lab with no paired lesson is
a lab that teaches instead of proving, and teaching is the site's job.

A fixture declared in `lab.yaml` must exist in `fixtures/`:
`dsoxlab validate-structure` refuses the lab otherwise.

## The tutorial never gives the solution

A lab's `README.md` teaches the mechanism on a **neutral example**, with names
unrelated to the challenge: a `demo.yml` workflow, not the `ci.yml` the
assignment asks for. No block of the tutorial may be copy-pasted into
`challenge/work`. Every output shown comes from a real run.

## Writing style

- **No emoji, no em dash** in what the learner reads: scenarios, READMEs,
  assignments, hints, assertion messages.
- **Assertion messages teach.** A failing test says what is wrong and why,
  not only what was expected. It is often the only text the learner reads
  carefully.
- A `scenario.md` describes a **situation**, never a list of commands.
- Content is written in French first, then translated to the English files,
  which are authoritative for dsoxlab.

## The workflows set the example

This repository teaches workflow security: its own workflows, and those of the
labs, follow it. Minimal permissions, actions pinned by SHA with the right
version comment, no dangerous `pull_request_target`.

```bash
actionlint
GH_TOKEN="$(gh auth token)" zizmor .github/workflows/ labs/
trufflehog filesystem . --no-update
```

## What a lab contradicts in the blog

Writing a lab means running what the lesson claims. A discrepancy is recorded
in [`docs/corrections-guides.md`](docs/corrections-guides.md), with the file,
the section, what the guide says, what is true, and the evidence. The blog is
fixed in its own repository, never from this one.

## Conventions

- **Commits**: messages in French, a factual subject that says what changed
  and why, no conventional prefix. The body tells what was **measured**,
  including the measurements discarded along the way.
- **One issue per lab**: tick its definition of done as you go, with the
  evidence in a comment.

## Security

Vulnerabilities are reported privately, never through a public issue: see
[`SECURITY.md`](SECURITY.md).
