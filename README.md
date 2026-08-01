# Attendance App

Attendance App is a lightweight prototype for tracking attendance using local network discovery. It is designed for early-stage learning, prototyping, and internal testing rather than production deployment.

## Overview

The current implementation provides a simple Flask-based web app that:
- scans the local network through the ARP cache
- detects visible devices and records their presence over time
- stores session and device information in a local SQLite database
- shows a dashboard with recent activity
- lets you assign a roll number and name to a detected MAC address
- exports attendance data as a CSV file

## Current Features

### Attendance tracking prototype
The app periodically runs an ARP scan and stores detected MAC addresses in a session table. This makes it useful for basic presence checks in a lab, event, classroom, or small team environment.

### Dashboard
The home page displays a table of detected devices, including:
- MAC address
- assigned roll number
- assigned name
- first seen timestamp
- last seen timestamp

### Registration and assignment
You can register a device by providing a MAC address, roll number, and name. These values are saved in the database and shown on the dashboard.

### CSV export
The app includes an export endpoint that downloads the current session data as a CSV file for reporting or backup.

## Project Structure

- app.py - Flask application, database helpers, scheduling, and routes
- db.py - database-related utilities
- chk.py - helper script related to checking attendance state
- wifi_scanner.py - network scanning logic
- templates/ - HTML templates for dashboard and registration views
- schema.sql - SQLite schema definition
- attendance.db - local SQLite database file
- requirements.txt - Python dependencies
- package.json - npm-compatible entry point for local development

## How It Works

1. The application starts a background scheduler.
2. Every 30 seconds, it runs an ARP scan to discover visible devices.
3. Detected MAC addresses are stored in the sessions table.
4. The dashboard merges session data with registered device metadata.
5. You can view, update, and export attendance information from the web interface.

## Requirements

Before running the app, make sure you have:
- Python 3.10 or newer
- pip
- access to the ARP command on your system

On many Linux environments, the ARP command is available by default. If it is missing, the scan may not return any results.

## Getting Started

### 1. Clone the repository
```bash
git clone <repository-url>
cd Attendance-App
```

### 2. Install Python dependencies
```bash
python -m pip install -r requirements.txt
```

### 3. Start the development server
You can use either of the following commands:

```bash
npm run dev
```

or

```bash
python app.py
```

The app will start on:
- http://127.0.0.1:5050

### 4. Use the dashboard
Open the browser and visit the local URL to view detected devices and manage attendance entries.

## Typical Workflow

1. Start the app.
2. Allow the scanner to collect device activity.
3. View the detected rows on the dashboard.
4. Assign names and roll numbers to known devices.
5. Export the attendance data as CSV when needed.

## Data Storage

The app uses SQLite for local persistence. The database file is stored as attendance.db and contains tables for:
- sessions - timestamped presence data
- devices - device metadata such as roll number and name

## Limitations and Warnings

Please keep the following in mind while using this project:
- This is not a production-ready deployment.
- There is no authentication or role-based access layer yet.
- The app is intended for learning, testing, and prototyping.
- Network detection depends on local ARP visibility and system environment.
- Future improvements may include better security, persistence design, reporting, and real-time updates.

## Roadmap Ideas

Potential enhancements for future versions include:
- user authentication and admin roles
- real-time updates in the browser
- improved reporting and analytics
- better device identification and validation
- deployment support with Docker or cloud hosting

## Contributing

Contributions are welcome. If you would like to improve the project, feel free to open an issue or submit a pull request with a clear description of the change.

## License

This project is licensed under the Apache License, Version 2.0. See the LICENSE file for details.
