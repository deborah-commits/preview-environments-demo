# PR preview demo

A small Flask + PostgreSQL task board for a Northflank preview-environments walkthrough.

The app creates its one table and inserts three sample tasks on startup. Existing
tasks and their completion status survive application restarts. Deleted starter
tasks are recreated on a later restart; custom tasks are not recreated.

## 1. Create the GitHub repository

Create an empty GitHub repository named `preview-environments-demo`.
Unzip the download and upload the four files **inside** `preview-demo` to the
repository root. `Dockerfile` must be at the root. Commit to `main`.

## 2. Set up a working baseline on Northflank

1. Create a demo project on Northflank Cloud.
2. Add a PostgreSQL addon, named `demo-db`. Use a small available plan.
3. Create a secret group and link the database's connection details. Set these aliases:

| Database detail | Environment variable alias |
|---|---|
| Host | `PG_HOST` |
| Port | `PG_PORT` |
| Database | `PG_DATABASE` |
| Username | `PG_USER` |
| Password | `PG_PASSWORD` |

The application defaults to PostgreSQL SSL mode `require`. Use the connection
details for that database; never put credentials in the repository. `DATABASE_URL`
is also supported, but use either it or the five variables consistently.

4. Create a combined build/deploy service from the repository's `main` branch.
5. Use Dockerfile build, path `/Dockerfile`, build context `/`.
6. Ensure the secret group is inherited by the app service at runtime.
7. Expose public HTTP port **8080** with a generated domain. Open the app.
8. Add a task, refresh, and confirm it is still there. `/health` is a readiness endpoint.

## 3. Set up the preview blueprint

Follow the current Northflank docs:
https://northflank.com/docs/v1/application/release/set-up-preview-blueprints

Open **Previews > New preview blueprint** in the project. Choose pull-request-ID
naming, add a Git pull request trigger for this repository, then configure:

- A build from the triggering PR using this Dockerfile.
- A **new PostgreSQL addon for each preview**.
- The application deployment using that build, with public HTTP port 8080.
- Credentials from **that preview's database**, using the same five aliases above.

Make the database available before the application starts. The app creates its
table and sample tasks automatically, so this demo needs no separate migration or
seed job. Do not point previews at the baseline database. Avoid inheriting its
database secret group into preview services; scope it to the baseline service.

Test the blueprint manually once. Then open a real PR to record the automatic trigger.

## 4. Two visible changes for the video

On a new branch named `preview-demo-change`, edit the two constants near the top
of `app.py`:

```python
APP_TITLE = "PR preview task board"
ACCENT = "#087f8c"
```

Open a PR targeting `main`. Its preview should have the new heading and teal
buttons, while the main-branch app keeps the original heading and purple buttons.
To show a second update, push another heading change to the same branch.

Add a task in the preview and refresh. Then show that task does not appear in the
baseline app. This demonstrates the preview is using its own database.

Verify PR-close cleanup in your connected Git provider before recording it. You
can also configure preview expiry to remove demo resources after a set lifetime.

## Recording

Do a practice run first. Record configuration, opening the PR, the triggered run,
the working app, an update and cleanup. Cut build waits. Move a short shot of the
finished preview to the start during editing if you want an outcome-first intro.

## Demo scope

This is an intentionally public, unauthenticated demo board: anyone with its URL
can edit the sample tasks. Use fake data only and delete demo resources when done.
It is not a production task-management application or a general migration pattern.

## Verification

Checked locally: Python syntax, page-template rendering, task form routes, HTML escaping.
Not yet checked: Docker image build, PostgreSQL integration, deployment on Northflank,
or preview creation/updates/cleanup. This workspace blocks local database sockets.
Run the baseline deployment and then the preview blueprint once before recording.
