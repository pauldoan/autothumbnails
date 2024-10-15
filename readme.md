# Auto Thumbnails 🎥

Auto Thumbnails is a Streamlit-based web app designed to generate YouTube-like thumbnails from audio or video content. The app leverages open source machine learning models to transcribe audio, summarize the content, and create engaging thumbnails based on the transcript.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Environment Setup](#environment-setup)
- [Usage](#usage)
- [Customization](#customization)
- [Contributing](#contributing)
- [License](#license)

## Overview

Auto Thumbnails allows users to upload an audio or video file, processes the file to extract audio, transcribes the content, summarizes the transcript, and then generates multiple thumbnail images based on the summary. The app is ideal for content creators looking to quickly generate YouTube thumbnails that align with the content of their videos.

## Features
- **File Upload**: Supports various audio and video file formats such as MP3, WAV, M4A, MP4, MOV, and AVI.
- **Automatic Transcription**: Converts the audio into text using a Speech-to-Text model.
- **Content Summarization**: Summarizes the transcript to capture the main theme for thumbnail creation.
- **Thumbnail Generation**: Uses AI to generate multiple YouTube-style thumbnail images.
  
## Installation

### Prerequisites
- Python 3.7 or higher
- [Replicate API token](https://replicate.com/account) (You’ll need to sign up and get an API key)
- ffmpeg (for handling media files; install instructions below)

### Clone the Repository
```bash
git clone https://github.com/yourusername/autothumbnails.git
cd autothumbnails
```

### Install Dependencies
Use `pip` to install the necessary dependencies:
```bash
pip install -r requirements.txt
```

### Install ffmpeg
- **Ubuntu**: 
  ```bash
  sudo apt update
  sudo apt install ffmpeg
  ```
- **macOS**:
  ```bash
  brew install ffmpeg
  ```
- **Windows**: 
  Download the executable from [ffmpeg.org](https://ffmpeg.org/download.html) and follow the setup instructions.

## Environment Setup

Create a `.env` file in the root directory to store your Replicate API token:
```bash
REPLICATE_API_TOKEN=your_replicate_api_token_here
```

## Usage

### Running the App
To start the Streamlit app, run the following command in your terminal:
```bash
streamlit run app.py
```
The app will open in your default web browser. Alternatively, you can access it by navigating to `http://localhost:8501` in your browser.

### Using the App
1. **Upload a File**: Click on the "Upload an audio or video file" section to upload your audio or video file. Supported formats include MP3, M4A, WAV, MP4, MOV, and AVI.
2. **Select Number of Thumbnails**: Use the number input to specify how many thumbnails you want to generate (1-4).
3. **File Type Display**: After uploading, the app displays the file type (audio or video) and provides an audio player for audio files or a video player for video files.
4. **Processing**: The app automatically processes the file, transcribes the audio, generates a summary, and creates the thumbnails.
5. **Thumbnails Display**: View the generated thumbnails on the app interface, which you can download by right-clicking on the images.

## Customization

### Adjusting the Number of Thumbnails
The default maximum number of thumbnails is set to 4. To change this, modify the `st.number_input` line in `app.py`:
```python
num_thumbnails = st.number_input("Number of thumbnails to generate", min_value=1, max_value=4, value=4, step=1)
```
You can increase `max_value` to allow more thumbnails.

### Changing Models
The app currently uses the following models:
- **Speech-to-Text**: `"vaibhavs10/incredibly-fast-whisper"`
- **Summarization**: `"meta/meta-llama-3-8b-instruct"`
- **Thumbnail Generation**: `"black-forest-labs/flux-schnell"`

If you want to try other models, replace these model IDs in the `replicate.run` calls.

### Customizing the Prompt
The prompt for generating the thumbnail description can be customized to fit different use cases. Update this line in `app.py` for different prompt styles:
```python
prompt = f"Create an engaging and concise YouTube video description for the following transcript: {transcript_text}. Only output the description."
```

## Have Fun 🎈