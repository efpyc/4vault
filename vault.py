#!/usr/bin/python3
# -*- coding:utf-8 -*-
__author__ = "efpyc"

from vault_core import VaultCore
from crypter import Crypter
from utils import checkDataFolder

if __name__ == '__main__':
    checkDataFolder()
    core = VaultCore()

    master_password = core.loginScreen()

    crypter = Crypter(master_password)
    crypter.setupCrypter()

    core.mainMenu(crypter=crypter)
else:
    raise Exception("This is main file just run it.")