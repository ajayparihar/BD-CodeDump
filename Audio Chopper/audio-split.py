import os
import librosa
import soundfile as sf
import numpy as np
from tqdm import tqdm

def split_audio_files(input_dir, output_base_dir):
    """
    Reads all audio files from input_dir, splits them based on silence using librosa,
    and saves the chunks into output_base_dir as WAV files.
    Shows progress using tqdm.
    """
    # Ensure output directory exists
    if not os.path.exists(output_base_dir):
        os.makedirs(output_base_dir)

    # Supported extensions
    extensions = ('.mp3', '.wav', '.ogg', '.flac')
    
    files = [f for f in os.listdir(input_dir) if f.lower().endswith(extensions)]
    
    if not files:
        print(f"No audio files found in {input_dir}")
        return

    # Overall progress bar for files
    file_pbar = tqdm(files, desc="Total Progress", unit="file")

    for filename in file_pbar:
        file_path = os.path.join(input_dir, filename)
        file_pbar.set_postfix_str(f"Working on: {filename}")
        
        try:
            # Load the audio file
            y, sr = librosa.load(file_path, sr=None)
            
            # Detect non-silent intervals
            # top_db: threshold for silence (in decibels)
            intervals = librosa.effects.split(y, top_db=30) 
            
            if len(intervals) <= 1 and (intervals[0][1] - intervals[0][0]) == len(y):
                 continue

            # Create a subfolder for this file's chunks
            file_output_dir = os.path.join(output_base_dir, os.path.splitext(filename)[0])
            if not os.path.exists(file_output_dir):
                os.makedirs(file_output_dir)

            # Export chunks with a nested progress bar
            chunk_pbar = tqdm(enumerate(intervals), 
                              total=len(intervals), 
                              desc=f"  Exporting {filename}", 
                              unit="chunk", 
                              leave=False)
            
            for i, (start, end) in chunk_pbar:
                chunk = y[start:end]
                chunk_filename = f"chunk_{i+1}.wav"
                chunk_path = os.path.join(file_output_dir, chunk_filename)
                
                sf.write(chunk_path, chunk, sr)
            
            chunk_pbar.close()

        except Exception as e:
            tqdm.write(f"Error processing {filename}: {e}")

    file_pbar.close()
    print("\nProcessing complete!")

if __name__ == "__main__":
    # Define paths
    base_path = os.path.dirname(os.path.abspath(__file__))
    input_media_dir = os.path.join(base_path, "media")
    output_media_dir = os.path.join(base_path, "output")

    split_audio_files(input_media_dir, output_media_dir)
