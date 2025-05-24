#!/usr/bin/python3
# -*- coding:utf-8 -*-
__author__ = "efpyc"

import os
import rich
from rich.prompt import Prompt
from datetime import datetime

sep = os.path.sep

default_paths = {
    "settings": f".{sep}data{sep}settings.SQL",
    "vault": f".{sep}data{sep}vault.SQL",
}

def checkDataFolder():
    if not os.path.exists("data/"):
        os.mkdir("data")

def getCreatedAt():
    return datetime.now().isoformat(timespec="seconds")

def menuList(texts : list):
    temp = 1
    last = texts[-1]
    texts.pop(-1)
    for text in texts:
        rich.print(f"[bold][cyan][[/cyan]{temp}[cyan]][/cyan] {text}[/bold]")
        temp += 1
    rich.print(f"[bold][cyan][[/cyan]0[cyan]][/cyan] {last}[/bold]")

def clear():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def prohibited(text):
    rich.print(f":NO_ENTRY_SIGN: [bold]{text}[/bold]")

def getPassword(text):
    answer = Prompt().ask(f"👉 [bold]{text}[/bold]",password=True)
    return answer

def question(text):
    answer = Prompt().ask(f"👉 [bold]{text}[/bold]")
    return answer

def success(text):
    rich.print(f":WHITE_HEAVY_CHECK_MARK: [bold]{text}[/bold]")

def failure(text):
    rich.print(f":CROSS_MARK: [bold]{text}[/bold]")

def info(text):
    rich.print(f"ℹ️  [bold]{text}[/bold]")

def warning(text):
    rich.print(f":warning: [bold]{text}[/bold]")

def banner():
    text = """[bold]
╔══════════════════════════════════╗
║          🔐 Welcome to           ║
║             4VAULT               ║
╚══════════════════════════════════╝[/bold]     
"""
    rich.print(text)
    info("Secure CLI-based password vault.")
    info("Your data is encrypted using AES-256-GCM.")
    print("")