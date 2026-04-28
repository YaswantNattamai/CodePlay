import copy

def expand_loops(blocks):
    expanded = []
    for block in blocks:
        if block['type'] == 'loop':
            inner_blocks = expand_loops(block['blocks'])
            seconds = [b['second'] for b in inner_blocks if b['type'] == 'second']
            if not seconds:
                continue
            min_sec = min(seconds)
            max_sec = max(seconds)
            duration = max_sec - min_sec + 1
            
            for i in range(block['count']):
                shift = i * duration
                for b in inner_blocks:
                    if b['type'] == 'second':
                        new_b = copy.deepcopy(b)
                        new_b['second'] += shift
                        expanded.append(new_b)
        elif block['type'] == 'second':
            expanded.append(copy.deepcopy(block))
    return expanded

def compile_ast(ast):
    patterns = {}
    effects = {"global": [], "per_track": {}}
    
    # 1. Extract patterns
    for block in ast['blocks']:
        if block['type'] == 'pattern':
            patterns[block['name']] = block['tracks']

    # 2. Expand loops
    expanded_blocks = expand_loops(ast['blocks'])
    
    # 3. Process seconds
    timeline = []
    max_duration = 0
    
    for block in expanded_blocks:
        if block['type'] != 'second': continue
        
        second_idx = block['second']
        max_duration = max(max_duration, second_idx)
        
        tracks = {}
        for item in block['body']:
            if item['type'] == 'use':
                pat_name = item['name']
                if pat_name in patterns:
                    for instr, notes in patterns[pat_name].items():
                        if instr not in tracks: tracks[instr] = []
                        tracks[instr].extend(copy.deepcopy(notes))
            elif item['type'] == 'instrument':
                instr, notes = item['data']
                if instr not in tracks: tracks[instr] = []
                tracks[instr].extend(copy.deepcopy(notes))
                
        # 4. Expand `every` and extract effects
        final_tracks = {}
        for instr, notes in tracks.items():
            final_notes = []
            for n in notes:
                # Extract effects
                if 'effects' in n:
                    if instr not in effects['per_track']:
                        effects['per_track'][instr] = []
                    for eff in n['effects']:
                        if eff not in effects['per_track'][instr]:
                            effects['per_track'][instr].append(eff)
                    del n['effects']
                
                # Expand every
                if 'every' in n:
                    interval = n['every']
                    current = 0.0
                    while current < 1.0: # A second has duration 1.0
                        new_n = {
                            "note": n['note'],
                            "start": round(current, 3),
                            "end": min(1.0, round(current + 0.1, 3)), # duration = 0.1
                            "velocity": n['velocity'],
                            "instrument": instr
                        }
                        final_notes.append(new_n)
                        current += interval
                else:
                    n['instrument'] = instr
                    final_notes.append(n)
            final_tracks[instr] = final_notes
            
        timeline.append({
            "second": second_idx,
            "tracks": final_tracks
        })
        
    return {
        "duration": max_duration,
        "effects": effects,
        "timeline": timeline
    }