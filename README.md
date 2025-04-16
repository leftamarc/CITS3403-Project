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

You will need a Steam account that is both non-limited and has 2FA set up through the Steam mobile app.

Instructions for setting up the Steam Guard Mobile Authenticator (2FA) are here: https://help.steampowered.com/en/faqs/view/6891-E071-C9D9-0134

New Steam accounts are limited until funds have added and atleast 1 purchase is made, the minimum amount of funds that can be added at one time is $5.

## Setting up your Steam API Key

The application will automatically parse your Steam API key through the STEAM_API_KEY local environment variable after it has been set on your machine.

Use the appropriate command for your machine to set up the STEAM_API_KEY local environment variable.

Note that the environment variable will only be set while the terminal remains open.

# cmd (Windows)
set STEAM_API_KEY=your_api_key_here

# bash (Linux/Mac)
export STEAM_API_KEY="your_api_key_here"




instructions for how to run the tests for the application.
