# AjedrezMX — Mejoras y documentación

Documento de referencia para usuarios y desarrolladores. Se actualiza incrementalmente conforme se completa cada fase del plan.

---

## 1. Mejoras implementadas respecto al prompt original

> Esta sección lista cada feature nueva añadida sobre el `index.html` base. Se va llenando fase por fase.

- _(Fase 0)_ Generador/parser de FEN estándar (`boardToFen`, `fenToBoard`), con 6 tests de round-trip pasando. Habilita persistencia y triple repetición de fases posteriores.
- _(Fase 1)_ Halfmove clock + regla de los 50 movimientos: `halfmoveClock` y `fullmoveNumber` en el estado global, reset en captura o avance de peón, botón "Reclamar tablas (50 mov)" visible al llegar a 100, auto-tablas a 150 (FIDE 75-mov). Display del contador en el panel derecho.
- _(Fase 1)_ Triple repetición: `positionCounts: Map<string,int>` keyed por FEN truncado (board+turn+castling+ep). Botón "Reclamar tablas (3 rep)" al llegar a 3 ocurrencias; auto-tablas a 5 (FIDE 9.6.2). Display "Repeticiones: N" en panel derecho. Test programático verificado con secuencia shuffle Nf3-Nf6-Ng1-Ng8.
- _(Fase 1)_ Material insuficiente: `isInsufficientMaterial(board)` detecta los 4 casos canónicos (K vs K, K+N vs K, K+B vs K, K+B vs K+B con alfiles del mismo color de casilla). Auto-tablas al detectarlo en `checkGameState`. Verificado con 10 tests (incluye falsos positivos para KQ, KR, KP, posición inicial, K+N+N).
- _(Fase 1)_ Botón "🏳 Rendirse" en barra de controles con modal de confirmación "¿Seguro que quieres rendirte?". Tras confirmar: `gameOver=true`, status "Blancas/Negras se rindieron · 0-1|1-0", se ocultan los botones de reclamación de tablas. Hook marcado con TODO para enviar `{type:'resign'}` al peer cuando llegue Fase 8 (LAN). 9 tests programáticos PASS.
- _(Fase 1)_ Oferta y aceptación de tablas: botón "🤝 Ofrecer Tablas". En 1p la IA acepta automáticamente si `|evaluate(board)| ≤ 50 cp`, sino rechaza con toast "IA rechaza tablas". En 2p abre modal síncrono al oponente con Aceptar/Rechazar. Aceptación → `gameOver=true`, status "Tablas por acuerdo · ½-½". Botón se deshabilita mientras hay oferta pendiente. Hook TODO para Fase 8 (LAN: enviar `{type:'draw_offer'}` y esperar response con timeout 60s). 21 tests programáticos PASS.
- _(Fase 2 — parcial)_ Función `evaluate()` extendida con estructura de peones (doblados/aislados/pasados), seguridad del rey (pawn shield + king-in-center) y movilidad (opt-in). Fix lateral: corrección de bug pre-existente en la fórmula de lectura del PST (filas invertidas para blancas). 9 tests programáticos PASS.
- _(Fase 2 — parcial)_ Funciones `cpToPct(cp)` y `cpToLabel(cp)`. `cpToPct` aplica `50 + 50·tanh(cp/400)` saturando a 0/100 cuando `|cp| ≥ 99000` (umbral mate). `cpToLabel` formatea con minus tipográfico: `+1.20`, `−0.85`, `M5`, `−M3`, `0.00` (cero sin signo). 21 tests programáticos PASS.
- _(Fase 2 — parcial)_ Barra de ventaja real (`updateEvalBar`) reemplaza al viejo `updateThermometer` (que solo usaba material). Usa `evaluate()` completo con movilidad. Suavizado: el display de la barra se mueve ±10pp máximo por jugada (excepto en los primeros 2 plies del juego). Display de label `cpToLabel(cp)` junto a la barra, sin suavizado (refleja el cp real). Funciona en vertical (desktop) y horizontal (mobile). 14 tests programáticos PASS, incluido el test de blunder de dama (rawPct 1% se renderiza como 40% por suavizado, baja a 30 → 20 en plies siguientes).
- _(Fase 2 — parcial)_ Display de mate-in-N: `minimax` ahora recibe `pliesFromRoot` y encoda mate como `±(100000 - plies)` (independiente del depth máximo, lo que arregla un bug latente para Easy/Medium). `getBestMove` devuelve `{move, score}`. `updateEvalBar` corre un minimax shallow (depth=3) para detectar mate-in-1 y mate-in-2 desde cualquier turno; al detectarlo, bypassa el suavizado y muestra `M{n}` con `n = ceil(plies/2)`. La barra va al extremo correspondiente (100% si el mate favorece blancas, 0% si las recibe). 15 tests programáticos PASS.
- _(Fase 3 — parcial)_ Drag & drop con pointer events (mouse + touch unificados). Handlers `pointerdown/move/up/cancel` por pieza, threshold de 5px antes de entrar en modo drag para coexistir con click-to-move. Overlay flotante con `position:fixed`, `pointer-events:none`. `touch-action:none` en `.piece` previene scroll en mobile durante drag. Drop fuera del tablero o sobre casilla inválida → cancela y restaura. Click-to-move sigue intacto (15 tests programáticos PASS). _Verificación visual del drag pendiente: requiere navegador real (Chrome desktop + Chrome Android)._
- _(Fase 3 — parcial)_ Botón "↶ Deshacer" con `stateStack` (capacidad 100). `pushSnapshot()` se llama al inicio de `executeMove`; snapshot incluye board, turn, ep, castling, halfmove/fullmove, moveHistory, capturedByWhite/Black, lastMove, displayPct, **positionCounts** (Map clonado para que triple-rep funcione tras undo), gameOver y drawOfferPending. En 1p hace dos pops (revertir IA + humano); en 2p uno; en LAN (gameMode≠1,2) está deshabilitado. 21 tests programáticos PASS.
- _(Fase 3 — parcial)_ Botón "Nueva Partida" ahora pasa por `confirmNewGame`: si `moveHistory.length === 0` reinicia directo (no hay nada que perder); si ≥1 movimiento, abre modal "¿Reiniciar la partida actual? Se perderá el progreso (no guardado)" con Sí/Cancelar. 16 tests programáticos PASS.
- _(Fase 3)_ Botón "💡 Sugerencia": corre `getBestMove` a depth 2 y dibuja una flecha SVG amarilla translúcida sobre el tablero (líneas + arrowhead estilo Lichess). El SVG está en `viewBox 0 0 8 8`, `position:absolute` dentro de `#board`, `pointer-events:none` para no bloquear interacción. La flecha se limpia al inicio de `executeMove` y en `newGame`. Botón deshabilitado si `gameOver`, en LAN, o si en 1p no es el turno del jugador. 12 tests programáticos PASS.
- _(Fase 4 — parcial)_ Modo claro/oscuro: refactor de colores hard-coded a CSS custom properties (`--bg`, `--fg`, `--accent`, `--accent-fg`, `--panel-bg`, `--panel-border`, `--text-muted`, `--text-secondary`, `--separator`, `--modal-overlay`, `--border-strong`). Set oscuro default; set claro vía `body.light-mode`. (Selector reubicado al panel ⚙ en la tarea 20.)
- _(Fase 4 — parcial)_ 4 temas de tablero vía CSS variables `--sq-light` / `--sq-dark`. Default Clásico (#f0d9b5 / #b58863); overrides en `body.board-theme-{madera|cristal|medianoche}`. (Selector reubicado al panel ⚙ en la tarea 20.)
- _(Fase 4 — parcial)_ 3 sets de piezas con infraestructura completa: constante `PIECE_SVG = {cburnett:{12 keys}, merida:{12 keys}}` con fallback a Unicode cuando la string está vacía. `renderBoard` y overlay de drag detectan set y usan `innerHTML` (SVG) o `textContent` (Unicode). _Strings SVG vacías por ahora — pegar las 24 strings desde el repo de Lichess MIT cuando estén disponibles._ (Selector reubicado al panel ⚙ en la tarea 20.)
- _(Fase 4 — parcial)_ **Panel de configuración consolidado** (⚙ Configuración). Modal con: toggle modo claro/oscuro, radios con preview para tema de tablero (4 opciones, swatch 40×40 con los 4 colores), radios con preview para set de piezas (3 opciones), toggle sonido, slider de volumen 0–100, toggle mostrar coordenadas. Estado unificado bajo `localStorage.chess_settings` (JSON único). `loadSettings` migra automáticamente desde las claves legacy (`chess_theme_mode`, `chess_board_theme`, `chess_piece_set`) si el JSON nuevo no existe. `updateSetting(key, value)` aplica + persiste + re-renderiza el tablero si es necesario. Hide-coords vía `body.hide-coords`. 37 tests programáticos PASS.
- _(Fase 4)_ Sonidos WebAudio sintetizados (sin archivos). 6 tipos: `move` (triangular 300Hz, 80ms), `capture` (square 150Hz + noise burst, 120ms), `check` (3 beeps de 600Hz), `castle` (glissando 200→400Hz, 300ms), `promote` (chord 400/500/600Hz, 400ms), `gameEnd` (arpeggio descendente C5→G4→E4→C4). Lazy init de `AudioContext` en la primera llamada a `playSound` (Chrome autoplay policy). `playSound` lee `settings.soundEnabled` y `settings.volume` directamente. Hook en `executeMove` con prioridad `gameEnd > promote > castle > capture > check > move`; `gameEnd` también en `executeResign`, `applyDrawAgreed`, `claimDraw50`, `claimDraw3rep`. 26 tests programáticos PASS con `AudioContext` mockeado.
- _(Fase 5 — parcial)_ Selector de control de tiempo. Modal "⏱ Control de Tiempo" con 9 presets (Sin tiempo, Bullet 1+0, Blitz 3+0/3+2/5+0/5+3, Rápido 10+0/15+10, Clásico 30+0) + entrada custom (1–180 min, 0–60 seg). Estado global `selectedTimeControl = {minutes, increment} | null`. Persistencia en `localStorage.chess_time_control` como JSON. Label compacto del control activo en el botón ("5+3", "Sin tiempo"). Aplicar un preset llama `newGame()`. Validación contra valores inválidos. 27 tests programáticos PASS.
- _(Fase 5 — parcial)_ UI de reloj con cuenta regresiva. Dos `.clock` (uno por lado) dentro de `player-info`, sólo visibles si hay control de tiempo activo. `setInterval(100ms)` decrementa el reloj del lado a mover. `formatClock(ms)` devuelve `MM:SS` cuando ≥10s y `M:SS.t` (décimas) cuando <10s. En `executeMove` se llama `onMoveCommittedForClock(sideThatMoved)` que aplica el incremento Fischer al que acaba de mover y pasa el reloj al oponente. Pausa automática cuando hay modal abierto (`anyModalOpen` checa `.modal-overlay.open` y `#promo-overlay.open`) o `gameOver`. Estado del reloj se snapshot/restora en undo. 31 tests programáticos PASS.
- _(Fase 5 — parcial)_ Pérdida por tiempo (FIDE Art. 6.9). Nueva función `cannotMate(b, color)` que clasifica si un bando NO puede mate solo (chequeo por bando, distinto de `isInsufficientMaterial` que mira ambos lados): K solo, K+B, K+N, K+NN (2 caballos sin alfil), K+BB del mismo color. `flagFall(side)` ahora cierra la partida: si el oponente puede mate → pérdida por tiempo (0-1 si pierden blancas, 1-0 si negras); si no puede mate → tablas "Tablas por tiempo y material insuficiente · ½-½". Sonido `gameEnd`. 21 tests programáticos PASS.
- _(Fase 5)_ Reloj cableado en 1p y 2p; deshabilitado en LAN (`gameMode=3`): `clocksEnabled()` retorna `false`, botón "⏱ Control de Tiempo" oculto vía `updateTimeControlButton()`. Limitación documentada en sección 3.
- _(Fase 6 — parcial)_ Wrapper IndexedDB para partidas: 5 funciones async (`openDB`, `saveGame`, `getAllGames`, `getGame`, `deleteGame`). DB `chess_games` v1, store `games` con keyPath `id` autoIncrement, índices `date`/`mode`/`result`. `getAllGames` retorna ordenado por fecha DESC. Schema de GameRecord: `{id, date (ISO), mode, white, black, result, pgn, moves[{san,uci,fen}], finalFen, timeControl, durationMs}`. 18 tests programáticos PASS (con fake-IDB in-memory).
- _(Fase 6 — parcial)_ Auto-save al finalizar partida + botón "💾 Guardar". `currentResult` y `gameStartTime` globales se setean en cada game-end branch (mate/stale/75-mov/5x rep/material insuficiente/3rep claim/50-mov claim/rendición/tablas acuerdo/flag fall). `buildGameRecord(result)` arma el objeto con fecha ISO, mode, moves (SAN+UCI), finalFen, timeControl y durationMs. `autoSaveGame()` llama `saveGame()` y muestra toast "Partida guardada". `manualSaveGame()` fuerza guardado con result='*'; no guarda si `moveHistory` está vacío. Helpers `moveToUCI` (UCI con sufijo q en promoción) y `buildMinimalPGN` (movetext). 22 tests programáticos PASS, incluido fool's mate end-to-end.
- _(Fase 6 — parcial)_ Panel "📂 Partidas Guardadas". Modal con tabla (Fecha DD/MM/YYYY HH:mm, Blancas, Negras, Modo, Resultado, #Jugadas) ordenada por fecha DESC (vía `getAllGames`). Filtros por modo (1p/2p/LAN/Todos) y resultado (1-0/0-1/½-½/En curso/Todos). Acciones por fila: 👁 Ver (visor de estudio), ↓ PGN (export), 🗑 Eliminar con modal de confirmación. Escape de HTML en campos para defenderse de nombres con caracteres especiales. Empty state cuando filtros no matchean. 33 tests programáticos PASS.
- _(Fase 6)_ Visor de estudio (replay): click "👁 Ver" en una partida del panel abre el visor, que reproduce la partida ply a ply. Controles `replayFirst/Prev/Next/Last/ExitReplay` (atajos teclado Home/← /→ /End / Esc). Renderiza tablero, eval bar y notación de cada ply. Reusa `renderBoard` con `replayMode=true` para bloquear input. 25 tests programáticos PASS.
- _(Fase 6)_ Evaluación visible durante el replay: en cada ply el visor corre `evaluate()` y muestra `cpToLabel(cp)` arriba del tablero + un chart SVG de la línea de evaluación a lo largo de la partida. Click en un punto del chart salta al ply correspondiente. Tooltip con cp + numeral del ply.
- _(Fase 7)_ Generador de PGN estándar (`gameToPgn(record)`): tags `[Event][Site][Date][Round][White][Black][Result][Mode]`, escape de caracteres especiales en tags, wrap de movetext a 80 cols. `gameMode=1` (vs IA) omite `[Mode]` por compatibilidad spec; 2p → `OTB`, lan → `ICS`. Round desconocido = `?` (spec 8.1.1.4).
- _(Fase 7)_ Botón "↓ Exportar PGN" en barra de controles + en cada fila del panel de partidas. Descarga archivo `ajedrezmx-YYYY-MM-DD-{moves}.pgn`. Si la partida no se ha guardado, exporta el estado actual.
- _(Fase 7)_ Parser PGN tolerante: maneja comments `{...}`, NAGs `$N`, variations `(...)`, headers con caracteres especiales (lichess/chess.com). Movimientos ilegales se rechazan limpiamente. Validado contra el Inmortal de Anderssen (45 plies) y round-trip export→import. Botón "↑ Importar PGN" en barra de controles.
- _(Fase 8)_ Modal "📡 Multijugador LAN" con wizard Host/Join. Pantalla inicial con 2 botones grandes (🖥 Anfitrión / 📱 Invitado), cada uno con 3 steps (`Paso N de 3`): generación/copia de oferta SDP, intercambio, conexión. Botón Cancelar en cada step. 45 tests.
- _(Fase 8)_ Host: oferta SDP generada con `RTCPeerConnection({iceServers:[]})` (LAN-only, sin STUN), `DataChannel('chess', {ordered:true})`, `createOffer` + `setLocalDescription`, espera ICE con timeout 3s, `JSON.stringify(localDescription)` en textarea. 23 tests.
- _(Fase 8)_ Guest: botón "✓ Procesar oferta" valida JSON + crea pc + `setRemoteDescription` + `createAnswer` + `setLocalDescription` + espera ICE, auto-avanza a step 2 con respuesta lista para copiar. DataChannel del host capturado vía `pc.ondatachannel`. 29 tests.
- _(Fase 8)_ Host: botón "✓ Conectar" valida respuesta, `setRemoteDescription(answer)`, escucha `onconnectionstatechange`. En `connected` → cierra modal, `setMode(3)`, toast "🟢 Conectado". En `failed`/`closed` → mensaje rojo + botón "Reintentar" que regenera oferta desde cero. 38 tests.
- _(Fase 8)_ Protocolo de mensajes JSON sobre `RTCDataChannel` con 7 tipos (`hello`/`move`/`resign`/`draw_offer`/`draw_response`/`chat`/`sync`). Dispatcher por `msg.type`; tipos desconocidos se ignoran silenciosamente (forward-compat). JSON inválido o `type` ausente cierra el canal. Move entrante validado vía `getLegalMoves` antes de aplicar — peer remoto es _untrusted_ aunque sea LAN. Send hooks en `executeMove`, `executeResign`, `offerDraw`, `acceptDraw`, `rejectDraw`. Detalle completo en Apéndice. 67 tests.
- _(Fase 8)_ Rotación automática del tablero en LAN: condición `flipped` extendida con `(gameMode===3 && lanLocalColor==='b')`, llamando `renderBoard` cuando se asigna el color (en `onopen` y en `hello` si guest cede). El invitado con negras ve su rey en e8/d8 abajo, normal.
- _(Fase 8)_ Reconnect: `pc.oniceconnectionstatechange` dispara `lanOnConnectionLost` si la conexión se pierde tras establecerla. Banner pasa a 🔴 + botón "Reconectar" inline que abre el wizard. `lanFinalizeConnection` idempotente preserva `gameMode=3` en reconexión (no resetea tablero) y muestra toast "🟢 Reconectado". Sync FEN automático en cada `onopen` verifica integridad. 53 tests.
- _(Fase 8)_ Banner LAN persistente sobre `.controls` con 3 estados (🟢 Conectado / 🟡 Conectando / 🔴 Desconectado) y peer name del `hello`. Helper `canInputOnCurrentTurn()` bloquea input cuando no es el turno del color local (reemplaza 4 condiciones inline previas en showHint, drag pointerdown, onSquareClick, updateHintButton). Undo oculto en LAN.
- _(Fase 9)_ Audit responsive (29 asserts): `env(safe-area-inset-*)` con `max()` fallback en body y toast (iOS notch/home-indicator); toast con `max-width: calc(100vw - 32px)` y `word-break: break-word`; LAN banner con `flex-wrap: wrap` + `max-width: min(480px, calc(100vw - 16px))`; games-table-container con `overflow: auto`; `@media 700px` compacta modal h2 / games-table cells / lan-textarea para mobile.
- _(Fase 9)_ Audit cross-browser estructural (33 asserts): matriz de versiones mínimas (Chrome 86+, Firefox 78+, Safari 14+ / iOS 14.5+, Chrome Android 88+). Guards confirmados: `webkitAudioContext` para Safari pre-14, `navigator.clipboard` con try/catch en cada call site, `typeof RTCPeerConnection` antes de constructor, `touch-action:none` en piezas. Sin uso de APIs bleeding-edge (`:has`, `dvh`, `aspect-ratio`, `@container`, `ResizeObserver`, `eval`).
- _(Fase 9)_ Performance audit de `renderBoard` (13 asserts): mean 0.55ms / p50 0.30ms en node con DOM mockeado. Browser estimado 3-7ms incluyendo layout+paint. Margen vs 60fps (16.67ms): >2×. Confirmado que `pointermove` NO llama `renderBoard` (drag mueve overlay con `style.left/top`). Sin optimización aplicada per Karpathy.
- _(Post-P1)_ Perfiles locales (81 asserts). IndexedDB schema bump v1→v2: nuevo almacén `profiles` (`{id, name, pinHash, createdAt, isGuest?}`) + índice `profileId` en `games`. Migración auto-crea perfil "Invitado" y asigna las partidas legacy. **PIN obligatorio de 4 dígitos en la creación** (con campo de confirmación para evitar tipearlo mal), hasheado con SHA-256 vía `crypto.subtle.digest`. Bloqueo de 30s tras 3 intentos fallidos (estado en memoria). Pantalla a pantalla completa al cargar bloquea el juego hasta elegir o crear perfil; el PIN se vuelve a pedir en cada arranque (sin sesión persistente). Botón `👤 nombre` en la barra de controles abre menú con editar/cambiar perfil/borrar. `buildGameRecord` asigna `profileId` y usa nombre del perfil en `white`/`black` para 1p y LAN. `lanOnDCOpen` envía el nombre del perfil en el `hello`. La creación rechaza con mensaje explicativo si el contexto no es seguro (HTTP sobre IP de LAN cruda → no hay Web Crypto disponible); funciona con HTTPS, `localhost`, o `file://`.

---

## 2. Decisiones de diseño

### Por qué single-file (`index.html`)

Se mantiene todo en un solo archivo (HTML + CSS + JS inline) por tres razones:
1. **Convención del repo** (`CLAUDE.md`).
2. **Funciona con doble clic** (`file://`) — los ES modules no.
3. **Cero infraestructura** para desplegar.

### Por qué motor de ajedrez propio (no `chess.js`)

- **Garantía de offline absoluto**: ningún CDN, ningún `vendor/`.
- El motor existente ya cubre pseudo/legal moves, jaque, enroque, en passant y promoción.
- Lo que falta (50-mov, triple-rep, material insuficiente) se añade en Fase 1.

### Por qué WebRTC con intercambio manual de SDP (sin STUN público)

WebRTC permite conexiones peer-to-peer en LAN sin servidor intermedio. Tres restricciones de diseño:

1. **`iceServers: []`** (sin STUN público): garantiza zero-internet. Los candidates son solo `host` (interfaces de red locales). Trade-off: solo funciona si ambos peers están en la misma LAN sin NAT entre ellos. No atraviesa NAT — sin TURN, no se puede.
2. **Intercambio manual de SDP** (copy-paste): elimina la necesidad de un servidor de signaling. El usuario copia la oferta del host por WhatsApp / AirDrop / cualquier canal y la pega en el invitado. Más lento que signaling automático pero **cero infraestructura**.
3. **`DataChannel` ordenado + confiable** (`{ordered: true}`): equivalente a TCP. Los mensajes de ajedrez deben llegar en orden (un `move` después de su predecesor); la confiabilidad evita estados inconsistentes entre peers.

Alternativas consideradas:
- **STUN público (ej. Google)**: viola "100% offline" — requiere internet para el handshake.
- **Servidor de signaling propio**: requiere hosting, certificado HTTPS, monitoreo. Out of scope.
- **WebSocket directo**: no es P2P; requiere servidor permanente.

### Cómo se calcula la barra de ventaja

La barra es una representación visual del `evaluate()` actual, mapeado a porcentaje 0-100:

```
pct = 50 + 50 · tanh(cp / 400)
```

- `cp` = centipawns desde la perspectiva de las blancas (positivo = blancas mejor).
- `400 cp` es la inflexión donde la curva está a 50% de saturación; modelo estándar de Lichess.
- Saturación a 0%/100% cuando `|cp| ≥ 99000` (umbral de mate forzado).

**Suavizado ±10pp por jugada**: el display NO salta al nuevo `pct` directamente sino que se mueve máximo 10 puntos porcentuales por jugada. Excepción: los primeros 2 plies del juego sí se renderizan directos (no hay historial). Razón: una blunder cae de 50% a 1% instantáneamente sería estridente; suavizar a 50→40→30→20→… da feedback gradual.

**Mate-in-N bypass**: `updateEvalBar` corre un minimax shallow (depth=3) para detectar mate-in-1 y mate-in-2. Al detectarlo, bypassa el suavizado y muestra `M{n}` con la barra al extremo correspondiente.

Label junto a la barra (`cpToLabel`): `+1.20` / `−0.85` / `M5` / `−M3` / `0.00`. Cero sin signo, mate con `M`, negativos con minus tipográfico (`−`, no `-`).

### Función de evaluación (`evaluate(b, opts?)`)

El score se mide en centipawns (cp) desde la perspectiva de las blancas: positivo = blancas mejor.

```
evaluate(b)  =  material(b)
              + PST(b)
              + pawnStructureScore(b)
              + kingSafetyScore(b)
              + mobilityScore(b)        (solo si opts.mobility = true)
```

**Material:** `PIECE_VALUES = { K:20000, Q:900, R:500, B:330, N:320, P:100 }` (cp).

**PST (piece-square tables):** una tabla 8×8 por tipo de pieza. La fila del PST es igual a la fila del tablero desde la perspectiva del color (las negras espejean verticalmente con `pr = 7 - r`). Fix de Fase 2: la fórmula original tenía la asignación de filas invertida para las blancas, lo que hacía que un peón blanco en su casilla de inicio recibiera el bono de "casi-promoción". Corregido a `pr = color === 'white' ? r : 7 - r`.

**Pawn structure:**
- Peones doblados: por cada peón extra en el mismo file, -15 cp.
- Peones aislados: si no hay peón propio en files adyacentes, -20 cp.
- Peones pasados: +30 cp + 10 cp por rank avanzado desde la casilla de salida. Un peón es pasado si no hay peones enemigos en su file ni en los dos files adyacentes por delante de él.

**King safety (solo midgame, ≥ 4 piezas mayores totales — Q+R):**
- Pawn shield: por cada peón propio en la fila inmediatamente delante del rey enrocado (kingside o queenside), +10 cp.
- Rey en centro (rank 3–4 blancas, rank 5–6 negras): -50 cp.

**Mobility (opt-in, costo ~2 llamadas a `getLegalMoves`):**
- `(legalMovesBlancas - legalMovesNegras) × 1 cp`.
- Por default está apagado para no doblar el costo de minimax. Solo lo activa quien tiene contexto fuera del search (eval bar, decisión de aceptar oferta de tablas).

**Valores de referencia (verificados con tests):**
- `evaluate(startpos)` = 0
- `evaluate(post-1.e4)` = +40
- `evaluate(1.e4 e5)` = 0 (simétrico)
- `evaluate(K + d6 vs K)` = +180 (peón pasado lejos + aislado)

### Por qué sonidos sintetizados (WebAudio) en lugar de archivos

Tres razones:

1. **Peso 0**: no hay archivos `.mp3` / `.ogg` que descargar. Los sonidos se generan en runtime con `AudioContext`. El bundle sigue siendo un solo `index.html`.
2. **Sin licencias**: archivos de audio típicamente vienen con CC-BY o restricciones de redistribución. Los osciladores WebAudio son libres por construcción.
3. **Funciona offline garantizado**: ningún CDN, ningún path relativo que falle.

Seis tipos implementados: `move` (triangular 300Hz, 80ms), `capture` (square 150Hz + noise burst, 120ms), `check` (3 beeps de 600Hz), `castle` (glissando 200→400Hz, 300ms), `promote` (chord 400/500/600Hz, 400ms), `gameEnd` (arpeggio descendente C5→G4→E4→C4). Lazy-init de `AudioContext` (Chrome autoplay policy) + `resume()` defensivo (iOS Safari).

---

## 3. Limitaciones conocidas

### Generales

- La IA llega a profundidad 4 (≈1500 ELO estimado), no nivel maestro.
- El intercambio de SDP por copy-paste es más lento que una conexión automática, pero garantiza zero-server.
- El reloj en modo LAN no se sincroniza entre dispositivos (decisión consciente por simplicidad). En modo LAN (`gameMode=3`), `clocksEnabled()` retorna `false` y el botón "⏱ Control de Tiempo" se oculta. Si en el futuro se quiere implementar reloj sincronizado, requeriría un protocolo de sincronización con compensación de latencia (ej. timestamps NTP-like) — fuera de scope de la versión actual.
- Drag & drop en mobile puede ser impreciso: se recomienda el modo click-to-move como alternativa.
- En LAN no hay UI de envío de chat (sólo recepción → toast). El protocolo del `chat` queda implementado bidireccionalmente para añadir caja de texto sin tocar el DataChannel.
- El `draw_offer` en LAN no tiene timeout: si el peer ignora la oferta, `drawOfferPending` queda en `true` hasta cancelación manual.

### Compatibilidad por navegador

Versiones mínimas verificadas mediante audit estructural (`/tmp/compat_audit_test.js`, 33 invariantes). Pendiente verificación funcional manual.

| Browser | Versión mínima | Notas |
|---|---|---|
| **Chrome desktop** (Linux/Win/Mac) | 86+ | Funcionamiento completo. |
| **Firefox desktop** | 78+ | Funcionamiento completo. |
| **Safari desktop** (macOS) | 14+ | WebAudio: `webkitAudioContext` fallback aplicado. CSS `flex+gap` requiere Safari 14.1+. |
| **Chrome Android** | 88+ | Drag&drop por pointer events (touch+mouse unificados). |
| **Safari iOS** | 14.5+ | `env(safe-area-inset-*)` para notch/home-indicator; `touch-action:none` en piezas para evitar scroll durante drag; AudioContext.resume() defensivo por autoplay policy. |

### Requisitos de contexto

- **Clipboard API** (botones 📋 Copiar/Pegar de SDP en LAN): requiere **HTTPS** o **localhost**. Sobre IP de LAN cruda (ej. `http://192.168.x.x:8000`), Chrome y Safari bloquean `navigator.clipboard`. Workaround: el usuario puede seleccionar manualmente el texto del `<textarea>` (todos los navegadores) y usar Cmd/Ctrl+C / Cmd/Ctrl+V. El código maneja el bloqueo silenciosamente (try/catch) sin romper el flujo.
- **WebRTC sin STUN** (`iceServers: []`): los peers deben estar en la misma red local. Sin servidor TURN, no atraviesa NAT.
- **IndexedDB** (persistencia de partidas): universal pero Safari iOS en "modo privado" la vacía al cerrar la pestaña.
- **WebAudio**: en iOS Safari requiere gesto del usuario para iniciar; resuelto por lazy-init + `resume()` defensivo.

### Lista de bugs por browser

_Pendiente: requiere ejecución manual de los 6 flujos del task_41 en cada browser. El audit estructural confirma que los guards/fallbacks están en su lugar, pero issues de layout o timing pueden aparecer en ejecución real._

### Rendimiento de `renderBoard`

Audit en node con DOM mockeado (cubre solo el costo algorítmico, sin layout/paint del browser):

| Escenario | mean | p50 | p99 |
|---|---|---|---|
| Posición inicial, sin highlights | 0.55ms | 0.30ms | 10ms* |
| Con casilla seleccionada + 5 validMoves + lastMove | 0.55ms | 0.30ms | 10ms* |

*p99 inflado por pausas de GC de node; no es coste algorítmico real.

Costo browser estimado (layout + paint para 64 elementos): **3-7ms por call**. Margen contra el budget de 60fps (16.67ms): >2×.

**Hallazgos clave:**
- `renderBoard` NO se llama en `pointermove` — el drag mueve un overlay flotante con asignación directa de `style.left`/`style.top`. La preocupación original del task era infundada.
- Bucles lineales en el tamaño del tablero: 64 (squares) + 8 (rank labels) + 8 (file labels) = 80 iteraciones. Sin O(n³).
- 4 `createElement` estáticos + 4 `appendChild` por call + 1 `addEventListener('click')` por casilla + ~16 highlights de SVG según pieceset.

**Conclusión: no se requirió optimización** (Karpathy: don't over-engineer; el task explícitamente lo permitía). Quedan disponibles si en el futuro aparece regresión observable:
- Cachear el `boardEl` en una global (saca un `getElementById` por call)
- Incremental update cuando solo cambia highlight (selected/validMoves) en vez de full rebuild
- `requestAnimationFrame` para batching

---

## 4. Instrucciones de despliegue

### Modo offline (recomendado para uso personal)

```
Abrir index.html con doble clic en cualquier navegador moderno.
```

### Modo servidor estático (recomendado para LAN entre dispositivos)

```
cd /ruta/al/repo
python3 -m http.server 8000
```

Luego abrir `http://<IP-de-tu-PC>:8000` desde cualquier dispositivo en la misma red.
Servir vía HTTP habilita el Clipboard API completo (necesario para los botones de copiar SDP en LAN).

---

## 5. Guía LAN paso a paso

### Prerequisitos

- Dos dispositivos conectados a la **misma red WiFi**.
- Ambos usando el mismo `index.html` (idealmente servido por HTTP estático — ver sección 4).
- Navegador moderno (Chrome 86+ / Firefox 78+ / Safari 14+ / Edge 86+ / Chrome Android 88+ / Safari iOS 14.5+).
- Un canal cualquiera para pasar el SDP entre dispositivos: chat, mensaje, AirDrop, o incluso una nota compartida. **No requiere internet** — funciona entre dos PCs en la misma WiFi aislada.

### Lado anfitrión

1. Click en **📡 LAN** (barra de controles superior).
2. En el modal, click en **🖥 Soy el anfitrión**.
3. **Paso 1 de 3** — Se genera la oferta SDP automáticamente (1-2s). Click **📋 Copiar** y envía el bloque de texto al invitado por el canal que prefieras. Click **Siguiente →**.
4. **Paso 2 de 3** — Pega la respuesta SDP del invitado en el textarea. Click **📋 Pegar** (si lo tienes en clipboard) o pega manualmente. Click **✓ Conectar**.
5. **Paso 3 de 3** — "Estableciendo conexión…". En 1-3s debe aparecer toast **🟢 Conectado**. El modal se cierra y entras en LAN mode (`gameMode=3`).
6. Si ves **🔴 No se pudo conectar — verifica que ambos estén en la misma red WiFi**: click **Reintentar**, vuelve al paso 3 con oferta nueva.

### Lado invitado

1. Click en **📡 LAN**.
2. Click en **📱 Soy el invitado**.
3. **Paso 1 de 3** — Pega la oferta del anfitrión en el textarea. Click **📋 Pegar** o pega manualmente. Click **✓ Procesar oferta**.
4. **Paso 2 de 3** — Se genera tu respuesta automáticamente. Click **📋 Copiar** y envíasela al anfitrión.
5. **Paso 3 de 3** — "Esperando conexión del anfitrión…". Cuando el anfitrión pegue tu respuesta y termine su conexión, verás toast **🟢 Conectado**. El modal se cierra.

### Durante la partida

- **Banner** persistente sobre la barra de controles muestra estado (🟢/🟡/🔴) + nombre del oponente.
- **Rotación automática**: si te tocó negras, ves tu rey en e8 abajo (normal).
- **Solo puedes mover en tu turno** (`canInputOnCurrentTurn` bloquea clicks/drag fuera de turno).
- **Rendirse** y **Ofrecer tablas** funcionan bidireccional vía DataChannel.
- **Reloj deshabilitado** en LAN por simplicidad (sin sincronización de reloj).
- **Deshacer oculto** en LAN (state stack no aplica a partidas multi-cliente).

### Reconexión

Si la conexión se pierde (cerraste la pestaña del oponente, perdiste WiFi temporalmente, etc.):

1. Banner cambia a **🔴 Desconectado** + aparece botón **Reconectar** inline.
2. Click **Reconectar** abre el wizard otra vez. Tu tablero local se preserva (no se resetea).
3. Completa el handshake (Anfitrión o Invitado) con SDP nuevo.
4. Al conectar, se envía un `sync` con FEN para verificar que ambos tableros coinciden. Si los FEN difieren, aparece toast **⚠ Desincronización detectada** (resolución manual: el lado correcto puede regenerar la conexión).

### Troubleshooting

**"No se pudo conectar"** (más de 5 segundos sin éxito):

- Verifica que ambos dispositivos estén en la **misma WiFi**, no en redes separadas (ej. uno en 2.4GHz, otro en 5GHz pueden estar aislados según router).
- Algunos routers tienen **"AP isolation"** o **"Client isolation"** activado por default — bloquea tráfico entre dispositivos. Desactivalo o usa un router diferente.
- **Firewall del SO** puede bloquear conexiones entrantes — temporalmente desactívalo para confirmar.
- **Algunos hotspots móviles** (compartir datos celular) **NO permiten P2P** entre clientes. Usa una WiFi real.

**Los botones 📋 Copiar/Pegar no funcionan**:

- El Clipboard API requiere **HTTPS o localhost**. Sobre `http://192.168.x.x` (IP de LAN cruda), Chrome y Safari lo bloquean.
- **Workaround manual**: selecciona el texto del textarea con click+arrastrar y usa Cmd/Ctrl+C / Cmd/Ctrl+V.
- Verifica que estés usando un navegador moderno (Chrome 66+ / Firefox 63+ / Safari 13.1+).

**Banner 🔴 aparece y desaparece intermitentemente**:

- Interferencia WiFi o señal débil. La conexión P2P se reestablece automáticamente vía ICE; si no, usa el botón Reconectar.

**Los tableros se desincronizan después de reconectar**:

- Toast **⚠ Desincronización detectada** indica diferentes FEN. Resolución actual: cierra la conexión LAN, vuelve a `1 Jugador` o `2 Jugadores`, y reinicia.

---

## Apéndice: Protocolo de mensajes LAN

Comunicación peer-to-peer sobre un `RTCDataChannel` (canal ordenado y confiable). Una vez establecido el canal tras el intercambio manual de SDP, ambos peers se hablan con mensajes JSON.

### Codificación y reglas generales

- **Formato**: cada mensaje es un objeto JSON serializado con `JSON.stringify` y enviado como un único `send()` (un mensaje = un envío). Sin delimitadores, sin batching.
- **Canal**: `ordered: true`, `maxRetransmits: null` (modo confiable, equivalente a TCP). Crear con `pc.createDataChannel('chess', { ordered: true })`.
- **Identidad de roles**: el _anfitrión_ (host) es el peer que genera la oferta SDP. El _invitado_ (guest) genera la respuesta. Los colores se acuerdan en el `hello` (ver abajo); por default el anfitrión juega blancas.
- **Validación local obligatoria**: ningún mensaje del peer remoto se aplica sin pasar primero por `getLegalMoves` / validación de estado. El peer remoto es _untrusted_ aunque sea LAN.
- **Versionado**: este es el `protocol_version: 1`. Si en el futuro hay incompatibilidad, se añade el campo a `hello` y se rechaza la conexión si no coincide.

### Resumen de tipos

| `type`           | Dirección        | Trigger                                                  |
| ---------------- | ---------------- | -------------------------------------------------------- |
| `hello`          | bidireccional    | Primer mensaje al abrir el DataChannel.                  |
| `move`           | jugador en turno | El usuario confirma una jugada legal localmente.         |
| `resign`         | bidireccional    | El usuario presiona "Rendirse" y confirma.               |
| `draw_offer`     | bidireccional    | El usuario presiona "Ofrecer tablas".                    |
| `draw_response`  | receptor de la oferta | Tras un `draw_offer` pendiente.                      |
| `chat`           | bidireccional    | El usuario envía un texto desde el chat opcional.        |
| `sync`           | bidireccional    | Reconexión o petición explícita de verificación.         |

### Detalle por mensaje

#### `hello` — handshake inicial

```json
{ "type": "hello", "protocol_version": 1, "color": "w", "name": "Reli" }
```

- **Payload**: `protocol_version` (entero), `color` (`"w"` blancas / `"b"` negras, el color que el emisor pretende jugar), `name` (string libre, ≤ 32 chars; se sanitiza al render).
- **Dirección**: ambos peers envían `hello` al abrir el canal; **no se asume orden**.
- **Cuándo**: en cuanto `dataChannel.onopen` se dispara.
- **Resolución de conflictos**: si ambos piden el mismo color, gana el anfitrión y al invitado se le asigna el opuesto. La UI del invitado se actualiza al recibir el `hello` del anfitrión.

#### `move` — jugada

```json
{ "type": "move", "uci": "e2e4" }
{ "type": "move", "uci": "e7e8", "promo": "q" }
```

- **Payload**: `uci` (string de 4 chars: casilla origen + casilla destino en notación algebraica, ej. `"g1f3"`); `promo` opcional cuando la jugada promociona un peón (`"q" | "r" | "b" | "n"`).
- **Dirección**: solo del jugador en turno hacia el oponente. Recibir un `move` cuando no es turno del remitente es un error de protocolo: se ignora y se loguea.
- **Cuándo**: tras `executeMove` local exitoso. El emisor ya aplicó la jugada en su tablero antes de enviar.
- **Validación remota**: el receptor reconstruye la jugada desde el UCI, la pasa por `getLegalMoves`, y solo si es legal la aplica. Si es ilegal, desconecta y muestra error.

#### `resign` — rendición

```json
{ "type": "resign" }
```

- **Payload**: ninguno.
- **Dirección**: bidireccional (cualquier peer en cualquier momento, siempre que el juego no haya terminado).
- **Cuándo**: tras confirmación local del botón "Rendirse".
- **Efecto en el receptor**: marca `gameOver = true`, muestra "Ganaste por rendición" y bloquea inputs.

#### `draw_offer` — oferta de tablas

```json
{ "type": "draw_offer" }
```

- **Payload**: ninguno.
- **Dirección**: bidireccional. Solo puede haber **una oferta pendiente por lado** a la vez; ofertas duplicadas se ignoran.
- **Cuándo**: tras confirmación local del botón "Ofrecer tablas".
- **Efecto en el receptor**: muestra diálogo Aceptar / Rechazar; al responder envía `draw_response`.

#### `draw_response` — respuesta a oferta

```json
{ "type": "draw_response", "accept": true }
```

- **Payload**: `accept` (boolean).
- **Dirección**: del peer que recibió el `draw_offer` hacia el oferente.
- **Cuándo**: tras la decisión del usuario en el diálogo de oferta.
- **Efecto**: si `accept: true`, ambos peers marcan tablas. Si `accept: false`, la oferta se descarta y el juego continúa.

#### `chat` — mensaje de texto opcional

```json
{ "type": "chat", "text": "buena jugada" }
```

- **Payload**: `text` (string, ≤ 280 chars; se trunca y se escapa al renderizar).
- **Dirección**: bidireccional.
- **Cuándo**: cada vez que el usuario envía un texto desde la caja de chat.
- **Notas**: no se aplica HTML; se renderiza como `textContent`.

#### `sync` — verificación de estado

```json
{ "type": "sync", "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", "halfmove": 0, "fullmove": 1 }
```

- **Payload**: `fen` (FEN completo del estado actual), `halfmove` (contador de la regla de 50), `fullmove` (número de movimiento completo).
- **Dirección**: bidireccional.
- **Cuándo**:
  - En **reconexión**: tras restablecer el DataChannel (si en el futuro se persiste sesión), ambos peers envían su `sync` para verificar que coinciden.
  - **Bajo petición**: si el receptor detecta una incongruencia (ej. UCI ilegal) puede pedir un `sync` al peer (mecanismo a definir en la fase de implementación).
- **Resolución de discrepancia**: si los FEN difieren, se detiene el juego y se muestra error. La fase 8 decidirá si se aborta o se re-sincroniza desde el FEN del anfitrión.

### Errores y desconexión

- Mensaje con `type` desconocido → se ignora silenciosamente (compatibilidad hacia adelante).
- JSON inválido o `type` ausente → se loguea y se cierra el canal.
- Movimiento ilegal recibido → se cierra el canal y se muestra "Conexión inválida con el oponente".
- Cierre del DataChannel (`onclose`) → se marca el juego como "Oponente desconectado" sin alterar el resultado; el usuario puede iniciar nueva conexión.
