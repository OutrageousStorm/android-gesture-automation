#!/usr/bin/env python3
"""
gesture_analyzer.py -- Analyze recorded gesture files for patterns
Useful for understanding touch patterns and optimizing replay timing.
Usage: python3 gesture_analyzer.py gesture_log.txt
"""
import sys, json, statistics
from pathlib import Path

def parse_gestures(file_path):
    """Parse gesture file format: timestamp,type,x,y,pressure,size"""
    gestures = []
    with open(file_path) as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            parts = line.strip().split(',')
            if len(parts) >= 4:
                try:
                    gesture = {
                        'ts': float(parts[0]),
                        'type': parts[1],  # down/move/up
                        'x': int(parts[2]),
                        'y': int(parts[3]),
                        'pressure': float(parts[4]) if len(parts) > 4 else 1.0,
                        'size': float(parts[5]) if len(parts) > 5 else 1.0,
                    }
                    gestures.append(gesture)
                except ValueError:
                    continue
    return gestures

def analyze(gestures):
    """Extract metrics from gesture sequence"""
    if not gestures:
        return {}
    
    # Group by touch events (down -> move* -> up)
    touches = []
    current = []
    for g in gestures:
        if g['type'] == 'down':
            current = [g]
        elif g['type'] == 'move':
            if current:
                current.append(g)
        elif g['type'] == 'up':
            if current:
                current.append(g)
                touches.append(current)
                current = []
    
    # Calculate metrics
    metrics = {
        'total_events': len(gestures),
        'total_touches': len(touches),
        'duration_ms': (gestures[-1]['ts'] - gestures[0]['ts']) * 1000 if gestures else 0,
        'touches': {}
    }
    
    if touches:
        touch_durations = []
        distances = []
        
        for touch in touches:
            start = touch[0]
            end = touch[-1]
            duration = (end['ts'] - start['ts']) * 1000
            touch_durations.append(duration)
            
            dx = end['x'] - start['x']
            dy = end['y'] - start['y']
            distance = (dx**2 + dy**2) ** 0.5
            distances.append(distance)
        
        metrics['touches'] = {
            'count': len(touches),
            'avg_duration_ms': statistics.mean(touch_durations),
            'median_duration_ms': statistics.median(touch_durations),
            'avg_distance_px': statistics.mean(distances),
            'max_distance_px': max(distances),
        }
    
    # Pressure & size stats
    pressures = [g['pressure'] for g in gestures if g['pressure'] > 0]
    sizes = [g['size'] for g in gestures if g['size'] > 0]
    
    if pressures:
        metrics['pressure'] = {
            'avg': statistics.mean(pressures),
            'min': min(pressures),
            'max': max(pressures),
        }
    
    if sizes:
        metrics['size'] = {
            'avg': statistics.mean(sizes),
            'min': min(sizes),
            'max': max(sizes),
        }
    
    return metrics

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 gesture_analyzer.py <gesture_file>")
        print("\nGesture file format (CSV):")
        print("  timestamp,type,x,y,pressure,size")
        print("  type: down|move|up")
        sys.exit(1)
    
    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"File not found: {file_path}")
        sys.exit(1)
    
    gestures = parse_gestures(file_path)
    metrics = analyze(gestures)
    
    print(f"\n📊 Gesture Analysis: {file_path.name}")
    print("=" * 50)
    print(f"Total events: {metrics['total_events']}")
    print(f"Total touches: {metrics.get('total_touches', 0)}")
    print(f"Duration: {metrics['duration_ms']:.1f} ms")
    
    if 'touches' in metrics and metrics['touches']:
        t = metrics['touches']
        print(f"\nTouch Statistics:")
        print(f"  Avg duration: {t.get('avg_duration_ms', 0):.1f} ms")
        print(f"  Avg distance: {t.get('avg_distance_px', 0):.1f} px")
        print(f"  Max distance: {t.get('max_distance_px', 0):.1f} px")
    
    if 'pressure' in metrics:
        p = metrics['pressure']
        print(f"\nPressure (0.0-1.0):")
        print(f"  Avg: {p.get('avg', 0):.2f}  Min: {p.get('min', 0):.2f}  Max: {p.get('max', 0):.2f}")
    
    print(f"\n💾 Full metrics (JSON):")
    print(json.dumps(metrics, indent=2))

if __name__ == "__main__":
    main()
