# 🎯 Android Gesture Automation

Record and replay touch gestures — taps, swipes, pinches, holds, multi-touch sequences.

## Tools

| Tool | Purpose |
|------|---------|
| `gesture_recorder.py` | Record live touch events to JSON |
| `gesture_player.py` | Replay recorded gestures |
| `gesture_builder.py` | Build gestures programmatically |
| `swipe_generator.py` | Generate swipe patterns (grid, diagonal, snake) |

## Quick start
```bash
# Record a tap sequence
python3 gesture_recorder.py --output my_gesture.json

# Play it back
python3 gesture_player.py --gesture my_gesture.json --repeat 3
```

## Gesture file format
```json
[
  {"type": "tap", "x": 540, "y": 960, "duration": 50},
  {"type": "swipe", "x1": 540, "y1": 1500, "x2": 540, "y2": 500, "duration": 300},
  {"type": "hold", "x": 540, "y": 960, "duration": 2000},
  {"type": "pinch", "x": 540, "y": 960, "start_dist": 200, "end_dist": 50, "duration": 500},
  {"type": "wait", "duration": 500}
]
```
