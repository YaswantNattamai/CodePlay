from mido import Message, MidiFile, MidiTrack, MetaMessage

NOTE_MAP = {
    'C': 0, 'C#': 1,
    'D': 2, 'D#': 3,
    'E': 4,
    'F': 5, 'F#': 6,
    'G': 7, 'G#': 8,
    'A': 9, 'A#': 10,
    'B': 11
}

DRUM_MAP = {
    "KICK": 36,
    "SNARE": 38,
    "HAT": 42,
    "CRASH": 49
}

def note_to_midi(note):
    if len(note) == 2:
        pitch = note[0]
        octave = int(note[1])
    else:
        pitch = note[:2]
        octave = int(note[2])

    return (octave + 1) * 12 + NOTE_MAP[pitch]


def generate_midi(ir, filename="output.mid"):
    mid = MidiFile()

    piano_track = MidiTrack()
    guitar_track = MidiTrack()
    drum_track = MidiTrack()

    mid.tracks.extend([piano_track, guitar_track, drum_track])

    ticks_per_beat = mid.ticks_per_beat

    # Default tempo (constant)
    piano_track.append(MetaMessage('set_tempo', tempo=500000, time=0))

    events = []

    for block in ir['timeline']:
        second = block['second']

        for instrument, notes in block['tracks'].items():
            for note in notes:
                start_tick = int((second + note['start']) * ticks_per_beat)
                end_tick = int((second + note['end']) * ticks_per_beat)

                velocity = note.get("velocity", 64)

                if instrument == "PIANO":
                    pitch = note_to_midi(note['note'])
                    track = piano_track
                    channel = 0

                elif instrument == "GUITAR":
                    pitch = note_to_midi(note['note'])
                    track = guitar_track
                    channel = 1

                elif instrument == "DRUMS":
                    pitch = DRUM_MAP.get(note['note'], 36)
                    track = drum_track
                    channel = 9

                else:
                    continue

                events.append((start_tick, 'on', pitch, track, channel, velocity))
                events.append((end_tick, 'off', pitch, track, channel, velocity))

    events.sort(key=lambda x: x[0])

    current_time = 0

    for tick, event_type, pitch, track, channel, velocity in events:
        delta = tick - current_time
        current_time = tick

        msg_type = 'note_on' if event_type == 'on' else 'note_off'

        track.append(Message(
            msg_type,
            note=pitch,
            velocity=velocity,
            time=delta,
            channel=channel
        ))

    mid.save(filename)
    print(f"MIDI file saved: {filename}")