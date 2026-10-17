# Security policy

**Language:** [English](./SECURITY.md) · [Français](./SECURITY.fr.md)

## Supported versions

`github-actions-training` is not versioned: there are no releases to
support. Security fixes are applied to the `develop` integration branch, the
only supported state of the catalogue.

## Reporting a vulnerability

**Do not open a public issue for a security vulnerability.**

If you believe you have found a vulnerability, report it privately:

- Preferably: open a
  [private security advisory](https://github.com/stephrobert/github-actions-training/security/advisories/new)
  on GitHub.
- Otherwise, use the contact details published on
  <https://blog.stephane-robert.info>.

Please include:

- a description of the vulnerability and its impact,
- the steps to reproduce it (command, environment, `dsoxlab --version`,
  `act --version`),
- any relevant log or proof of concept.

We will keep you informed of the fix and credit you in the advisory if you
wish.

## Disclosure policy

We practise coordinated disclosure and commit to the following timelines,
counted from the receipt of your report:

| Step | Target |
| --- | --- |
| Acknowledgement of your report | within **48 hours** |
| Initial assessment and severity rating | within **5 days** |
| Fix released, or written remediation plan | within **30 days** |
| Public disclosure of the vulnerability | within **90 days** |

We publish the advisory as soon as a fix is available, or at the latest when
the **90 days** expire, whichever comes first. If a vulnerability is actively
exploited, we may disclose it earlier to protect users. If a complex fix needs
more time, we tell you before the deadline and agree on a new date with you.

## Scope

This repository ships **lab content** run by the external `dsoxlab` CLI:
scenarios, starting points, reference solutions, tests, and the workflows that
act runs on the learner's machine.

**In** scope:

- dangerous or malicious lab material: a fixture, a solution or a test that
  does something other than what it announces;
- a workflow of the repository or of a lab that would expose a secret, widen
  the token permissions without reason, or run untrusted code;
- an action pinned to a SHA that does not match the announced version;
- a secret committed by mistake.

A specific note about this catalogue: **several labs deliberately ship a
vulnerable workflow**, because that is their subject. The template injection
lab starts from an injectable workflow, the `pull_request_target` lab from the
dangerous pattern, the pinning lab from moving tags. This is not a
vulnerability of the repository: it is the material of the exercise. These
workflows run **locally, with act**, in the lab's working directory, not on a
repository that serves any other purpose.

**Out** of scope: vulnerabilities of the `dsoxlab` engine, which belong to
[its own repository](https://github.com/stephrobert/dsoxlab), and those of act
and of third-party actions, to be reported to their respective projects.
