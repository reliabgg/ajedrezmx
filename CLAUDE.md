# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Single-file vanilla chess application (`index.html`). No build system, no dependencies, no package manager. Open directly in a browser (`file://`) or serve via `python3 -m http.server`. The full documentation for end users lives in `MEJORAS.md` (also rendered inside the app's "Acerca de" modal).

## Architecture

Everything lives in `index.html` in four inline sections:

**CSS (`<style>`)** — uses a single CSS custom property `--sq` (`min(calc((100vw - 56px) / 8), 60px)`) to drive all board dimensions responsively. Layout is a horizontal flex (`main-area`) with three columns: thermometer · board · right panel. A `@media (max-width: 700px)` block reorders them vertically, switches the thermometer from vertical to horizontal, and applies mobile-specific tweaks (compact modal h2, tighter games-table, smaller LAN textareas). Safe-area-inset for iOS notch/home-indicator applied to `body` and `.toast`.

**HTML** — static shell. The board (`#board`) is populated entirely by JavaScript. Notable elements: `#thermo-fill` (thermometer), `#lan-banner` (LAN connection state), `#history-modal`, `#promo-overlay`, `#about-modal`, `#lan-modal` (wizard), `#settings-modal`, `#games-modal`, `#time-control-modal`.

**Embedded markdown (`<script type="text/markdown" id="mejoras-md-source">`)** — the entire `MEJORAS.md` is embedded inline before the main script. The "Acerca de" modal reads its `textContent` and renders it via the inline markdown parser. This duplication keeps `file://` working without `fetch()` — any edit to `MEJORAS.md` must be mirrored in this block (re-run the Python embed in `task_44` closure if regenerating).

**JavaScript** — all game logic in a single `<script>` block, organized by comment sections:

