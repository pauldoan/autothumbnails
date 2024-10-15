# app.py
import streamlit as st
import replicate
import os
import dotenv
from utils import process_file_to_mp3, get_file_type  # Ensure get_file_type is imported
from PIL import Image
from io import BytesIO

# Load environment variables
dotenv.load_dotenv()
replicate_api_token = os.getenv("REPLICATE_API_TOKEN")

# Set the Replicate API token
replicate.Client(api_token=replicate_api_token)

# Streamlit title
st.set_page_config(page_title="Autothumbnails")
st.title("Auto Thumbnails 🎥")

# File uploader for audio or video files
uploaded_file = st.file_uploader("Upload an audio or video file", type=["mp3", "m4a", "wav", "mp4", "mov", "avi"])

# Input for number of thumbnails to generate
num_thumbnails = st.number_input("Number of thumbnails to generate", min_value=1, max_value=4, value=4, step=1)

# If a file is uploaded, proceed with the processing
if uploaded_file is not None:
    # Determine if the file is audio or video
    file_type = get_file_type(uploaded_file)

    if file_type == "audio":
        st.success("Uploaded file type: Audio")
    elif file_type == "video":
        st.success("Uploaded file type: Video")
    else:
        st.error("Unsupported file type.")
        st.stop()  # Stop further execution if unsupported file type

    # Process the file to MP3
    st.subheader("Processing file")
    with st.spinner("Processing the file to extract audio..."):
        mp3_data = process_file_to_mp3(uploaded_file)

    if mp3_data:
        # Display video for video files, or audio for audio files
        if file_type == "video":
            st.video(uploaded_file)  # Display the video directly
        else:
            st.audio(mp3_data.getvalue(), format="audio/mp3")

        # Prepare for Speech-to-Text
        input_audio = {
            "audio": mp3_data,
            "batch_size": 64,
        }

        # Run the Speech-to-Text model
        st.subheader("Captions Generation", divider=True)
        with st.spinner("Transcribing audio to text..."):
            transcript_output = replicate.run(
                "vaibhavs10/incredibly-fast-whisper:3ab86df6c8f54c11309d4d1f930ac292bad43ace52d10c80d87eb258b3c9f79c",
                input=input_audio,
            )

        transcript_text = transcript_output.get("text", "")
        st.write(transcript_text)

        # Summarize the transcript
        st.subheader("Summarizing transcript", divider=True)
        with st.spinner("Generating a concise summary of the content..."):
            prompt = f"Create an engaging and concise YouTube video description for the following transcript: {transcript_text}. Only output the description."
            summary_output = replicate.run("meta/meta-llama-3-8b-instruct", input={"prompt": prompt})
            summary = "".join(summary_output)

        st.write(summary)

        # Generate images
        st.subheader("Generating thumbnails", divider=True)
        with st.spinner("Creating thumbnails based on the summary..."):
            image_input = {"prompt": summary, "num_outputs": num_thumbnails, "output_quality": 100}
            image_outputs = replicate.run("black-forest-labs/flux-schnell", input=image_input)

        # Display images directly
        cols = st.columns(len(image_outputs))
        for idx, image_output in enumerate(image_outputs):
            # If image_output is an in-memory file-like object, read directly from it
            img = Image.open(BytesIO(image_output.read()))  # Open directly without further requests
            with cols[idx]:
                st.image(img, caption=f"Thumbnail {idx + 1}", use_column_width=True)

    else:
        st.error("Unable to process the file.")
