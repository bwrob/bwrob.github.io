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

eza ls replacment
```{bash}
brew install eza 
echo 'alias ls='eza -la --group-directories-first --icons'' >> .zshrc
```

thefuck
```{bash}
brew install thefuck
echo 'eval $(thefuck --alias)' >> .zshrc
```

tmux



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
brew install pipx
pipx ensurepath
pipx install poetry poethepoet pre-commit pytest ruff basedpyright
which poetry 
```

```{bash}
# Instal dependencies
poetry install
# Install pre-commit
pre-commit install
# Update pre-commit
pre-commit autoupdate
# Run pre-commit to test setup
pre-commit run --all-files
```

## Rust setup

```{bash}
brew install rustup
rustup toolchain install stable
```

# Dotfiles managment via Stow
