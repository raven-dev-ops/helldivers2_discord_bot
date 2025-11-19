Helldivers 2 Discord Bot - LFG & Mission Stats
==============================================

This project is an open-source Discord bot for Helldivers 2 communities that:

- Provides a Clan Hub menu for registration and mission uploads
- OCRs scoreboard screenshots into structured stats
- Builds monthly leaderboards and awards medals / MVP roles
- Manages LFG ping and region roles
- Offers utilities for guild management and automated cleanup

It is designed to run in a single guild but supports multiple guilds via MongoDB collections.


Features
--------

- Registration and roles
  - Clan Hub menu buttons to register players and assign the LFG ping role
  - Optional ship name and region (NA / EU / UK / AU / ASIA) with automatic region-role management
  - Auto-upsert of members into the `Alliance` collection on join (`ArrivalCog`)

- Mission upload and OCR
  - Upload scoreboard screenshots (`.png` / `.jpg` / `.jpeg`, up to 5 MB)
  - OpenCV + Tesseract OCR pipeline (`ocr_processing.py`) with multiple preprocessing passes
  - Per-player stats stored in MongoDB for later querying and leaderboards

- Leaderboards and promotions
  - Monthly leaderboard ranking by Most Shots Fired, then games played
  - Rolling 28-day window for submitter medals (Class A / Achievement / Commendation / Bronze / Silver / Medal of Honor)
  - Automatic MVP role handling per guild at month end

- SOS / LFG network
  - SOS network support for cross-server LFG (`sos_cog.py`, `sos_view.py`)
  - LFG ping role assignment during registration

- Admin and quality-of-life tools
  - Guild configuration and management helpers (`guild_management_cog.py`)
  - Message cleanup utilities (`cleanup_cog.py`)
  - Centralized monitor channel logging via `utils.log_to_monitor_channel`

For an end-user perspective of the Clan Menu and stats flow, see `PATCH.md` (Clan Menu User Guide and FAQ).


Architecture
------------

- Language / runtime: Python (tested with 3.10+)
- Discord library: `discord.py` with commands and views (`discord.ext.commands`)
- Database: MongoDB (via `motor` async driver)
  - `Alliance` - player registrations and profile metadata
  - `User_Stats` - mission results, per-player stats, leaderboard data
  - `Server_Listing` - per-guild configuration (used by some cogs)
- OCR / image processing:
  - OpenCV (`opencv-python`)
  - Tesseract OCR (via `pytesseract`) - Tesseract must be installed on the host (unless using the Docker image)
- Configuration:
  - Environment variables loaded via `python-dotenv` into `config.py`
  - Optional per-guild IDs for roles and channels

The bot entrypoint is `main.py`, which:

1. Loads environment variables (`DISCORD_TOKEN`, `MONGODB_URI`, etc.)
2. Connects to MongoDB (`AsyncIOMotorClient`)
3. Creates indexes via `database.py`
4. Loads all cogs from the `cogs/` package
5. Starts the Discord bot


Prerequisites
-------------

- Python 3.10 or newer
- A MongoDB instance/cluster and connection URI
- A Discord application with a bot token and the following intents enabled:
  - Server Members Intent
  - Message Content Intent
  - Guilds Intent
- Tesseract OCR installed and available in the system path (if not running via Docker)


Environment Variables
---------------------

Configuration is managed via environment variables (for local development, typically through a `.env` file loaded by `python-dotenv`). The most important ones are:

Required for basic operation:

- `DISCORD_TOKEN` - Discord bot token
- `MONGODB_URI` - connection string for your MongoDB cluster
- `GUILD_ID` - primary guild ID where the bot runs
- `BOT_CHANNEL_ID` - default bot interaction channel
- `MONITOR_CHANNEL_ID` - channel for operational logs and error messages
- `CLASS_B_ROLE_ID` - Discord role ID required to submit stats
- `LFG_PING_ROLE_ID` - role pinged for LFG pings