| Section | Key exports |
|---|---|
| `CHESS ENGINE` | `getPseudoMoves`, `getLegalMoves`, `applyMove`, `isInCheck`, `findKing`, `pieceColor`, `pieceType` |
| `FEN ENCODE/DECODE` | `boardToFen`, `fenToBoard`, `squareToAlgebraic`, `algebraicToSquare`, `positionKey` |
| `EVALUATION` | `evaluate(b, opts?)` — material + PST + pawn structure + king safety + mobility (opt-in) |
| `MINIMAX` | `minimax` (alpha-beta with `pliesFromRoot` for mate encoding), `getBestMove → {move, score}` |
| `ALGEBRAIC NOTATION` | `toAlgebraic` |
| `CP → DISPLAY` | `cpToPct(cp)` (sigmoid), `cpToLabel(cp)` (typographic minus, `M{n}` for mates) |
| `EVAL BAR` | `updateEvalBar` — applies ±10pp/move smoothing; bypasses for mate-in-N |
| `RENDERING` | `renderBoard` (full DOM rebuild), `renderHintArrow` |
| `DRAG & DROP` | `attachDragHandlers` — pointer events (touch+mouse unified) with 5px threshold |
| `UNDO STACK` | `pushSnapshot`, `undoMove`, `updateUndoButton` |
| `GAME LOGIC` | `onSquareClick`, `executeMove`, `checkGameState`, `doAIMove`, `canInputOnCurrentTurn` |
| `PROMOTION` | `showPromotion`, promotion overlay handlers |
| `HISTORY` | `openHistory`, `closeHistory` |
| `REINICIO` | `confirmNewGame`, `executeRestart` |
| `RENDICIÓN` | `confirmResign`, `executeResign` (LAN: sends `{type:'resign'}`) |
| `TABLAS POR ACUERDO` | `offerDraw`, `acceptDraw`, `rejectDraw`, `applyDrawAgreed`, `claimDraw50`, `claimDraw3rep`, `showToast` |
| `ACERCA DE` | `aboutEscapeHtml`, `aboutSlugify`, `aboutInline`, `aboutParseMarkdown`, `aboutBuildTOC`, `aboutScrollTo`, `openAbout` (renders embedded MEJORAS.md) |
| `CONTROLS` | `setMode`, `setDifficulty`, `setPlayerColor`, `newGame` |
| `MULTIJUGADOR LAN (wizard)` | `openLAN`, `lanPickRole`, `lanHostStartOffer`, `lanGuestProcessOffer`, `lanHostConnect`, `lanHostRetry`, `lanSetupDC`, `lanSend`, `lanDispatch`, 7 message handlers (`lanHandleHello/Move/Resign/DrawOffer/DrawResponse/Chat/Sync`), `lanFinalizeConnection`, `lanOnConnectionLost`, `lanReconnect`, `lanSetBanner`, `lanParseUciToMove`, `lanSendMyMove` |
| `RELOJ` | `formatClock`, `tickClock`, `startClockInterval`, `stopClockInterval`, `renderClocks`, `flagFall`, `cannotMate`, `clocksEnabled` |
| `CONTROL DE TIEMPO (selector)` | `openTimeControl`, `applyCustomTimeControl`, `updateTimeControlButton` |
| `PERSISTENCIA (IndexedDB)` | `openDB`, `saveGame`, `getAllGames`, `getGame`, `deleteGame`, `listProfiles`, `getProfile`, `createProfile`, `updateProfile`, `deleteProfile`, `hashPin`, `verifyPin`, `isCryptoSubtleAvailable`, `autoSaveGame`, `manualSaveGame`, `buildGameRecord`, `gameToPgn`, `moveToUCI`, `renderGamesTable`, `exportCurrentGamePGN`, `exportGamePGN` |
| `PERFILES (sesión local)` | `profileShowOverlay`, `profileShowPick`, `profileShowCreate`, `profileShowPin`, `profileSelectByClick`, `profileCreateSubmit`, `profilePinSubmit`, `profileSetCurrent`, `profileSignOut`, `profileRestore`, `profileUpdateButtonLabel`, `openProfileMenu`, `profileMenuSwitch`, `profileMenuEdit`, `profileMenuDelete`, `profileEditSubmit`, `profileDeleteConfirm` |
| `PGN IMPORT (parser tolerante)` | `triggerPgnImport`, `handlePgnImport`, `parsePgn`, `parsePgnHeaders`, `parsePgnMoves` |
| `VISOR DE ESTUDIO (replay)` | `viewGame`, `exitReplay`, `replayFirst/Prev/Next/Last`, `renderReplayList`, `renderReplayChart` |
| `SONIDOS (WebAudio)` | `ensureAudio`, `playSound` — 6 types (move/capture/check/castle/promote/gameEnd), lazy-init |
| `SETTINGS` | `loadSettings`, `saveSettings`, `updateSetting`, `openSettings`, `refreshSettingsPanel` — single `chess_settings` JSON in `localStorage` |
| `INIT` | DOM ready handler, default `newGame()`, settings load, keyboard handlers |

**Global state variables** (top of script, grouped by domain):

- Board & turn: `board` (8×8), `turn`, `selected`, `validMoves`, `gameMode` (1=vs IA, 2=hot-seat, 3=LAN), `playerColor`, `aiDepth`, `moveHistory`, `capturedByWhite/Black`, `lastMove`, `enPassantTarget`, `castlingRights`, `gameOver`, `promotionCallback`, `currentResult`, `gameStartTime`.
- FIDE rules: `halfmoveClock`, `fullmoveNumber`, `positionCounts` (Map keyed by FEN-truncated key), `drawOfferPending`.
- UX state: `toastTimeout`, `displayPct` (smoothed eval bar), `dragState`, `stateStack` (undo, cap 100), `hintArrow`, `currentPieceSet`.
- Clock: `selectedTimeControl`, `clockWhiteMs`, `clockBlackMs`, `clockActive`, `clockLastTickAt`, `clockIntervalId`.
- LAN: `lanWizardState`, `lanPC`, `lanDC`, `lanConnected`, `lanLocalColor`, `lanPeerName`, `lanReceivingMove`, `LAN_PROTOCOL_VERSION` (const), `LAN_ICE_TIMEOUT_MS` (const).
- Perfiles: `currentProfile` ({id, name, pinHash?, isGuest?} | null), `_pinAttempts` (per-id lockout state), `PROFILE_LS_KEY`, `PIN_MAX_ATTEMPTS`, `PIN_LOCKOUT_MS` (consts).
- About modal: `_aboutRendered` (cache flag for the markdown parse).

