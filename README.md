# p.b.q 新ホームページ

更新日：2026-10-23。既存LPとは別のホームページ。同じSitesプロジェクトを継続して更新。

## 目的・構成

20代社会人のバスケ経験者が活動・雰囲気・参加条件を確認し、公式LINEで体験参加を申し込む。
トップ / 想い / 活動紹介 / グッズ販売（準備中） / 参加案内 / 写真 / プライバシー、ほか404。
トップの重複していたINFORMATION・JOIN GUIDE・OUR MOMENTSは削除。
バスケ・イベント・サードプレイスの3つの輪が交差し、共通部分に黒いp.b.qロゴを配置。
上部は日本語のテキストナビ。LINEボタンは公式アイコンと緑、Instagramボタンはピンク〜紫。

## 参照と実素材

全体構成：gbsmedical.jp。ヘッダーのみ：sunfluoro.co.jp。Instagram欄のみ：next-jonan.co.jp。
他社の写真・文章・ロゴ・コードは使用しない。写真はp.b.qの実素材をトリミング・圧縮して利用。人物の生成や顔の改変は行わない。
映像の出典・時刻はqa/media-selection.json。ヒーローはシュート成功を確認した10/13の映像と、別場面の笑顔。ゴール後の反応と誤認させる編集にしない。音声なし。

## Instagram最新3件

公開投稿のGraph APIを使う。取得した投稿のうち時刻順の最新3件を表示。画像はAPIのURLを直接参照し、投稿を押すとInstagramの公式埋め込みを開く。
15分キャッシュ。更新時の一時的な取得エラーでは最後に成功したデータを残す。
接続はサイト所有者専用の /instagram-connect。アカウントp.b.q_fukuokaだけを許可する。
トークンはR2にAES-GCMで暗号化保存。復号鍵と所有者識別はSitesのシークレット環境変数。ブラウザ向けレスポンスやローカルファイルにはトークンを含めない。
7日以上経ったトークンはアクセス時に更新。長期間アクセスがない場合、期限切れ・権限取り消し時は再接続が必要。
認証コードから接続する場合は、Metaが返すアクセス許可の一覧がinstagram_business_basicだけであることを検証し、余分な権限がある接続は保存しない。App Secretと認証コードは交換時だけ使用し、保存・返却しない。2026-10-23に実アカウントで再接続し、権限がinstagram_business_basicのみであること、最新3件の取得とHP表示を確認済み。認証の戻り先はこのHPの/instagram-connectで、stateを管理者のHttpOnly Cookieと照合する。

## 実装・検証

build_site.py → site/ と public/ のHTML。public/assets/ がCSS・JSと媒体。
VinextがホームページとAPIを提供。 .openai/hosting.json に同じSite IDとR2バインディングを保持。
生成：python3 build_site.py
リンク・構造：python3 qa/check_site.py
接続の境界・暗号化・キャッシュ：node qa/instagram-check.mjs
構文：node --check public/assets/site.js
ビルド：npm run build。公開梱包にはSites公式build-site.mjs / site-workflow.mjsを使用。

## 公開範囲

既存の一般公開サイトを維持。公開URL・所有者・Instagram連携の権限は変更しない。

## アクセス解析（2026-11-01）

GA4「p.b.q｜HP・LP」、測定ID `G-R6ZDP89L27`。HPと既存LPで同じウェブストリームを使い、`content_group` を `hp` / `lp` に分ける。共通の `public/assets/analytics.js` をジェネレーターから全公開ページに読み込む。

- `line_click`：参加案内のLINEリンク。問い合わせは別イベント `line_contact_click`。
- `instagram_click`：Instagramへのリンク。
- `content_progress`：実際のスクロールで25/50/75/90%に到達したとき、各ページで各1回。
- `faq_open`：FAQを開いたときの番号。
- `button_position`：header / hero / menu / content / join / final / footer / mobile_fixed。
- ページURLは公開パスと安全なUTM値だけを送信。ハッシュやその他のクエリは除外。広告パーソナライズ・Googleシグナルは無効。
- 本番のHP・LP以外ではGoogleタグを読み込まない。LINEユーザーIDや会員データ、フォーム入力は解析対象にしない。
- プライバシーページの停止設定とGPCを尊重。停止時はタグの新規読み込みと独自イベント送信を行わない。

検証：`node --test qa/analytics-check.cjs`。LINEクリックは友だち追加完了・参加申込完了を意味しない。

認証手順の一次資料：https://developers.facebook.com/documentation/instagram-platform/instagram-api-with-instagram-login/business-login （2026-10-23にMeta公式画面で確認）。


## 日本語の改行（2026-10-23）

原因は文字単位の標準折り返し、画面幅に固定されたbr、FAQのflex収縮、タブレットで狭くなる3列表示。
通常の禁則処理と、語・文節をなるべく分断しない編集上の配慮は分けて扱う。

- Google BudouXで文節に近いまとまりを生成。幅に収まるまとまりは分割しない。
- まとまり自体が枠より長い場合、Intl.Segmenterと固有語辞書による単語境界で折り返す。
- 段落は維持し、日本語の固定brは任意の改行候補へ変更。コピー・読み上げの本文も維持する。
- 単語自体が枠より長い極端な条件だけ、はみ出しを防ぐ緊急折り返しを許す。
- 生成HTMLはJS不要。Instagramと写真ビューアの動的な説明にも同じ分節を使い、ブラウザへの解析ライブラリ追加や外部解析通信を行わない。
- 生成：python3 build_site.py。検証：node qa/japanese-wrap-check.mjs、python3 qa/check_site.py。画面幅別の測定はqa/typography-responsive.json。

一次資料：
[W3C 日本語組版処理の要件](https://www.w3.org/TR/jlreq/)、
[CSS Textの改行制御（草案）](https://www.w3.org/TR/css-text-4/#word-break-property)、
[Google BudouX](https://github.com/google/budoux)。
BudouXの区切りは推定で、全ての文で言語学的に完全な文節を保証するものではない。
