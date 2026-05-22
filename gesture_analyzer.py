#!/usr/bin/env python3
import subprocess, re, json, time
from datetime import datetime

class GestureAnalyzer:
    def __init__(self):
        self.events = []
        self.start_time = None
    
    def capture_touch_events(self, duration_seconds=10, device=None):
        cmd = f"adb {f'-s {device}' if device else ''} shell getevent /dev/input/event*"
        print(f"[*] Capturing for {duration_seconds}s... Touch the screen.")
        start = time.time()
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, text=True)
        
        try:
            while time.time() - start < duration_seconds:
                line = proc.stdout.readline()
                if line and '/dev/input' in line:
                    self.parse_event_line(line)
        finally:
            proc.terminate()
        
        self.calculate_timing()
        return self.events
    
    def parse_event_line(self, line):
        match = re.search(r'\[(.*?)\].*event(\d+):(.*)', line)
        if match:
            timestamp = float(match.group(1))
            if not self.start_time:
                self.start_time = timestamp
            relative_time = timestamp - self.start_time
            self.events.append({'timestamp': relative_time, 'raw': match.group(3)})
    
    def calculate_timing(self):
        for event in self.events:
            event['relative_ms'] = int(event['timestamp'] * 1000)
    
    def save_pattern(self, filename):
        pattern = {'name': filename, 'created': datetime.now().isoformat(), 'events': self.events}
        with open(filename, 'w') as f:
            json.dump(pattern, f, indent=2)
        print(f"[✓] Saved to {filename}")

if __name__ == '__main__':
    import sys
    analyzer = GestureAnalyzer()
    if len(sys.argv) > 1:
        analyzer.capture_touch_events(duration_seconds=int(sys.argv[1]))
    else:
        analyzer.capture_touch_events(duration_seconds=15)
    analyzer.save_pattern('gesture_pattern.json')
