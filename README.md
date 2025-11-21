# Airbnb Lock Sync

Automatically synchronize Airbnb reservations with Seam smart lock access codes using the Seam API. This project fetches upcoming reservations from your Airbnb iCal feed and manages temporary access codes on your Seam lock, ensuring guests have the correct PIN code for their stay duration.

## Features

- 🔄 **Automatic Synchronization**: Fetches Airbnb reservations and syncs them with lock access codes
- 🔐 **Smart Access Codes**: Uses the last 4 digits of guest phone numbers as PIN codes
- ⏰ **Time Management**: Configurable check-in/check-out times with timezone support
- 📅 **Future Events Filtering**: Only processes reservations within a configurable time window
- 🔍 **Discrepancy Detection**: Identifies mismatches between reservations and access codes
- ✨ **Auto Cleanup**: Removes expired or invalid access codes automatically
- 📱 **Telegram Notifications**: Get instant notifications when codes are created, updated, or deleted
- 🧪 **Dry Run Mode**: Test your configuration without making actual changes to the lock
- 🌍 **Timezone Support**: Automatically converts times to your local timezone

## Prerequisites

- Python 3.10 or higher
- A smart lock compatible with Seam API ([see supported devices](https://www.seam.co/supported-devices-and-systems))
- Seam API account and API key
- Airbnb iCal calendar URL

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd airbnb_lock_sync
   ```

2. **Install UV package manager** (if not already installed)
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Install dependencies**
   ```bash
   uv sync
   ```

4. **Configure environment variables**
   
   Copy the example environment file:
   ```bash
   cp env/api.env.example env/api.env
   ```
   
   Edit `env/api.env` with your actual credentials:
   ```bash
   export SEAM_API_KEY=your_seam_api_key_here
   export SEAM_LOCK=your_lock_device_id_here
   export AIRBNB_ICAL=your_airbnb_ical_url_here
   export AIRBNB_MAX_START=15  # Check only for stays 15 days in the future
   export AIRBNB_CHECK_IN="13:00"  # Your check-in time
   export AIRBNB_CHECK_OUT="10:30"  # Your check-out time
   export AIRBNB_TZ="America/Sao_Paulo"  # Your timezone
   export MAIN_UPDATE_TIMES=true  # Set to false to only check codes, not times
   export MAIN_DRY_RUN=false  # Set to true to test without making actual changes
   export TELEGRAM_TOKEN=your_telegram_bot_token_here  # Optional: for notifications
   export TELEGRAM_CHAT_ID=123456789  # Optional: your Telegram chat ID(s)
   ```

5. **Set up Telegram notifications** (Optional)
   
   - Create a bot with [@BotFather](https://t.me/botfather) on Telegram
   - Copy the bot token to `TELEGRAM_TOKEN`
   - Send a message to your bot, then run:
     ```bash
     source env/api.env && python telegram_bot/telegram_bot.py
     ```
   - Copy your chat ID to `TELEGRAM_CHAT_ID` (supports comma-separated list for multiple recipients)

## Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SEAM_API_KEY` | Your Seam API key | `seam_xxxxx...` |
| `SEAM_LOCK` | Device ID of your lock | `994edb27-9d9b-...` |
| `AIRBNB_ICAL` | Airbnb iCal calendar URL | `https://www.airbnb.com/calendar/ical/...` |
| `AIRBNB_MAX_START` | Maximum days ahead to check reservations | `15` |
| `AIRBNB_CHECK_IN` | Check-in time in HH:MM format | `"13:00"` |
| `AIRBNB_CHECK_OUT` | Check-out time in HH:MM format | `"10:30"` |
| `AIRBNB_TZ` | Timezone for check-in/check-out times | `"America/Sao_Paulo"` |
| `MAIN_UPDATE_TIMES` | Update access code times (true/false) | `true` |
| `MAIN_DRY_RUN` | Test mode without making actual changes | `false` |
| `TELEGRAM_TOKEN` | Telegram bot token (optional) | `123456:ABC-DEF...` |
| `TELEGRAM_CHAT_ID` | Telegram chat ID(s), comma-separated (optional) | `123456789,987654321` |

### Getting Your Credentials

1. **Seam API Key**: Sign up at [Seam Console](https://console.seam.co/) and create an API key
2. **Lock Device ID**: After connecting your lock to Seam, get the device ID from the Seam dashboard
3. **Airbnb iCal URL**: 
   - Go to your Airbnb hosting dashboard
   - Navigate to Calendar → Availability settings
   - Find the "Export calendar" link and copy the iCal URL

4. **Telegram Bot** (Optional):
   - Open Telegram and search for [@BotFather](https://t.me/botfather)
   - Create a new bot with `/newbot` command
   - Save the bot token
   - Send a message to your bot
   - Run `python telegram_bot/telegram_bot.py` to get your chat ID

## Usage

1. **Load environment variables and run the script**
   ```bash
   source env/api.env && python main.py
   ```

   Or with uv:
   ```bash
   source env/api.env && uv run python main.py
   ```

2. **Set up a cron job for automatic synchronization** (optional)
   ```bash
   # Edit crontab
   crontab -e
   
   # Add a line to run every hour
   0 * * * * cd /path/to/airbnb_lock_sync && source env/api.env && python main.py
   ```

## How It Works

1. **Fetch Reservations**: Retrieves upcoming "Reserved" events from your Airbnb iCal feed
2. **Extract Guest Info**: Extracts confirmation codes and last 4 digits of phone numbers
3. **Apply Time Settings**: Applies your configured check-in/check-out times and converts to UTC
4. **Filter Events**: Only processes events that haven't ended and start within the configured window
5. **Sync Access Codes**: 
   - Creates new access codes for new reservations
   - Updates existing codes if details have changed
   - Deletes access codes without matching reservations

## Project Structure

```
airbnb_lock_sync/
├── main.py                  # Main synchronization script
├── airbnb_ical/
│   └── airbnb_ical.py      # Airbnb iCal parsing and event extraction
├── locks/
│   └── seam.py             # Seam lock interface via Seam API (tested with Yale locks)
├── telegram_bot/
│   └── telegram_bot.py     # Telegram notification integration
├── env/
│   ├── api.env             # Your credentials (gitignored)
│   └── api.env.example     # Template for credentials
├── pyproject.toml          # Project dependencies
├── LICENSE                 # MIT License
└── README.md               # This file
```

## Security Notes

⚠️ **Important**: Never commit your `env/api.env` file with real credentials to version control!

- All sensitive credentials are stored in `env/api.env` (gitignored)
- Use `env/api.env.example` as a template
- The `.gitignore` file is configured to exclude all `.env` files

## Troubleshooting

**Module not found errors**:
```bash
uv sync
```

**Access codes not updating**:
- Verify your `SEAM_API_KEY` and `SEAM_LOCK` are correct
- Check that your lock supports online access code programming
- Ensure `MAIN_UPDATE_TIMES` is set to `true` if you want time updates

**No reservations found**:
- Verify your `AIRBNB_ICAL` URL is correct and accessible
- Check if `AIRBNB_MAX_START` is set high enough to include your reservations
- Ensure reservations exist in your Airbnb calendar

**Timezone issues**:
- Use standard IANA timezone names (e.g., `America/New_York`, `Europe/London`)
- Verify check-in/check-out times are in 24-hour format (HH:MM)

**Telegram notifications not working**:
- Verify your bot token is correct
- Make sure you've sent at least one message to your bot
- Check that `TELEGRAM_CHAT_ID` is set correctly
- For multiple recipients, use comma-separated values: `123,456,789`

**False time discrepancies**:
- The system now normalizes datetime formats automatically
- Times are compared without microseconds to avoid false positives

## Telegram Notifications

When enabled, you'll receive beautifully formatted notifications for:

**New Access Code:**
```
✅ New Lock Code Created

📋 Reservation: HMABCDEF123
🔑 Access Code: 1234
📅 Check-in: Nov 25, 2025 at 01:00 PM -03
📅 Check-out: Nov 27, 2025 at 10:30 AM -03
🔗 View Reservation
```

**Updated Code:**
```
🔄 Lock Code Updated

📋 Reservation: HMABCDEF123
🔑 Access Code: 1234
📅 Check-in: Nov 25, 2025 at 01:00 PM -03
📅 Check-out: Nov 27, 2025 at 10:30 AM -03
```

**Deleted Code:**
```
🗑️ Lock Code Deleted

📋 Reservation: HMABCDEF123
🔑 Access Code: 1234
ℹ️ Reason: No matching reservation found
```

All times are displayed in your configured timezone for easy reference!

## Contributing

Contributions are welcome! Whether it's bug fixes, new features, documentation improvements, or suggestions, feel free to open a pull request or issue.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

All contributions are appreciated! 🎉

## License

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
