# ♟ AjedrezMX

**Ajedrez offline en un solo archivo HTML. Sin instalación, sin internet, sin cuentas.**

## ¿Qué es AjedrezMX?

Una aplicación de ajedrez completa que cabe en un archivo `index.html`. Jugá contra una IA, contra otra persona en la misma compu, o conectate por WiFi a otro dispositivo y jugá en LAN — todo sin necesidad de internet, servidor ni instalación. Incluye reglas oficiales (50-mov, triple repetición, material insuficiente), reloj con incremento Fischer, barra de evaluación al estilo Lichess, sonidos, temas, sets de piezas SVG, importación y exportación PGN, e historial de partidas guardadas en tu navegador.

---

## Cómo abrir

1. Descargá `index.html` (clonando este repo o copiando el archivo).
2. Hacé doble clic en `index.html` — se abre en tu navegador.

> Para jugar en LAN con otra persona en tu misma WiFi, abrí una terminal en la carpeta y corré `python3 -m http.server 8000`. Después en cada dispositivo abrí `http://<tu-IP-local>:8000` (ej. `http://192.168.1.42:8000`).

---

## Modos de juego

- **1 Jugador (vs IA)** — La computadora juega con dificultad ajustable (Fácil / Medio / Difícil). Elegí si jugás con blancas o negras.
- **2 Jugadores (mismo dispositivo)** — Hot-seat: dos personas comparten el mouse y el teclado en la misma compu.
- **Multijugador LAN** — Conectate por WiFi a otra persona en tu misma red. Sin servidor, sin signaling externo: el establecimiento de conexión se hace copiando y pegando un bloque de texto (SDP) entre ambos dispositivos.

---

## Características destacadas

- **🎯 Barra de evaluación real** — No es solo material; usa una función de evaluación completa (estructura de peones, seguridad del rey, movilidad opcional) con suavizado tipo Lichess (±10% por jugada). Detecta mate en N y lo muestra como `M3`, `M5`, etc.
- **♟ Reglas oficiales completas** — Halfmove clock + regla de los 50 movimientos, triple repetición, material insuficiente, rendirse, oferta de tablas. Reloj con incremento Fischer (Bullet 1+0, Blitz 3+0/3+2, Rápido 10+0/15+10, Clásico, o personalizado).
- **🔄 Drag & drop + click-to-move** — Funcionan en conjunto: arrastrá la pieza o hacé click en origen y destino. Touch + mouse unificados (funciona igual en celular y desktop).
- **💡 Sugerencia** — Botón que dibuja una flecha SVG con el mejor movimiento según la IA.
- **↶ Deshacer** — Stack de hasta 100 estados; en 1p revierte tu movimiento + el de la IA en un solo click.
- **🎨 Temas y piezas** — 4 temas de tablero (Clásico, Madera, Cristal, Medianoche), 3 sets de piezas (Unicode + 2 SVG embebidos), modo claro/oscuro.
- **🔊 Sonidos sintetizados** — 6 efectos (move, capture, check, castle, promote, gameEnd) generados con WebAudio. Sin archivos `.mp3`. Volumen ajustable.
- **📂 Historial de partidas** — Auto-guardado al terminar + botón "💾 Guardar". Panel con filtros (modo / resultado) y acciones (ver replay, exportar PGN, eliminar). Persistencia en IndexedDB del navegador.
- **👁 Visor de estudio** — Replay ply a ply con eval bar en cada momento + chart SVG de la evaluación a lo largo de la partida. Click en el chart salta al ply.
- **📄 PGN export / import** — Generador estándar compatible con Lichess y Chess.com. Parser tolerante (acepta comments, NAGs, variations, headers de Lichess/Chess.com). Botones en barra de controles + en cada fila del panel de partidas.
- **📡 Multijugador LAN** — WebRTC peer-to-peer con intercambio manual de SDP. Sin servidor, sin STUN público, garantía 100% offline. Banner con estado de conexión (🟢/🟡/🔴), nombre del oponente, rotación automática del tablero según color asignado, reconexión con verificación de FEN.

---

## Cómo jugar LAN (paso a paso)

Necesitás dos dispositivos en la **misma red WiFi**. Funciona entre cualquier combinación (PC + celular, dos PCs, dos celulares).

### Setup

En **uno** de los dispositivos, abrí una terminal en la carpeta del repo y corré:

```
python3 -m http.server 8000
```

Después abrí `http://<IP-de-esa-PC>:8000` en ambos dispositivos (averiguá la IP con `ip a` en Linux, `ipconfig` en Windows, o `Configuración > WiFi > info`).

### Anfitrión (decide quién hace de "host")

1. Click en **📡 LAN** (barra de arriba).
2. Click en **🖥 Soy el anfitrión**.
3. Esperá 1-2s a que se genere la **oferta SDP**. Click **📋 Copiar** y mandala al invitado por chat / WhatsApp / mensaje. Click **Siguiente →**.
4. Cuando el invitado te mande su **respuesta**, pegala en el textarea. Click **✓ Conectar**.
5. En 1-3s deberías ver el toast **🟢 Conectado**. El modal se cierra y entrás en modo LAN.

