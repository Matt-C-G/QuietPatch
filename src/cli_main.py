# src/cli_main.py
def main() -> int:
    # Import your real CLI
    from qp_cli import main as real_main  # qp_cli.py is at repo root

    return int(real_main() or 0)
