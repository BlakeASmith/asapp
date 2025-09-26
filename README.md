# asapp

Open websites in Chrome's app mode on Linux and macOS.

## Motivation

I use several GSuite apps such as Google Sheets and Google Docs, but there are not suitable 
desktop clients available for these apps. Running them in [app](https://superuser.com/questions/33548/starting-google-chrome-in-application-mode) mode using the `--app` CLI option
is a good substitute for this. 

## Installation

### PyPi

```shell script
pip install asapp
```

### Git Clone

```shell script
git clone https://github.com/BlakeASmith/as_app.git
pip install . 
```

## Usage

### Open Websites

Launch a website in it's own window, without any borders or browser options. 

```shell script
asapp open https://duckduckgo.com
```

### Create a Desktop Entry

```shell script
asapp shortcut --name DuckDuckGo https://duckduckgo.com
```

**On Linux:** This will add a `.desktop` file to the `~/.local/share/applications/` folder, causing
`DuckDuckGo` to appear in your app launcher of choice!

**On macOS:** This will create a `.app` bundle in the `~/Applications/` folder, making it available in Launchpad and Spotlight.

## Supported Browsers

The tool automatically detects and uses the following browsers:

**Linux:**
- Chromium Browser
- Google Chrome
- Google Chrome Beta

**macOS:**
- Google Chrome
- Chromium
- Google Chrome Canary

You can also specify a custom browser path using the `--chrome` option.