### Invitado

1. Click en **📡 LAN**.
2. Click en **📱 Soy el invitado**.
3. Pegá la **oferta** que te mandó el anfitrión. Click **✓ Procesar oferta**.
4. Se genera tu **respuesta** automáticamente. Click **📋 Copiar** y mandala al anfitrión.
5. Cuando el anfitrión pegue tu respuesta, ambos ven **🟢 Conectado** y se cierran los modales.

> Solo podés mover en tu turno. Si te tocó negras, ves el tablero rotado (tu rey en e8 abajo, como es normal). Rendirse, ofrecer tablas y desconexiones se manejan automáticamente.

Para más detalle, troubleshooting y protocolo técnico, mirá `MEJORAS.md` sección 5 — o desde la app, click en **ℹ Acerca de**.

---

## FAQ

**¿Funciona sin internet?**

Sí, completamente. Una vez descargado `index.html`, no hace ningún request a la red. Para LAN, los dispositivos solo necesitan estar en la misma WiFi (puede ser un router casero, un hotspot móvil, o incluso una WiFi sin internet — no requiere salida a la red externa).

**¿Funciona en celular?**

Sí — Chrome Android 88+ y Safari iOS 14.5+ están verificados. Drag & drop puede ser un poco impreciso en pantallas chicas; usá click-to-move como alternativa. La rotación automática + safe-area-inset (para el notch) están aplicadas.

**¿Por qué los botones de Copiar/Pegar SDP no funcionan en mi tablet?**

El Clipboard API requiere **HTTPS o localhost**. Si abriste la app vía `http://192.168.x.x:8000` (IP de tu LAN), el navegador bloquea `navigator.clipboard`. Workaround: seleccioná el texto del cuadro a mano y usá Cmd/Ctrl+C / Cmd/Ctrl+V. Funciona en todos los navegadores.

**¿Mis partidas se guardan?**

Sí, en el IndexedDB de tu navegador, asociadas a tu perfil. Cada partida que terminás se guarda automáticamente; también podés guardar manualmente con el botón **💾 Guardar**. Para verlas: click en **📂 Partidas**. Caveat: si usás Safari en modo privado, IndexedDB se vacía al cerrar la pestaña.

**¿Cómo funcionan los perfiles? ¿Pueden compartir el dispositivo varias personas?**

Sí. La primera vez que abrís la app, tenés que crear un perfil (solo nombre, o nombre + PIN opcional de 4 dígitos). Cada perfil tiene su propio historial de partidas. Para cambiar de perfil: click en **👤 [nombre]** en la barra de controles → "Cambiar de perfil". Los perfiles con PIN re-piden el PIN cada vez que abrís la app (no se quedan logueados). Tres PINs incorrectos seguidos = lockout de 30 segundos.

**Aclaración importante**: los perfiles son **locales al navegador**. No hay servidor, no hay cuentas en la nube, no hay password recovery. Si perdés el PIN, las partidas del perfil quedan inaccesibles (técnicamente recuperables vía DevTools, pero el flujo normal no las muestra). El PIN evita que alguien casual mire tu historial, **no** es protección criptográfica fuerte.

**¿Qué tan fuerte juega la IA?**

Aproximadamente nivel ~1500 ELO en dificultad Difícil (profundidad 4 de minimax con poda alpha-beta + heurísticas de estructura de peones, seguridad del rey, y movilidad). No es nivel maestro, pero da pelea decente a un club player promedio.

**¿Por qué el reloj no funciona en LAN?**

Por simplicidad: sincronizar relojes entre peers con latencia variable requiere un protocolo de compensación (timestamps NTP-like) que escapa al scope de este proyecto. En LAN el botón ⏱ se oculta automáticamente. Si querés cronometrar, usá un reloj externo (de teléfono, ajedrez, etc.).

---

## Créditos

- **Piezas SVG** — Sets `cburnett` y `merida` adaptados del [proyecto Lichess](https://github.com/lichess-org/lila) (licencia MIT). Las piezas Unicode están embebidas como caracteres estándar (no requieren atribución).
- **Inspiración de diseño** — La eval bar, el visor de estudio y el PGN siguen el comportamiento de [Lichess](https://lichess.org); los sonidos y los temas de tablero siguen la línea de [Chess.com](https://chess.com).
- **Reglas FIDE** — Implementadas siguiendo las [Laws of Chess 2023](https://handbook.fide.com/chapter/E012023) (regla de los 50 movimientos, triple repetición, material insuficiente, mecánica de tablas).

---

## Licencia

Por definir. El código de la app es original; los sets de piezas heredan la licencia MIT de Lichess.

---

Documentación técnica completa para developers: [`CLAUDE.md`](./CLAUDE.md) · Notas de implementación, decisiones de diseño, y protocolo LAN: [`MEJORAS.md`](./MEJORAS.md).
