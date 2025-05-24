#!/usr/bin/python3
# -*- coding:utf-8 -*-
__author__ = "efpyc"

import sqlite3
import sys
import rich
import utils
from rich.table import Table
from datetime import datetime
from crypter import Crypter, CryptoUtils

class VaultCore:
    def __init__(self):
        self.DATETIME_FORMAT = "%d %b %Y, %H:%M"
        self.IGNORE_STRING = "-"

    def loginScreen(self):
        utils.banner()
        c_utils = CryptoUtils()
        is_first_run = c_utils.checkFirstRun()
        if is_first_run:
            utils.warning("Please be careful! You must write your master password to a notepad and keep it securely.\nIf you lose your master password you CANNOT access your datas.")
            utils.info("The password will be not shown while you typing.")
            master_password = utils.getPassword("Master password")
            self.master_password = master_password
            c_utils.saveSettingsDB(master_password)
            utils.success("Settings was saved!")
        else:
            utils.info("The password will be not shown while you typing.")
            master_password = utils.getPassword("Master password")
            if not c_utils.checkHashedMasterPassword(master_password):
                utils.prohibited("Invalid master password!")
                self.exitTool()
            else:
                self.master_password = master_password
                utils.success("Welcome!")
        return self.master_password
    def mainMenu(self, crypter : Crypter):
        self.crypter = crypter
        self.db_path = utils.default_paths["vault"]
        self.db = sqlite3.connect(self.db_path)
        self.cursor = self.db.cursor()
        texts = [
            ":HEAVY_PLUS_SIGN: Add New Entry",
            ":SPIRAL_NOTE_PAD: List All Entries",
            "🔍 Search by Service",
            ":PENCIL: Update Entry",
            ":CROSS_MARK: Delete Entry",
            "📄 Show Entry Details",
            "🔚 Exit",
        ]
        utils.menuList(texts)
        print("")
        try:
            option = int(utils.question("Choose an option"))
        except:
            utils.failure("Please give an integer value when choosing an option.")
            self.exitTool()

        if(option == 1):
            self.menuAddEntry()
        elif(option == 2):
            self.menuListAllEntries()
        elif(option == 3):
            self.menuSearch()
        elif(option == 4):
            self.menuUpdateEntry()
        elif(option == 5):
            self.menuDeleteEntry()
        elif(option == 6):
            self.showEntry()
        elif(option == 0):
            self.exitTool()
        else:
            self.menuInvalidOption()

    def menuInvalidOption(self):
        utils.prohibited("Invalid option. Please try again.")
        self.exitTool()

    def formatCreatedAt(self, created_at):
        dt = datetime.fromisoformat(created_at)
        return dt.strftime(self.DATETIME_FORMAT)

    def menuAddEntry(self):
        global note
        utils.clear()
        utils.banner()
        service_name = utils.question("Service name")
        username = utils.question("Username (or e-mail)")
        password = utils.question("Password")
        note = utils.question("Note (you can leave it blank)")
        created_at = utils.getCreatedAt()
        if service_name == "":
            utils.prohibited("Service name CANNOT be empty.")
            self.exitTool()
        if username == "":
            utils.prohibited("Username CANNOT be empty.")
            self.exitTool()
        if password == "":
            utils.prohibited("Password CANNOT be empty.")
            self.exitTool()
        encrypted_datas = (
            service_name,
            self.crypter.encrypt(username),
            self.crypter.encrypt(password),
            created_at,
            self.crypter.encrypt(note) if note != "" else "NULL"
        )
        self.cursor.execute("INSERT INTO VAULT (SERVICE,USERNAME,PASSWORD,CREATED_AT,NOTE) VALUES (?,?,?,?,?)", encrypted_datas)
        self.db.commit()
        utils.success(f"Entry added successfully for {service_name} !")
        self.exitTool()

    def menuDeleteEntry(self):
        utils.clear()
        utils.banner()
        entry_id = utils.question("Give an entry ID")
        try:
            entry_id = int(entry_id)
        except:
            utils.prohibited("The entry id must be integer.")
            self.exitTool()
        self.cursor.execute("SELECT SERVICE,USERNAME,CREATED_AT,NOTE FROM VAULT WHERE ID=?", (entry_id,))
        results = self.cursor.fetchall()
        if len(results) == 0:
            utils.failure(f"No entry exists with this ID: {entry_id}")
            self.exitTool()
        else:
            service, username, created_at, note = results[0]
            created_at = self.formatCreatedAt(created_at)
            username = self.crypter.decrypt(username)
            if not note == "NULL":
                note = self.crypter.decrypt(note)
            rich.print(f"""[bold]
🔐 Entry Details
────────────────────────────
[cyan]Service:[/cyan]       {service}
[cyan]Username:[/cyan]      {username}
[cyan]Created At:[/cyan]    [green]{created_at}[/green]
[cyan]Note:[/cyan]          [magenta]{note}[/magenta]
────────────────────────────
[/bold]""")
            answer = utils.question("Are you want to delete this entry? (y/n)")
            answer = answer.lower()
            if answer == "y" or answer == "yes":
                self.cursor.execute("DELETE FROM VAULT WHERE ID=?", (entry_id,))
                self.db.commit()
                utils.success(f"The entry with this ID: {entry_id} is deleted.")
            elif answer == "n" or answer == "no":
                utils.info("This entry will be not deleted.")
            else:
                utils.prohibited(f"'{answer}' is not valid choice please choose 'yes' or 'no'.")
        self.exitTool()

    def menuListAllEntries(self):
        global note
        utils.clear()
        utils.banner()
        self.cursor.execute("SELECT ID, SERVICE, USERNAME, CREATED_AT, NOTE FROM VAULT")
        datas = self.cursor.fetchall()
        if len(datas) == 0:
            utils.info("No entries found in your vault.")
        else:
            table = Table(title="[bold]🔐 Stored Entries[/bold]")
            table.add_column("ID", justify="center", no_wrap=True, style="cyan")
            table.add_column("Service Name", justify="left", no_wrap=True)
            table.add_column("Username", justify="left", no_wrap=True)
            table.add_column("Created", justify="left", no_wrap=True)
            table.add_column("Note", justify="left", no_wrap=False, style="yellow")
            for entry in datas:
                _id, service, username, created_at, note = entry
                if not note == "NULL":
                    note = self.crypter.decrypt(note)
                    note = (note[:30] + '...') if len(note) > 30 else note
                username = self.crypter.decrypt(username)
                created_at = self.formatCreatedAt(created_at)
                table.add_row(str(_id),str(service),str(username),str(created_at),str(note))
            rich.print(table)
            print("")
            selection = utils.question("Enter the ID of the entry you want to view in detail (or press Enter to cancel)")
            if selection == "":
                utils.info("Process was canceled.")
                self.exitTool()
            else:
                try:
                    selection = int(selection)
                except:
                    utils.prohibited("The ID should be an integer.")
                    self.exitTool()
                self.showEntry(_id=selection)
        self.exitTool()

    def showEntry(self, _id : int = None, dont_exit=False):
        global note
        utils.clear()
        utils.banner()
        if _id is None:
            _id = utils.question("Enter an ID")
            try:
                _id = int(_id)
            except:
                utils.prohibited("The ID should be an integer.")
                self.exitTool()

        self.cursor.execute("SELECT SERVICE, USERNAME, PASSWORD, CREATED_AT, NOTE FROM vault WHERE id = ?", (_id,))
        data = self.cursor.fetchall()
        if not len(data) == 0:
            data = data[0]
            service,username,password,created_at,note = data
            created_at = self.formatCreatedAt(created_at)
            username = self.crypter.decrypt(username)
            password = self.crypter.decrypt(password)
            if not note == "NULL":
                note = self.crypter.decrypt(note)
            rich.print(f"""[bold]
🔐 Entry Details
────────────────────────────
[cyan]Service:[/cyan]       {service}
[cyan]Username:[/cyan]      {username}
[cyan]Password:[/cyan]      [yellow]{password}[/yellow]
[cyan]Created At:[/cyan]    [green]{created_at}[/green]
[cyan]Note:[/cyan]          [magenta]{note}[/magenta]
────────────────────────────
[/bold]""")
        else:
            utils.prohibited(f"No entry is exists with this ID: {_id}")
        if not dont_exit:
            self.exitTool()

    def menuSearch(self):
        utils.clear()
        utils.banner()
        service_input = utils.question("Give a service name")
        self.cursor.execute("SELECT ID, SERVICE, USERNAME, CREATED_AT, NOTE FROM VAULT WHERE SERVICE=?",(service_input,))
        datas = self.cursor.fetchall()
        if len(datas) == 0:
            utils.info(f"No entries found in your vault for '{service_input}'.")
        else:
            table = Table(title=f"[bold]🔐 Stored Entries for {service_input}[/bold]")
            table.add_column("ID", justify="center", no_wrap=True, style="cyan")
            table.add_column("Service Name", justify="left", no_wrap=True)
            table.add_column("Username", justify="left", no_wrap=True)
            table.add_column("Created", justify="left", no_wrap=True)
            table.add_column("Note", justify="left", no_wrap=False, style="yellow")
            for entry in datas:
                _id, service, username, created_at, note = entry
                if not note == "NULL":
                    note = self.crypter.decrypt(note)
                    note = (note[:30] + '...') if len(note) > 30 else note
                username = self.crypter.decrypt(username)
                created_at = self.formatCreatedAt(created_at)
                table.add_row(str(_id), str(service), str(username), str(created_at), str(note))
            rich.print(table)
        self.exitTool()

    def menuUpdateEntry(self):
        global entry_id
        utils.clear()
        utils.banner()
        entry_id = utils.question("Give an entry ID: ")
        try:
            entry_id = int(entry_id)
        except:
            utils.prohibited("The entry id must be integer.")
            self.exitTool()
        self.cursor.execute("SELECT SERVICE,USERNAME,PASSWORD,NOTE FROM VAULT WHERE ID=?",(entry_id,))
        data = self.cursor.fetchall()
        if len(data) == 0:
            utils.failure(f"No entry exists with this ID: {entry_id}")
        else:
            self.showEntry(entry_id,dont_exit=True)
            answer = utils.question("Are you sure update this entry? (y/n)").lower()
            if answer == "y" or answer == "yes":
                print("")
                utils.info(f"If you don't want to update a value just type '{self.IGNORE_STRING}' (without ') so this value will be not updated.")
                print("")
                original_entry = data[0]
                service_name = utils.question("Service name")
                username = utils.question("Username (or e-mail)")
                password = utils.question("Password")
                note = utils.question("Note (you can leave it blank)")
                if service_name == "":
                    utils.prohibited("Service name CANNOT be empty.")
                    self.exitTool()
                if username == "":
                    utils.prohibited("Username CANNOT be empty.")
                    self.exitTool()
                if password == "":
                    utils.prohibited("Password CANNOT be empty.")
                    self.exitTool()
                if service_name == self.IGNORE_STRING:
                    service_name = original_entry[0]
                if username == self.IGNORE_STRING:
                    username = original_entry[1]
                else:
                    username = self.crypter.encrypt(username)
                if password == self.IGNORE_STRING:
                    password = original_entry[2]
                else:
                    password = self.crypter.encrypt(password)
                if note == self.IGNORE_STRING:
                    note = original_entry[3]
                else:
                    self.crypter.encrypt(note) if note != "" else "NULL"
                utils.info("Updating...")
                encrypted_datas = (
                    service_name,
                    username,
                    password,
                    note,
                    entry_id
                )
                self.cursor.execute("UPDATE VAULT SET SERVICE=?,USERNAME=?,PASSWORD=?,NOTE=? WHERE ID=?",(encrypted_datas))
                self.db.commit()
                utils.success(f"The entry with this ID: {entry_id} is updated.")
            elif answer == "n" or answer == "no":
                utils.info("This entry will be not updated.")
            else:
                utils.prohibited(f"'{answer}' is not valid option please type 'yes' or 'no'.")
        self.exitTool()

    def exitTool(self):
        rich.print(":CLOSED_LOCK_WITH_KEY: [bold]Session ended. Stay secure, see you next time.[/bold]")
        sys.exit()