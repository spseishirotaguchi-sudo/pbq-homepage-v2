import {readFile,writeFile,readdir} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {parse,serialize} from 'parse5';
import {hasJapanese,segmentJapanese} from '../lib/japanese-wrap.mjs';

const root=fileURLToPath(new URL('../',import.meta.url));
const textNode=(text,parent)=>({nodeName:'#text',value:text,parentNode:parent});
const element=(tag,parent,attrs=[])=>({nodeName:tag,tagName:tag,attrs,namespaceURI:'http://www.w3.org/1999/xhtml',childNodes:[],parentNode:parent});
const addClass=(node,name)=>{const attr=node.attrs?.find(a=>a.name==='class');if(attr){if(!attr.value.split(/\s+/).includes(name))attr.value+=' '+name;}else node.attrs?.push({name:'class',value:name});};
const skipTags=new Set(['head','script','style','svg','textarea','code','pre','pbq-phrase']);
const skipClasses=new Set(['wordmark','brand-caption','hero-title','message-ghost','entry-ghost']);
const content=node=>node.nodeName==='#text'?node.value:(node.childNodes||[]).map(content).join('');
let phrases=0;
function visit(node,skip=false,preserveBreaks=false){
  const attrs=Object.fromEntries((node.attrs||[]).map(a=>[a.name,a.value]));
  preserveBreaks=preserveBreaks||Object.hasOwn(attrs,'data-preserve-breaks');
  skip=skip||skipTags.has(node.tagName)||attrs['aria-hidden']==='true'||(attrs.class||'').split(/\s+/).some(c=>skipClasses.has(c));
  if(skip)return;
  const children=[];
  for(const child of node.childNodes||[]){
    if(child.nodeName==='#text'&&hasJapanese(child.value)){
      addClass(node,'ja-typeset');
      for(const group of segmentJapanese(child.value)){
        const phrase=element('pbq-phrase',node);
        group.forEach((word,i)=>{if(i)phrase.childNodes.push(element('wbr',phrase));phrase.childNodes.push(textNode(word,phrase));});
        children.push(phrase);phrases++;
      }
    }else if(child.tagName==='br'&&!preserveBreaks&&hasJapanese(content(node))){
      // Editorial paragraphs remain paragraphs; screen-specific hard breaks
      // become optional opportunities, so they do not create orphan fragments.
      children.push(element('wbr',node));
    }else{visit(child,skip,preserveBreaks);children.push(child);}
  }
  if(node.childNodes)node.childNodes=children;
}

for(const file of (await readdir(root+'site')).filter(x=>x.endsWith('.html'))){
  const document=parse(await readFile(root+'site/'+file,'utf8'));
  const before=content(document);
  visit(document);
  if(content(document)!==before)throw new Error('Text changed during typesetting: '+file);
  const dataNode=(function find(n){if(n.attrs?.some(a=>a.name==='id'&&a.value==='gallery-data'))return n;for(const c of n.childNodes||[]){const r=find(c);if(r)return r;}})(document);
  if(dataNode){const rows=JSON.parse(content(dataNode));for(const row of rows)row[5]={title:segmentJapanese(row[1]),caption:segmentJapanese(row[2])};dataNode.childNodes=[textNode(JSON.stringify(rows),dataNode)];}
  const html=serialize(document);
  await Promise.all(['site','public'].map(dir=>writeFile(root+dir+'/'+file,html)));
}
console.log('Japanese typesetting: '+phrases+' phrase groups across 8 pages.');
