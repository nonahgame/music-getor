# bark_generator.py ; new 24 11 25
import os
import uuid
import torch

# Bark (Suno / Suno-like) usage: see Bark docs for exact API; this implementation uses the open-source bark package
# Install requirement: pip install -U bark-client  (or the library name you use)
# If using "bark" pip package by suno-ai, adapt imports accordingly.
try:
    from bark import generate_audio, preload_models, SAMPLE_RATE, save_audio  # best-effort import
    BARK_AVAILABLE = True
except Exception:
    BARK_AVAILABLE = False

def ensure_bark():
    if not BARK_AVAILABLE:
        raise RuntimeError("Bark library is not installed or import failed. Install it and try again.")

class BarkGenerator:
    def __init__(self):
        if BARK_AVAILABLE:
            preload_models()  # may download models on first run
        else:
            print("[BarkGenerator] bark is not available; vocals won't generate until you install bark package.")

    def generate_vocals(self, lyrics: str, voice: str = "male", out_path: str = "output/vocals.wav", tempo: float = 1.0):
        """
        Generate sung vocals audio from lyrics using Bark.
        voice: 'male', 'female', or 'custom'
        If voice == 'custom', we will try to use a sample at 'voice_samples/latest_sample.wav' if present.
        Returns path to generated WAV file.
        """
        ensure_bark()
        # prepare prompt: we craft a short prompt telling Bark to sing the lyrics
        # Bark often prefers short chunks; split long lyrics into lines/pause markers
        # We'll ask Bark to sing in a melodic manner.
        prompt = "Singing voice. A melodic vocalist. Lyrics:\n\n" + lyrics

        # If custom voice sample exists and voice == 'custom', include history prompt handling (scaffold)
        if voice == "custom":
            sample_path = os.path.join("voice_samples", "latest_sample.wav")
            if os.path.exists(sample_path):
                print("[BarkGenerator] custom voice sample found; attempting to condition generation (scaffold).")
                # NOTE: real voice cloning requires extra steps / model - here we attempt to pass sample as prompt if Bark supports
                # Real implementation depends on your chosen cloning approach.
                prompt = f"[voice_sample:{sample_path}]\n" + prompt
            else:
                print("[BarkGenerator] custom voice requested but sample not found. Falling back to male voice.")
                voice = "male"

        # voice style mapping (these are arbitrary labels — tune to your Bark version)
        voice_style = {
            "male": "deep male singer",
            "female": "female soulful singer",
        }.get(voice, "deep male singer")

        final_prompt = f"{voice_style}. {prompt}"

        # Generate using Bark (API varies by installation)
        print(f"[BarkGenerator] Generating vocals with style '{voice_style}' ...")
        audio_arr = generate_audio(final_prompt)  # generate_audio should return numpy or sound array
        # save using bark helper if available
        try:
            save_audio(audio_arr, out_path)
        except Exception:
            # fallback: use soundfile
            import soundfile as sf
            sf.write(out_path, audio_arr, SAMPLE_RATE)

        return out_path
