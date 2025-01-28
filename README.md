# RCM Pilot Photo Assistant

## Overview

This application is designed to assist race organizers in taking and managing pictures of participants (pilots) during a race event. It fetches the **race categories** and **series** from a myRCM page, displays them in a user-friendly interface, and allows the user to select a pilot and eventually **trigger a DSLR camera** (to be implemented) and save the resulting photo in a location tied to the pilot's profile.

## Features

1. **Parse categories and series** from a myRCM URL via the `build_categories()` function.
2. Display **Category** and **Serie** dropdown lists.
3. Generate a **pilot list** as clickable buttons.
4. Provide a **status bar** to show which pilot was clicked.
5. Let the user **change** the URL and reload the data on the fly.

## How to Use

1. **Install Python requirements** (e.g., `requests`, `beautifulsoup4`) if your code references them.
2. **Run** the main script (for example, `python main.py`).
3. The **main window** will show:
   - A **URL** field (defaulting to a known myRCM URL).
   - A **Load** button to fetch data from that URL.
   - Two dropdowns (one for **Category**, one for **Serie**).
   - A set of **pilot** buttons displayed below.
   - A **status bar** showing the current status.
4. **Select** a different **Category** or **Serie** to see the relevant pilots.
5. **Click** a pilot button to see the pilot’s name in the status bar.

> **Note**: The camera control is **not** yet implemented. See **To-Do** for details.

## Development

- The script obtains categories and series from the function `build_categories(url)`, which returns a hierarchy of objects: `Category` → `Serie` → `myRCMPilot`.
- Tkinter is used for the **GUI**.

## To-Do

- **Trigger the DSLR Camera**: Integrate Canon’s EDSDK or similar approach (e.g., `python-edsdk`) to remotely shoot a photo when a pilot button is clicked.
- **Save the JPG file** in a path contained in each pilot object (for instance, using `pilot.carPicPath` or `pilot.profilePicPath`).

