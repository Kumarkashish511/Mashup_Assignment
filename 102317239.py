import sys
import os
import shutil
from yt_dlp import YoutubeDL
from moviepy.editor import VideoFileClip
from pydub import AudioSegment

def validate_inputs():
    if len(sys.argv) != 5:
        print("Usage: python <program.py> <SingerName> <NumberOfVideos> <AudioDuration> <OutputFileName>")
        sys.exit(1)

    singer = sys.argv[1]
    
    try:
        num_videos = int(sys.argv[2])
        duration = int(sys.argv[3])
    except ValueError:
        print("Error: NumberOfVideos and AudioDuration must be integers.")
        sys.exit(1)

    output_file = sys.argv[4]

    if num_videos <= 10:
        print("Error: NumberOfVideos must be greater than 10.")
        sys.exit(1)

    if duration <= 20:
        print("Error: AudioDuration must be greater than 20 seconds.")
        sys.exit(1)

    return singer, num_videos, duration, output_file


def download_videos(singer, num_videos):
    os.makedirs("downloads", exist_ok=True)

    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'quiet': True
    }

    search_query = f"ytsearch{num_videos}:{singer}"

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([search_query])
    except Exception as e:
        print("Error downloading videos:", e)
        sys.exit(1)


def convert_to_audio():
    os.makedirs("audios", exist_ok=True)

    for file in os.listdir("downloads"):
        if file.endswith((".mp4", ".mkv", ".webm")):
            try:
                video_path = os.path.join("downloads", file)
                audio_path = os.path.join("audios", file.rsplit('.', 1)[0] + ".mp3")

                video = VideoFileClip(video_path)
                video.audio.write_audiofile(audio_path, verbose=False, logger=None)
                video.close()
            except Exception as e:
                print("Error converting video:", file, e)


def cut_audios(duration):
    os.makedirs("cuts", exist_ok=True)

    for file in os.listdir("audios"):
        if file.endswith(".mp3"):
            try:
                audio_path = os.path.join("audios", file)
                cut_path = os.path.join("cuts", file)

                audio = AudioSegment.from_mp3(audio_path)
                cut_audio = audio[:duration * 1000]
                cut_audio.export(cut_path, format="mp3")
            except Exception as e:
                print("Error cutting audio:", file, e)


def merge_audios(output_file):
    try:
        final_audio = AudioSegment.empty()

        for file in os.listdir("cuts"):
            if file.endswith(".mp3"):
                audio = AudioSegment.from_mp3(os.path.join("cuts", file))
                final_audio += audio

        final_audio.export(output_file, format="mp3")
        print("Mashup created successfully:", output_file)

    except Exception as e:
        print("Error merging audios:", e)
        sys.exit(1)


def cleanup():
    shutil.rmtree("downloads", ignore_errors=True)
    shutil.rmtree("audios", ignore_errors=True)
    shutil.rmtree("cuts", ignore_errors=True)


def main():
    singer, num_videos, duration, output_file = validate_inputs()

    print("Downloading videos...")
    download_videos(singer, num_videos)

    print("Converting videos to audio...")
    convert_to_audio()

    print("Cutting audios...")
    cut_audios(duration)

    print("Merging audios...")
    merge_audios(output_file)

    cleanup()


if __name__ == "__main__":
    main()