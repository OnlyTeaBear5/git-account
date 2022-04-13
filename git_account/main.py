from argparse import ArgumentParser, Namespace
import getpass
import os
from pathlib import Path
import pickle
from typing import Dict, List


class GitCredentials:

    def __init__(
        self,
        username: str,
        personal_access_token: str,
        email: str,
        name: str,
        account_nickname: str or None = None):
        self.username = username
        self.pat = personal_access_token
        self.name = name
        self.email = email
        self.account_nickname  = account_nickname if account_nickname is not None else username

    def save(self, path: str):
        with open(os.path.join(path, f"{self.account_nickname}.pkl"), 'wb') as file:
            pickle.dump(self, file)

    def write(self, path: str):
        with open(os.path.join(path, ".git-credentials"), 'w') as git_credentials:
            git_credentials.write(self.generate_credential_string())
        with open(os.path.join(path, ".git-config"), 'w') as gitconfig:
            gitconfig.write(self.generate_git_config_string())

    def generate_credential_string(self):
        return f"https://{self.username}:{self.pat}@github.com"

    def generate_git_config_string(self):
        return f"""
[user]
	name = {self.name}
	email = {self.email}
[credential]
	helper = store
 """

    def __str__(self) -> str:
        return (
            f"Account Name: {self.account_nickname}\n"
            f"Username: {self.username}\n"
            f"Email: {self.email}\n"
            f"Name: {self.name}"
        )

    @staticmethod
    def from_pickle(filename: str) -> "GitCredentials":
        with open(filename, 'rb') as file:
            credentials = pickle.load(file)
        return credentials

    @classmethod
    def load_all_accounts(cls, path: str) -> List["GitCredentials"]:
        accounts = []
        for file in os.listdir(path):
            if file.endswith(".pkl"):
                try:
                    accounts.append(cls.from_pickle(os.path.join(path, file)))
                except Exception as e:
                    print(f"Unable to load {os.path.join(path, file)}")
                    raise e
        return accounts



def add(args: Namespace, accounts: List[GitCredentials]):
    names = [account.account_nickname for account in accounts]
    account_name = input("What do you want to name the account? ")

    if account_name in names:
        good_ans = False
        print("This account already exist. ", end="")
        while not good_ans:
            ans = input("Would you like to overwrite it?(y/n) ")

            good_ans =  ans.lower() in "yn"

            if good_ans and ans.lower() == "y":
                good_ans = True
            elif good_ans and ans.lower() == "n":
                add(args, accounts)
                return

    username = input("Github username: ")
    pac = getpass.getpass("Personal access: ")

    email = input("Email: ")
    name = input("Your name: ")

    credentials = GitCredentials(username, pac, email, name, account_name)

    credentials.save(args.save_path)


def add_parser(parser: ArgumentParser):
    parser.add_argument("--switch",
                        help="Switches credentials from one github account to another",
                        type=str,
                        default=None
                        )

    parser.add_argument("--list", '-l',
                        help="Prints list of saved github accounts",
                        action="store_true",
                        default=False)

    parser.add_argument("--add",
                        help="Adds an github account",
                        action="store_true",
                        default=False)

    parser.add_argument("--path",
                        help="Path folder with .git-credential. Default is '~/'",
                        type=str,
                        default=str(Path.home())
                        )

    parser.add_argument("--save-path",
                        help="Path to save credentials. Default is '~/.git-accounts'",
                        type=str,
                        default=os.path.join(str(Path.home()), ".git-accounts")
                        )


def switch(args: Namespace, accounts: List[GitCredentials]):
    names = [account.account_nickname for account in accounts]
    
    for account in accounts:
        if account.account_nickname == args.switch:
            credentials: GitCredentials = account
            break
    else:
        raise Exception(f"'{args.switch}' not found in accounts. Use --list or -l to list accounts")
        
    credentials.write(args.path)
        
    print(f"Switched to {credentials.account_nickname} with username {credentials.username}")


def main():
    parser: ArgumentParser = ArgumentParser()
    add_parser(parser)
    args: Namespace = parser.parse_args()

    if not os.path.exists(args.path):
        os.mkdir(args.path)
    if not os.path.exists(args.save_path):
        os.mkdir(args.save_path)
    accounts = GitCredentials.load_all_accounts(args.save_path)
    if args.list:
        for account in accounts:
            print(account, "\n")
    if args.add:
        add(args, accounts)
    if args.switch is not None:
        switch(args, accounts)