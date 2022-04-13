# git-account

## Setup
    
- Install python >= 3.8
  -  https://www.python.org/downloads/
- Install poetry
  - Run
  
        pip3 install poetry

- After cloning the repo, open the terminal into the repo's directory. 
  - Install it by running
        
        pip3 install .

## Usage

- Add a account by running

        git-account --add
    
  - Follow the instructions to setup the account

- Switch to account using

        git-account --switch <name-of-account>

- See saved accounts by running

        git-account --list