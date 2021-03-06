import json
import platform
import random
import webbrowser
from datetime import datetime, time
from os import path, getenv, system
from time import sleep
from urllib.request import urlopen, Request
from enum import Enum
import sys
import requests
from requests.exceptions import Timeout
from dotenv import load_dotenv
import logging

platform = platform.system()
PLT_WIN = "Windows"
PLT_LIN = "Linux"
PLT_MAC = "Darwin"

class Methods(str, Enum):
    GET_SELENIUM = "GET_SELENIUM"
    GET_URLLIB = "GET_URLLIB"
    GET_API = "GET_API"


'''
    Adding a new website to check:

    sites.json

    [url]: url of the website you want to check
    [api]: API URL for the site, if omitted; keyword is required
    [keyword]: The substring that you're looking for in the html of the website
    [method]: Set this to GET_SELENIUM, GET_URLLIB, or GET_API to choose which method is used to fetch data from the site. USE_SELENIUM is useful for jsx pages
    [name]: A nickname for the alert to use. This is displayed in alerts.
    [enabled]: check the site? true or false
'''

# Set up environment variables and constants. Do not modify this unless you know what you are doing!
load_dotenv()
USE_TWILIO = False
USE_SELENIUM = False
USE_DISCORD_HOOK = False
WEBDRIVER_PATH = path.normpath(getenv('WEBDRIVER_PATH'))
DISCORD_WEBHOOK_URL = getenv('DISCORD_WEBHOOK_URL')
TWILIO_TO_NUM = getenv('TWILIO_TO_NUM')
TWILIO_FROM_NUM = getenv('TWILIO_FROM_NUM')
TWILIO_SID = getenv('TWILIO_SID')
TWILIO_AUTH = getenv('TWILIO_AUTH')
ALERT_DELAY = int(getenv('ALERT_DELAY'))
MIN_DELAY = int(getenv('MIN_DELAY'))
MAX_DELAY = int(getenv('MAX_DELAY'))
OPEN_WEB_BROWSER = getenv('OPEN_WEB_BROWSER') == 'true'

with open('sites.json', 'r') as f:
    sites = json.load(f)

# Selenium Setup - includes specific setup for MS Edge Chromium Webdriver
if WEBDRIVER_PATH:
    USE_SELENIUM = True
    print("Enabling Selenium/MSEdge... ", end='')

    from msedge.selenium_tools import Edge, EdgeOptions
    options = EdgeOptions()
    options.use_chromium = True
    options.headless = True
    options.page_load_strategy = 'eager'
    options.add_argument('log-level=3')

    # Set the threshold for selenium to WARNING
    from selenium.webdriver.remote.remote_connection import LOGGER as seleniumLogger
    seleniumLogger.setLevel(logging.WARNING)
    # Set the threshold for urllib3 to WARNING
    from urllib3.connectionpool import log as urllibLogger
    urllibLogger.setLevel(logging.WARNING)
    
    driver = Edge(options = options)
    reload_count = 0
    print("Done!")

# Twilio Setup
if TWILIO_TO_NUM and TWILIO_FROM_NUM and TWILIO_SID and TWILIO_AUTH:
    USE_TWILIO = True
    print("Enabling Twilio... ", end='')
    from twilio.rest import Client

    client = Client(TWILIO_SID, TWILIO_AUTH)
    print("Done!")

# Discord Setup
if DISCORD_WEBHOOK_URL:
    USE_DISCORD_HOOK = True
    print('Enabled Discord Web Hook.')

# Platform specific settings
print("Running on {}".format(platform))
if platform == PLT_WIN:
    from win10toast import ToastNotifier

    toast = ToastNotifier()


def alert(site):
    product = site.get('name')
    print("{} IN STOCK".format(product))
    print(site.get('url'))
    if OPEN_WEB_BROWSER:
        webbrowser.open(site.get('url'), new=1)
    os_notification("{} IN STOCK".format(product), site.get('url'))
    sms_notification(site.get('url'))
    discord_notification(product, site.get('url'))
    sleep(ALERT_DELAY)


def os_notification(title, text):
    if platform == PLT_MAC:
        system("""
                  osascript -e 'display notification "{}" with title "{}"'
                  """.format(text, title))
        system('afplay /System/Library/Sounds/Glass.aiff')
        system('say "{}"'.format(title))
    elif platform == PLT_WIN:
        toast.show_toast(title, text, duration=5, icon_path="icon.ico")
    elif platform == PLT_LIN:
        # Feel free to add something here :)
        pass


def sms_notification(url):
    if USE_TWILIO:
        client.messages.create(to=TWILIO_TO_NUM, from_=TWILIO_FROM_NUM, body=url)


def discord_notification(product, url):
    if USE_DISCORD_HOOK:
        data = {
            "content": "{} in stock at {}".format(product, url),
            "username": "In Stock Alert!"
        }
        result = requests.post(DISCORD_WEBHOOK_URL, data=json.dumps(data), headers={"Content-Type": "application/json"})
        try:
            result.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
        else:
            print("Payload delivered successfully, code {}.".format(result.status_code))


def selenium_get(url):
    global driver
    global reload_count

    try:
        driver.get(url)
        http = driver.page_source
    except:
        http = ''

    reload_count += 1
    if reload_count == 10:
        reload_count = 0
        driver.close()
        driver.quit()
        driver = Edge(options = options)
    return http


def urllib_get(url):
    try:
        # for regular sites
        # Fake a Firefox client
        request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        page = urlopen(request, timeout=10)
        html_bytes = page.read()
        html = html_bytes.decode("utf-8")
        return html
    except Timeout as ex:
        return ''


def nvidia_get(url, api_url):
    try:
        response = requests.get(api_url, timeout=5)
        item = response.json()
        if item['products']['product'][0]['inventoryStatus']['status'] != "PRODUCT_INVENTORY_OUT_OF_STOCK":
            alert(url)
    except Timeout as ex:
        dummyvar = 1


def is_test():
    try:
        if sys.argv[1] == 'test':
            alert(sites[0])
            print("Test complete, if you received notification, you're good to go.")
            return True
    except:
        return False


def main():
    search_count = 0
    
    exit() if is_test() else False

    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("Starting search {} at {}".format(search_count, current_time))
        search_count += 1
        for site in sites:
            if site.get('enabled'):
                print("\tChecking {}...".format(site.get('name')))

                try:
                    if site.get('method') == Methods.GET_SELENIUM:
                        if not USE_SELENIUM:
                            continue
                        html = selenium_get(site.get('url'))
                    elif site.get('method') == Methods.GET_API:
                        if 'nvidia' in site.get('name').lower():
                            nvidia_get(site.get('url'), site.get('api'))
                        continue
                    else:
                        html = urllib_get(site.get('url'))
                except Exception as e:
                    print("\t\tConnection failed...")
                    print("\t\t{}".format(e))
                    continue
                keyword = site.get('keyword')
                alert_on_found = site.get('alert')
                index = html.upper().find(keyword.upper())
                if alert_on_found and index != -1:
                    alert(site)
                elif not alert_on_found and index == -1:
                    alert(site)

        base_sleep = 1
        total_sleep = base_sleep + random.uniform(MIN_DELAY, MAX_DELAY)
        print("\t\tSleeping for {0:.1f} seconds...".format(total_sleep))
        sleep(total_sleep)


if __name__ == '__main__':
    main()
