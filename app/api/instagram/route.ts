import { env } from 'cloudflare:workers';
import { getInstagramFeed } from '../../../lib/instagram-feed.mjs';
export const dynamic='force-dynamic';
export async function GET(){return getInstagramFeed(env);}
