﻿
# The Free Dogs Bot

🖱️ Auto-clicker for [https://t.me/theFreeDogs_bot](https://t.me/theFreeDogs_bot/app?startapp=ref_nqrF9bYq)

## Recommendation Before Use
🔥🔥 Use Python 3.10+ for best compatibility 🔥🔥

## Features
| Feature                                                     | Supported  |
|-------------------------------------------------------------|:----------:|
| Auto-Click coin                                              |     ✅     |
| Multi Account                                                |     ✅     |
| Multithreading                                               |     ✅     |
| Proxy binding to session                                     |     ✅     |
| Support for tdata / pyrogram `.session` / telethon `.session`|     ✅     |
| Support for Query Data if not using `.seesion`               |     ✅     |

## Settings
| Setting           | Description                                                                 |
|-------------------|-----------------------------------------------------------------------------|
| **API_ID / API_HASH** | Platform data from which to run the Telegram session                    |

## Prerequisites
Before you begin, make sure you have the following installed:
- [Python](https://www.python.org/downloads/) **version 3.10+**

## Obtaining API Keys
1. Go to [my.telegram.org](https://my.telegram.org) and log in using your phone number.
2. Select "API development tools" and fill out the form to register a new application.
3. Record the API_ID and API_HASH provided after registering your application in the `.env` file.

## Installation and Setup

### 1. Clone the Repository
First, clone the repository to your local machine:

```bash
git clone https://github.com/kh0sr0w/free-dogs-bot.git
cd free-dogs-bot
```

### 2. Create a Virtual Environment (Recommended)
It’s recommended to use a virtual environment to avoid conflicts with other Python projects. Run the following commands:

For **Windows**:
```bash
python -m venv venv
venv\Scripts\activate
```

For **Linux/Mac**:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Required Dependencies
Once the virtual environment is activated, install the required Python packages by running:

```bash
pip install -r requirements.txt
```

### 4. Configure the Environment File
- Copy the `.env-example` file and rename it to `.env`:
  
  ```bash
  cp .env-example .env
  ```

- Open the `.env` file and add your `API_ID` and `API_HASH` obtained from [my.telegram.org](https://my.telegram.org/auth).

Example:
```bash
API_ID=your_api_id
API_HASH=your_api_hash
```

### 5. Run the Bot
Finally, run the bot with the following command:

```bash
python main.py
```
### 6. If running with query
To use query ID use the following command/sittings:

Add your queryIds each in seperate lines like bellow on the query.txt file:

query_id=First query.....

query_id=Second query....

query_id= and soo on ....

```bash
python querytapper.py
```
The bot will now start interacting with the Free Dogs Bot on Telegram according to the settings provided.

## Telegram Channel

✅ Channel for information and training on Telegram airdrop bots 🔷 Follow us on Telegram: [Bot Channel](https://t.me/kh0sr0w_bot)

## Discussion
If you have any questions or need help, feel free to reach out here: [Khosrow](https://t.me/kh0sr0w)
