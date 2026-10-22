import { env } from 'cloudflare:workers';
import { connectInstagram } from '../../../../lib/instagram-feed.mjs';
export const dynamic='force-dynamic';
export async function POST(request:Request){return connectInstagram(request,env);}
