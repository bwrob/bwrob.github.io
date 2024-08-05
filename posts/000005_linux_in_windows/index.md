---
title: "Linux in Windows via WSL"
description: "Great dev setup and still CS coffee break"
author: "bwrob"

date: "2024-08-07"
date-modified: "2024-08-01"

categories: [Dev setup]
image: image.jpg

draft: true
---
![](image.jpg){width="95%" fig-align="center"}

## Installing WSL

With administrative priviliges

```{shell}
wsl --update
wsl --version
wsl -l - -o
wsl --install -d 'Ubuntu-24.04'
```

Reboot system and see `Ubuntu' in programs

## Base Python and Rust setup

```{bash}
sudo apt-get update
```

## Base setup

[Install homebrew](https://dikabrenda.medium.com/how-to-install-brew-on-ubuntu-20-04-lts-linux-714c73379dd4)

```{bash}
sudo apt update
sudo apt-get install build-essential git -y
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
(echo; echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"') >> /home/bwrob/.zshrc
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
brew doctor
```

[Install zshell](https://phoenixnap.com/kb/install-zsh-ubuntu)

```{bash}
brew install zsh
zsh --version
zsh
echo $SHELL
sudo chsh -s $(which zsh)
```

Install oh my posh!
https://ohmyposh.dev/docs/installation/linux

```{bash}
brew install jandedobbeleer/oh-my-posh/oh-my-posh
echo 'eval "$(oh-my-posh init zsh)"' >> .zshrc 
```

## Aliases

```{bash}
# Alias definitions.
# You may want to put all your additions into a separate file like
# ~/.bash_aliases, instead of adding them here directly.
# See /usr/share/doc/bash-doc/examples in the bash-doc package.

if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi

alias zshconfig='nano ~/.zshrc'
alias ls='eza -la --group-directories-first --icons'
```

## Minor packages

fzf
```{bash}
brew install fzf
# Set up fzf key bindings and fuzzy completion
echo 'source <(fzf --zsh)' >> .zshrc 
```

```{bash}
brew install eza 
echo 'alias ls='eza -la --group-directories-first --icons'' >> .zshrc
```

```{bash}
brew install thefuck
echo 'eval $(thefuck --alias)' >> .zshrc
```

## Git and github

https://cis106.com/guides/Ubuntu%20Github%20Setup/

```{bash}
brew install git gh
```

# Rust setup 

For basic usage
```{bash}
brew install rust
```

## Python setup

```{bash}
brew install python@3.12
```

## Setting Up Poetry for Python Environment Management

### Understanding the Concerns
You're right to be cautious about installing Poetry globally. It's generally recommended to avoid global installations of environment managers to prevent conflicts and maintain isolation between projects.

### Recommended Setup

Here's a step-by-step guide to a robust Poetry setup:

#### 1. Install Poetry in a Virtual Environment
* Create a temporary virtual environment:
  ```bash
  python3 -m venv poetry_install_env
  ```
* Activate the environment:
  ```bash
  source poetry_install_env/bin/activate  # or activate.bat on Windows
  ```
* Install Poetry:
  ```bash
  pip install poetry
  ```

#### 2. Create Project-Specific Virtual Environments
* Navigate to your project directory:
  ```bash
  cd your_project_directory
  ```
* Initialize Poetry:
  ```bash
  poetry init
  ```
  Follow the prompts to configure your project.
* Create the virtual environment:
  ```bash
  poetry install
  ```
  Poetry will create a virtual environment within your project directory (usually in a `.venv` folder) and install the specified dependencies.

#### 3. Activate the Virtual Environment
* Activate the environment:
  ```bash
  poetry shell
  ```

### Additional Considerations

* **Using `pyenv` (Optional):** If you need to manage multiple Python versions, consider using `pyenv` to switch between them. Poetry can then leverage the active Python version.
* **Poetry Configuration:** You can customize Poetry's behavior by creating a `pyproject.toml` file in your project root and adding configuration options. Refer to the Poetry documentation for details.
* **Dependency Management:** Poetry excels at managing project dependencies. Use the `poetry add` and `poetry remove` commands to add or remove packages.

### Benefits of This Approach
* **Isolation:** Each project has its own isolated environment, preventing conflicts between dependencies.
* **Reproducibility:** You can easily recreate the project environment on different machines.
* **Efficiency:** Poetry optimizes the installation process and provides features like dependency resolution and locking.

By following these steps, you'll have a well-structured Python development environment that effectively utilizes Poetry's capabilities.

**Would you like to delve deeper into any specific aspect of this setup, such as configuring Poetry, managing dependencies, or using `pyenv`?**



## Rust setup

```{bash}
brew install rustup
rustup toolchain install stable
```