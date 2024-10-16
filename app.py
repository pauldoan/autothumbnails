# app.py
import streamlit as st
import replicate
import os
import dotenv
from utils import process_file_to_mp3, get_file_type  # Ensure get_file_type is imported
from PIL import Image
from io import BytesIO
import time

# Load environment variables
dotenv.load_dotenv()
replicate_api_token = os.getenv("REPLICATE_API_TOKEN")

# Set the Replicate API token
replicate.Client(api_token=replicate_api_token, timeout=300)

# Streamlit title
st.set_page_config(page_title="Autothumbnails")
st.title("Auto Thumbnails 🎥")

st.markdown(
    """
    Welcome to **Auto Thumbnails**! 🎈
    This app (inspired by my usage of Captions) lets you upload a video or audio file, and it will automatically transcribe, summarize,
    and generate custom YouTube-style thumbnails based on the content, using only open-source models!

    Perfect for content creators
    looking to quickly produce high-quality thumbnails for their videos.
    Just upload a file, select the number of thumbnails, the image generation model, and watch the magic happen!

    Cheers,

    Paul 📸
    """
)

# File uploader for audio or video files
uploaded_file = st.file_uploader("Upload an audio or video file", type=["mp3", "m4a", "wav", "mp4", "mov", "avi"])

# Input for number of thumbnails to generate
num_thumbnails = st.number_input("Number of thumbnails to generate", min_value=1, max_value=4, value=4, step=1)

# Image generation model selector
model_options = {
    "Flux Dev": "black-forest-labs/flux-dev",
    "Flux Schnell (faster)": "black-forest-labs/flux-schnell",
    "Stable Diffusion": "stability-ai/stable-diffusion:ac732df83cea7fff18b8472768c88ad041fa750ff7682a21affe81863cbe77e4",
    "SDXL Lightning": "bytedance/sdxl-lightning-4step:5599ed30703defd1d160a25a63321b4dec97101d98b4674bcc56e41f62f35637",
}

selected_model = st.selectbox("Choose the Image Generation Model", options=list(model_options.keys()), index=0)
image_generation_model = model_options[selected_model]

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
        try:
            mp3_data = process_file_to_mp3(uploaded_file)
        except Exception as e:
            st.error(f"Error during audio processing: {e}")
            st.stop()  # Stop execution if processing fails

    if mp3_data:
        # Display video for video files, or audio for audio files
        if file_type == "video":
            col1, col2 = st.columns([1, 2])
            with col1:
                st.video(uploaded_file)  # Display the video directly
        else:
            st.audio(mp3_data.getvalue(), format="audio/mp3")

        # Add a button to start generating thumbnails
        generate_button = st.button("Generate Thumbnails 📸")

        # When the button is clicked, proceed with transcription, summarization, and thumbnail generation
        if generate_button:

            # Prepare for Speech-to-Text
            input_audio = {
                "audio": mp3_data,
                "batch_size": 64,
            }

            # Run the Speech-to-Text model
            st.subheader("Captions Generation", divider=True)

            max_retries = 3  # Maximum number of retries
            retry_delay = 2  # Delay between retries in seconds
            transcript_output = None

            with st.spinner(
                "Transcribing audio to text...This can take a few seconds if the model is cold on Replicate..."
            ):
                for attempt in range(max_retries):
                    try:
                        transcript_output = replicate.run(
                            "vaibhavs10/incredibly-fast-whisper:3ab86df6c8f54c11309d4d1f930ac292bad43ace52d10c80d87eb258b3c9f79c",
                            input=input_audio,
                            wait=True,
                        )
                        if transcript_output:
                            break  # Exit the loop if successful

                    except Exception as e:
                        print(e)
                        time.sleep(retry_delay)
                else:
                    # This block runs if all retries fail
                    st.error("Transcription failed after multiple attempts.")

            if transcript_output:
                st.write("✅ Transcription completed")
                transcript_text = transcript_output.get("text", "")
                st.write(transcript_text)

            # Generate images
            st.subheader("Generating thumbnails", divider=True)

            with st.spinner("Generating a concise summary of the content..."):
                prompt = f"Create an well thought prompt for a image generation model to generate an engaging realistic photography thumbnail for the following social media video description. Make sure we do not have someone in the foreground as it could be misleading if different from the creator. Description: {transcript_text}. Only output the prompt."

                for attempt in range(max_retries):
                    try:
                        image_prompt = replicate.run(
                            "meta/meta-llama-3-8b-instruct", input={"prompt": prompt}, wait=True
                        )
                        if image_prompt:
                            break  # Exit the loop if successful
                    except Exception as e:
                        print(e)
                        time.sleep(retry_delay)
                else:
                    st.error("Summary generation failed after multiple attempts.")
                image_prompt = "".join(image_prompt)

            if image_prompt:
                st.write("✅ Summary generated")
            print(image_prompt)

            with st.spinner("Creating thumbnails based on the summary..."):
                image_input = {"prompt": image_prompt, "num_outputs": num_thumbnails, "output_quality": 100}

                for attempt in range(max_retries):
                    try:
                        image_input = {
                            "prompt": "".join(image_prompt),
                            "num_outputs": num_thumbnails,
                            "output_quality": 100,
                        }
                        image_outputs = replicate.run(image_generation_model, input=image_input, wait=True)
                        if image_outputs:
                            break  # Exit the loop if successful
                    except Exception as e:
                        print(e)
                        time.sleep(retry_delay)
                else:
                    st.error("Thumbnail generation failed after multiple attempts.")

            if image_outputs:
                st.write("✅ Thumbnails generated")

            # Display images directly
            cols = st.columns(len(image_outputs))
            for idx, image_output in enumerate(image_outputs):
                # If image_output is an in-memory file-like object, read directly from it
                img = Image.open(BytesIO(image_output.read()))  # Open directly without further requests
                with cols[idx]:
                    st.image(img, caption=f"Thumbnail {idx + 1}", use_column_width=True)

    else:
        st.error("Unable to process the file.")