Strongly recommended:

- `CLASS_A_ROLE_ID` - Discord role ID for Class A Citizen
- `LEADERBOARD_CHANNEL_ID` - channel where leaderboards are posted
- `KIA_CHANNEL_ID` - optional channel for KIA / death reports
- `MVP_ROLE_ID` - MVP role granted to monthly winners

Optional role IDs:

- Regional roles:
  - `NA_ROLE_ID`, `EU_ROLE_ID`, `UK_ROLE_ID`, `AU_ROLE_ID`, `ASIA_ROLE_ID`
- Medal roles used by promotion logic:
  - `GPT_ACHIEVEMENT_MEDAL_ROLE_ID`
  - `GPT_COMMENDATION_MEDAL_ROLE_ID`
  - `GPT_BRONZE_STAR_MEDAL_ROLE_ID`
  - `GPT_SILVER_STAR_MEDAL_ROLE_ID`
  - `GPT_MEDAL_OF_HONOR_ROLE_ID`
- SOS network:
  - `SOS_NETWORK_ID` - optional network / hub guild for cross-server SOS features

OCR and image tuning (optional, see `config.py` for defaults):

- `MATCH_SCORE_THRESHOLD` - integer threshold for fuzzy name matching
- `TARGET_WIDTH`, `TARGET_HEIGHT` - expected scoreboard resolution
- `PLAYER_OFFSET` - vertical offset to the first player row
- `NUM_PLAYERS` - expected number of players in the screenshot

Never commit your `.env` file or secrets (Discord token, MongoDB URI) to version control.


Local Development
-----------------

1. Clone and install dependencies:

   ```bash
  git clone <this-repo-url>
  cd <repo-folder>
   python -m venv .venv
   .venv\Scripts\activate  # on Windows
   pip install -r requirements.txt
   ```

2. Create a `.env` file:

   Copy the example file and fill in values:

   ```bash
   cp .env.example .env  # or copy .env.example to .env on Windows
   ```

   Then edit `.env` and define at least the required variables described below.

Quick start (.env layout)
-------------------------

For a production-style setup similar to the one this repo was developed with, your `.env` will typically include:

```env
# Core connectivity
DISCORD_TOKEN=your_discord_bot_token_here
MONGODB_URI=your_mongodb_uri_here

# Primary guild and channels
GUILD_ID=your_main_guild_id
BOT_CHANNEL_ID=bot_commands_channel_id
MONITOR_CHANNEL_ID=monitor_log_channel_id
LEADERBOARD_CHANNEL_ID=leaderboard_channel_id
KIA_CHANNEL_ID=optional_kia_channel_id

# Submission and LFG roles
CLASS_A_ROLE_ID=class_a_role_id
CLASS_B_ROLE_ID=class_b_role_id   # required to submit stats
LFG_PING_ROLE_ID=lfg_ping_role_id
MVP_ROLE_ID=mvp_role_id

# Region roles (optional)
NA_ROLE_ID=na_region_role_id
EU_ROLE_ID=eu_region_role_id
UK_ROLE_ID=uk_region_role_id
AU_ROLE_ID=au_region_role_id
ASIA_ROLE_ID=asia_region_role_id

# Medal roles (optional, for monthly submitter awards)
GPT_ACHIEVEMENT_MEDAL_ROLE_ID=achievement_medal_role_id
GPT_COMMENDATION_MEDAL_ROLE_ID=commendation_medal_role_id
GPT_BRONZE_STAR_MEDAL_ROLE_ID=bronze_star_role_id
GPT_SILVER_STAR_MEDAL_ROLE_ID=silver_star_role_id
GPT_MEDAL_OF_HONOR_ROLE_ID=medal_of_honor_role_id

# SOS network (optional)
SOS_NETWORK_ID=hub_or_network_guild_id

# OCR tuning (optional, defaults work for most setups)
MATCH_SCORE_THRESHOLD=80
TARGET_WIDTH=1920
TARGET_HEIGHT=1080
PLAYER_OFFSET=460
NUM_PLAYERS=4
```

