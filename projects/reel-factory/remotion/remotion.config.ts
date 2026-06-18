import {Config} from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setCodec('h264');
// OffthreadVideo (B-Roll) profitiert von genügend Threads beim Render.
Config.setConcurrency(null); // null = automatisch nach CPU-Kernen
