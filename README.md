# Plex Share Manager

Web App to help automate and manage Plex shared library access. Supports importing users that you have already shared libraries with in Plex.

## Features

- Assign shared section to a user.
- Add a name to identify Friends easier
- Sort, Search and Filter Friends list
- Set/Change expiry date
- Display User Avatars
- Import Friends from Plex
- Import Sections from Plex
- Daily Task scheduler to disable Friends based on Expiry status
- Invite Friends, no need to do so in plex
- *Uninvite Friends* **Currently broken**

## Planned features

- TODO: add Authentication.
- TODO: Fix Known issues

## Known Issues

- add user dialog dims toast messages for form errors
- Uninvite does not remove invite from plex. This is an issue with API change from plex that has not yet been implemented in plexapi. The current API library does not support the changes.

## Setup for Dev

### Docker

Use the provided compose.dev.yaml.

### local

Using uv

`uv venv && uv sync`

Database init

`reflex db migrate`

You will need to comment out the following lines in `rxconfig.py`

```python
state_manager_mode="redis",
redis_url="redis://localhost",
```

Run Reflex

`reflex run`

## Setup with Docker

Use the included Docker Compose files.