All IDs above are Discord snowflakes (large integers) but must be provided as plain strings in the `.env` file.

3. Run the bot:

   ```bash
   python main.py
   ```

   On startup you should see log output indicating that the bot connected and cogs were loaded, plus a list of loaded cogs.


Docker and Deployment
---------------------

This repository includes a `Dockerfile` and `heroku.yml`.

Build and run with Docker:

```bash
docker build -t helldivers2-bot .
docker run --env-file .env helldivers2-bot
```

The image installs OpenCV and Tesseract for you. Make sure your `.env` file is present and contains the required environment variables.

Heroku (container stack):

- `heroku.yml` defines a `worker` process that runs `python main.py` using the Docker image.
- Set your environment variables as Heroku Config Vars (do not commit secrets).


Testing
-------

This project uses `pytest` and `pytest-asyncio` for tests.

Run the full test suite:

```bash
pytest
```

Tests live under the `tests/` directory and cover core cogs and promotion / leaderboard logic.


Project Structure
-----------------

- `main.py` - bot entrypoint, event loop, and cog loader
- `config.py` - environment configuration and role / channel IDs
- `database.py` - MongoDB connection helpers and index creation
- `ocr_processing.py` - OCR helpers and scoreboard parsing
- `boundary_drawing.py` - scoreboard boundary helpers for OCR
- `cogs/` - Discord cogs:
  - `arrival_cog.py` / `departure_cog.py` / `members_cog.py` - member join / leave handling and registration
  - `guild_management_cog.py` - guild configuration and admin tools
  - `menu_view.py` / `register_modal.py` - Clan Hub menu, registration form, mission edit views
  - `extract_cog.py` / `extract_helpers.py` - image upload pipeline and OCR integration
  - `leaderboard_cog.py` - monthly leaderboards and promotion / medal logic
  - `sos_cog.py` / `sos_view.py` - SOS network and LFG utilities
  - `cleanup_cog.py` - cleanup / maintenance tasks
  - `dm_response.py` - DM helper responses and fallbacks
- `tests/` - automated tests
- `PATCH.md` - Clan Menu User Guide and FAQ (player-facing explanation)
- `privacy_policy.md` - privacy policy for hosting this bot
- `terms_of_service.md` - terms of service and usage conditions (template for self-hosted deployments)
- `ads.txt` - advertising configuration for web hosting contexts (not used by the Discord bot itself)
- `gpt_network.png`, `sos_leaderboard.png` - example images for documentation or embeds


Notes and Disclaimers
---------------------

- This project is not affiliated with or endorsed by Arrowhead Game Studios, Sony, or any official Helldivers 2 entity.
- You are responsible for:
  - Complying with Discord's Terms of Service and Developer Policies
  - Securing your MongoDB instance and Discord token
  - Customizing `privacy_policy.md` and `terms_of_service.md` to match your jurisdiction and server rules

If you extend or modify the bot, consider updating this README and the user-facing guide in `PATCH.md` to reflect your changes.


Contributing
------------

Contributions are welcome. To propose changes:

- Fork this repository and create a feature branch.
- Make your changes, keeping to the existing code style and structure.
- Run the test suite with `pytest` to ensure everything still passes.
- Open a pull request describing the change, motivation, and any relevant Discord / MongoDB configuration details.

Bug reports and feature requests can also be opened as issues, ideally including logs, stack traces, and steps to reproduce.

See `CONTRIBUTING.md` for detailed contributor guidelines, setup instructions, and expectations for tests and pull requests.


License
-------

This project is open source software released under the MIT License.
See `LICENSE` for the full text. In short: you may use, copy, modify,
and redistribute this code (including self-hosting your own instance)
provided that the copyright and license notice are included in
copies or substantial portions of the Software.
