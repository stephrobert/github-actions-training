# Challenge: the calculator's first workflow

5 tasks, 100 points, 30 minutes.

The project sits in `challenge/work`. Everything happens in
`.github/workflows/`, which you create. The tests grade what act produces; they
never read your commands.

### Task 1: the tests run on every push (20 pts)

`act push` runs a job that succeeds, and pytest reports its nine tests there.

### Task 2: the tests run on every pull request (20 pts)

`act pull_request` runs the same job, with the same outcome.

### Task 3: the workflow only asks for read access to the code (20 pts)

A `permissions:` block is declared, and no job gets more than `contents: read`.
Not `write-all`, and not a missing block that would leave the repository
defaults in place.

### Task 4: every action is pinned to its commit SHA (20 pts)

Every `uses:` names a full forty-character SHA, followed by the version as a
comment, and `zizmor --offline` reports nothing on the `.github/workflows`
directory.

### Task 5: a broken test turns the pipeline red (20 pts)

On a copy of the project where `add` returns a wrong sum, `act push` produces a
failed job; on the intact project, the same job succeeds. This is the check
that tells a workflow which tests apart from a workflow which prints
"tests OK".
