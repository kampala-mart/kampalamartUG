# Kampala Mart v8 - EVERYTHING fixed in one build

## What v8 fixes
1. FREE/PAID that sticks: feeMode now SAVES to cloud + localStorage and cloud load APPLIES settings. Other browsers see FREE -> Sell shows "Upload Product". PAID -> "Continue to Listing Fee".
2. Owner notifications: v8 polls cloud every 5s. Owner Panel open + pending approvals increase -> red pill + bell badge + (N) in tab title. New live product -> alert. New chat -> alert. Chats now saved to cloud, message icon count follows you.
3. No refresh needed: v8 polls cloud; when it changes and you are idle it shows "New changes - refreshing..." and reloads. Owner changes reach every browser/app within seconds.
4. Refresh shows products immediately: a "Loading your shop..." cover hides the empty flash until products render.
5. Install App button bottom-left on ALL devices (old code hid it above 900px, so laptops never saw it). Android: menu > Add to Home screen. iPhone: Share > Add to Home Screen. Laptop Chrome: menu > Install.
6. Login that works: users are now saved to the cloud. Register once -> session saved in your browser (km_session) -> refresh keeps you logged in, straight to buying/selling. Other browser: login with the SAME phone + password -> works. Wrong phone/password -> "Phone or password did not match" (denied). Logout clears the session.
7. Listing fees collected: payments list now saved to cloud. Owner Panel shows the total on ANY phone/browser, even with no account. Only the owner can delete (Payments tab). It survives refresh, other browsers, and redeploys (Postgres).
8. Undo: every cloud save snapshots the previous shop. Owner Panel gets "Undo last change" (next to Save) - restores the previous shop. Everyone then sees the undo live.
9. Broadcasts + OneSignal: Owner Panel > Notifications gets "Send notification to ALL users" - everyone sees it in-app instantly + browser notification if allowed. OneSignal push was already in the site with your App ID - the allow-notifications banner now asks once a day. To push to phones that have the app CLOSED, also send the same message from your OneSignal dashboard (needs your OneSignal login - the site cannot send phone push by itself without your REST API key).

## Upload (ONCE)
1. GitHub: delete ALL files, extract this zip ONCE into an EMPTY folder, upload all files. No _1 files.
2. Render > kampala-mart > Manual Deploy > Deploy latest commit > wait Live.
3. HARD REFRESH: Ctrl+Shift+R (phone: clear site data).
4. DO NOT touch Environment Variables - DATABASE_URL stays as is.

## Test checklist
- Owner Panel > Payments Settings > FREE > Save. Other browser: Sell = "Upload Product". Submit -> goes live, owner gets "New product live" alert without refresh.
- Register on phone, refresh -> still logged in. Other browser: login same phone+password -> in. Wrong password -> denied.
- Owner Panel > Notifications > send broadcast -> other browser sees it in seconds.
- Owner Panel > Overview shows Listing fees collected on another phone.
- Change something, tap Undo last change -> it reverts everywhere.
