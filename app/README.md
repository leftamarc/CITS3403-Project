# CITS3403-Project
a description of the purpose of the application, explaining its design and use.

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

After creating your virtual environment navigate to its 'Scripts' subfolder.

You will need to edit the file associated with your console of choice and add the appropriate line.

### activate.bat (Windows CMD)
set STEAM_API_KEY=your_api_key_here

### Activate.ps1 (Windows PowerShell)
$env:$env:STEAM_API_KEY = "your_api_key_here"

### bash (Linux/Mac)
export STEAM_API_KEY="your_api_key_here"

Now when you run the application from the python virtual environment your api key will always be initialised.


instructions for how to run the tests for the application.
