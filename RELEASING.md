# Releasing github-actions-training

**Language:** [English](./RELEASING.md) · [Français](./RELEASING.fr.md)

This repository ships **lab content**, not a Python package. A release
publishes a **`tar.gz` bundle** of the catalogue as an asset of a GitHub
Release: no PyPI, no wheel, no external artifact registry.

## What a release contains

The `release.yml` workflow builds
`github-actions-training-<version>.tar.gz` with:

- `labs/`, `meta.yml`, `meta.fr.yml`, `curriculums.yml`, `conftest.py`,
  `pyproject.toml`, `uv.lock` and `mise.toml`,
- `scripts/` and `tests/`, because a catalogue that claims to validate itself
  must ship the means to do so,
- `validation-labs.json`, the proof that every lab was played in both
  directions by the real dsoxlab commands, with its date and the versions of dsoxlab and of the tools the labs use,
- the governance documents (`README`, `LICENSE`, `CONTRIBUTING`,
  `CODE_OF_CONDUCT`, `SECURITY`, `CHANGELOG`, `RELEASING`), **in both
  languages**: the
  archive is what someone who does not have the repository receives.

The lock file travels with `pyproject.toml` deliberately. A `>=` constraint
lets every installation resolve whatever it likes; an archive that claims to
ship the means to validate itself would not be saying *with what*.

It **excludes** the reference solutions (`solution/`, encrypted, they are the
answers), unversioned local steering and generated files (caches, dsoxlab
runtime state). An exclusion that matches nothing does not fail `tar`, unlike a path that is listed but absent,
which has already broken a release in the sibling Linux catalogue.

Four artifacts accompany the archive:

| Artifact | Purpose |
| --- | --- |
| `<pkg>.tar.gz.sha256` | integrity digest |
| `provenance.intoto.jsonl` | SLSA provenance, what Scorecard Signed-Releases reads |
| `<pkg>.tar.gz.cosign.bundle` | keyless Cosign signature bundle |
| (registry side) | GitHub's native build attestation |

## Why three jobs, and not one

The workflow is split into **build**, **attest**, **publish**, and that split is
the only thing separating SLSA Build Level 2 from Level 3.

GitHub's documentation puts it in two sentences: "Artifact attestations by
itself provides SLSA v1.0 Build Level 2", and "Reusable workflows can provide
isolation between the build process and the calling workflow, to meet SLSA v1.0
Build Level 3". As long as the job that builds the archive is also the one that
signs its provenance, nothing technically stops the build process from
producing provenance that lies. Level 3 requires the signing to happen out of
its reach.

Hence `.github/workflows/attester.yml`, called as a reusable workflow:

- it is the **only workflow in the repository** granted `attestations: write`;
- it receives **a name and a digest**, never the archive nor the repository: it
  performs no `checkout`;
- the publish job can write the release but **cannot attest**, lacking that
  permission;
- the archive is re-checked against its digest **before** publication, so that
  an artifact altered between two jobs is not published with provenance that
  does not describe it.

The call reads `uses: ./.github/workflows/attester.yml`, and not the newer
`$/` "self-repository" form, even though zizmor recommends the latter. The
reason is worth recording: security tooling cannot read `$/` yet, and an
analyser that does not understand a construct cannot judge it safe. Measured on
2026-09-15, on that exact line: actionlint rejects it as an invalid format,
zizmor 1.26.1 refuses to load the file and audits nothing at all, and Plumber
takes it for an unpinned third-party action from an unauthorised source, two
HIGH findings and a score of 70/100 instead of 100/100. The called workflow is
the one that *signs*: it is the last line in the repository on which to give up
the analysers' scrutiny.

## Cutting a release

1. Check that the catalogue is green, not merely shippable:

   ```bash
   dsoxlab validate-structure --check-urls
   pre-commit run --all-files --hook-stage pre-push
   python3 scripts/verify-solutions.py --deux-sens --check
   python3 scripts/valider-labs.py      # writes validation-labs.json
   ```

2. **Re-attest the labs that changed since their verdict.** A lab whose tests,
   files, shared `conftest.py` or descriptors changed after the commit that
   recorded its verdict is no longer attested by `validation-labs.json`. From
   the site repository (`test-astro-5`, cloned next to this one), run:

   ```bash
   python3 scripts/reattester-labs.py --depot github-actions-training           # plan and safeguards
   python3 scripts/reattester-labs.py --depot github-actions-training --apply   # replay and commit
   ```

   The script replays each lab marked "to re-attest" through
   `scripts/valider-labs.py`, one at a time (modified tests and labs first,
   then shared `conftest.py`, then descriptors), checks that the
   `validation-labs.json` diff only touches those labs, reruns `--check` and
   `pytest tests/`, and makes a **local** commit of the record alone. It
   refuses a dirty repository and an active lab. A RED verdict is not
   committed: fix the lab, then run it again.

   Before tagging, run the dry-run again: it must print
   **"0 lab(s) à réattester"**. Then push the record commit with the rest of
   the release.

