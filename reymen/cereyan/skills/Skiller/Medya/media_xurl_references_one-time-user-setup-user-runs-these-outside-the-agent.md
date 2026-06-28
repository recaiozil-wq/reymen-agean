
> **Kategori:** Medya

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Media_Xurl_References_One Time User Setup User Runs These Outside The Agent |
| **Nerede?** | Medya/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## One-Time User Setup (user runs these outside the agent)

These steps must be performed by the user directly, NOT by the agent, because they involve pasting secrets. Direct the user to this block; do not execute it for them.

1. Create or open an app at https://developer.x.com/en/portal/dashboard
2. Set the redirect URI to `http://localhost:8080/callback`
3. Copy the app's Client ID and Client Secret
4. Register the app locally (user runs this):
   ```bash
   xurl auth apps add my-app --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET
   ```
5. Authenticate (specify `--app` to bind the token to your app):
   ```bash
   xurl auth oauth2 --app my-app
   ```
   (This opens a browser for the OAuth 2.0 PKCE flow.)

   If X returns a `UsernameNotFound` error or 403 on the post-OAuth `/2/users/me` lookup, pass your handle explicitly (xurl v1.1.0+):
   ```bash
   xurl auth oauth2 --app my-app YOUR_USERNAME
   ```
   This binds the token to your handle and skips the broken `/2/users/me` call.
6. Set the app as default so all commands use it:
   ```bash
   xurl auth default my-app
   ```
7. Verify:
   ```bash
   xurl auth status
   xurl whoami
   ```

After this, the agent can use any command below without further setup. OAuth 2.0 tokens auto-refresh.

> **Common pitfall:** If you omit `--app my-app` from `xurl auth oauth2`, the OAuth token is saved to the built-in `default` app profile — which has no client-id or client-secret. Commands will fail with auth errors even though the OAuth flow appeared to succeed. If you hit this, re-run `xurl auth oauth2 --app my-app` and `xurl auth default my-app`.

> **Docker HOME pitfall:** In the official Hermes Docker layout, `/opt/data` is `HERMES_HOME`, but Hermes tool subprocesses use `/opt/data/home` as `HOME`. That means `~/.xurl` resolves to `/opt/data/home/.xurl` for Hermes-run `xurl` commands, not `/opt/data/.xurl`. Run the user setup with the same HOME:
> ```bash
> HOME=/opt/data/home xurl auth apps add my-app --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET
> HOME=/opt/data/home xurl auth oauth2 --app my-app YOUR_USERNAME
> HOME=/opt/data/home xurl auth default my-app YOUR_USERNAME
> HOME=/opt/data/home xurl auth status
> ```
> If `HOME=/opt/data xurl auth status` succeeds but `HOME=/opt/data/home xurl auth status` shows no apps or tokens, Hermes tool calls will not see the credentials.

---