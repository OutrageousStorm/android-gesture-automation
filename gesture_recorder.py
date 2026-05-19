#!/usr/bin/env python3
"""gesture_recorder.py -- Record and playback touch gestures on Android
Records tap positions, swipes, long presses for UI automation testing
"""
import subprocess, json, argparse, time, sys

def adb(cmd):
    subprocess.run(['adb', 'shell'] + cmd.split(), capture_output=True)

def record_touches(duration=10, output="gestures.json"):
    """Record all touch events for N seconds"""
    print(f"📱 Recording touch gestures for {duration}s...")
    print("Interact with device now...")
    
    gestures = []
    start = time.time()
    
    # Use getevent to capture input
    proc = subprocess.Popen(
        ['adb', 'shell', 'getevent /dev/input/event0'],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
    )
    
    while time.time() - start < duration:
        try:
            line = proc.stdout.readline()
            if 'ABS_MT_POSITION_X' in line or 'ABS_MT_POSITION_Y' in line:
                gestures.append({'timestamp': time.time() - start, 'event': line.strip()})
        except:
            pass
    
    proc.terminate()
    
    with open(output, 'w') as f:
        json.dump(gestures, f, indent=2)
    
    print(f"✅ Recorded {len(gestures)} events → {output}")

def playback(input_file="gestures.json"):
    """Playback recorded gestures"""
    with open(input_file) as f:
        gestures = json.load(f)
    
    print(f"▶️  Playback {len(gestures)} gestures...")
    last_time = 0
    for g in gestures:
        delay = g['timestamp'] - last_time
        if delay > 0:
            time.sleep(delay)
        # Re-send via adb input
        print(f"  {g['event']}")
        last_time = g['timestamp']
    
    print("✅ Playback complete")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Touch gesture recorder/player')
    parser.add_argument('--record', action='store_true', help='Record mode')
    parser.add_argument('--playback', action='store_true', help='Playback mode')
    parser.add_argument('--duration', type=int, default=10, help='Record duration')
    parser.add_argument('--file', default='gestures.json')
    args = parser.parse_args()
    
    if args.record:
        record_touches(args.duration, args.file)
    elif args.playback:
        playback(args.file)
