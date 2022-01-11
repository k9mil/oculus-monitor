# Oculus 👁️

Oculus is an open source, scraper/monitor for multiple polish-based websites, searching for analog cameras under a certain price range however it can be easily tweaked to search for any product.

This project is currently unmaintained, therefore, I cannot guarantee it works as intended.

## Features

- Camera config (Models, Max Price) for user's required input.
- Supports two websites being: OLX and Allegro.
- Has an in-built monitor which checks if new products have been added.
- Ignores sponsored and promoted items on both websites.
- Discord Webhook integration for notifications.

## Working on
- Fixing bugs
- Improving Finder/Scraper functionality

## Setup

As for now, [Python](https://www.python.org/) is **necessary** for you to be able to run this script.
1. Open your terminal/command line where the source code for Oculus is located.
2. In the command line, enter "pip install -r requirements.txt" (if that doesn't work, try pip3 instead of pip)
3. Run the file via "python oculus.py" (once again, try python3 if python does not work!)

After you confirmed that the file is working, you can tweak the settings inside the **camera_config.json** file, provided in the repo. As well as that, if you wish to receive notifications from the Monitor mode, you have to change the Discord Webhook to your desired webhook.

## Modes

There are two modes for Oculus.
1. <ins>Monitor</ins>
   - Monitors the websites to check if new products have been added.
2. <ins>Finder/Scraper</ins>
   - Searches through the websites and prints out products.

## Oculus Demo

<p align="center"><img src="https://thumbs.gfycat.com/ArcticAngelicCats-small.gif"></p>

## License

Licensed under the MIT License - see the [LICENSE file](https://github.com/k9mil/Oculus/blob/master/LICENSE) for more details.
