"""
Interactive application to take user inputs
"""
import os
import sys

from ..bots import run_bot

def init():
    print("Welcome to ScanCrawl")
    run_bot("Telegram")    


def start_app():
    init()
