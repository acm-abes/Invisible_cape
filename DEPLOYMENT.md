<!-- @format -->

# Invisible Cloak - Deployment Guide

This is a Flask-based computer vision application that creates a Harry Potter-style invisible cloak effect using your webcam.

## 🚨 Important Note About Deployment

**This app requires webcam access**, so it's designed for **local deployment only**. Cloud platforms (AWS, Heroku, Railway, Render) cannot access your computer's camera.

---

## 📦 Deployment Options

### **Option 1: Direct Python (Easiest)**

#### Prerequisites

- Python 3.8 or higher
- Webcam connected to your computer

#### Steps

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the application:

```bash
python app.py
```

3. Open your browser and go to:

```
http://localhost:5000
```

---

### **Option 2: Docker (Recommended for consistency)**

#### Prerequisites

- Docker installed ([Download Docker](https://www.docker.com/))
- Webcam connected

#### For Windows

```bash
# Build and run
docker build -t invisible-cloak .
docker run --rm -p 5000:5000 --device=/dev/video0:/dev/video0 invisible-cloak
```

**Note**: Camera access from Docker on Windows requires WSL2 and may have limitations. Option 1 is recommended for Windows users.

#### For Linux/Mac

```bash
# Using Docker Compose (easier)
docker-compose up --build

# OR using Docker directly
docker build -t invisible-cloak .
docker run --rm -p 5000:5000 --device=/dev/video0:/dev/video0 --privileged invisible-cloak
```

3. Open browser to `http://localhost:5000`

---

### **Option 3: Network Deployment (Local Network Access)**

To access from other devices on your local network:

1. Find your local IP address:

   - **Windows**: Run `ipconfig` in PowerShell (look for IPv4 Address)
   - **Mac/Linux**: Run `ifconfig` or `ip addr`

2. Run the app (it's already configured for network access):

```bash
python app.py
```

3. Access from other devices using:

```
http://YOUR_LOCAL_IP:5000
```

Example: `http://192.168.1.100:5000`

---

## 🌐 Where Can You Deploy This?

### ✅ **Recommended: Local Deployment**

- Your computer (Python or Docker)
- Local network access for demos
- Raspberry Pi with camera module

### ❌ **NOT Recommended: Cloud Platforms**

These won't work because they can't access your webcam:

- ~~AWS EC2~~
- ~~Google Cloud~~
- ~~Heroku~~
- ~~Railway~~
- ~~Render~~
- ~~Azure App Service~~

### 🤔 **Alternative: VPS with Remote Desktop**

If you need remote access:

1. Deploy on a VPS (DigitalOcean, Linode, etc.)
2. Connect a camera to the server
3. Access via Remote Desktop
4. Run the application there

---

## 🚀 Quick Start Commands

### Python (Simplest)

```bash
pip install -r requirements.txt
python app.py
```

### Docker on Linux/Mac

```bash
docker-compose up
```

### Docker on Windows (if you must)

```bash
docker build -t invisible-cloak .
docker run -p 5000:5000 invisible-cloak
```

_(Camera may not work - use Python instead)_

---

## 📱 Usage

1. Open `http://localhost:5000` in your browser
2. Click "Start Camera"
3. Step out of frame
4. Click "Capture Background"
5. Step back in with your colored cloak (blue, red, green, etc.)
6. Select the cloak color
7. Watch the magic happen!

---

## 🔧 Troubleshooting

**Camera not detected:**

- Make sure no other app is using the camera
- Check camera permissions in your OS settings
- Try a different camera index (edit `app.py`, change `cv2.VideoCapture(0)` to `1` or `2`)

**Docker camera issues on Windows:**

- WSL2 has limited USB/camera support
- Use Option 1 (direct Python) instead

**Port already in use:**

- Change port in `app.py`: `app.run(port=5001)`
- Or in Docker: `-p 5001:5000`

---

## 📝 Dependencies

See `requirements.txt`:

- Flask - Web framework
- OpenCV - Computer vision
- NumPy - Array processing
- SciPy - Scientific computing

---

## 🎯 Best Setup for Demos

**Laptop/Desktop:**

```bash
pip install -r requirements.txt
python app.py
```

**Network Demo (multiple viewers):**

1. Run on your laptop
2. Share your local IP
3. Others connect via browser on same WiFi

---

## 💡 Tips

- Use a solid-colored cloth (blue works best)
- Good lighting improves results
- Calibrate background without any moving objects
- Experiment with different color ranges

---

Enjoy your invisible cloak! 🧙‍♂️✨
