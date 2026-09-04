# Elementi di programmazione

Note didascaliche su *come è fatto* Omino Stick: Hill Climb. Non è il manuale completo del file `index.html`: è una mappa dei concetti, con qualche pezzo di codice vero e un po’ di pseudocodice.

Il gioco è un programma che gira **nel browser**. Il browser legge HTML (struttura), CSS (aspetto) e JavaScript (comportamento).

---

## Indice

1. [A cosa serve questo foglio](#1-a-cosa-serve-questo-foglio)
2. [Linguaggi usati](#2-linguaggi-usati)
3. [Tecniche usate](#3-tecniche-usate)
4. [Come si integrano HTML e JavaScript](#4-come-si-integrano-html-e-javascript)
5. [Struttura base del programma](#5-struttura-base-del-programma)
6. [Cosa demandiamo alle funzioni](#6-cosa-demandiamo-alle-funzioni)
7. [Esempio: il ciclo di gioco](#7-esempio-il-ciclo-di-gioco)
8. [Esempio: il terreno come funzione matematica](#8-esempio-il-terreno-come-funzione-matematica)
9. [Esempio: le collisioni](#9-esempio-le-collisioni)
10. [Esempio: lo stato del gioco](#10-esempio-lo-stato-del-gioco)
11. [Cosa questo foglio non copre](#11-cosa-questo-foglio-non-copre)

---

## 1. A cosa serve questo foglio

Un programma è un testo che una macchina esegue **in ordine**, secondo regole fisse.

Qui le regole importanti sono tre:

- **Separare i ruoli.** HTML dice *cosa c’è* (canvas, pulsanti). JavaScript dice *cosa succede* (muovere la bici, contare i punti).
- **Non fare tutto in un unico blocco.** Si spezza il lavoro in **funzioni**: ciascuna ha un nome, un compito, e può essere richiamata molte volte.
- **Ripetere il lavoro nel tempo.** Un gioco non “finisce” dopo una riga: ogni frazione di secondo si aggiorna il mondo e si ridisegna lo schermo.

---

## 2. Linguaggi usati

| Linguaggio | Ruolo in questo progetto |
| --- | --- |
| **HTML** | Pagina: titoli, canvas, overlay, pulsanti. |
| **CSS** | Posizione e aspetto (pulsanti a sinistra/destra, overlay, adattamento telefono/desktop). |
| **JavaScript** | Logica: fisica, input, collisioni, punteggio, audio, pausa, record. |
| **JSON** (nel `manifest.webmanifest`) | Scheda “app” per installare il gioco sul telefono. |

Non usiamo un motore di gioco esterno (Unity, Phaser, Matter.js). La grafica è **Canvas 2D**: un rettangolo di pixel su cui JavaScript disegna linee e forme.

---

## 3. Tecniche usate

Elenco breve, con il significato rigoroso.

**Ciclo di gioco (game loop).** Una funzione `loop` si auto-richiama con `requestAnimationFrame`. È il metronomo: *aggiorna → collisioni → disegna → ripeti*.

**Delta time.** Il tempo tra un fotogramma e il successivo non è costante (60 Hz, 120 Hz, lag). Si calcola un fattore `dt` e si moltiplicano velocità e gravità per `dt`, così il gioco non corre il doppio su uno schermo più veloce.

**Mondo e schermo.** La bici resta circa ferma in X sullo schermo; è il **mondo** (`worldXpos`) che scorre. Un oggetto ha una coordinata mondiale; sullo schermo vale:

```text
screenX = worldX - worldXpos
```

**Stato a macchina finita.** La variabile `gameState` vale solo uno tra: `start`, `playing`, `paused`, `gameover`. Le azioni permesse dipendono dallo stato (in pausa non si pedala).

**Eventi.** Tastiera e dita non si “leggono in continuo” da sole: il browser **notifica** il programma (`keydown`, `pointerdown`). Noi registriamo ascoltatori (`addEventListener`).

**Funzioni matematiche per il paesaggio.** Le colline non sono un elenco di punti salvato su disco: l’altezza del suolo in un punto `x` è una somma di seni.

**Test geometrici per le collisioni.** Non c’è un motore fisico da laboratorio. Si misura una distanza o una sovrapposizione di rettangoli/cerchi (vedi [§9](#9-esempio-le-collisioni)).

**Persistenza locale.** Il record sta in `localStorage`: una piccola memoria del browser, non un server.

---

## 4. Come si integrano HTML e JavaScript

Tre modi, tutti usati qui.

### 4.1 Il JS vive nella stessa pagina

In fondo a `index.html` c’è:

```html
<canvas id="gameCanvas" width="1280" height="720"></canvas>
<button type="button" id="btnLeft">…</button>

<script>
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    // … resto del programma
</script>
```

`getElementById` è il **ponte**: dal nome HTML si ottiene un oggetto JavaScript su cui chiamare metodi (`getContext`, `addEventListener`).

### 4.2 Il CSS decide il layout; il JS decide se mostrarlo

I pulsanti touch sono nell’HTML sempre. Il CSS li nasconde sul desktop:

```css
.mobile-controls { display: none; }
body.is-touch .mobile-controls { display: block; }
```

JavaScript aggiunge o toglie la classe `is-touch` sul `body` dopo aver chiesto al browser se il puntatore è “grosso” (dito) o “fine” (mouse).

### 4.3 Disegno: due strati

- **DOM** (HTML): overlay “Fine corsa”, pulsante Riprova, pausa.
- **Canvas**: cielo, colline, bici, stelle, HUD punti/km.

Il canvas è un elemento HTML; *dentro* si disegna solo con `ctx.lineTo`, `ctx.arc`, `ctx.fillText`. Non si usano i tag `<img>` per la bici: è geometria calcolata.

---

## 5. Struttura base del programma

Ordine di lettura (e, all’avvio, di esecuzione):

```text
1. Il browser costruisce il DOM (HTML + CSS).
2. Parte lo <script>.
3. Si prendono i riferimenti (canvas, pulsanti, overlay).
4. Si definiscono le funzioni (ancora non girano, sono solo “ricette”).
5. Si collegano gli eventi (tastiera, tocco, resize).
6. resize() adatta il canvas alla finestra.
7. initWorld() crea nubi e montagne.
8. loop() parte e non si ferma più.
```

Durante il gioco, ogni fotogramma fa solo questo:

```text
loop:
    calcola dt
    update(dt)         // fisica, spawn, km
    collideObjects()   // stelle e rocce
    draw()             // ridisegna tutto
    chiedi il prossimo fotogramma
```

**Variabili globali del modulo** (nello script, visibili a tutte le funzioni di quel file): `player`, `gameObjects`, `score`, `lives`, `worldXpos`, `gameState`. Non è l’unica architettura possibile; in un programma piccolo è onesta e leggibile.

---

## 6. Cosa demandiamo alle funzioni

Una funzione è un pezzo di programma con:

- un **nome** (cosa fa, non come);
- eventuali **parametri** (dati in ingresso);
- un **corpo** (istruzioni);
- a volte un **valore di ritorno**.

Qui il criterio è: *una responsabilità per funzione*.

| Funzione | Compito che le affidiamo | Cosa *non* deve fare |
| --- | --- | --- |
| `update` | Muovere bici e mondo, spawn oggetti | Disegnare |
| `draw` | Disegnare il fotogramma | Cambiare `score` |
| `collideObjects` | Decidere se bici e oggetti si toccano | Calcolare la gravità |
| `getTerrainHeight` | Dire quanto è alto il suolo in un `x` | Sapere dove sta il giocatore |
| `handleCrash` | Vite, invincibilità, fine corsa | Testare la geometria della roccia |
| `resetGame` | Azzera una partita nuova | Salvare il record (lo fa `commitRecord` a fine corsa) |
| `pauseGame` / `resumeGame` | Cambiare stato senza distruggere il mondo | |

Se mescolassimo disegno e fisica nella stessa funzione, sarebbe più difficile correggere un bug: non si saprebbe se il problema è “si vede storto” o “si muove storto”.

---

## 7. Esempio: il ciclo di gioco

Codice reale (semplificato nei commenti):

```javascript
function loop(now) {
    if (!lastTime) lastTime = now;
    let dt = (now - lastTime) / (1000 / 60); // 1 = un sessantesimo di secondo
    lastTime = now;
    if (dt > 3) dt = 3; // se il PC si è fermato, non fare un salto enorme

    update(dt);
    collideObjects();
    draw();
    requestAnimationFrame(loop);
}
```

**Pseudocodice** della fisica, dentro `update`, quando `gameState` è `playing`:

```text
pendenza ← angolo tra suolo(x) e suolo(x + un po’)
velocità ← velocità + componente della gravità lungo la pendenza × dt

se tasto gas    allora velocità ← velocità + pedale × dt
se tasto freno  allora velocità ← velocità − freno × dt
se tasto salto e sono a terra allora vy ← potenza_salto

vy ← vy + gravità × dt
y  ← y + vy × dt

se y ≥ suolo(x) allora appoggia la bici, vy ← 0, a_terra ← vero

worldXpos ← worldXpos + velocità × dt
```

`dt` è adimensionale rispetto a “un frame a 60 fps”: a 60 Hz vale circa `1`, a 120 Hz circa `0,5`.

---

## 8. Esempio: il terreno come funzione matematica

Non memorizziamo migliaia di altezze. Definiamo una funzione:

\[
h(x) = h_0 + A_1\sin(k_1 x) + A_2\sin(k_2 x) + A_3\sin(k_3 x)
\]

Nel codice:

```javascript
function getTerrainHeight(worldX) {
    const base = WORLD_H * 0.72;
    const h1 = Math.sin(worldX * 0.0024) * (WORLD_H * 0.16);
    const h2 = Math.sin(worldX * 0.0075) * (WORLD_H * 0.04);
    const h3 = Math.sin(worldX * 0.019) * 6;
    return base + h1 + h2 + h3;
}
```

Stesso `x` ⇒ stessa altezza, sempre. Per questo si può chiedere il suolo sotto la bici e, tre pixel più avanti, calcolare la **pendenza** con `atan2`.

Per **disegnare** la collina si campiona la funzione a passi:

```text
per x da -60 a larghezza+60 a passo 8:
    y ← getTerrainHeight(worldXpos + x)
    traccia una linea fino a (x, y)
riempi sotto la linea con il colore dell’erba
```

---

## 9. Esempio: le collisioni

### 9.1 Idea

Due oggetti “si toccano” se una misura geometrica scende sotto una soglia. Non simuliamo il contatto ruota-sasso atomo per atomo.

Prima si porta l’oggetto nello **spazio schermo** (`screenX = obj.worldX - worldXpos`), dove sta anche `player.x`.

### 9.2 Roccia: rettangolo (soglia su X e su Y)

La roccia è larga circa 40 px e sta sul suolo. Si considera un colpo se:

1. la bici è abbastanza vicina in orizzontale al centro della roccia, **e**
2. la bici non è abbastanza in alto da passarci sopra (salto).

```javascript
const hit = Math.abs(player.x - screenX - 22) < 26
         && player.y > groundY - 28;
```

In pseudocodice:

```text
se |x_bici − x_roccia| < metà_larghezze
   e  y_bici è sotto (suolo − margine_salto)
allora C’È COLLISIONE
```

Poi si interpreta il colpo:

```text
se cooldown_roccia > 0     → ignora (evita dieci collisioni nello stesso istante)
se |velocità| > soglia     → handleCrash()   // toglie una vita o fine corsa
altrimenti                 → rimbalzo: inverti e riduci la velocità
```

Il **cooldown** è un timer: dopo un urto si aspetta qualche fotogramma prima di ricalcolare. Senza di esso, nello stesso overlap, `hit` sarebbe vero *ogni frame* e la velocità oscillerebbe.

### 9.3 Stella: distanza euclidea (cerchio)

La stella è un punto `(screenX, starY)`. Si usa la distanza dal “petto” della bici `(player.x, player.y - 22)`:

\[
d = \sqrt{(x_1-x_2)^2 + (y_1-y_2)^2}
\]

```javascript
const dist = Math.hypot(player.x - screenX, (player.y - 22) - starY);
if (dist < 42) {
    obj.taken = true;
    score += obj.val;
}
```

`Math.hypot(a, b)` è esattamente \(\sqrt{a^2+b^2}\), scritto in modo stabile.

Se `d` è minore del raggio `42`, la stella è **presa**. Il flag `taken` impedisce di riassegnare i punti ogni frame.

### 9.4 Schema a blocchi

```text
per ogni oggetto ancora nel mondo:
    se è fuori dallo schermo → salta
    se è una roccia e hit e cooldown a zero:
        se troppo veloce → crash
        senno → rimbalzo
    se è una stella non ancora taken e d < raggio:
        taken ← vero
        score ← score + valore
```

---

## 10. Esempio: lo stato del gioco

```text
        ┌─────────┐  Spazio / tocco   ┌──────────┐
        │  start  │ ───────────────► │ playing  │
        └─────────┘                   └────┬─────┘
                                           │
                          Esc / ⏸          │  vite = 0
                              ▼            ▼
                        ┌─────────┐   ┌──────────┐
                        │ paused  │   │ gameover │
                        └────┬────┘   └────┬─────┘
                             │ Riprendi     │ Riprova
                             └──────► playing
```

In codice, un solo valore:

```javascript
let gameState = 'start'; // start | playing | paused | gameover
```

Molte funzioni **escono subito** se lo stato non è quello giusto:

```javascript
function collideObjects() {
    if (gameState !== 'playing') return;
    // …
}
```

Così in pausa le stelle non si raccolgono da sole e il mondo non avanza (`update` fa lo stesso controllo).

---

## 11. Cosa questo foglio non copre

Volutamente assenti, per non copiare tutto `index.html`:

- il disegno della bici a linee (`drawPlayer`);
- l’audio Web Audio (vento, jingle Re♯–Do);
- il ridimensionamento del canvas e il `devicePixelRatio`;
- il service worker e la PWA;
- il salvataggio del record in `localStorage`.

Quei pezzi seguono le stesse idee: **funzioni con un compito**, **stato**, **eventi**. Si possono leggere nel sorgente partendo dai nomi.

Per giocare e pubblicare: [README.md](README.md).
