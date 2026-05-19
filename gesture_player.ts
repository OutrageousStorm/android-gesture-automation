#!/usr/bin/env node
/**
 * gesture_player.ts -- TypeScript gesture replay engine for Android
 * Compile: tsc gesture_player.ts
 * Usage: node gesture_player.js --sequence sequence.json --repeat 3
 */

import { execSync } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';

interface Step {
  action: 'tap' | 'swipe' | 'wait' | 'key' | 'text';
  x?: number;
  y?: number;
  x2?: number;
  y2?: number;
  duration?: number;
  code?: number;
  input?: string;
  delay?: number;
  seconds?: number;
}

class GesturePlayer {
  private sequence: Step[];
  private repeat: number = 1;
  private speedMult: number = 1.0;

  constructor(sequence: Step[], repeat: number = 1, speedMult: number = 1.0) {
    this.sequence = sequence;
    this.repeat = repeat;
    this.speedMult = speedMult;
  }

  private adb(cmd: string): void {
    try {
      execSync(`adb shell ${cmd}`, { stdio: 'ignore' });
    } catch (e) {
      console.error(`ADB failed: ${cmd}`);
    }
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async play(): Promise<void> {
    console.log(`\n▶️  Playing ${this.sequence.length} steps × ${this.repeat}\n`);

    for (let r = 0; r < this.repeat; r++) {
      if (this.repeat > 1) console.log(`\nRun ${r + 1}/${this.repeat}`);

      for (let i = 0; i < this.sequence.length; i++) {
        const step = this.sequence[i];
        const delay = (step.delay || 0) * this.speedMult;

        switch (step.action) {
          case 'tap':
            console.log(`  [${i + 1}] tap(${step.x}, ${step.y})`);
            this.adb(`input tap ${step.x} ${step.y}`);
            break;

          case 'swipe':
            const dur = step.duration || 300;
            console.log(`  [${i + 1}] swipe (${step.x},${step.y}) → (${step.x2},${step.y2}) ${dur}ms`);
            this.adb(`input swipe ${step.x} ${step.y} ${step.x2} ${step.y2} ${dur}`);
            break;

          case 'key':
            console.log(`  [${i + 1}] key(${step.code})`);
            this.adb(`input keyevent ${step.code}`);
            break;

          case 'text':
            console.log(`  [${i + 1}] text: ${step.input?.slice(0, 30)}`);
            const escaped = step.input?.replace(/'/g, "\\'") || '';
            this.adb(`input text '${escaped}'`);
            break;

          case 'wait':
            console.log(`  [${i + 1}] wait ${step.seconds}s`);
            await this.sleep(step.seconds! * 1000);
            continue;
        }

        if (delay > 0) {
          await this.sleep(delay * 1000);
        }
      }
    }

    console.log('\n✅ Done.');
  }
}

async function main() {
  const args = process.argv.slice(2);
  let seqFile = 'sequence.json';
  let repeat = 1;
  let speed = 1.0;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--sequence') seqFile = args[++i];
    if (args[i] === '--repeat') repeat = parseInt(args[++i]);
    if (args[i] === '--speed') speed = parseFloat(args[++i]);
  }

  if (!fs.existsSync(seqFile)) {
    console.error(`File not found: ${seqFile}`);
    process.exit(1);
  }

  const sequence: Step[] = JSON.parse(fs.readFileSync(seqFile, 'utf-8'));
  const player = new GesturePlayer(sequence, repeat, speed);
  await player.play();
}

main();
