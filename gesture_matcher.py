#!/usr/bin/env python3
"""
gesture_matcher.py -- Compare gesture patterns and find similar touch sequences
Useful for UI automation and gesture recognition.
"""
import json, math, sys

def euclidean_distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def gesture_similarity(gestures_a, gestures_b, threshold=50):
    """Calculate similarity between two gesture sequences (0.0-1.0)"""
    if not gestures_a or not gestures_b:
        return 0.0
    
    # Normalize lengths
    max_len = max(len(gestures_a), len(gestures_b))
    distances = []
    
    for i in range(max_len):
        if i < len(gestures_a) and i < len(gestures_b):
            a = gestures_a[i]
            b = gestures_b[i]
            if 'x' in a and 'y' in a and 'x' in b and 'y' in b:
                dist = euclidean_distance((a['x'], a['y']), (b['x'], b['y']))
                distances.append(dist)
        else:
            distances.append(threshold)  # penalty for length mismatch
    
    avg_distance = sum(distances) / len(distances) if distances else threshold
    similarity = max(0, 1.0 - (avg_distance / threshold))
    return similarity

def load_gesture(file_path):
    with open(file_path) as f:
        data = json.load(f)
        return data if isinstance(data, list) else data.get('events', [])

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 gesture_matcher.py <gesture1.json> <gesture2.json> [threshold]")
        sys.exit(1)
    
    file1, file2 = sys.argv[1], sys.argv[2]
    threshold = int(sys.argv[3]) if len(sys.argv) > 3 else 50
    
    try:
        g1 = load_gesture(file1)
        g2 = load_gesture(file2)
        
        similarity = gesture_similarity(g1, g2, threshold)
        
        print(f"\n🎯 Gesture Matcher")
        print(f"File 1: {file1} ({len(g1)} events)")
        print(f"File 2: {file2} ({len(g2)} events)")
        print(f"Similarity: {similarity:.1%}")
        
        if similarity > 0.8:
            print("Status: ✅ Very similar (likely same action)")
        elif similarity > 0.6:
            print("Status: ⚠️  Similar (related actions)")
        elif similarity > 0.4:
            print("Status: ~ Somewhat similar")
        else:
            print("Status: ❌ Very different gestures")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