## Key conventions

- **Board coordinates**: `board[row][col]` where `row=0` is rank 8 (black's back rank), `row=7` is rank 1 (white's back rank).
- **Pieces** are encoded as 2-char strings: `'w'|'b'` + `'K'|'Q'|'R'|'B'|'N'|'P'` (e.g. `'wK'`, `'bP'`).
- **Move objects**: `{from: [r,c], to: [r,c], special?: 'double'|'ep'|'castleK'|'castleQ'|'promo'}`.
- **`renderBoard()`** does a full DOM rebuild — no incremental patching. Bounded at ~80 iterations (64 squares + 8 rank + 8 file labels). NOT called on `pointermove` (drag moves a floating overlay via direct `style` assignment).
- **`canInputOnCurrentTurn()`** is the single source of truth for "can the user act this turn?". Used by `onSquareClick`, `attachDragHandlers`, `showHint`, `updateHintButton`. Returns true for hot-seat (mode 2), checks `turn === playerColor` for vs IA (mode 1), and `turn` color === `lanLocalColor` for LAN (mode 3).
- **AI difficulty** maps directly to Minimax depth: Easy=2, Medium=3, Hard=4. `getBestMove` returns `{move, score}` where score encodes mate as `±(100000 - pliesFromRoot)` (independent of depth).
- **`evaluate(b, opts?)`** is in centipawns from White's perspective. `opts.mobility` opt-in (extra cost = 2× `getLegalMoves`); off by default to keep minimax fast. Used WITH mobility only by eval bar and AI draw-decision.
- **CSS custom properties** drive theming (`--bg`, `--fg`, `--accent`, `--sq-light`, `--sq-dark`, etc.). Light/dark via `body.light-mode`. Board theme via `body.board-theme-{clasico|madera|cristal|medianoche}`. Piece set via `currentPieceSet` (`'unicode'|'cburnett'|'merida'`).
- **`window.innerWidth <= 700`** branch is checked at runtime in `updateEvalBar` for vertical-vs-horizontal fill logic.
- **Settings** are persisted as a single `localStorage.chess_settings` JSON; `loadSettings` migrates from legacy keys (`chess_theme_mode`, `chess_board_theme`, `chess_piece_set`) automatically.
- **WebAudio**: `AudioContext` is **lazy-initialized** on the first `playSound` call (Chrome autoplay policy). `ensureAudio()` also calls `ctx.resume()` if state is `'suspended'` (iOS Safari).
- **`navigator.clipboard`** every call site is guarded (`if (!navigator.clipboard) return;`) and wrapped in `try/catch`. Required because Chrome/Safari block the Clipboard API over raw `http://192.168.x.x` (only HTTPS or localhost allowed).
- **`RTCPeerConnection`** is guarded by `typeof RTCPeerConnection === 'undefined'` before construction. LAN uses `iceServers: []` (no STUN — guarantees zero-internet but only works in same LAN; no NAT traversal).
- **LAN connection has two modes.** *Automatic* (preferred): `chess-lan-server.py` (stdlib-only) serves the app AND provides WebRTC signaling over HTTP (`/lan/ping`, `POST/GET /lan/offer`, `POST/GET /lan/answer`; in-memory rooms, 10-min TTL). On `openLAN`, the app `GET /lan/ping`; if ok it shows "Crear sala / Unirse a sala" (host gets a 4-digit room code, guest types it) and auto-exchanges SDP via `lanCreateOffer`/`lanCreateAnswer` + `lanPollForAnswer`. *Manual* (fallback for `file://` or plain `http.server`): the original copy-paste SDP wizard. Both reuse the same WebRTC data channel + 7-message protocol — moves are always DTLS-encrypted P2P; the server only relays the SDP handshake. Run for LAN play with `python3 chess-lan-server.py` (binds `0.0.0.0:8000`; use `--host 127.0.0.1` for tunnel-only).
- **LAN protocol** (7 JSON message types: `hello/move/resign/draw_offer/draw_response/chat/sync`) is fully documented in `MEJORAS.md` "Apéndice". Every incoming `move` must pass through `getLegalMoves` before applying — peer is treated as untrusted even on LAN. Unknown `type` is ignored silently (forward-compat); JSON parse error or missing `type` closes the channel.
- **`lanReceivingMove` flag** in `executeMove` suppresses the move-send hook when applying a remote move (prevents infinite ping-pong).
- **Modal cleanup respects `lanConnected`**: `closeLANBtn` only calls `lanCleanupConnection()` if NOT connected — protects the active LAN session when the user just closes the modal after connecting.
- **`MEJORAS.md` is duplicated** between the on-disk file and the embedded `<script type="text/markdown">` block. Edits must be mirrored in both, or re-run the embed step (see `task_44` closure for the Python snippet).
- **Profile session required to play.** `profileRestore()` runs at INIT; if no profile found in `localStorage.chess_current_profile_id`, a full-screen overlay forces sign-in. PIN-protected profiles re-prompt on every load (no persistent session). `saveCurrentGame` bails silently when `currentProfile == null`. `getAllGames(profileId?)` defaults to filtering by `currentProfile.id` and returns `[]` if no profile is active.
- **IndexedDB schema v2.** Two stores: `games` (existing) and `profiles` (new). Migration v1→v2 auto-creates a profile named "Invitado" and assigns all legacy games to it. `games.profileId` index added at migration time. Bumping the schema again means adding a v3 branch in `openDB.onupgradeneeded`.
- **PIN hashing via Web Crypto SHA-256.** `crypto.subtle.digest` requires secure context (HTTPS, localhost, `file://`). On raw `http://192.168.x.x`, `isCryptoSubtleAvailable()` returns false → PIN creation is rejected with a friendly message; PIN verification is also rejected (denies sign-in). The 3-attempts → 30s lockout state lives in-memory only (`_pinAttempts`), so it resets across page reloads.

