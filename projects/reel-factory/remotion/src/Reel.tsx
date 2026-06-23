import React from 'react';
import {
  AbsoluteFill,
  Audio,
  interpolate,
  OffthreadVideo,
  Sequence,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import type {ReelProps} from './schema';

// Faceless-Reel-Template: B-Roll (gefilmte Realität) + Voiceover + animierte
// Wort-für-Wort-Untertitel. Bewusst KEIN "KI-Look" — es gibt sich nicht als
// echte Person aus, sondern wirkt wie professionell geschnittener Nischen-Content.

const FALLBACK_BG = 'linear-gradient(160deg, #0c0c0c 0%, #1a1a1a 100%)';

export const Reel: React.FC<ReelProps> = ({hook, cta, tool_name, accent_color, audio_url, scenes, captions}) => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const timeMs = (frame / fps) * 1000;

  // Aktuell sichtbares Untertitel-Wort (Karaoke-Stil).
  const activeWords = captions.filter((c) => timeMs >= c.from_ms && timeMs < c.to_ms);
  const caption = activeWords.map((c) => c.text).join(' ');

  const hookOpacity = interpolate(frame, [0, 8, fps * 1.5, fps * 1.8], [0, 1, 1, 0], {
    extrapolateRight: 'clamp',
  });
  const ctaScale = spring({fps, frame: frame - (durationInFrames - fps * 1.5), config: {damping: 120}});

  return (
    <AbsoluteFill style={{background: FALLBACK_BG, fontFamily: 'Inter, system-ui, sans-serif'}}>
      {/* B-Roll je Szene */}
      {scenes.map((scene, i) => (
        <Sequence
          key={i}
          from={Math.round(scene.from_sec * fps)}
          durationInFrames={Math.max(1, Math.round((scene.to_sec - scene.from_sec) * fps))}
        >
          {scene.b_roll_url && scene.b_roll_url !== 'PLACEHOLDER_BROLL' ? (
            <OffthreadVideo src={scene.b_roll_url} muted style={{width: '100%', height: '100%', objectFit: 'cover'}} />
          ) : (
            <AbsoluteFill style={{background: FALLBACK_BG}} />
          )}
          {/* Abdunkelung für Lesbarkeit der Untertitel */}
          <AbsoluteFill style={{background: 'linear-gradient(transparent 55%, rgba(0,0,0,0.75))'}} />
        </Sequence>
      ))}

      {/* Voiceover */}
      {audio_url && audio_url !== 'PLACEHOLDER_AUDIO' ? <Audio src={audio_url} /> : null}

      {/* Tool-Badge oben (durchgehendes Branding der Affiliate-Nische) */}
      <AbsoluteFill style={{justifyContent: 'flex-start', alignItems: 'center', paddingTop: 120}}>
        <span
          style={{
            color: accent_color,
            border: `3px solid ${accent_color}`,
            borderRadius: 999,
            padding: '8px 24px',
            fontSize: 40,
            fontWeight: 700,
            backgroundColor: 'rgba(0,0,0,0.35)',
          }}
        >
          {tool_name}
        </span>
      </AbsoluteFill>

      {/* Hook (erste ~2s) */}
      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', padding: 80, opacity: hookOpacity}}>
        <span style={{color: 'white', fontSize: 96, fontWeight: 800, textAlign: 'center', lineHeight: 1.1}}>
          {hook}
        </span>
      </AbsoluteFill>

      {/* Animierte Untertitel */}
      <AbsoluteFill style={{justifyContent: 'flex-end', alignItems: 'center', paddingBottom: 360}}>
        <span
          style={{
            color: 'white',
            background: accent_color,
            padding: '12px 28px',
            borderRadius: 16,
            fontSize: 64,
            fontWeight: 800,
            textAlign: 'center',
            maxWidth: '88%',
          }}
        >
          {caption}
        </span>
      </AbsoluteFill>

      {/* CTA (letzte ~1.5s) */}
      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', transform: `scale(${ctaScale})`}}>
        {frame > durationInFrames - fps * 1.5 ? (
          <span style={{color: accent_color, fontSize: 80, fontWeight: 800, textAlign: 'center'}}>{cta}</span>
        ) : null}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
