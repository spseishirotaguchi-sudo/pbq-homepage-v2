import {segmentJapanese} from './japanese-wrap.mjs';
const ACCOUNT = 'p.b.q_fukuoka';
export const INSTAGRAM_REDIRECT = 'https://pbq-fukuoka-20261022.s-taguchi323.chatgpt.site/instagram-connect';
export const OAUTH_COOKIE = '__Host-pbq-ig-state';
const GRAPH = 'https://graph.instagram.com/v25.0';
const CONNECTION = 'instagram/connection-v1.enc';
const FEED = 'instagram/public-feed-v1.json';
const MAX_AGE = 15 * 60 * 1000;

const encode = bytes => btoa(String.fromCharCode(...bytes)).replaceAll('+','-').replaceAll('/','_').replaceAll('=','');
const decode = text => Uint8Array.from(atob(text.replaceAll('-','+').replaceAll('_','/') + '='.repeat((4-text.length%4)%4)), c => c.charCodeAt(0));
const json = (data, status=200) => Response.json(data, {status,headers:{'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'}});

async function encryptionKey(env) {
  return crypto.subtle.importKey('raw', decode(env.INSTAGRAM_TOKEN_KEY), 'AES-GCM', false, ['encrypt','decrypt']);
}
async function saveConnection(env, value) {
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const encrypted = await crypto.subtle.encrypt({name:'AES-GCM',iv}, await encryptionKey(env), new TextEncoder().encode(JSON.stringify(value)));
  await env.BUCKET.put(CONNECTION, JSON.stringify({iv:encode(iv),cipher:encode(new Uint8Array(encrypted))}));
}
async function readConnection(env) {
  const object = await env.BUCKET.get(CONNECTION);
  if (!object) return null;
  const {iv,cipher} = await object.json();
  const data = await crypto.subtle.decrypt({name:'AES-GCM',iv:decode(iv)}, await encryptionKey(env), decode(cipher));
  return JSON.parse(new TextDecoder().decode(data));
}
async function graph(path, token, params={}) {
  const url = new URL(GRAPH+path);
  for (const [key,value] of Object.entries(params)) url.searchParams.set(key,value);
  const response = await fetch(url, {headers:{Authorization:`Bearer ${token}`},signal:AbortSignal.timeout(12000)});
  const body = await response.json();
  if (!response.ok || body.error) throw new Error('instagram_request_failed');
  return body;
}
export function sanitizePosts(rows) {
  return rows.filter(row => /^https:\/\/(www\.)?instagram\.com\/(p|reel)\/[A-Za-z0-9_-]+\/?/.test(row.permalink || ''))
    .map(row => ({id:String(row.id),caption:String(row.caption || '').slice(0,2000),captionParts:segmentJapanese(String(row.caption || '').slice(0,2000)),type:row.media_type,
      image:row.media_type==='VIDEO' ? (row.thumbnail_url || '') : (row.media_url || ''),
      permalink:row.permalink,timestamp:row.timestamp}))
    .sort((a,b)=>new Date(b.timestamp)-new Date(a.timestamp)).slice(0,3);
}
async function media(connection) {
  const body = await graph(`/${connection.id}/media`,connection.token,{fields:'id,caption,media_type,media_url,thumbnail_url,permalink,timestamp',limit:'12'});
  return {status:'connected',account:ACCOUNT,updatedAt:new Date().toISOString(),posts:sanitizePosts(body.data || [])};
}
async function refreshToken(env, connection) {
  if (Date.now()-connection.refreshedAt < 7*86400000) return connection;
  // Instagram's long-lived token is renewed before its normal expiry. An
  // account that revokes access, or stays unused beyond expiry, must reconnect.
  const url = new URL('https://graph.instagram.com/refresh_access_token');
  url.searchParams.set('grant_type','ig_refresh_token');
  url.searchParams.set('access_token',connection.token);
  const response = await fetch(url,{signal:AbortSignal.timeout(12000)});
  const body = await response.json();
  if (response.ok && body.access_token) {
    connection={...connection,token:body.access_token,refreshedAt:Date.now()};
    await saveConnection(env,connection);
  }
  return connection;
}
export function isOwner(request,env) {
  const email=request.headers.get('oai-authenticated-user-email');
  return !!email && !!env.INSTAGRAM_OWNER_EMAIL && email.toLowerCase()===env.INSTAGRAM_OWNER_EMAIL.toLowerCase();
}
function connectionError(code){const error=new Error(code);error.safeCode=code;return error;}
async function exchangeCode(data){
  if(typeof data.code!=='string'||data.code.length<20||data.code.length>4096||typeof data.appSecret!=='string'||!/^[a-fA-F0-9]{32}$/.test(data.appSecret)) throw connectionError('invalid_authorization');
  const form=new FormData();
  form.set('client_id','1052557270857113');form.set('client_secret',data.appSecret);form.set('grant_type','authorization_code');
  form.set('redirect_uri',INSTAGRAM_REDIRECT);form.set('code',data.code);
  const response=await fetch('https://api.instagram.com/oauth/access_token',{method:'POST',body:form,signal:AbortSignal.timeout(12000)});
  const body=await response.json();const authorization=body.data?.[0]||body;
  if(!response.ok||!authorization.access_token) throw connectionError('authorization_exchange_failed');
  const permissions=Array.isArray(authorization.permissions)?authorization.permissions:String(authorization.permissions||'').split(',').map(x=>x.trim()).filter(Boolean);
  if(permissions.length!==1||permissions[0]!=='instagram_business_basic') throw connectionError('unexpected_permissions');
  const url=new URL('https://graph.instagram.com/access_token');url.searchParams.set('grant_type','ig_exchange_token');url.searchParams.set('client_secret',data.appSecret);url.searchParams.set('access_token',authorization.access_token);
  const extended=await fetch(url,{signal:AbortSignal.timeout(12000)});const long=await extended.json();
  if(!extended.ok||!long.access_token||long.expires_in<86400) throw connectionError('long_token_exchange_failed');
  return {token:long.access_token,permissions,expiresIn:long.expires_in};
}
export async function connectInstagram(request,env) {
  if (!isOwner(request,env)) return json({error:'forbidden'},403);
  if (request.headers.get('origin')!==new URL(request.url).origin || !request.headers.get('content-type')?.startsWith('application/json')) return json({error:'invalid_request'},403);
  if (!env.BUCKET || !env.INSTAGRAM_TOKEN_KEY) return json({error:'not_configured'},503);
  if(Number(request.headers.get('content-length')||0)>10000) return json({error:'invalid_request'},413);
  try {
    const data=await request.json();let token=data.token,authorization;
    if(data.code) {
      const cookie=request.headers.get('cookie')?.split(';').map(x=>x.trim()).find(x=>x.startsWith(OAUTH_COOKIE+'='))?.slice(OAUTH_COOKIE.length+1);
      if(typeof data.state!=='string'||!/^[a-f0-9]{64}$/.test(data.state)||data.state!==cookie) return json({error:'invalid_state'},403);
      authorization=await exchangeCode(data);token=authorization.token;
    }
    if (typeof token!=='string' || token.length<30 || token.length>4096) return json({error:'invalid_token'},400);
    const account=await graph('/me',token,{fields:'user_id,username'});
    if (String(account.username).toLowerCase()!==ACCOUNT) return json({error:'wrong_account'},400);
    const connection={id:String(account.user_id),username:ACCOUNT,token,refreshedAt:Date.now(),...(authorization?{permissions:authorization.permissions}: {})};
    const feed=await media(connection);
    if (!feed.posts.length) return json({error:'no_public_posts'},400);
    await saveConnection(env,connection);
    await env.BUCKET.put(FEED,JSON.stringify(feed));
    const result=json({connected:true,account:ACCOUNT,count:feed.posts.length,updatedAt:feed.updatedAt,...(authorization?{permissions:authorization.permissions,expiresIn:authorization.expiresIn}:{})});
    if(authorization) result.headers.set('Set-Cookie',`${OAUTH_COOKIE}=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0`);
    return result;
  } catch(error) {
    return json({error:error.safeCode||'connection_failed'},400);
  }
}

let inFlight;
export async function getInstagramFeed(env) {
  if (!env.BUCKET || !env.INSTAGRAM_TOKEN_KEY) return json({status:'not_connected',posts:[]});
  let cached;
  try {
    const object=await env.BUCKET.get(FEED);
    cached=object ? await object.json() : null;
    if (cached && Date.now()-Date.parse(cached.updatedAt)<MAX_AGE) return json(cached);
    if (!inFlight) inFlight=(async()=>{
      let connection=await readConnection(env);
      if (!connection) return {status:'not_connected',posts:[]};
      connection=await refreshToken(env,connection);
      const feed=await media(connection);
      await env.BUCKET.put(FEED,JSON.stringify(feed));
      return feed;
    })().finally(()=>{inFlight=null;});
    return json(await inFlight);
  } catch {
    // Keep the last successful feed rather than replacing it with an empty grid.
    return json(cached ? {...cached,status:'cached'} : {status:'temporarily_unavailable',posts:[]});
  }
}