## Development workflow

- **No build, no install**. Edit `index.html` directly; refresh the browser.
- **Smoke testing**: serve with `python3 -m http.server 8000` and use `http://localhost:8000` to enable the full Clipboard API (necessary for the LAN wizard's copy/paste buttons in development).
- **Syntax check**: extract the main `<script>` content (NOT the `type="text/markdown"` one) and run `node --check`. Example:
  ```bash
  node -e "
    const fs=require('fs');
    const html=fs.readFileSync('index.html','utf8');
    const idx=html.indexOf('</script>\n\n<script>');
    const start=idx+'</script>\n\n<script>'.length;
    const end=html.indexOf('</script>', start);
    fs.writeFileSync('/tmp/chess.js', html.slice(start, end));
  " && node --check /tmp/chess.js
  ```
- **Programmatic tests** for individual features have historically been written to `/tmp/{feature}_test.js` and run with `node`. They use a minimal DOM mock and the `with(env)` pattern (newer tests) or factory args (older tests) to extract a function section and run it in isolation. See the `closure.get` output for `task_38`-`task_44` for examples.
- **Plan / task tracking** lives in `.ipman/ipman.db` (managed via the `ipman` CLI). `ipman -S` for status, `ipman -L` for pending tasks, `ipman -R P1` to render the full plan as markdown.
- **`MEJORAS.md` is the user-facing source of truth.** When adding a new feature, update both `MEJORAS.md` (section 1 entry + decision in section 2 if non-obvious) and the embed in `index.html`. Re-run the markdown audit test (`/tmp/mejoras_md_test.js`) to catch missing entries.

## Idioma

Communication with the user is in Spanish (Mexican), technical-register dial at 40% (see auto-memory `feedback_language_register.md`). Code identifiers, comments, and commit messages stay in English where the existing convention is English, Spanish where existing is Spanish (mixed by section in this codebase).
