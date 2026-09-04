# Omino Stick: Hill Climb

Gioco HTML5 a file unico: un omino stick in bici su colline, stelle da raccogliere e rocce da evitare.

Gioca online: **[https://digitald.github.io/stickbike/](https://digitald.github.io/stickbike/)**

Come è fatto il programma (HTML, JS, ciclo di gioco, collisioni): **[elementi_di_programmazione.md](elementi_di_programmazione.md)**.

## Controlli

**Desktop:** `A` / `←` freno · `D` / `→` pedala · `W` / `↑` / Spazio salto · `Esc` pausa  
**Mobile:** Freno e salto a sinistra, gas a destra. Pulsante pausa in alto. In verticale si può giocare; in orizzontale si vede più strada.

A fine corsa vedi punteggio, km e record (salvati sul dispositivo). **Riprova** (su desktop anche Spazio o Invio).

Su telefono puoi aggiungere il gioco alla schermata Home (PWA).

## Avvio in locale

Apri `index.html` nel browser, oppure dalla cartella del progetto:

```bash
python -m http.server 8765
```

Poi vai su `http://127.0.0.1:8765/`.

## GitHub Pages

Il sito è pubblicato dalla branch `main`, cartella `/` (root del repo). Ogni push su `main` ricostruisce le pagine.

### Come controllare la pubblicazione

1. **Apri il gioco**  
   [https://digitald.github.io/stickbike/](https://digitald.github.io/stickbike/)  
   Se non vedi l’ultimo commit, aspetta 1–2 minuti e fai un refresh forzato (`Ctrl+F5`).

2. **Stato della build**  
   [Settings → Pages](https://github.com/digitald/stickbike/settings/pages)  
   Deve risultare *Your site is live* con source **Deploy from a branch** → `main` / `/ (root)`.

3. **Log della pubblicazione**  
   [Actions](https://github.com/digitald/stickbike/actions) → workflow *pages-build-deployment*.  
   L’ultimo run su `main` deve essere verde.

Da terminale:

```bash
gh api repos/digitald/stickbike/pages --jq "{status, html_url, source}"
```

`status` vale `built` quando il sito è online, `building` mentre GitHub sta pubblicando.
