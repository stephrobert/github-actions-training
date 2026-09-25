# GitHub Actions Training: verifiable labs

**Language:** [English](./README.md) · [Français](./README.fr.md)

[![OpenSSF Scorecard](https://img.shields.io/ossf-scorecard/github.com/stephrobert/github-actions-training?label=OpenSSF%20Scorecard)](https://securityscorecards.dev/viewer/?uri=github.com/stephrobert/github-actions-training)
[![License: MIT](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

A catalogue of **verifiable labs** for the
[GitHub Actions training](https://blog.stephane-robert.info/docs/pipeline-cicd/github/parcours/)
on Stéphane Robert's blog. Played by the
[dsoxlab](https://github.com/stephrobert/dsoxlab) CLI.

Reading a workflow does not prove you can write one. Each lab in this
repository exercises **one skill of the course**, paired with the lesson that
teaches it: it sets a starting point, states a goal, and checks the work by
**actually running the workflow**, then reading what it produced. Never by
re-reading the YAML you wrote.

> **Status: being rebuilt (2026-09-25).** The catalogue is being redone from
> scratch to follow the 12 modules of the course. No lab is validated yet; the
> full plan is below, and every lab has its issue. The former
> `tp-01-premier-workflow` exercise remains available on the `master` branch
> until its replacement, `fondations-premier-workflow`, is ready.

## Getting started

```bash
uv tool install dsoxlab        # the CLI, an external tool

git clone https://github.com/stephrobert/github-actions-training.git
cd github-actions-training
mise install                   # act, actionlint, zizmor, pinact, poutine, uv

dsoxlab list-labs
dsoxlab run       fondations-premier-workflow
dsoxlab challenge fondations-premier-workflow
dsoxlab check     fondations-premier-workflow
```

`dsoxlab hint <id>` gives a hint, deducted from the score. `dsoxlab clean <id>`
resets the lab.

## Prerequisites

- **A responsive Docker** (`docker info`). act runs each job in a container
  that mimics GitHub's `ubuntu-24.04` runner.
- **The tools in [`mise.toml`](mise.toml)**, installed by `mise install` at
  the measured version: act 0.2.89, actionlint, zizmor, pinact, poutine, uv.
  act must be 0.2.86 or later: earlier versions are vulnerable to
  CVE-2026-34041 and CVE-2026-34042.
- **For the "platform" labs only**: a GitHub account, a repository of your
  own, and an authenticated `gh`. These labs read your repository, named by
  `LAB_REPO=your-account/your-repo`.

## How a lab is played

`dsoxlab run` copies the starting point into `labs/<id>/challenge/work`: a
small application, sometimes a workflow to fix. You work in it as in a real
repository. `dsoxlab check` then runs your workflows with **act**, on your
machine, and checks what they did: jobs that succeeded or were skipped,
outputs, artifacts, scanner findings.

Some things only exist on GitHub: protected environments and their approvals,
OIDC, attestations, rulesets, Scorecard, trigger filters. The labs about them
are checked against **your repository**, through the GitHub API. The "act"
column of the catalogue says, for each lab, what runs locally.

| What the lab needs to run | Locally with act |
| --- | --- |
| jobs, `needs`, `if`, outputs, matrices, reusable workflows, composite actions | yes |
| cache, masked secrets, `vars`, an event payload | yes |
| `branches:` and `paths:` filters of `on:` | no, on your repository |
| `services:` | no, on your repository |
| `upload-artifact` v6 and later | no: the labs pin v5.0.0 until [nektos/act#6174](https://github.com/nektos/act/pull/6174) is merged |
| environments, approvals, OIDC, attestations, rulesets, Scorecard, `concurrency` | no, on your repository |

Measured on 2026-09-25 with act 0.2.89 and Docker 29.1.3. The details, command
by command, are in [`docs/conception.md`](docs/conception.md) (French).

## The catalogue

<!-- LABS:START -->

This is the order of the [blog course](https://blog.stephane-robert.info/docs/pipeline-cicd/github/parcours/),
as declared by [`meta.yml`](meta.yml). Each module of the course is a section,
and each lab has an issue holding its definition of done. Lab names stay in
French: they are the course's identifiers.

**act**: "yes" when the whole proof runs locally, "partial" when only part of
it does, "no" when it needs your GitHub repository.

### Writing your first workflow

| Lab | What it proves | act | Tracking |
| --- | --- | --- | --- |
| `fondations-premier-workflow` | the tests run on every `push` and `pull_request`, and a broken test fails the pipeline | yes | [#16](https://github.com/stephrobert/github-actions-training/issues/16) |
| `secrets-et-variables` | a secret goes through `env:` and stays masked, a derived value no longer is | yes | [#17](https://github.com/stephrobert/github-actions-training/issues/17) |
| `evaluer-et-epingler-une-action` | every action on the SHA of the announced tag, and Dependabot to maintain them | partial | [#18](https://github.com/stephrobert/github-actions-training/issues/18) |

### Designing dynamic workflows

| Lab | What it proves | act | Tracking |
| --- | --- | --- | --- |
| `pipeline-en-graphe` | `needs`, job outputs, `if` on the event, a report that survives failure | yes | [#19](https://github.com/stephrobert/github-actions-training/issues/19) |
| `matrice-de-tests` | Cartesian product, `include`, `exclude`, dynamic matrix through `fromJSON` | yes | [#20](https://github.com/stephrobert/github-actions-training/issues/20) |
| `reutiliser` | a reusable workflow with inputs and outputs, a composite action | yes | [#21](https://github.com/stephrobert/github-actions-training/issues/21) |
| `declencheurs` | `workflow_dispatch` with typed inputs, `github.event_name`, filters proven on the platform | partial | [#22](https://github.com/stephrobert/github-actions-training/issues/22) |
| `services-conteneurs` | a job that waits for its service to be healthy | no | [#23](https://github.com/stephrobert/github-actions-training/issues/23) |

### Defending the supply chain

| Lab | What it proves | act | Tracking |
| --- | --- | --- | --- |
| `neutraliser-une-injection` | the payload of an issue title executes before, is printed as is after | yes | [#24](https://github.com/stephrobert/github-actions-training/issues/24) |
| `epingler-et-maintenir` | a repository on moving tags moves to SHAs, Dependabot maintains them with a cooldown | partial | [#25](https://github.com/stephrobert/github-actions-training/issues/25) |
| `auditer-avec-les-scanners` | a booby-trapped repository reaches 0 findings with zizmor, poutine and plumber, and its workflows still run | yes | [#26](https://github.com/stephrobert/github-actions-training/issues/26) |
| `harden-runner-et-threat-model` | harden-runner blocking with an allowlist, and a versioned threat model | partial | [#27](https://github.com/stephrobert/github-actions-training/issues/27) |

### Least privilege, OIDC and provenance

| Lab | What it proves | act | Tracking |
| --- | --- | --- | --- |
| `permissions-minimales` | `permissions: {}` at the top, `write` only in the job that publishes | yes | [#28](https://github.com/stephrobert/github-actions-training/issues/28) |
| `desamorcer-pull-request-target` | the two-workflow pattern, and the fork guard exercised with a fork payload | partial | [#29](https://github.com/stephrobert/github-actions-training/issues/29) |
| `oidc-sans-cle-longue-duree` | no cloud key in the secrets, and a trust policy that refuses the wildcard | partial | [#30](https://github.com/stephrobert/github-actions-training/issues/30) |
| `attester-et-verifier` | `gh attestation verify` and `cosign verify`, on a public image then on yours | no | [#31](https://github.com/stephrobert/github-actions-training/issues/31) |

### A hardened GitHub pipeline, end to end

Five workshops whose reference result is
[`stephrobert/secure-python-pipeline`](https://github.com/stephrobert/secure-python-pipeline).
This repository provides the starting point, the check and the solution.

| Lab | What it proves | act | Tracking |
| --- | --- | --- | --- |
| `1-bootstrap-securise` | governance, hash-pinned dependencies, non-root image, zero HIGH or CRITICAL vulnerability | yes | [#32](https://github.com/stephrobert/github-actions-training/issues/32) |
| `2-pipeline-ci-durci` | actionlint, zizmor, poutine and plumber at zero, and a CI that really tests | yes | [#33](https://github.com/stephrobert/github-actions-training/issues/33) |
| `3-build-verifiable` | SLSA provenance, attested SBOM, Cosign signature, verified by a third party | no | [#34](https://github.com/stephrobert/github-actions-training/issues/34) |
| `4-protection-et-gouvernance` | a ruleset read back through the API, CODEOWNERS without errors | no | [#35](https://github.com/stephrobert/github-actions-training/issues/35) |
| `5-scoring-et-durcissement` | Scorecard taken apart check by check | no | [#36](https://github.com/stephrobert/github-actions-training/issues/36) |

### Delivering: environments and deployments

| Lab | What it proves | act | Tracking |
| --- | --- | --- | --- |
| `promouvoir-un-deploiement-approuve` | two environments, an approval, promotion by digest, rollback without rebuild | no | [#37](https://github.com/stephrobert/github-actions-training/issues/37) |

### Speeding up and debugging the pipelines

| Lab | What it proves | act | Tracking |
| --- | --- | --- | --- |
| `artefacts-entre-jobs` | a build shared through an artifact, a report produced even on failure | yes | [#38](https://github.com/stephrobert/github-actions-training/issues/38) |
| `cache-des-dependances` | the cache hit on the second run, invalidated when the lockfile changes | yes | [#39](https://github.com/stephrobert/github-actions-training/issues/39) |
| `debug-d-un-workflow` | a workflow failing for three distinct reasons, diagnosed then fixed | yes | [#40](https://github.com/stephrobert/github-actions-training/issues/40) |
| `concurrency` | obsolete runs cancelled, and a deployment that is never cancelled | no | [#41](https://github.com/stephrobert/github-actions-training/issues/41) |

### Choosing and securing the runners

| Lab | What it proves | act | Tracking |
| --- | --- | --- | --- |
| `runner-ephemere-en-conteneur` | a non-root runner image, registered as ephemeral, gone after one job | no | [#42](https://github.com/stephrobert/github-actions-training/issues/42) |
| `securiser-un-runner` | cleanup between jobs, dedicated account, filtered outbound network | partial | [#43](https://github.com/stephrobert/github-actions-training/issues/43) |

### Governing CI beyond the YAML

| Lab | What it proves | act | Tracking |
| --- | --- | --- | --- |
| `rulesets-et-codeowners` | an active ruleset, CODEOWNERS without errors, a PR blocked without review | no | [#44](https://github.com/stephrobert/github-actions-training/issues/44) |
| `actions-autorisees` | the actions policy set through the API, and a workflow outside the list refused | no | [#45](https://github.com/stephrobert/github-actions-training/issues/45) |

### Command-line tooling

| Lab | What it proves | act | Tracking |
| --- | --- | --- | --- |
| `actionlint-corriger-des-workflows` | three faulty workflows made clean, a configuration for custom labels | yes | [#46](https://github.com/stephrobert/github-actions-training/issues/46) |
| `act-rejouer-en-local` | a workflow replayed with an event, inputs, secrets and a filtered matrix | yes | [#47](https://github.com/stephrobert/github-actions-training/issues/47) |
| `gh-piloter-les-runs` | trigger, follow to the verdict, rerun only the failed jobs | no | [#48](https://github.com/stephrobert/github-actions-training/issues/48) |

Total: **33 labs planned, 0 validated.** A lab is validated only once played
both ways: 0 before the work, 100 after the reference solution, and 0 again
after a reset.

<!-- LABS:END -->

## Contributing

The rules for writing a lab, the testing doctrine and the conventions live in
[`CONTRIBUTING.md`](CONTRIBUTING.md). The catalogue foundation is tracked in
issues [#11 to #15](https://github.com/stephrobert/github-actions-training/milestones).

## What the labs correct in the lessons

Every lab is paired with a lesson of the blog, and writing it means running
what the lesson claims. A full read of the course already found **23 findings
across 9 lessons**, 7 of them false statements, recorded with their evidence
in [`docs/corrections-guides.md`](docs/corrections-guides.md) (French). For
instance, the act lesson installed a vulnerable version, and the first
workflow of the course contained the template injection that the next lesson
forbids.

The training teaches, this catalogue proves: what it contradicts goes back to
the blog.

## License

Copyright (c) 2024 Stéphane Robert, https://blog.stephane-robert.info

This repository is released under the [MIT license](LICENSE).
