# Oculus ✨

Oculus is an open source, basic scraper/monitor for multiple polish-based websites, searching for analog cameras under a certain price range. It was created with the sole intention of learning, however I will be keeping it updated in case given websites under-go some changes.

## Features 💫

- Camera config (Models, Max Price) for user's required input.
- Supports two websites being: OLX and Allegro.
- Has an in-built monitor which checks if new products have been added.

## Working on 🦛

- Front-end for the data gathered (most likely a Flask dashboard).
- Once an item is found via monitor - send data to Discord/Email.
- More websites to be scraped/searched.

## Setup

As for now, [Python](https://www.python.org/) is **necessary** for you to be able to run this script.
1. Open your terminal/command line where the source code for Oculus is located.
2. In the command line, enter "pip install -r requirements.txt" (if that doesn't work, try pip3 instead of pip)
3. Run the file via "python oculus.py" (once again, try python3 if python does not work!)

## Oculus Demo
<p align="center"><img src="https://media.giphy.com/media/iBEhIO7ap1SkTNGH2O/giphy.gif"></p>

## License

Licensed under the MIT License - see the [LICENSE file](https://github.com/k9mil/Oculus/blob/master/LICENSE) for more details.