3. Move the `CHANGELOG.md` and `CHANGELOG.fr.md` entries under a new version.
4. Tag and push the tag, which triggers `release.yml`:

   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

5. The workflow builds the `tar.gz`, attests its provenance, signs it keyless
   and creates the GitHub Release with auto-generated notes.

## Verifying a release

Integrity and contents:

```bash
sha256sum -c github-actions-training-<version>.tar.gz.sha256
tar tzf github-actions-training-<version>.tar.gz | head
```

Build provenance. Proves the archive really was produced by this repository's
workflow, and not rebuilt by someone else:

```bash
gh attestation verify github-actions-training-<version>.tar.gz \
  --repo stephrobert/github-actions-training
```

**The check that establishes Build Level 3** names the signing workflow. It
fails if the provenance was produced anywhere other than the isolated attester
workflow, and it is the one to run on the first release to confirm the chain
holds:

```bash
gh attestation verify github-actions-training-<version>.tar.gz \
  --repo stephrobert/github-actions-training \
  --signer-workflow stephrobert/github-actions-training/.github/workflows/attester.yml
```

Keyless Cosign signature. **Both** certificate flags are mandatory: without
them, `cosign verify-blob` accepts any identity, which empties the verification
of its meaning.

```bash
cosign verify-blob \
  --bundle github-actions-training-<version>.tar.gz.cosign.bundle \
  --certificate-identity-regexp "https://github.com/stephrobert/github-actions-training/.github/workflows/release.yml@.*" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  github-actions-training-<version>.tar.gz
```

> **Cosign version trap.** The CI installs **Cosign 3.x**, which writes a new
> bundle format. A local **Cosign 2.x** answers `no signatures found` on a
> perfectly signed archive: the release is not broken, the local tool cannot
> read the format. Check `cosign version` and align it before concluding
> anything.

## GitHub settings to do once

Two workflows need configuration that does not live in the repository:

- **`plumber.yml`** expects a `security` environment, restricted to the `main`
  branch, holding the `PLUMBER_ADMIN_TOKEN` secret: a fine-grained PAT with
  Administration, Contents and Metadata read access. Without it the workflow
  still runs, on the job token, but the `branchMustBeProtected` control abstains
  and the score stays incomplete.
- **Protection of the `main` branch**, through the "Protection de main" ruleset:
  that is what Scorecard and Plumber measure. Linear history, deletion and force
  pushes forbidden, pull request required with review thread resolution, and the
  CI jobs as required status checks.

### The "Protection de main" ruleset, ready to apply

A ruleset is a GitHub setting, not a file of the repository: it does not travel
with a `git push`. It is set **once**, after the repository is created and the
CI has run for the first time (a required check must have run at least once for
GitHub to offer it). The payload below takes over the rules of the sibling
catalogs; the contexts are the job names of `ci.yml`, the CodeQL matrix giving
two.

No approval is required (`required_approving_review_count: 0`): the repository
has a single maintainer, who cannot approve their own pull request. Going
through a pull request, resolving threads and a green CI stay mandatory.

```bash
gh api --method POST repos/stephrobert/github-actions-training/rulesets \
  --input - <<'JSON'
{
  "name": "Protection de main",
  "target": "branch",
  "enforcement": "active",
  "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
  "rules": [
    {"type": "deletion"},
    {"type": "non_fast_forward"},
    {"type": "required_linear_history"},
    {"type": "pull_request", "parameters": {
      "required_approving_review_count": 0,
      "dismiss_stale_reviews_on_push": true,
      "require_code_owner_review": false,
      "require_last_push_approval": false,
      "required_review_thread_resolution": true}},
    {"type": "required_status_checks", "parameters": {
      "strict_required_status_checks_policy": true,
      "required_status_checks": [
        {"context": "Zizmor (workflow static analysis)"},
        {"context": "Actionlint (workflow syntax)"},
        {"context": "Poutine (CI/CD exploit chains)"},
        {"context": "Pre-commit parity (all hooks)"},
        {"context": "Contrat du catalogue (leçons jumelées comprises)"},
        {"context": "CodeQL (python)"},
        {"context": "CodeQL (actions)"}]}}
  ]
}
JSON
```

This block has **never been applied**: the repository does not exist on GitHub
yet. On first application, read the created ruleset back in *Settings > Rules*
and check that a direct push to `main` is refused.
