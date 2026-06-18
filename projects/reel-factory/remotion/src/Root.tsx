import React from 'react';
import {Composition} from 'remotion';
import {Reel} from './Reel';
import {reelProps, type ReelProps} from './schema';

// Demo-Props, damit die Composition im Remotion Studio ohne Python-Pipeline editierbar ist.
const defaultProps: ReelProps = {
  hook: 'Most people get compound interest completely wrong.',
  cta: 'Follow for part two.',
  accent_color: '#00E0A4',
  audio_url: 'PLACEHOLDER_AUDIO',
  duration_in_seconds: 8,
  scenes: [
    {b_roll_url: 'PLACEHOLDER_BROLL', from_sec: 0, to_sec: 4},
    {b_roll_url: 'PLACEHOLDER_BROLL', from_sec: 4, to_sec: 8},
  ],
  captions: [
    {text: 'Compound', from_ms: 0, to_ms: 500},
    {text: 'interest', from_ms: 500, to_ms: 1000},
    {text: 'is', from_ms: 1000, to_ms: 1300},
    {text: 'misunderstood.', from_ms: 1300, to_ms: 2000},
  ],
};

const FPS = 30;
const WIDTH = 1080;
const HEIGHT = 1920;

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="Reel"
      component={Reel}
      schema={reelProps}
      defaultProps={defaultProps}
      fps={FPS}
      width={WIDTH}
      height={HEIGHT}
      // Dauer aus den Props ableiten -> jedes Reel ist exakt so lang wie sein Voiceover.
      calculateMetadata={({props}) => ({
        durationInFrames: Math.max(1, Math.round(props.duration_in_seconds * FPS)),
      })}
    />
  );
};
