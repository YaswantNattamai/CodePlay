import numpy as np
import scipy.io.wavfile as wav
import json

SAMPLE_RATE = 44100

NOTE_MAP = {
    'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4,
    'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11
}

def note_to_freq(note_str):
    if len(note_str) == 2:
        pitch = note_str[0]
        octave = int(note_str[1])
    else:
        pitch = note_str[:2]
        octave = int(note_str[2])
    
    midi = (octave + 1) * 12 + NOTE_MAP[pitch]
    # A4 is MIDI 69, 440 Hz
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))

def apply_adsr(wave, attack=0.01, decay=0.1, sustain=0.7, release=0.1):
    total_samples = len(wave)
    attack_samples = int(attack * SAMPLE_RATE)
    decay_samples = int(decay * SAMPLE_RATE)
    release_samples = int(release * SAMPLE_RATE)
    
    # Cap samples if wave is too short
    if attack_samples + decay_samples + release_samples > total_samples:
        attack_samples = int(total_samples * 0.1)
        decay_samples = int(total_samples * 0.2)
        release_samples = int(total_samples * 0.3)
        
    sustain_samples = total_samples - attack_samples - decay_samples - release_samples
    
    env = np.ones(total_samples)
    
    # Attack
    if attack_samples > 0:
        env[:attack_samples] = np.linspace(0, 1, attack_samples)
    
    # Decay
    if decay_samples > 0:
        env[attack_samples:attack_samples+decay_samples] = np.linspace(1, sustain, decay_samples)
        
    # Sustain
    if sustain_samples > 0:
        env[attack_samples+decay_samples:attack_samples+decay_samples+sustain_samples] = sustain
        
    # Release
    if release_samples > 0:
        start_rel = total_samples - release_samples
        env[start_rel:] = np.linspace(sustain, 0, release_samples)
        
    return wave * env

def generate_ep(freq, duration):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    wave = np.sin(2 * np.pi * freq * t) + 0.5 * np.sin(2 * np.pi * freq * 2 * t)
    return apply_adsr(wave, attack=0.01, decay=0.2, sustain=0.4, release=0.2)

def generate_bass(freq, duration):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    wave = 2 * (t * freq - np.floor(0.5 + t * freq))
    return apply_adsr(wave, attack=0.05, decay=0.2, sustain=0.8, release=0.1)

def generate_lead(freq, duration):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    vibrato = np.sin(2 * np.pi * 5 * t) * 0.02
    wave = np.sign(np.sin(2 * np.pi * freq * (t + vibrato)))
    return apply_adsr(wave, attack=0.05, decay=0.1, sustain=0.6, release=0.2)

def generate_pad(freq, duration):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    wave = np.sin(2 * np.pi * freq * t) + 0.5 * np.sin(2 * np.pi * freq * 1.01 * t)
    return apply_adsr(wave, attack=0.4, decay=0.2, sustain=0.8, release=0.4)

def generate_strings(freq, duration):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    wave1 = 2 * (t * freq - np.floor(0.5 + t * freq))
    wave2 = 2 * (t * freq * 1.005 - np.floor(0.5 + t * freq * 1.005))
    wave = (wave1 + wave2) * 0.5
    return apply_adsr(wave, attack=0.3, decay=0.1, sustain=0.9, release=0.3)

def generate_drum(note, duration):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    if note == 'KICK':
        freqs = np.linspace(150, 40, len(t))
        wave = np.sin(2 * np.pi * freqs * t)
        return apply_adsr(wave, attack=0.005, decay=0.1, sustain=0.0, release=0.1)
    elif note in ['SNARE', 'HAT', 'CRASH']:
        wave = np.random.uniform(-1, 1, len(t))
        if note == 'HAT':
            return apply_adsr(wave, attack=0.005, decay=0.05, sustain=0.0, release=0.05)
        elif note == 'SNARE':
            return apply_adsr(wave, attack=0.005, decay=0.2, sustain=0.0, release=0.1)
        else:
            return apply_adsr(wave, attack=0.01, decay=0.5, sustain=0.2, release=0.5)
    return np.zeros_like(t)

def generate_audio(ir_file="ir.json", output_file="output.wav"):
    with open(ir_file, "r") as f:
        ir = json.load(f)
        
    duration = ir.get("duration", 0) + 1 # Add 1s for reverb/delay tail
    total_samples = int(duration * SAMPLE_RATE)
    master = np.zeros(total_samples)
    
    tracks = {
        "EP": np.zeros(total_samples),
        "BASS": np.zeros(total_samples),
        "LEAD": np.zeros(total_samples),
        "PAD": np.zeros(total_samples),
        "STRINGS": np.zeros(total_samples),
        "DRUMS": np.zeros(total_samples)
    }
    
    for block in ir.get('timeline', []):
        second_offset = block['second'] - 1
        
        for instr, notes in block['tracks'].items():
            for note in notes:
                start_sec = second_offset + note['start']
                note_dur = note['end'] - note['start']
                start_idx = int(start_sec * SAMPLE_RATE)
                
                if instr == 'DRUMS':
                    wave = generate_drum(note['note'], note_dur)
                else:
                    freq = note_to_freq(note['note'])
                    if instr == 'EP': wave = generate_ep(freq, note_dur)
                    elif instr == 'BASS': wave = generate_bass(freq, note_dur)
                    elif instr == 'LEAD': wave = generate_lead(freq, note_dur)
                    elif instr == 'PAD': wave = generate_pad(freq, note_dur)
                    elif instr == 'STRINGS': wave = generate_strings(freq, note_dur)
                    else: wave = np.zeros(int(note_dur * SAMPLE_RATE))
                    
                vel = note.get('velocity', 64) / 127.0
                wave = wave * vel
                
                end_idx = start_idx + len(wave)
                
                if end_idx > total_samples:
                    wave = wave[:total_samples - start_idx]
                    end_idx = total_samples
                    
                if instr in tracks:
                    tracks[instr][start_idx:end_idx] += wave

    for t in tracks.values():
        master += t
        
    max_val = np.max(np.abs(master))
    if max_val > 0:
        master = master / max_val * 0.9
        
    master_16bit = np.int16(master * 32767)
    
    wav.write(output_file, SAMPLE_RATE, master_16bit)
    print(f"Saved audio to {output_file}")
    return ir
    
if __name__ == "__main__":
    generate_audio()
