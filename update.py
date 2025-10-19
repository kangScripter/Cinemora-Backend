from logging import FileHandler, StreamHandler, INFO, basicConfig, error as log_error, info as log_info
from os import path as ospath, environ
from subprocess import run as srun
from requests import get as rget
from dotenv import load_dotenv

basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[FileHandler('log.txt'), StreamHandler()],
                    level=INFO)

# Clear old log if present
if ospath.exists('log.txt'):
    try:
        with open('log.txt', 'r+') as f:
            f.truncate(0)
    except Exception:
        pass

# Try fetch remote config file if provided
CONFIG_FILE_URL = environ.get('CONFIG_FILE_URL')
if CONFIG_FILE_URL:
    try:
        res = rget(CONFIG_FILE_URL, timeout=15)
        if res.status_code == 200:
            with open('config.env', 'wb+') as f:
                f.write(res.content)
            log_info('Downloaded config.env from CONFIG_FILE_URL')
        else:
            log_error(f"Failed to download config.env {res.status_code}")
    except Exception as e:
        log_error(f"CONFIG_FILE_URL: {e}")

# Load (possibly newly downloaded) config.env
load_dotenv('config.env', override=True)

UPSTREAM_REPO = environ.get('UPSTREAM_REPO')
UPSTREAM_BRANCH = environ.get('UPSTREAM_BRANCH', 'master')

if UPSTREAM_REPO:
    try:
        # Remove existing .git if any
        if ospath.exists('.git'):
            srun(["rm", "-rf", ".git"], shell=False)

        cmd = (
            "git init -q && "
            "git config --global user.email \"noreply@example.com\" && "
            "git config --global user.name \"autoupdate\" && "
            "git remote add origin {repo} && "
            "git fetch origin -q && "
            "git reset --hard origin/{branch} -q"
        ).format(repo=UPSTREAM_REPO, branch=UPSTREAM_BRANCH)

        update = srun(cmd, shell=True)

        if update.returncode == 0:
            log_info('Successfully updated with latest commit from UPSTREAM_REPO')
        else:
            log_error('Something went wrong while updating, check UPSTREAM_REPO if valid or not!')
    except Exception as e:
        log_error(f'Update error: {e}')
else:
    log_info('No UPSTREAM_REPO configured, skipping update.')
