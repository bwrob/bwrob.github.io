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
```

## Minor packages

```{bash}
brew install gcc eza thefuck fzf bat neovim
```

## Python venv setup
