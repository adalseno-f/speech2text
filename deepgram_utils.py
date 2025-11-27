"""
Utility functions for Deepgram transcription processing
"""
import json


def serialize_value(value):
    """Convert datetime and other non-serializable objects to strings"""
    if hasattr(value, 'isoformat'):  # datetime objects
        return value.isoformat()
    return value


def extract_response_dict(response):
    """
    Extract and structure the Deepgram response into a dictionary

    Args:
        response: Deepgram API response object

    Returns:
        dict: Structured response dictionary
    """
    response_dict = {
        "metadata": {
            "transaction_key": serialize_value(getattr(response.metadata, "transaction_key", None)),
            "request_id": serialize_value(getattr(response.metadata, "request_id", None)),
            "sha256": serialize_value(getattr(response.metadata, "sha256", None)),
            "created": serialize_value(getattr(response.metadata, "created", None)),
            "duration": serialize_value(getattr(response.metadata, "duration", None)),
            "channels": serialize_value(getattr(response.metadata, "channels", None)),
        },
        "results": {
            "channels": []
        }
    }

    if hasattr(response, "results") and hasattr(response.results, "channels"):
        for channel in response.results.channels:
            channel_dict = {"alternatives": []}
            for alt in channel.alternatives:
                alt_dict = {
                    "transcript": alt.transcript,
                    "confidence": getattr(alt, "confidence", None),
                }

                # Add words with timestamps if available
                if hasattr(alt, "words") and alt.words:
                    alt_dict["words"] = []
                    for word in alt.words:
                        word_dict = {
                            "word": word.word,
                            "start": getattr(word, "start", None),
                            "end": getattr(word, "end", None),
                            "confidence": getattr(word, "confidence", None),
                        }
                        alt_dict["words"].append(word_dict)

                # Add paragraphs if available
                if hasattr(alt, "paragraphs") and alt.paragraphs:
                    alt_dict["paragraphs"] = []
                    if hasattr(alt.paragraphs, "paragraphs"):
                        for para in alt.paragraphs.paragraphs:
                            para_dict = {
                                "sentences": [],
                                "start": getattr(para, "start", None),
                                "end": getattr(para, "end", None),
                            }
                            if hasattr(para, "sentences"):
                                for sent in para.sentences:
                                    sent_dict = {
                                        "text": sent.text,
                                        "start": getattr(sent, "start", None),
                                        "end": getattr(sent, "end", None),
                                    }
                                    para_dict["sentences"].append(sent_dict)
                            alt_dict["paragraphs"].append(para_dict)

                channel_dict["alternatives"].append(alt_dict)
            response_dict["results"]["channels"].append(channel_dict)

    return response_dict


def extract_formatted_text(response_dict):
    """
    Extract formatted text from response dictionary, using paragraphs if available

    Args:
        response_dict: Structured response dictionary from extract_response_dict()

    Returns:
        str: Formatted text with paragraph breaks
    """
    formatted_text = ""

    if response_dict["results"]["channels"]:
        alt = response_dict["results"]["channels"][0]["alternatives"][0]
        plain_transcript = alt["transcript"]

        # Try to build formatted text from paragraphs
        if "paragraphs" in alt and alt["paragraphs"]:
            paragraphs_list = []
            for para in alt["paragraphs"]:
                if "sentences" in para and para["sentences"]:
                    # Join sentences with spaces
                    para_text = " ".join(sent["text"] for sent in para["sentences"])
                    paragraphs_list.append(para_text)
            # Join paragraphs with double newlines
            formatted_text = "\n\n".join(paragraphs_list)

        # If no paragraphs, use the plain transcript
        if not formatted_text:
            formatted_text = plain_transcript

    return formatted_text


def save_transcription(response_dict, base_filename="transcript"):
    """
    Save transcription to both JSON and TXT files

    Args:
        response_dict: Structured response dictionary from extract_response_dict()
        base_filename: Base name for output files (without extension)

    Returns:
        tuple: (json_path, txt_path, formatted_text)
    """
    json_path = f"{base_filename}.json"
    txt_path = f"{base_filename}.txt"

    # Save JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(response_dict, f, indent=4, ensure_ascii=False)

    # Extract and save formatted text
    formatted_text = extract_formatted_text(response_dict)
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(formatted_text)

    return json_path, txt_path, formatted_text


def print_transcription_summary(json_path, txt_path, formatted_text, model_name=None):
    """
    Print a summary of the transcription results

    Args:
        json_path: Path to JSON file
        txt_path: Path to TXT file
        formatted_text: The formatted transcript text
        model_name: Optional model name to display
    """
    model_info = f" with {model_name}" if model_name else ""
    print(f"Transcription completed{model_info}!")
    print(f"- Full JSON saved to: {json_path}")
    print(f"- Plain text saved to: {txt_path}")
    print("\nTranscript preview:")
    print("-" * 50)
    print(formatted_text[:500] + ("..." if len(formatted_text) > 500 else ""))
    print("-" * 50)


def transcribe_audio_file(deepgram_client, audio_file_path, model="nova-3", language="it", **kwargs):
    """
    Transcribe an audio file using Deepgram API

    Args:
        deepgram_client: Initialized DeepgramClient instance
        audio_file_path: Path to audio file
        model: Model to use (default: "nova-3")
        language: Language code (default: "it")
        **kwargs: Additional parameters for transcribe_file (e.g., smart_format, paragraphs, etc.)

    Returns:
        Deepgram API response object
    """
    # Set default options if not provided
    if "smart_format" not in kwargs:
        kwargs["smart_format"] = True
    if "paragraphs" not in kwargs:
        kwargs["paragraphs"] = True
    if "punctuate" not in kwargs:
        kwargs["punctuate"] = True

    with open(audio_file_path, "rb") as audio:
        buffer_data = audio.read()

    response = deepgram_client.listen.v1.media.transcribe_file(
        request=buffer_data,
        model=model,
        language=language,
        **kwargs
    )

    return response
