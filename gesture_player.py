#!/usr/bin/env python3
"""
gesture_player.py -- Replay recorded touch gestures on Android device
Usage: python3 gesture_player.py --gesture gesture.json --repeat 1 --speed 1.0
"""
import subprocess, json, time, argparse, sys

def adb(cmd):
    subprocess.run(f"adb shell {cmd}", shell=True, capture_output=True)

def play_gesture(gesture_data, speed_mult=1.0):
    """Play a single gesture"""
    g_type = gesture_data.get("type")
    
    if g_type == "tap":
        x, y = gesture_data["x"], gesture_data["y"]
        adb(f"input tap {x} {y}")
        print(f"  tap({x}, {y})")
    
    elif g_type == "swipe":
        x1, y1 = gesture_data["x1"], gesture_data["y1"]
        x2, y2 = gesture_data["x2"], gesture_data["y2"]
        dur = int(gesture_data["duration"] * speed_mult)
        adb(f"input swipe {x1} {y1} {x2} {y2} {dur}")
        print(f"  swipe({x1},{y1}→{x2},{y2}) {dur}ms")
    
    elif g_type == "hold":
        x, y = gesture_data["x"], gesture_data["y"]
        dur = int(gesture_data["duration"] * speed_mult / 1000)
        adb(f"input swipe {x} {y} {x} {y} {dur}")
        print(f"  hold({x}, {y}) {dur}s")
    
    elif g_type == "wait":
        dur = gesture_data["duration"] / 1000 * speed_mult
        print(f"  wait {dur:.1f}s")
        time.sleep(dur)
        return
    
    # Apply delay
    delay = gesture_data.get("delay", 100) / 1000 * speed_mult
    time.sleep(delay)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gesture", required=True)
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--speed", type=float, default=1.0, help="1.0=normal, 0.5=2x fast, 2.0=half speed")
    args = parser.parse_args()
    
    with open(args.gesture) as f:
        gestures = json.load(f)
    
    print(f"\n▶️  Playing {len(gestures)} gestures × {args.repeat} times (speed: {args.speed}x)\n")
    
    for r in range(args.repeat):
        if args.repeat > 1:
            print(f"Run {r+1}/{args.repeat}:")
        for g in gestures:
            play_gesture(g, args.speed)
    
    print("\n✅ Playback complete")

if __name__ == "__main__":
    main()
