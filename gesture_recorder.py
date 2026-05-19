#!/usr/bin/env python3
"""
gesture_recorder.py -- Record touch gestures from Android device
Uses getevent to capture raw input, converts to gesture format.
Usage: python3 gesture_recorder.py --output gesture.json
"""
import subprocess, re, json, sys, argparse, time
from datetime import datetime

def record_gesture(output_file):
    print("📱 Gesture Recorder — Touch the screen (Ctrl+C when done)\n")
    
    gestures = []
    start_time = time.time()
    
    proc = subprocess.Popen(
        "adb shell getevent /dev/input/event0",
        shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
    )
    
    current_touch = None
    x, y = 0, 0
    touch_start_time = None
    
    try:
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            
            m = re.match(r'\[\s*(\d+\.\d+)\]\s+(\w+)\s+(\w+)\s+(\w+)', line)
            if not m:
                continue
            
            ts, type_hex, code_hex, val_hex = m.groups()
            ts = float(ts)
            
            # EV_KEY BTN_TOUCH
            if type_hex == "0001" and code_hex == "014a":
                if val_hex == "00000001":
                    # Touch down
                    touch_start_time = ts
                    current_touch = {"x": x, "y": y}
                    print(f"  ✓ DOWN at ({x}, {y})")
                elif val_hex == "00000000":
                    # Touch up
                    if current_touch and touch_start_time:
                        duration = int((ts - touch_start_time) * 1000)
                        dx = abs(x - current_touch["x"])
                        dy = abs(y - current_touch["y"])
                        distance = (dx**2 + dy**2)**0.5
                        
                        if distance < 50:
                            g = {
                                "type": "tap",
                                "x": current_touch["x"],
                                "y": current_touch["y"],
                                "duration": duration
                            }
                        else:
                            g = {
                                "type": "swipe",
                                "x1": current_touch["x"],
                                "y1": current_touch["y"],
                                "x2": x,
                                "y2": y,
                                "duration": duration
                            }
                        
                        gestures.append(g)
                        print(f"  ✓ {g['type'].upper()}: {duration}ms")
                        current_touch = None
            
            # EV_ABS
            elif type_hex == "0003":
                if code_hex == "0035":  # ABS_X
                    x = int(val_hex, 16)
                elif code_hex == "0036":  # ABS_Y
                    y = int(val_hex, 16)
    
    except KeyboardInterrupt:
        print("\n\nRecording stopped.")
    finally:
        proc.terminate()
    
    if gestures:
        with open(output_file, 'w') as f:
            json.dump(gestures, f, indent=2)
        print(f"\n✅ Recorded {len(gestures)} gestures → {output_file}")
    else:
        print("No gestures recorded.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="gesture.json")
    args = parser.parse_args()
    record_gesture(args.output)

if __name__ == "__main__":
    main()
