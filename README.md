# Itrat Rubab – Portfolio

Static portfolio site (HTML, CSS, vanilla JS, no build step) for GitHub Pages.

## Customize

1. **Projects** – edit `js/projects.js`. The five entries are placeholders; replace them with real projects and set `draft: false`.
2. **CV download** – put your PDF at `assets/Itrat_Rubab_CV.pdf` (create the `assets` folder).
3. **GitHub link** – in `index.html`, replace `YOUR-GITHUB-USERNAME`.
4. **Colors** – CSS variables at the top of `css/style.css`.

## Preview locally

```sh
python3 -m http.server 8000
# open http://localhost:8000
```

## Deploy to GitHub Pages

```sh
git init -b main
git add .
git commit -m "Initial portfolio"
# create an empty repo on GitHub first, e.g. <username>.github.io
git remote add origin https://github.com/<username>/<username>.github.io.git
git push -u origin main
```

- Repo named `<username>.github.io` → live at `https://<username>.github.io`.
- Any other repo name → in the repo go to **Settings → Pages**, choose **Deploy from a branch**, `main` / `(root)`. All paths here are relative, so it works either way.
