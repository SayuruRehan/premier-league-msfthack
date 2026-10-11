# MatchShift judge-ready deployment — no paid AI required

This guide publishes a **synthetic, precomputed** MatchShift demo. The asset export uses real Microsoft Agent Framework orchestration and grounded verification before deployment, but **browser visitors do not run live agents**. No Azure AI or other usage-billed service is needed for this version.

## 1. Preferred: Azure Static Web Apps Free

1. Open [Azure Portal](https://portal.azure.com/) and choose **Create a resource** → **Static Web Apps**.
2. Select a subscription, a resource group, a unique name (e.g. `matchshift-ai`) and the **Free** hosting plan. Avoid upgrading to Standard, enabling other billable services, or provisioning Azure OpenAI/Foundry endpoints.
3. Choose **Other** (manual deployment) as the source, rather than letting Azure generate a conflicting workflow in your repository. Finish creating the app.
4. In your new Static Web App, open **Manage deployment token** (or the equivalent deployment token page) and copy the token.
5. In GitHub repo `SayuruRehan/premier-league-msfthack` open **Settings → Secrets and variables → Actions → New repository secret**.
6. Name it **`AZURE_STATIC_WEB_APPS_API_TOKEN`** and paste the token. Do not commit or share the token.
7. Merge the deployment PR to `master` or open **Actions → Deploy judge demo to Azure Static Web Apps → Run workflow**.
8. Review the workflow result: the Azure deploy step must show **success**, not **skipped**. Find your app's assigned `*.azurestaticapps.net` URL in the Azure portal.
9. Open the URL in a private browser window. Click a highlight and switch all three audiences; the app must load without any signed-in account.

**Important:** A successful *build* is not confirmation that Azure publishing happened. When the secret is missing, publishing is deliberately skipped and the workflow only validates the bundle.

The deploy action receives the already-built `apps/web/dist` directory using `skip_app_build: true`. It must include `staticwebapp.config.json` and `data/{replay,stories}.json`.

## 2. Secondary free option: GitHub Pages

Use GitHub Pages if an Azure subscription is unavailable. GitHub Pages is free for public repositories but does not demonstrate Azure hosting.

1. In the repository, open **Settings → Pages**.
2. In **Build and deployment**, select **GitHub Actions** as the source. This permission/settings step must be done once by the repository administrator.
3. After merging to `master`, open **Actions → Deploy free GitHub Pages fallback → Run workflow**, if not already triggered.
4. Confirm the deployment job succeeds. Get the published URL from the **github-pages** environment or Settings → Pages; it will generally have a project subpath.
5. Run the same private-window acceptance checks as for Azure. The Vite build uses a relative base for this reason.

If the deployment job fails with "Pages site not found," enable Pages in the settings above and rerun. Do not claim a link is live until a published site responds correctly.

## 3. Offline preview / self-hosted static test

From repo root:

```sh
python -m pip install -r services/api/requirements.txt
python -m scripts.export_static --output apps/web/public/data
python -m scripts.export_static --output apps/web/public/data --verify-only
cd apps/web
npm install
VITE_STATIC_DEMO=true npm run build
npm run preview
```

The preview should load replay and agent results entirely from built JSON, without requiring `uvicorn` or Foundry Local. `VITE_STATIC_DEMO` is a **build-time** switch, not a runtime server environment variable.

## 4. Judge acceptance checklist

- [ ] Public URL returns HTTP 200 without authentication, paid account or an API service.
- [ ] Pitch, scoreboard, cue markers, and broadcast lower thirds render.
- [ ] Clicking every cue advances playback to the correct moment.
- [ ] Fan, analyst and broadcast personas load their corresponding precomputed verified stories.
- [ ] No `/api/*` or external model requests occur when browsing the public static build.
- [ ] The UI says **public offline demo / precomputed**, not live model inference.
- [ ] Source evidence can be clicked through and always references synthetic events in the replay.
- [ ] Static asset responses load successfully on a project subpath (GitHub Pages).
- [ ] Site and README avoid unlicensed footage, league crests, trademarks or official live feeds.
- [ ] GitHub `master` build and Pages/Azure publishing are green; save proof/screenshots for the submission.
- [ ] Demo video is **less than two minutes**, public, and shows the product working.

## What remains genuinely live?

Run FastAPI and the React dev server locally for interactive Microsoft Agent Framework execution on each story request. To use a local Phi model, see `docs/agents.md`; verify that environment separately. The judge-hosted static site shows saved outputs of the **real deterministic** framework runs. It does not claim that inference was executed at viewer request time.

## Automated release verification (post-deployment gate)

After the Azure upload completes, the workflow calls `python -m scripts.check_public_site` against the **public HTTPS production domain**, retrying briefly to account for Azure CDN propagation.

The smoke checker downloads `/`, `/data/replay.json` and `/data/stories.json` without authentication. It verifies all cues, model provenance, all persona stories, and complete real Microsoft Agent Framework stage traces. A broken live deployment now causes the **deployment workflow to fail** instead of leaving a misleading green check.

The regular `CI` workflow also runs Playwright Chromium scenarios against the *locally served, compiled static artifact*, in desktop and mobile viewports. The tests cover match cues, evidence drilldown, persona modes, and player controls, and ensure the static build makes no backend/AI calls. On browser failure, Actions retains screenshots and traces as a downloadable artifact.

If Azure's URL ever changes, update `MATCHSHIFT_PUBLIC_URL` in `.github/workflows/deploy-azure-static.yml` before deploying the next version. The URL is public; **never** put the deployment token into the smoke command.
