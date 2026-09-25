# GitHub Actions DevSecOps Training: the course labs

**Language:** [English](./README.md) · [Français](./README.fr.md)

[![OpenSSF Scorecard](https://img.shields.io/ossf-scorecard/github.com/stephrobert/github-actions-training?label=OpenSSF%20Scorecard)](https://securityscorecards.dev/viewer/?uri=github.com/stephrobert/github-actions-training)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](./LICENSE)

Hands-on training in **GitHub Actions and supply chain security**, driven by
the [`dsoxlab`](https://github.com/stephrobert/dsoxlab) CLI. This repository is
the **lab catalogue** of the GitHub Actions course on
[blog.stephane-robert.info](https://blog.stephane-robert.info/docs/pipeline-cicd/github/parcours/),
from the first workflow to self-hosted runners, with a systematic hardening
angle.

## What it is

`github-actions-training` is a **content repository**, not an application. It
provides:

- **labs**, each paired with a lesson of the course, from the first workflow
  to CI governance,
- **challenges** with no step-by-step, to check your autonomy,
- **automatic validation** that **actually runs your workflows** and proves
  what they produced (not that you wrote a given keyword),
- **scoring** with hints of variable cost.

The `dsoxlab` CLI is the single entry point: it starts a lab, shows the
instructions, validates, scores and reports. It lives in **its own
repository** and is installed **separately**: it is not part of this
repository.

> **Status: being rebuilt (2026-09-25).** The catalogue is being redone to
> follow the 12 modules of the course. The full plan, one lab per skill, is
> tracked in the [milestones](https://github.com/stephrobert/github-actions-training/milestones)
> and [issues](https://github.com/stephrobert/github-actions-training/issues).

## Requirements

- Python 3.11+ and [`uv`](https://docs.astral.sh/uv/)
- `git`
- A responsive **Docker** (`docker info`): act runs each job in a container
  that mimics GitHub's `ubuntu-24.04` runner.
- [`mise`](https://mise.jdx.dev/), which installs act, actionlint, zizmor,
  pinact, poutine and uv at the versions pinned in `mise.toml`.
- For the **platform** labs only: a GitHub account, a repository of your own
  and an authenticated `gh`.

## Install

`dsoxlab` is published on [PyPI](https://pypi.org/project/dsoxlab/): install
it as a standalone tool.

```bash
# 1. Install the dsoxlab CLI (external tool, outside this repository)
uv tool install dsoxlab        # or: pipx install dsoxlab

# 2. Clone this lab catalogue
git clone https://github.com/stephrobert/github-actions-training.git
cd github-actions-training

# 3. Install the pinned tooling (act, actionlint, zizmor, pinact, poutine, uv)
mise install

# 4. Check that everything is in place
dsoxlab doctor
```

### Your first lab, in five minutes

**Start with the `fondations` section.** Its labs run entirely on your
machine: act runs your workflows in Docker, without pushing anything to
GitHub.

```bash
dsoxlab use fondations                # starting section
dsoxlab next                          # → fondations-premier-workflow
```

Then, for this lab as for every other, the same four-step cycle:

```bash
dsoxlab course fondations-premier-workflow      # 1. the context, then the course
dsoxlab challenge fondations-premier-workflow   # 2. what is asked of you
dsoxlab run fondations-premier-workflow         # 3. prepares your workspace
                                                #    (challenge/work/) and puts you there
dsoxlab check fondations-premier-workflow       # 4. runs your workflows, validates and scores
```

`run` is the step people forget: it copies the starting point (a small
application, sometimes a workflow to fix) into `challenge/work/`. A `check`
run without `run` fails by reporting that nothing is done, which is true but
misleading.

Stuck? `dsoxlab hint <id>` reveals a hint, at the cost of a few points.

### Moving on to "platform" labs

Some features only exist on GitHub: protected environments and approvals,
OIDC, attestations, rulesets, Scorecard, trigger filters. The labs about them
are checked against **your repository**, through the GitHub API.

```bash
gh auth status                              # gh must be authenticated
export LAB_REPO=your-account/your-repo      # the repository the lab reads
dsoxlab check <id>
```

Check your environment with `dsoxlab doctor` (Python, pytest, runtimes,
detected labs).

### Keeping it up to date

New labs arrive in this repository, and the CLI evolves on its own. Update each
separately:

```bash
git pull                       # fetches new/updated labs into your clone
mise install                   # aligns the tooling with the pinned versions
uv tool upgrade dsoxlab        # updates the CLI (or: pipx upgrade dsoxlab)
```

Your work in progress lives in each lab's `challenge/work/`, which is
gitignored: `git pull` therefore brings new labs without ever touching your
work.

## How it works

### The declarative contract (two levels)

The catalogue is described by data, not by code: the `dsoxlab` engine stays
domain-agnostic and reads two levels of files.

- **`meta.yml`** at the root declares the repository identity and the
  **order** of the sections shown by `list-labs`. Each section is a module of
  the blog course. There is no `infra` block: no machine to provision.
- **`lab.yaml`** per lab (under `labs/<module>-<subject>/`) declares its
  `skills`, its `level` (the course module), its `runtime` and `fixtures`, its
  `doc_url` (the paired lesson) and a `validation` block. An optional
  `lab.fr.yaml` overrides the `title` and `description` in French.

`dsoxlab validate-structure` checks the whole contract: `meta.yml` is
compliant, every referenced lab exists with a valid `lab.yaml`, and every
referenced fixture or test file is present.

### The lab lifecycle

The learner drives everything through the CLI; a typical path:

```bash
dsoxlab doctor                        # check the environment (Python, pytest, runtimes, labs)
dsoxlab list-labs                     # browse the catalogue
dsoxlab show <id>                     # a lab's metadata and status
dsoxlab run <id>                      # prepare the workspace
dsoxlab course <id>                   # read the guided course (optional)
dsoxlab challenge <id>                # read the mission (no step-by-step)
dsoxlab hint <id>                     # reveal a hint (deducted from the score)
dsoxlab check <id>                    # run the workflows, compute and score
dsoxlab submit <id>                   # final submission, closes the session
dsoxlab progress                      # progress per block, average score
```

`run` is what sets up the environment: it creates the lab's `workdir` and
copies the declared fixtures. Everything then happens on your machine, in that
directory, as in a real repository.

### Runtimes

| Runtime | Backend | What it brings |
|---|---|---|
| `shell` | local shell, act and Docker | Every lab. act replays your workflows in containers that mimic the `ubuntu-24.04` runner, on your machine, without pushing anything. |

What act cannot run is checked against your GitHub repository. Measured on
2026-09-25 with act 0.2.89 and Docker 29.1.3:

| What the lab needs to run | Locally with act |
|---|---|
| jobs, `needs`, `if`, outputs, matrices, reusable workflows, composite actions | yes |
| cache, masked secrets, `vars`, an event payload | yes |
| `branches:` and `paths:` filters of `on:` | no, on your repository |
| `services:` | no, on your repository |
| `upload-artifact` v6 and later | no: the labs pin v5.0.0 until [nektos/act#6174](https://github.com/nektos/act/pull/6174) is merged |
| environments, approvals, OIDC, attestations, rulesets, Scorecard, `concurrency` | no, on your repository |

act must be 0.2.86 or later: earlier versions are vulnerable to CVE-2026-34041
and CVE-2026-34042. The measurements are detailed in
[`docs/conception.md`](./docs/conception.md) (French).

### The validation model

Validation **proves what your workflows do, it does not trust the learner**.
Every lab ships `pytest` tests under `challenge/tests/` that **run your
workflows with act** and check what they produced: the test job succeeded
**and** fails when a test breaks, the secret went through **and** stays
masked, the action is pinned **and** on the SHA of the announced tag. A test
that only checks that a keyword appears in the YAML is rejected.

- On the trainer side, `scripts/valider-labs.py` chains `dsoxlab run`, `check`
  and `clean` to prove each lab **both ways**: 0 before the work, 100 after the
  reference solution (`solution/`), and 0 again after a reset.
- In `dsoxlab check` (the learner path), the tests validate **your** work, in
  your `challenge/work/`.
- The last test of a lab exercises **both sides**: what must be refused is
  refused, what must pass passes.

### Scoring, hints, progress

`check` records a score (passed tests/total, minus the cost of the hints used).
Hints have a **variable cost**: revealing one deducts points, hence their
opt-in nature. The history lives in a SQLite database **specific to this
repository** (`.dsoxlab.db`, at the root, gitignored); `dsoxlab scores` and
`dsoxlab progress` read it. The active session is stored per repository in
`.dsoxlab-context.json`.

## Catalog

The labs live under `labs/` and are ordered by `meta.yml`, one course module
per section. The table below is generated from the actual `lab.yaml` files:
run `python3 scripts/gen_catalog.py` to refresh it. Upcoming labs are tracked
in the [milestones](https://github.com/stephrobert/github-actions-training/milestones).

<!-- LABS:START -->
### Writing your first workflow

| Lab (id) | Title | Level | Certif | Runtime | Companion guide |
|---|---|---|---|---|---|
| `fondations-premier-workflow` | First workflow: the tests run on every push, and a broken test turns the pipeline red | fondations | - | shell | [guide](https://blog.stephane-robert.info/docs/pipeline-cicd/github/fondations/workflow/) |

_1 lab, table generated by `scripts/gen_catalog.py`._
<!-- LABS:END -->

## Contributing & license

- Contributing: see [CONTRIBUTING](./CONTRIBUTING.md).
- Conduct: [Code of Conduct](./CODE_OF_CONDUCT.md) · Security: [SECURITY](./SECURITY.md).
- Corrections to the blog lessons found by the labs: [corrections-guides](./docs/corrections-guides.md) (French).
- License: [CC BY 4.0](./LICENSE).

### License

Copyright (c) 2026 Stéphane Robert, https://blog.stephane-robert.info

This work is licensed under the
[Creative Commons Attribution 4.0 International License (CC BY 4.0)](./LICENSE).
You are free to share and adapt it for any purpose, even commercially, under one
condition: give appropriate credit to Stéphane Robert, provide a link to the
blog, and indicate if changes were made, without suggesting the author endorses
you or your use.

`LICENSE` holds the official license text only, with no added header: that is
what lets GitHub detect the license.
