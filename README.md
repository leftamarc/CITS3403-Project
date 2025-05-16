# CITS3403-Project


## SteamWrapped
SteamWrapped is a Steam Web API based application designed to provide entertaining insights regarding Steam user data.

The application allows users to input a Steam ID associated with a public steam profile and the application will make various calls 
to the Steam Web API and Steam Storefront API to collect data such as profile info, user game data, global achievement data, game storefront
metadata and more.

The user is then shown a collection of specific insights that were successfully drawn from the collected data, being able to save and share 
these collections with other users.

The insights are designed to both provide interesting facts about the users Steam data but also be entertaining. The flavour text presented 
alongside the insights take a mocking tone using language relevant to online gaming culture.


## Group Members

| UWA ID    | Name              | GitHub Username  |
|-----------|-------------------|------------------|
| 23351854  | Marc Luis Aquino  | leftamarc        |
| 23777804  | Ryan Schofield    | RS-23777804      |
| 23475224  | Cam Hardy         | UWA23475224      |
| 23940384  | Jacob Popal       | Jacobpop123      |

## Obtaining a Steam API Key

To run this project on your own machine you will need your own Steam API key available here: https://steamcommunity.com/dev

Steam API keys cannot be shared and must be kept private as per the Steam Web API Terms of Use (https://steamcommunity.com/dev/apiterms).

## Setting up your Steam API Key

It is recommended that you use a python virtual environment to manage your api key.

Instructions for setting up a python virtual environment can be found here: https://docs.python.org/3/library/venv.html

After creating your virtual environment navigate to its 'Scripts' subfolder.

You will need to edit the file associated with your console of choice and add the appropriate line.

### activate.bat    (Windows CMD)
set STEAM_API_KEY=your_api_key_here

### Activate.ps1    (Windows PowerShell)
$env:STEAM_API_KEY = "your_api_key_here"

### activate        (bash)
export STEAM_API_KEY="your_api_key_here"

Now when you run the application from the python virtual environment your api key will always be initialised.


## Running the application

After activating the virtual environment, simply use the command "flask run" to run the application.

You may use "pip install -r requirements.txt" to install the dependencies for the application.

The full list of dependencies is found in requirements.txt


## Running tests

To run automated system and unit tests, enter the command "python -m unittest test.<name of test file>".

The tests can be located in the /test folder.
