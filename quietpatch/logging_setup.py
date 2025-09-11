import logging, os, pathlib
from logging.handlers import RotatingFileHandler

LOG_DIR = pathlib.Path(os.environ.get('QP_LOG_DIR') or (pathlib.Path.home()/'.quietpatch'/'logs'))
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG = LOG_DIR / 'quietpatch.log'

handler = RotatingFileHandler(LOG, maxBytes=512*1024, backupCount=3, encoding='utf-8')
fmt = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
root = logging.getLogger()
root.setLevel(logging.INFO)
handler.setFormatter(fmt)
root.addHandler(handler)

# Rule: never log PII or full paths of user documents. Keep messages short, actionable.
