
# TeleBot Scheduler - Telegram Bot with Google Sheets Integration

A complete backend solution for a Telegram bot that manages services, appointments, and users with different roles (Clients, Admins, CEO), all stored in Google Sheets.

## Features

### Role-Based Access
- **Clients**: Book services, view and cancel appointments
- **Administrators**: Manage services and appointments, view statistics
- **CEO**: Manage administrators, view comprehensive statistics

### Google Sheets Integration
- Store all data in Google Sheets - no traditional database required
- Services, client data, appointments, and history all managed in separate sheets
- Easy to view and manage data manually if needed

### Booking System
- Service listing and selection
- Date and time scheduling
- Confirmation flow
- Appointment management

### Admin Capabilities
- Add/remove services
- Manage client appointments
- View booking statistics

### Extensible Architecture
- Clean separation of concerns for easy maintenance
- Ready for future integration with AI tools and analytics

## Setup Guide

### 1. Create a Telegram Bot
- Open Telegram and search for [@BotFather](https://t.me/BotFather)
- Send `/newbot` command
- Follow the instructions to set a name and username
- Copy the provided bot token

### 2. Set Up Google Sheets
1. Create a new Google Sheet with the following worksheets:
   - `Services` (columns: `id`, `name`, `description`, `price`)
   - `Clients` (columns: `user_id`, `username`, `full_name`, `role`)
   - `Appointments` (columns: `id`, `user_id`, `service_id`, `date`, `time`, `status`)
   - `History` (columns: `timestamp`, `user_id`, `service_id`, `date`, `time`, `amount`)

2. Set up Google Sheets API:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable the Google Sheets API
   - Create a service account and download the JSON credentials
   - Share your Google Sheet with the service account email (with Editor permissions)

### 3. Install Required Packages
```bash
pip install aiogram gspread oauth2client python-dotenv
```

### 4. Configure Environment Variables
Create a `.env` file with:
```
BOT_TOKEN=your_telegram_bot_token_here
GOOGLE_CREDENTIALS_FILE=path/to/your/credentials.json
SPREADSHEET_ID=your_spreadsheet_id_here
```

### 5. Run the Bot
```bash
python main.py
```

## Project Structure
```
project_folder/
├── main.py               # Main entry point
├── .env                  # Environment variables
├── credentials.json      # Google API credentials
├── database/
│   └── sheets_manager.py # Google Sheets integration
├── handlers/
│   ├── client_handlers.py # Client command handlers
│   ├── admin_handlers.py  # Admin command handlers
│   └── ceo_handlers.py    # CEO command handlers
├── keyboards/
│   ├── client_keyboards.py # Client-specific keyboards
│   └── admin_keyboards.py  # Admin-specific keyboards
└── middlewares/
    └── role_middleware.py  # Role-based access control
```

## Future Extensions

### AI Integration
- **Content Generation**: Use AI to generate personalized messages to clients
- **Smart Scheduling**: Implement AI-based scheduling recommendations
- **Chatbot Capabilities**: Enhance user interactions with natural language processing

### Analytics
- Implement more comprehensive reporting
- Add visualizations for business insights
- Track customer engagement and retention

## Contributing
Feel free to fork this project and submit pull requests or open issues for features and bug fixes.

## License
MIT License
