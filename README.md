# 🎥 VISCA PTZ Web Controller

![Project
Status](https://img.shields.io/badge/status-active-brightgreen)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/flask-webapp-black)
![VISCA](https://img.shields.io/badge/protocol-VISCA-purple)

A modern, responsive **Web-based controller for VISCA PTZ cameras** with
full Gamepad (Joystick) support.

Designed for smooth, broadcast-style control via browser, supporting
both **TCP (IP VISCA)** and **Serial (RS-232)** connections.

------------------------------------------------------------------------

## ✨ Features

-   🎮 **Analog Gamepad Control**
    -   Smooth pan/tilt with exponential curve
    -   Instant direction change (no stop glitch)
    -   Adjustable deadzone
-   🔍 **Proportional Zoom Control**
    -   Trigger-based analog zoom
    -   Proper zoom stop detection
-   🎯 **Raw VISCA Motion Engine**
    -   Independent pan & tilt direction control
    -   Direct speed override
-   🌐 **Web-Based Interface**
    -   Works from any device on the network
    -   Touch and mouse friendly
-   🔌 **Dual Connection Support**
    -   TCP/IP (VISCA over IP)
    -   Serial (RS-232)
-   ⚡ **Low-Latency Real-Time Control**
    -   WebSocket-based communication
    -   Optimized command deduplication

------------------------------------------------------------------------

## 📸 Interface Overview

                Main Control Interface
  --------------------------------------------------
   Web-based PTZ Control Panel with Gamepad Support

------------------------------------------------------------------------

## 🛠️ Requirements

-   **Python 3.8+**
-   A VISCA-compatible PTZ camera
-   One of:
    -   Serial connection (USB to RS-232 adapter)
    -   VISCA over IP support

------------------------------------------------------------------------

## 🚀 Installation

### 1️⃣ Clone the Repository

``` bash
git clone https://github.com/simoneluconi/visca-ptz-web-controller.git
cd visca-ptz-web-controller
```

### 2️⃣ Create Virtual Environment (Recommended)

``` bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3️⃣ Install Dependencies

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

## ▶️ Running the Application

``` bash
python app.py
```

Then open:

    http://localhost:5000

Or from another device:

    http://YOUR_PC_IP:5000

------------------------------------------------------------------------

## 🎮 Gamepad Controls

  Control         Function
  --------------- ---------------------
  Left Stick      Pan / Tilt (Analog)
  RT (R2)         Zoom In
  LT (L2)         Zoom Out
  D-Pad Up/Down   Focus Near/Far
  A Button        Emergency Stop
  Y Button        Auto Focus

### Movement Engine

The system uses:

-   Exponential sensitivity curve (EXPO)
-   Deadzone filtering
-   Continuous `move_raw` VISCA commands
-   Direction-based motion control

This allows:

✔ Instant direction reversal\
✔ No jitter at center crossing\
✔ Smooth slow movements\
✔ Broadcast-style responsiveness

------------------------------------------------------------------------

## ⚙️ Configuration

You can modify sensitivity directly in `index.html`:

``` javascript
const DEADZONE = 0.10;
const EXPO = 1.8;
const MAX_PAN = 24;
const MAX_TILT = 20;
```

------------------------------------------------------------------------

## 📂 Project Structure

``` text
visca-ptz-web-controller/
├── app.py              # Flask backend + VISCA engine
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html      # Frontend (HTML + JS + Gamepad logic)
```

------------------------------------------------------------------------

## 🔧 Supported Commands

-   Pan / Tilt (Raw Direction Control)
-   Zoom (Variable Speed)
-   Focus (Auto / Manual / Near / Far)
-   Iris Control
-   Gain Control
-   White Balance
-   IR Remote Enable/Disable
-   LED Control

------------------------------------------------------------------------

## 🧠 How It Works

The backend:

-   Wraps VISCA commands in correct header/footer format
-   Supports both Serial and TCP sockets
-   Sends optimized packets only when motion changes

The frontend:

-   Reads Gamepad API
-   Applies exponential smoothing
-   Sends WebSocket commands in real time

------------------------------------------------------------------------

## 🌍 Deployment Ideas

-   Run on Raspberry Pi
-   Install as Docker container
-   Deploy behind Nginx reverse proxy
-   Use on tablet as wireless PTZ controller

------------------------------------------------------------------------

## 📜 License

MIT License

------------------------------------------------------------------------

## 💡 Future Improvements

-   Adjustable sensitivity via UI
-   Multi-camera preset switching
-   Rate limiting for serial stability
-   Motion smoothing filter
-   Camera position feedback (if supported)

------------------------------------------------------------------------

## 👤 Author

Created by Simone Luconi\
Industrial automation & software development enthusiast\
Specialized in IoT, AI integration, and intelligent control systems.

------------------------------------------------------------------------

If you found this useful, consider starring the repository ⭐
