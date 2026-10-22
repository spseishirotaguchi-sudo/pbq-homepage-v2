import {loadDefaultJapaneseParser} from 'budoux';

const parser=loadDefaultJapaneseParser();
const words=typeof Intl.Segmenter==='function' ? new Intl.Segmenter('ja',{granularity:'word'}) : null;
const protectedWords=['p.b.q','Instagram','公式LINE','20代社会人','バスケットボール','バスケ','サードプレイス','コミュニティ','コミュニケーション','親睦会','交流イベント','イベント','体験参加','参加申込み','参加費','社会人','夢中になれる','キャンセル料','500円'];
const noStart=/^[、。，．！？!?：:；;・）)］\]｝}」』】〉》ーぁぃぅぇぉっゃゅょァィゥェォッャュョ]/u;
const noEnd=/[（(［\[｛{「『【〈《]$/u;
const attached=new Set(['は','が','を','に','へ','と','も','の','で','や','か','から','まで','より','など','だけ','こそ','です','ます','ません','たい','た','て']);
const japanese=/[\p{Script=Han}\p{Script=Hiragana}\p{Script=Katakana}]/u;

export function hasJapanese(text){return japanese.test(text);}
function allowedBoundaries(text,positions){
  const forbidden=[];
  for(const word of protectedWords){
    let from=0,index;
    while((index=text.indexOf(word,from))!==-1){forbidden.push([index,index+word.length]);from=index+word.length;}
  }
  return positions.filter(i=>i>0&&i<text.length&&!noStart.test(text.slice(i))&&!noEnd.test(text.slice(0,i))&&!forbidden.some(([a,b])=>a<i&&i<b));
}
function splitAt(text,positions){let from=0;return [...positions,text.length].map(i=>{const part=text.slice(from,i);from=i;return part;}).filter(Boolean);}

// Primary units are BudouX phrases. Only a phrase wider than its container
// falls back to the word boundaries within that phrase.
export function segmentJapanese(text){
  text=String(text);
  if(!hasJapanese(text))return [[text]];
  let offset=0;
  const phraseEnds=parser.parse(text).slice(0,-1).map(p=>offset+=p.length);
  return splitAt(text,allowedBoundaries(text,phraseEnds)).map(phrase=>{
    if(!words)return [phrase];
    const tokens=[...words.segment(phrase)];
    const boundaries=tokens.slice(1).filter(t=>!attached.has(t.segment)).map(t=>t.index);
    return splitAt(phrase,allowedBoundaries(phrase,boundaries));
  });
}
