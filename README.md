# PixelFed Bot

A small automation bot for PixelFed. This repository contains the code and configuration needed to run a PixelFed client bot, including setup and run instructions.

## Overview

`pixelfed_bot` is designed to automate interactions with a PixelFed instance. It may include features such as posting images, scheduling uploads, and managing captions or metadata.

## Getting Started

### Requirements

- Python 3.11+ (or whichever version is required by the project)
- `pip`
- A virtual environment is strongly recommended

### Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If the project uses `pyproject.toml` instead of `requirements.txt`:

```bash
python3 -m pip install -e .
```

## Configuration

Configure the bot using environment variables or configuration files used by the repository.

Required environment variables to update these values in your shell or in a `.env` file if the project supports it:

```bash
ACCOUNT_ID="<pixelfed-id>"
TOKEN="<your-access-token>"
APP_LOG="/path/to/pixelbot.log"
```

## Usage

help:

```bash
usage: Pixelfed Bot [-h] -t {home,public,notifications,global,tag} [-l LIMIT] [--report]
                    [--migrate] [--version]

Get home, public, notification timelines and like posts and follow users.

options:
  -h, --help            show this help message and exit
  -t, --timeline_type {home,public,notifications,global,tag}
                        timeline type
  -l, --limit LIMIT     override session like limit
  --report              print out db data
  --migrate             run migrations, manual flag
  --version             show program's version number and exit

the pixels go on and on...
```

Run the bot with:

```bash
python ./src/main.py -t "home"
```
unfollow option 
 ```bash
python ./src/main.py --unfollow <"pixelfed-id-to-unfollow">
```

## Testing

Run the test suite with `pytest`:

```bash
pytest
```

## Contributing

- Create a new branch for your work
- Open a pull request with a clear description of changes
- Include tests for new features or bug fixes

## Notes

- Inspect the repository layout to confirm the exact entrypoint and configuration file names.
- Update the environment variables and commands above to match the actual implementation details in your codebase.
