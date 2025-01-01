from flask import Flask, request , jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from langdetect import detect
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound



app = Flask(__name__)
# 192.168.100.235
@app.route('/')
def home():
    return '<h1>Flask Rest API</h1>'



@app.route('/process_text', methods=['POST'])
def process_text():
    data = request.json
    inputTxt = data.get('text')
    processed_text = inputTxt[::-1]

    return jsonify({"processed_text": processed_text})




def get_youtube_transcript(video_id):
    try:
        # List all available transcripts for the video
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Attempt to find the first available transcript
        for transcript in transcript_list:
            # Check if the transcript is auto-generated or manually created
            language = transcript.language_code
            caption_type = "auto" if transcript.is_generated else "manual"

            # Fetch the transcript in the available language
            transcript_data = transcript.fetch()

            # Join all text segments into one string
            transcript_text = " ".join([item['text'] for item in transcript_data])

            # Detect the language of the transcript text
            detected_language = detect(transcript_text)

            return transcript_text, detected_language, caption_type

        # If no transcript is found
        return None, None, None

    except TranscriptsDisabled as e:
        # Catching specific error if no transcript is found (manual or auto)
        print(f"Error: Transcripts are disabled for this video: {e}")
        return None, None, None
    except NoTranscriptFound as e:
        # Catching case where no transcript is available
        print(f"Error: No transcripts found for this video: {e}")
        return None, None, None
    except Exception as e:
        # Catching other general exceptions
        print(f"Error fetching transcript: {e}")
        return None, None, None

@app.route('/process_video_txt', methods=['POST'])
def process_video_txt():
    data = request.json
    inputTxt = data.get('text')
    text, language, caption_type = get_youtube_transcript(inputTxt)
    if text:
        print(f"Detected Language: {language}")
        print(f"Caption Type: {caption_type}")
        print(f"Transcript: {text}")
        return jsonify({"processed_text": text})
    else:
        print("No transcript available.")
        return jsonify({"processed_text": "no text available"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
