#!/usr/bin/env python3

from __future__ import annotations

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


def main():
    from .core import start_app
    print("Starting app...")  # Add console log statement

    start_app()


if __name__ == "__main__":
    main()