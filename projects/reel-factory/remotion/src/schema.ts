import {z} from 'zod';

// Dieses Schema ist der Node-seitige Spiegel von pipeline/schema.py -> RenderProps.
// Beide müssen dieselbe Form haben; das JSON aus Python wird hiergegen validiert.

export const captionToken = z.object({
  text: z.string(),
  from_ms: z.number(),
  to_ms: z.number(),
});

export const renderScene = z.object({
  b_roll_url: z.string(),
  from_sec: z.number(),
  to_sec: z.number(),
});

export const reelProps = z.object({
  hook: z.string(),
  cta: z.string(),
  accent_color: z.string(),
  audio_url: z.string(),
  duration_in_seconds: z.number(),
  scenes: z.array(renderScene),
  captions: z.array(captionToken),
});

export type ReelProps = z.infer<typeof reelProps>;
