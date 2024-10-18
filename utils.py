import os
from moviepy.editor import VideoFileClip
import mimetypes
from pydub import AudioSegment
from io import BytesIO
import tempfile


def get_file_type(file):
    """Determines if a file is audio, video, or image based on MIME type."""
    # Check if input is a file-like object
    if hasattr(file, "name"):
        # If a file-like object is passed, get its name attribute
        file_name = file.name
    else:
        # Otherwise, assume it's a file path
        file_name = file

    mime_type, _ = mimetypes.guess_type(file_name)

    if mime_type:
        if mime_type.startswith("audio"):
            return "audio"
        elif mime_type.startswith("video"):
            return "video"
        elif mime_type.startswith("image"):
            return "image"

    # Return None if the MIME type is unknown or doesn't match these categories
    return None


def process_audio_to_mp3(audio_file):
    """
    Converts an opened audio file to MP3 format and returns the audio data in a BytesIO object.

    Parameters:
    audio_file (file-like object): An opened file-like object containing the audio.

    Returns:
    BytesIO: In-memory MP3 data.
    """
    try:
        # Load the audio file from the file-like object
        audio = AudioSegment.from_file(audio_file)
    except Exception as e:
        print(f"Error loading audio file: {e}")
        return None

    # Create an in-memory bytes buffer
    mp3_data = BytesIO()

    # Export the audio as MP3 to the buffer
    try:
        audio.export(mp3_data, format="mp3")
        mp3_data.seek(0)  # Rewind the buffer to the beginning
        print("Audio converted to MP3 format in memory.")
        return mp3_data
    except Exception as e:
        print(f"Error exporting audio to MP3: {e}")
        return None


def extract_audio_from_video(video_file):
    """
    Extracts audio from an opened video file and returns it as a file-like object (BytesIO).

    Parameters:
    video_file (file-like object): An opened file-like object containing the video.

    Returns:
    BytesIO: In-memory audio data in WAV format.
    """
    print("Extracting audio from video...")

    with tempfile.TemporaryDirectory() as temp_dir:
        # Save the video file-like object to a temporary file
        temp_video_path = os.path.join(temp_dir, "temp_video.mp4")
        with open(temp_video_path, "wb") as temp_video_file:
            temp_video_file.write(video_file.read())

        # Load the video clip from the temporary file path
        video_clip = VideoFileClip(temp_video_path, verbose=False)
        audio_clip = video_clip.audio

        # Create a temporary file to save the audio
        temp_audio_path = os.path.join(temp_dir, "temp_audio.wav")

        # Write the audio clip to the temporary audio file
        audio_clip.write_audiofile(
            temp_audio_path, codec="pcm_s16le", verbose=False, logger=None
        )

        # Load the audio data into a BytesIO object
        audio_buffer = BytesIO()
        with open(temp_audio_path, "rb") as temp_audio:
            audio_buffer.write(temp_audio.read())

        # Clean up
        video_clip.close()

    # Rewind the BytesIO buffer for further reading
    audio_buffer.seek(0)
    print("Audio extracted and loaded into memory.")
    return audio_buffer


def process_file_to_mp3(file):
    """
    Processes an audio or video file and returns the audio data in MP3 format.

    Parameters:
    file_path (str): Path to the audio or video file.

    Returns:
    BytesIO: In-memory MP3 data.

    Raises:
    ValueError: If the file type is not audio or video.
    """
    file_type = get_file_type(file)
    if file_type == "audio":
        print("Processing audio file to MP3...")
        return process_audio_to_mp3(file)

    if file_type == "video":
        print("Processing video file to MP3...")
        audio_buffer = extract_audio_from_video(file)
        return process_audio_to_mp3(audio_buffer)

    else:
        raise ValueError(
            "Unsupported file type. Only audio and video files are supported."
        )
