# Changelog

**Language:** [English](./CHANGELOG.md) · [Français](./CHANGELOG.fr.md)

This log is **dated and versioned**, following
[Keep a Changelog](https://keepachangelog.com/) and semantic versioning like
the sibling catalogues. From 2026-09-25 to 2026-10-17 it was dated only, on the
grounds that a lab catalogue promises no compatibility between two of its
states; the twelve catalogues now publish one release each, and this one is no
longer the exception.

What the date brings, and which the version does not replace: knowing **when** a
lab was proven, with which version of act and on which runner image. That is
what `validation-labs.json` records lab by lab, and what this log summarises.

Releases `v1.0.0` through `v1.2.0`, published in December 2025, have been
**deleted**. They had 39 downloads between them, measured before the deletion,
and their numbering made any restart unreadable: a version does not go
backwards, and 0.2.0 under v1.2.0 would have lied about the order of things.

---

## [0.2.1] - 2026-10-19

### Changed

- **Every `doc_url` now points at `www.stephane-robert.info`.** The site moved
  from `blog.` to `www.`, and the old host redirects with a 301 to the same
  path. Nothing was broken: `validate-structure --check-urls` follows
  redirections, and this catalogue was green before a single line changed. The
  migration is housekeeping, not repair: a `doc_url` should point at the page
  rather than depend on a redirection that will be removed one day.

  The paths are identical between the two hosts, so only the host changed. The
  359 `doc_url` the catalogues declare were looked up in the site's own
  repository, offline: all of them exist there, including twenty-three pages
  the old host answered with a 404.

## [0.2.0] - 2026-10-17

### Changed

- **The versioning restarts at 0.2.0, and the five old releases are gone.** This
  catalogue was the only one of the twelve without a release, and its
  `pyproject.toml` nevertheless declared `0.2.0` under tags published up to
  `v1.2.0`: the version went backwards, which no ordering can make sense of. The
  releases `v1.0.0` through `v1.2.0` and their tags have been deleted, and this
  one is the first of the new count.

- **The default branch is `main`.** It was the only one of the thirteen
  repositories still on `master`. Three workflows triggered on
  `branches: [master]`, namely `ci.yml`, `codeql.yml` and `scorecard.yml`: renaming a
  branch does **not** update the files that name it, so CodeQL and Scorecard
  would simply have stopped running, with no error and nothing to say so. They
  trigger on `main`, and a check reads the loaded workflow rather than the text
  to prove it.

- **The publishing chain is in place**: `release.yml`, `attester.yml` and the two
  `RELEASING` files, whose bundle distinguishes required paths from optional
  ones. Since dsoxlab 0.5.1 these come from `new catalog`, and a ratchet in the
  engine compares the required list to what a fresh catalogue actually holds.

- **The validator reads the contract, not the terminal panel.**
  `scripts/valider-labs.py` parsed the score out of what `dsoxlab check`
  *displays*. That panel is interface: it changed in dsoxlab 0.4.0 and the
  regex stopped finding anything. It now reads `check --json`, which carries a
  `schema`, and the reading lives in `scripts/verdict_check.py`, **identical in
  all twelve catalogs**.

- **Three verdicts, not two.** A run where every collected test skipped
  measured nothing: it is **SKIP**, neither green nor red, and it stays to be
  measured. Painting it red would accuse the lab of what is missing from the
  machine. `--check` therefore exits `10` in that case, against `1` for a RED,
  mirroring `dsoxlab doctor --strict` where 9 is repaired and 10 is remeasured.

- **The README takes the reference structure** shared by the twelve catalogs:
  fourteen sections, in both languages. Seven of them describe dsoxlab rather
  than the subject, and are therefore identical everywhere.

### Requires

- **dsoxlab 0.4.1 or later**, which introduced the `status` field of
  `check --json`. Without it the validator refuses to conclude rather than
  guessing.

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
