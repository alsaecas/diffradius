# Security model

DiffRadius is intentionally conservative: the agent can inspect a repository but cannot modify it or run
arbitrary project commands.

## What the agent can do

- list repository files;
- read bounded text ranges;
- search text;
- read the supplied ticket;
- read the supplied diff.

All file paths are resolved against the configured repository root and attempts to escape that root are
rejected.

## What the agent cannot do

- write, delete or rename repository files;
- execute shell commands or tests in the reviewed repository;
- access benchmark ground truth/oracle files;
- receive credentials from the application;
- perform release/deployment actions.

The benchmark runner executes only the synthetic fixtures committed in this repository. Do not replace
those fixtures with untrusted third-party code and execute them on a host you care about.

## Data handling

Hosted Agents SDK tracing is disabled. Local trajectory files can contain source excerpts and should only
be shared when the reviewed repository is safe to disclose. `OPENAI_API_KEY` is read from the environment
and is never serialized by DiffRadius.
