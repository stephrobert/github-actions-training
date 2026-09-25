# Changelog

**Language:** [English](./CHANGELOG.md) · [Français](./CHANGELOG.fr.md)

This log is dated, not versioned. That is a deliberate departure from the
sibling catalogues, which follow [Keep a Changelog](https://keepachangelog.com/)
and semantic versioning: **this project has no tags, no releases and no
versioned changelog** since the decision of 2026-09-25. A version number
promises compatibility between two states of a piece of software; a lab
catalogue has no such promise to make, and a learner never plays "version 1.2"
of a lab, they play the one that is online.

What the date does bring: knowing **when** a lab was proven, with which version
of act and on which runner image. That is what `validation-labs.json` records
lab by lab, and what this log summarises.

Releases `v1.0.1` through `v1.2.0`, published in December 2025, remain in place
and are not continued.

---

## 2026-09-25

### The first lab runs, and the cycle proves it

`fondations-premier-workflow` was a skeleton: three fixtures declared but
missing, no tests, no solution, no hints. `dsoxlab validate-structure` rejected
it. It now carries five twenty-point checks, run by act in the runner image
pinned by digest.

```
before the work: 0/5
after the solution: 5/5
after clean and run: 0/5
machine left intact
VALIDE
```

The fifth check carries both of its halves together: it breaks a function in a
copy of the project and requires the pipeline to say so, then verifies on the
intact project that it does not always go red. Split apart, the second half
would be true from the first check onwards, and therefore worthless.

### Validation leaves a trace that can be held against it

`scripts/valider-labs.py` chains dsoxlab commands without reimplementing any of
them, and writes its verdict to `validation-labs.json` with the date, the
version of act and the digest of the runner image: a validation holds for one
image.

It was proven in both directions. On a solution stripped of its `pull_request`
trigger:

```
after the solution: 4/5
- the solution leaves 1 test failing: test_les_tests_tournent_a_chaque_pull_request
ROUGE
```

At first it only said "the solution does not make every test pass", which
reports a problem without saying which.

`--check` re-reads the verdict without replaying anything, and checks the least
obvious thing first: that no lab has been **added without being validated**. A
file of all-green verdicts that ignored half the catalogue would pass without
it.

### Nineteen hooks, four catalogue checks

The repository had no `.pre-commit-config.yaml` and a single checker.

`tests/test_solutions_exemplaires.py` covers what no lab test looks at: a lab's
tests grade the learner's work, never the solution shown to them afterwards. It
found a real case on its first run.

actionlint and zizmor **never** run against the starting points: a `challenge/`
may carry an unpinned action or an injection, since that is what the learner
must fix. They only look at `.github/` and `labs/**/solution/`, and
`scripts/hooks/cibles-workflows.sh` computes that list once, for the local hook
and for CI alike.

### CI that runs the labs

Five jobs: zizmor, actionlint, poutine, pre-commit parity at both stages, and a
job that replays the full cycle with act on the GitHub runner. That last one is
what makes `validation-labs.json` binding: a local verdict that does not
reproduce in CI is ROUGE.

`dependabot.yml` is aligned with the model shared by the six repositories, plus
one ecosystem the siblings do not have: the `requirements.txt` of the starting
points, which live outside the catalogue's lock file and must stay current.

### Three defects fixed that only showed at runtime

**The reference solution was not exemplary.** It scored 80/100 against its own
challenge: `actions/checkout` left the job token in `.git/config`, which task 4
forbids and which zizmor reports as `artipacked`. The same defect existed in
`codeql.yml`.

**ruff was rewriting the labs' subject matter.** It sorted the imports of a
fixture, that is, of the starting point handed to the learner. The exclusion set
in `pyproject.toml` is **ignored** for any file passed as an argument, and
pre-commit passes files as arguments: `--force-exclude` is required, without
which the exclusion only protects the manual runs, the ones that do not need it.

**An action SHA had been written from memory.** `jdx/mise-action` carried a
non-existent SHA with an outdated version in its comment. Checked against the
API action by action, it was the only wrong one out of five. A repository that
teaches pinning cannot invent a SHA.

### The catalogue takes the dsoxlab shape

`meta.yml`, a `conftest.py` exposing `jouer_act()`, a README following the other
courses' layout with its generated catalogue, aligned documentation, and a
`mise.toml` pinning act, actionlint, zizmor, pinact, poutine and uv to the
versions measured that day.

Every version of act before 0.2.86 is vulnerable to CVE-2026-34041 and
CVE-2026-34042: `mise.toml` pins 0.2.89, and the validator refuses to run with
any other.

### The licence moves from MIT to CC BY 4.0

Like the Linux and Kubernetes catalogues, and for the same reason: this
repository is **teaching content**, not software. The official text is used
bare, with no custom header, otherwise GitHub does not detect the licence.

### Versioning is dropped

No tags, no releases, no `RELEASING`. The `release.yml` workflow was removed,
and with it the SLSA badge that depended on it.

---

## 2026-01-26

The OpenSSF Scorecard section is removed from the README, and actions are
bumped.

---

## 2025-12-29 and earlier

The repository is born under the MIT licence, with a single lab verified by
`validate.py`, a static analysis that looked for `pytest` in a `run:` without
ever executing anything. SLSA provenance, CodeQL, Scorecard, and releases
`v1.0.1` through `v1.2.0`.

That is the approach the 2026-09-25 overhaul replaces: a test that reads the
code does not prove that a workflow runs, let alone that a broken test would
turn the pipeline red.
