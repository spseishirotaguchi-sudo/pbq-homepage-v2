import assert from 'node:assert/strict';
import {segmentJapanese} from '../lib/japanese-wrap.mjs';

for(const text of ['親睦会・交流イベント','日常に、夢中になれる時間を。','福岡の20代社会人バスケコミュニティです。','「もう一度、バスケットボールを。」','<script>alert("test")</script>を見る']){
  const groups=segmentJapanese(text);
  assert.equal(groups.flat().join(''),text,'Typesetting must preserve every character');
  for(const group of groups)for(const word of group)assert.ok(!/^[、。）」』・]/u.test(word),'Punctuation must remain with the preceding text');
}
assert.deepEqual(segmentJapanese('親睦会・交流イベント'),[['親睦会・','交流イベント']]);
assert.ok(segmentJapanese('日常に、夢中になれる時間を。').some(group=>group.join('')==='夢中になれる'));
assert.deepEqual(segmentJapanese('Instagram'),[['Instagram']]);
console.log('PASS: exact text, phrase priority, compound-word fallback, punctuation and brand names.');
