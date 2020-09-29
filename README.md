**CHECK PINNED ISSUES - NVIDIA API Is frequently down, this is a known issue and is on NVIDIA's end. If you get timeout issues, best course of action is to wait it out. Check [HERE](https://github.com/samuelm2/Nvidia-Notify/issues/18) for more info.**

# Nvidia-Notify-MSEdge
A fork of the Nvidia-Notify project using Microsoft Edge Chromium for better performance on Windows, and no need for Firefox.

As originally described:
Simple, quick to set up stock notification bot for Nvidia 3080 that I used to get my 3080. Less than 250 lines of code.

[Check the Wiki!](https://github.com/samuelm2/Nvidia-Notify/wiki) - We'll post frequently asked questions, tips, and other useful info there.

## Requirements
- [New Edge (Chromium)](https://www.microsoft.com/en-us/edge)
- [Python 3](https://www.python.org/downloads/) (not python 2.x!)
- [pip](https://pip.pypa.io/en/stable/installing/) (to handle installing dependencies)
- [edgedriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/#downloads) (make sure to pick the correct version for your Edge release)

## Optional Components
- SMS Support: [A Twilio account](https://www.twilio.com/try-twilio) (can be a trial account)
- Discord Notifications via Webhooks: [Discord Webhook guide here](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks)

## How to set up
1. Clone/Download the notifier.py file and the icon.ico file and put them in the same folder
2. Download geckodriver
3. Open the .env file in a text editor and fill in the variables.
    -   Windows users can place `msedgedriver.exe` in the same folder as the script. Otherwise, update `WEBDRIVER_PATH`
	-	refer to the .env file for instructions on specific values.
	-   Many features are optional, you can leave them blank if you don't want to use them.
4. pip install dependencies
	-  `pip install -r win-requirements.txt` or `python -m pip install -r win-requirements.txt`
5. You can open `sites.json` in a text editor and modify the list of pages that get scanned.
  
## How to Run

```
python notifier.py
```

Note that on some linux and mac systems, you may have to use the following instead:
```
python3 notifier.py
```

## Testing if Notifications Work (Twilio/Discord)

```
python notifier.py test
```
*replace 'python' with 'python3' if that is how your system is configured*
