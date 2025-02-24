# Introduction

This project automates the process of archiving tracks from Spotify's Discover Weekly playlist into a specified archive playlist. It uses Python with the spotipy library for interacting with the Spotify API and BeautifulSoup for web scraping, as the API endpoint for accessing Spotify-owned playlists like Discover Weekly is deprecated.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setup](#setup)
3. [Environment Variables](#environment-variables)
4. [GitHub Actions](#github-actions)
5. [Troubleshooting](#troubleshooting)
6. [Why Web Scraping?](#why-web-scraping)

## Prerequisites

- **Spotify Account**: You need a Spotify account.
- **Spotify Developer Account**: Create a Spotify Developer account for a client ID and client secret.
- **GitHub Account**: You need a GitHub account for hosting and using GitHub Actions.

## Setup

### Step 1: Create a Spotify Developer App

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
2. Create an app and note down the **Client ID** and **Client Secret**.

### Step 2: Create a Spotify Playlist

1. Open Spotify and create a new playlist.
2. Note down the **Playlist ID** from the playlist URL.



### Step 3: Obtain a Refresh Token

1. Run `refresh_token.py` to get a refresh token.
2. Authenticate via a web browser.
3. The script will print the refresh token.

### Step 4: Create a `.env` File

Create a `.env` file with:

    client_id=YOUR_CLIENT_ID
    client_secret=YOUR_CLIENT_SECRET
    refresh_access_token=YOUR_REFRESH_TOKEN
    archive_weekly_id=YOUR_ARCHIVE_PLAYLIST_ID
    discover_weekly_url=YOUR_DISCOVER_WEEKLY_URL

Replace `YOUR_CLIENT_ID`, `YOUR_CLIENT_SECRET`, `YOUR_REFRESH_TOKEN`,  `YOUR_ARCHIVE_PLAYLIST_ID`, and `YOUR_DISCOVER_WEEKLY_URL` with your actual values.

### Step 5: Create a `requirements.txt` File

Create a `requirements.txt` file with:

    beautifulsoup4==4.9.3
    python-dotenv==1.0.1
    Requests==2.32.3
    spotipy==2.23.0


## Environment Variables

For GitHub Actions, store environment variables as secrets:

1. Go to your GitHub repository settings.
2. Navigate to **Actions** > **Secrets**.
3. Add secrets:
   - `CLIENT_ID`
   - `CLIENT_SECRET`
   - `REFRESH_ACCESS_TOKEN`
   - `ARCHIVE_PLAYLIST_ID`
   - `DISCOVER_WEEKLY_URL`

## GitHub Actions

- The `actions.yml` file runs automatically every Tuesday at noon using GitHub Actions. Ensure your repository has the necessary permissions and secrets.

- You can also trigger it manually from the GitHub Actions UI.


## Troubleshooting

- Ensure all dependencies are correctly installed.
- Verify that your .env file and GitHub secrets are correctly configured.
- Check the Spotify API documentation for any changes to authentication or API endpoints.

## Why Web Scraping? 

The Spotify API no longer supports accessing tracks from Spotify-owned playlists like Discover Weekly directly. As noted in the [Spotify Developer Blog](https://developer.spotify.com/blog/2024-11-27-changes-to-the-web-api), these endpoints are deprecated. Therefore, we use web scraping with BeautifulSoup to extract track links from the Discover Weekly webpage.

---

This project automates archiving your Discover Weekly to your Spotify playlist. Feel free to modify it as needed.

