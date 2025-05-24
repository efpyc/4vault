#!/usr/bin/python3
# -*- coding:utf-8 -*-
__author__ = "efpyc"

import os
import sqlite3
import bcrypt
from utils import default_paths
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class CryptoUtils:
    def __init__(self):
        self.settings_db = default_paths["settings"]
        self.vault_db = default_paths["vault"]
        self.IV_SIZE = 12
        self.SALT_SIZE = 16
        self.TAG_SIZE = 16
        self.ENCODING = "utf-8"
    def checkFirstRun(self):
        global status
        if not os.path.exists(self.settings_db) or not os.path.exists(self.vault_db):
            if not os.path.exists(self.settings_db):
                self.createSettingsDB()
            if not os.path.exists(self.vault_db):
                self.createVaultDB()
            status = True
        else:
            connection = sqlite3.connect(self.settings_db)
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM SETTINGS")
            datas = cursor.fetchall()
            if len(datas) == 0:
                status = True
            else:
                status = False
        return status
    def createSalt(self):
        return os.urandom(self.SALT_SIZE)
    def saveSettingsDB(self, master_password):
        salt = self.createSalt()
        hashed_master_password = self.hashMasterPassword(master_password)
        connection = sqlite3.connect(self.settings_db)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO SETTINGS (hash, salt) VALUES (?, ?)", (hashed_master_password, salt))
        connection.commit()
    def getSalt(self):
        connection = sqlite3.connect(self.settings_db)
        cursor = connection.cursor()
        cursor.execute("SELECT SALT FROM SETTINGS")
        rows = cursor.fetchall()
        if not len(rows) == 0:
            salt = rows[0][0]
        else:
            salt = None
        return salt
    def hashMasterPassword(self, master_password : str):
        hashed = bcrypt.hashpw(master_password.encode(),salt=bcrypt.gensalt())
        return hashed
    def getHashedMasterPassword(self):
        connection = sqlite3.connect(self.settings_db)
        cursor = connection.cursor()
        cursor.execute("SELECT HASH FROM SETTINGS")
        rows = cursor.fetchall()
        if not len(rows) == 0:
            hashed_master_password = rows[0][0]
        else:
            hashed_master_password = None
        return hashed_master_password
    def checkHashedMasterPassword(self, master_password : str):
        hashed_master_password = self.getHashedMasterPassword()
        if bcrypt.checkpw(master_password.encode(), hashed_master_password):
            return True
        else:
            return False
    def createRandomIV(self):
        return os.urandom(self.IV_SIZE)
    def createKey(self,master_password : str):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.getSalt(),
            iterations=1200000
        )
        key = kdf.derive(master_password.encode())
        return key
    def createSettingsDB(self):
        connection = sqlite3.connect(self.settings_db)
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE "SETTINGS" (
	"id"	INTEGER,
	"hash"	TEXT,
	"salt"	BLOB
)''')
        connection.commit()
    def createVaultDB(self):
        connection = sqlite3.connect(self.vault_db)
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE "VAULT" (
	"id"	INTEGER NOT NULL,
	"SERVICE"	TEXT,
	"USERNAME"	BLOB,
	"PASSWORD"	BLOB,
	"CREATED_AT"	TEXT,
	"NOTE"	BLOB,
	PRIMARY KEY("id" AUTOINCREMENT)
);''')
        connection.commit()

class Crypter(CryptoUtils):
    def __init__(self,master_password):
        super().__init__()
        self.master_password = master_password
    def setupCrypter(self):
        self.key = self.createKey(self.master_password)
    def encrypt(self, text : str):
        crypter = AESGCM(self.key)
        iv = self.createRandomIV()
        encrypted_data_with_tag = crypter.encrypt(nonce=iv, data=text.encode(), associated_data=None)
        ciphertext = iv + encrypted_data_with_tag
        return ciphertext
    def decrypt(self, cipher):
        crypter = AESGCM(self.key)
        iv = cipher[:12]
        encrypted_data_with_tag = cipher[12:]
        plaintext = crypter.decrypt(nonce=iv, data=encrypted_data_with_tag, associated_data=None).decode(self.ENCODING)
        return plaintext