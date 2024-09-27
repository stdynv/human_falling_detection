# Human Falling Detection

This project aims to detect falls of elderly people in nursing homes (EHPADs) using a Raspberry Pi with a camera. It leverages Mediapipe's BlazePose model to detect falls in real-time and uses Azure Blob Storage to store incident videos and Flask for an API to manage data and alerts.

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Architecture](#architecture)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Features

- Real-time detection of falls using a Raspberry Pi and camera.
- Video recording before and after fall detection.
- Upload of videos to Azure Blob Storage.
- API to manage incident data and alerts in real-time using Flask.
- Web-based dashboard for viewing alerts and videos.
- Notification system for staff in EHPADs.

## Technologies Used

- **Python**: Core programming language for the detection logic and backend API.
- **Mediapipe**: Used for pose estimation and fall detection using the BlazePose model.
- **OpenCV**: For video capture and processing.
- **Azure Blob Storage**: For storing recorded videos of incidents.
- **Flask**: Backend framework to manage API and real-time alerts.
- **SocketIO**: For real-time notifications and alerts.
- **Raspberry Pi**: Edge device for video capture and processing.
- **dbdiagram.io**: Database schema and ERD design.

## Architecture

The architecture consists of the following main components:

1. **Raspberry Pi + Camera**: Captures video and performs fall detection using Mediapipe BlazePose.
2. **Azure Blob Storage**: Stores the videos of detected incidents securely.
3. **Flask API**: Manages communication between the Raspberry Pi and storage, as well as provides an interface for real-time alerts and incident data.
4. **Web Application**: Dashboard for EHPAD staff to view incident details, videos, and receive real-time alerts.

![System Architecture](https://github.com/user-attachments/assets/ccb72c29-16a7-4b9d-a1db-b9c2352ba552)

## Setup and Installation

To set up the project, follow these steps:

### Prerequisites

- **Python 3.8+**
- **Raspberry Pi** with a camera module
- **Azure Account**: For Blob Storage setup
- **Virtual Environment**: Recommended to isolate dependencies

### Clone the Repository

```
git clone https://github.com/stdynv/human_falling_detection.git
cd human_falling_detection
```

### Configure Environment Variables
Create a ```.env``` file to store your Azure Blob Storage connection string and other sensitive information:

```
DB_SERVER=db server name
DB_DATABASE=database name 
DB_USERNAME=your db username
DB_PASSWORD=your db password
API_URL = APP LINK
AZURE_BLOB_STORAGE= azure_blob_storage
NAME_CONTAINER= container name
```

### Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

### Run Application 

```bash
python app.py
```


