"""
Simple transcription script using deepgram_utils
"""
import os
from dotenv import load_dotenv
from deepgram import DeepgramClient
from deepgram_utils import (
    transcribe_audio_file,
    extract_response_dict,
    save_transcription,
    print_transcription_summary
)

# Load environment variables
load_dotenv()
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
AUDIO_FILE = "lezione_aggiornata.mp3"


def main():
    try:
        # Check if API key is available
        if not DEEPGRAM_API_KEY:
            print("Error: DEEPGRAM_API_KEY not found in .env file")
            print("Please create a .env file with your API key or use the GUI Settings tab")
            return

        # Initialize client
        deepgram = DeepgramClient(api_key=DEEPGRAM_API_KEY)

        # Choose model: "nova-3", "nova-2", "whisper-large", etc.
        model = "whisper-large"

        print(f"Transcribing with model: {model}")

        # Transcribe audio
        response = transcribe_audio_file(
            deepgram,
            AUDIO_FILE,
            model=model,
            language="it"
        )

        # Extract structured data
        response_dict = extract_response_dict(response)

        # Save to files
        json_path, txt_path, formatted_text = save_transcription(
            response_dict,
            base_filename=f"transcript_{model.replace('-', '_')}"
        )

        # Print summary
        print_transcription_summary(json_path, txt_path, formatted_text, model)

    except Exception as e:
        print(f"Exception: {e}")


if __name__ == "__main__":
    main()
