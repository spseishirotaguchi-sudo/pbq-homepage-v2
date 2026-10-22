declare namespace Cloudflare {
  interface Env {
    DB?: D1Database;
    BUCKET?: R2Bucket;
    INSTAGRAM_TOKEN_KEY?: string;
    INSTAGRAM_OWNER_EMAIL?: string;
  }
}
