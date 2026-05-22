import { spawn } from 'child_process';
import * as fs from 'fs';

class GestureAutomation {
  private pattern: any[];
  
  constructor(patternFile: string) {
    this.pattern = JSON.parse(fs.readFileSync(patternFile, 'utf8')).events;
  }
  
  async replay(device?: string): Promise<void> {
    console.log('[*] Replaying gesture pattern...');
    
    for (let i = 0; i < this.pattern.length; i++) {
      if (i > 0) {
        const waitMs = this.pattern[i].relative_ms - this.pattern[i-1].relative_ms;
        await new Promise(r => setTimeout(r, waitMs));
      }
    }
    
    console.log('[✓] Replay complete');
  }
}

export default GestureAutomation;
