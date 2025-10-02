from __future__ import annotations
from jinja2 import Environment, FileSystemLoader, select_autoescape
from .util import sha256_bytes

def jinja_env(template_dir: str):
    return Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )

def render_template(env, name: str, model: dict) -> str:
    tpl = env.get_template(name)
    html = tpl.render(**model)
    return html

def compute_html_hash(html: str) -> str:
    return sha256_bytes(html.encode("utf-8"))
