# Card Sequence Validator — Targeted Interview Q&A

This is a focused prep sheet built directly from the actual codebase (`src/app_state.py`,
`src/services/udp_reader.py`, `src/services/udp_writer.py`, `src/services/com_writer.py`,
`src/services/licensing.py`, `src/card_types.py`). Use it alongside the longer
`Interview-Preparation-Guide.md` and `Complete-Interview-Questions-Bank.md` for extra depth.

---

## 1. Architecture & Workflow

### Explain the complete workflow, end to end
1. **Setup**: Operator opens Network/COM Port Setup and configures, per head, a *main scanner*
   (UDP or serial), an optional *on-demand scanner* (used for ad-hoc lookups like "scan this card
   to see its details"), and an *output* channel (UDP or serial) that talks to the PLC.
2. **File load**: A CPD (Card Production Data) file is parsed (`src/logic/file_parser.py`). Based on
   `CardType` (SINGLE / HALF / QUARTER), the parser builds the expected sequence and two lookup
   dictionaries: `qr_to_index` (QR code → (array index, position)) and `numcard_to_qrs`.
3. **Start scanning**: Operator hits Start. `main_port_reader` (a `UDPReader` or serial reader)
   begins listening in a background thread.
4. **Scan event**: A QR code arrives → checksum digits are stripped → the code is looked up in
   `qr_to_index` in O(1).
   - Matches current expected card → `OK` (or `LAST OK` if it's the final card).
   - Matches a *future* card → `OK (JUMPED)`, and the skipped cards are logged.
   - Matches a *past* card, wrong side, or isn't in the file at all → `NOT OK`.
5. **Output**: The result is sent immediately via `UDPWriter`/`ComPortWriter` to the PLC so the
   production line can accept or reject the physical card.
6. **Logging & persistence**: Every scan is appended to an in-memory log (later exportable to CSV)
   and the running state (`current_card_index`, scan side, etc.) is atomically written to a JSON
   cache so a crash or power loss doesn't lose progress.
7. **Repeat** for Head A and Head B independently — they run as two separate `AppState` instances
   coordinated by `DualHeadManager`, so two lines can be validated at the same time.

### Why was this project needed / what problem does it solve?
Manual (human) sequence checking on a card production line doesn't scale: operators get tired,
miss out-of-order cards, and can't keep pace with scanner speed. A single wrong card getting
through — say, the wrong ICCID ending up in the wrong SIM card slot — becomes a warranty/compliance
problem downstream. This tool automates that check: it takes over the "does this QR code match
what should be here right now" decision in milliseconds, flags mismatches instantly, feeds a
pass/fail signal straight back to the PLC to gate the line, and keeps an audit trail for QA. Dual
heads let one operator supervise two lines instead of one.

### Why Python?
- Fast to build and iterate on an industrial tool with a small dev team.
- `socket` and `pyserial` cover both communication needs (network scanners and legacy COM-port
  scanners) without custom drivers.
- The performance bottleneck here is I/O (waiting on network/serial packets), not CPU — Python's
  interpreter overhead is irrelevant to that. The GIL is a non-issue because I/O calls release it.
- `PyInstaller` gives a single-file Windows executable, so there's nothing for a factory floor PC to
  "install" beyond copying an .exe and a license file.

### Why PyQt6?
- Needed a real desktop GUI (not a browser tab) that operators trust and that survives on a
  factory PC without internet access.
- The signal/slot system is the actual reason it was chosen over Tkinter: background threads
  (`UDPReader`, `ComPortReader`) can't safely touch widgets directly, so they `emit` a signal
  (`state_changed`, `com_status_changed`, etc.) and Qt marshals that back onto the UI thread safely.
  That's the backbone of how this app stays responsive while doing network I/O in the background.
- Rich widgets (`QTableWidget` for the live log, `QComboBox`, custom styled buttons) look
  professional without much custom work.

### Why UDP for scanner communication?
- Scanners fire short, independent QR payloads — there's no "session" to maintain, so a
  connectionless protocol fits naturally.
- Lower latency and less overhead than TCP's handshake/ack machinery — every millisecond matters
  when a card is moving on a belt.
- Industrial PLCs and network barcode scanners on the factory floor are typically configured to
  send/receive raw UDP datagrams, not open TCP sockets — matching UDP avoids extra protocol
  translation work on the hardware side.
- Each scan is validated independently in-app anyway, so we don't need the transport layer to
  guarantee delivery — the application layer already has its own correctness check (see "zero data
  loss" below).

### Why a serial (COM port) fallback?
Not every scanner on a factory floor is networked. Older or on-demand handheld scanners are
wired via RS-232/USB-serial. The `ondemand_scanner_config` and `ComPortReader`/`ComPortWriter`
classes exist so the same app logic (`handle_ondemand_scan`, validation, logging) works whether
the physical link is UDP or serial — the app checks the saved config (`if 'port' in config` vs
`if 'local_ip' in config`) and reconnects with the right reader type. This also covers customers
whose network infrastructure isn't reliable enough for UDP, or who don't want to put the scanner on
the plant network at all.

---

## 2. Networking: TCP vs UDP

### TCP vs UDP, plainly
- **TCP**: connection-oriented, ordered, reliable (retransmits lost packets), has handshake and ACK
  overhead, flow/congestion control. Good for things where every byte must arrive and order matters
  (file transfer, web pages).
- **UDP**: connectionless, no ordering or delivery guarantees, minimal overhead, lower and more
  predictable latency. Good for small, frequent, independent messages where an occasional miss is
  tolerable or is handled at the application level.

### Why UDP was chosen (repeat, network-specific angle)
Because each scan event is self-contained — there's no multi-packet "conversation" to keep in
order — TCP's guarantees buy nothing here and its connection setup/teardown would add latency on
every scan burst. UDP's low overhead matches the "fire QR code, get pass/fail back fast" pattern
of the hardware.

### What happens if packets are lost?
At the UDP layer, a lost packet is simply a scan that never arrived — the reader's
`socket.recvfrom()` call just doesn't return for that scan. In practice this means the physical
card was scanned but the validator never saw it. This is a real and known trade-off. The design
choice is: if a scan genuinely reaches the socket, the app's checksum + dictionary lookup is 100%
reliable — the risk is entirely at the network layer, not the application layer. Mitigations
actually in the app:
- `SO_REUSEADDR` + binding to the *specific* NIC (not `0.0.0.0`) avoids a whole class of silent
  drops caused by multi-NIC systems listening on the wrong interface.
- Short socket timeout (0.5s) means the read loop is always alive and ready, not blocked
  indefinitely — it never "misses" a packet because it was busy elsewhere.
- The output side (`UDPWriter.send`) reports success/failure back to the UI immediately, so a
  failed send to the PLC is visible, not silent.
- For links where even occasional loss is unacceptable, the serial fallback is used instead —
  serial is a wired, point-to-point, ordered stream with no packet loss in the way UDP can have.

### How did you ensure "zero data loss" (be precise about what this means)
It's important to be accurate here in an interview: UDP itself doesn't guarantee delivery, so
"zero data loss" in this project refers to **state and log integrity**, not "every UDP packet is
guaranteed to arrive." Concretely:
- **Atomic cache writes**: `atomic_write_cache()` writes to a `.tmp` file, `flush()`s and `fsync()`s
  it to force the OS to actually commit it to disk, then does an atomic `os.replace()` onto the real
  cache file. That means a crash or power cut mid-write leaves either the old file or the fully-new
  file — never a half-written, corrupted one.
- **Retry on save**: cache saves retry up to 3 times with a short backoff if the file is
  transiently locked (`PermissionError`/`OSError`), which happens on Windows when antivirus or
  another process briefly holds the file.
- **State recovery on restart**: `current_card_index`, scan side, and start-card status are part of
  the persisted cache, so after a crash the app resumes from the last confirmed position instead of
  restarting the whole batch.
- **Thread-safe cache access**: `RLock` guards cache read/modify/write so the two heads (or a
  save triggered mid-scan) can't corrupt each other's writes.
- If you're asked "so could a UDP packet still be lost" — the honest answer is yes, that's a
  physical network layer risk, which is why the app is built to *never lose what it did receive*
  rather than claim it can force UDP to be lossless (that would require switching transport or
  adding an app-level ACK/retransmit protocol, which wasn't necessary for this use case).

---

## 3. Real-Time Systems

### What is "real-time processing" here?
In the strict embedded-systems sense, this isn't a hard real-time system (no guaranteed
worst-case deadline enforced by an RTOS). What's meant in this project is **soft real-time**: the
system responds fast enough (sub-second, typically single-digit milliseconds for the actual
validation logic) that from the operator's and the production line's point of view, the pass/fail
decision feels instantaneous and keeps up with the physical card speed.

### How did you process ~2 cards/sec (or scanner-limited throughput) without lag?
- **O(1) validation**: the expected sequence isn't searched linearly. On file load, every QR code
  is placed into a dictionary (`qr_to_index`), so validating a scan is a single hash lookup
  regardless of whether the file has 100 or 100,000 cards.
- **Non-blocking I/O with short timeouts**: `UDPReader` uses `socket.settimeout(0.5)` in a loop, so
  it's always either receiving a packet or briefly checking `self.running` — it never blocks the
  thread indefinitely and never blocks the UI thread at all, since it lives in its own
  `threading.Thread`.
- **Signals instead of direct calls**: the background thread never touches a widget. It emits a Qt
  signal; Qt queues that to the UI thread's event loop. This decouples "how fast scans arrive" from
  "how fast the UI can redraw," so a burst of scans can't stall the reader.
- **Two cards/sec is well within scanner + Python's headroom** — the actual ceiling is the physical
  scanner hardware, not the validation code. The dictionary lookup and signal emit both run in
  microseconds.

### How did you prevent application lag?
- All blocking work (socket reads, serial reads, file parsing of large CPD files) happens off the
  UI thread.
- UI updates happen via signal/slot, batched implicitly by Qt's event loop rather than being forced
  synchronously on every single scan.
- Heavy one-off operations (like network interface pings for connectivity checks) run in their own
  background thread rather than on the scan path, so a slow ping never delays a live scan.

---

## 4. RSA Licensing

### What is RSA, in this context?
RSA is an asymmetric (public/private key) cryptographic algorithm. It's used here not to encrypt
license data, but to **sign** it — proving a license file was issued by the actual vendor and
hasn't been tampered with or copied to another machine.

### Public key vs private key — how it's actually used in `licensing.py`
- The **private key** stays with the vendor/developer and is never shipped with the app. It's used
  offline to sign a customer's machine fingerprint when issuing a license.
- The **public key** is embedded directly in the shipped code (`PUBLIC_KEY_PEM` in
  `src/services/licensing.py`). It can only *verify* signatures, not create them — so even if
  someone fully decompiles the .exe, they get the public key, which is useless for forging a new
  valid license.
- Machine identity: `get_machine_fingerprint()` reads hardware serials (motherboard, CPU, primary
  disk via `wmic`) and hashes them with SHA-256 into a single fingerprint string. This ties a
  license to one physical machine.
- License file (`license.dat`) format is `fingerprint:signature_hex` — the fingerprint the vendor
  signed, plus the RSA signature (PSS padding, SHA-256) over that fingerprint.
- On startup, `validate_license()`:
  1. Recomputes the current machine's fingerprint.
  2. Loads `license.dat`, splits it into `license_fingerprint` and `signature`.
  3. Uses the embedded public key to verify the signature against `license_fingerprint`
     (`public_key.verify(...)`, catching `InvalidSignature`).
  4. If the signature is valid *and* `license_fingerprint == machine_fingerprint`, the app runs;
     otherwise it shows a `QMessageBox.critical` and calls `sys.exit(1)`.

### Why RSA instead of a simple license key string?
A plain license key (e.g., "XXXX-XXXX-XXXX") only proves the user typed *something* — it can be
guessed, brute-forced, or the same key can be shared across unlimited machines with no way to
detect it. RSA signing solves two things a plain key can't:
1. **Authenticity** — only someone holding the private key can produce a signature the embedded
   public key will accept. You can't forge a valid `license.dat` without the private key, even
   knowing exactly how the format works.
2. **Machine binding without a server** — because the signed payload *is* the hardware fingerprint,
   a license is cryptographically tied to one machine. Copying `license.dat` to another PC changes
   the recomputed fingerprint, so `license_fingerprint == machine_fingerprint` fails, without
   needing an internet connection or license server (important for factory floor PCs that may be
   air-gapped).

### Honest limitation to mention if pushed
Signature verification only proves the *license data* wasn't tampered with — it doesn't stop
someone from patching the compiled app itself to skip the `validate_license()` call entirely (the
internal testing report flags this explicitly as "licensing bypass via source modification"). A
fully tamper-proof scheme would need code signing / obfuscation (the project does bundle
`pyarmor` for this) or a server-side check, which is a legitimate trade-off given this is an
offline, factory-floor deployment.

---

## 5. Debugging & Testing

### Biggest bug you faced (a real, concrete story)
The most subtle bug was in **bottom-to-top scan-direction jump handling**
(`BOTTOM_TO_TOP_SCAN_JUMP_BUG_FIX.md`). The app tracks two different notions of position:
`current_card_index` (the scan position, counting from the direction scanning started) and the
underlying array index in the loaded file. For top-to-bottom scanning these are the same number,
which hid a bug for a long time — it only showed up for bottom-to-top scanning.

When a card was skipped and scanned out of order (a "jump"), the code converted array index → scan
position *before* emitting a signal, then the resolution handler converted scan position → array
index *again* when the user confirmed the skip. That double conversion meant that on a 2500-card
file, jumping from entry 399 to entry 398 sent the UI to entry **2101** instead — completely wrong,
and dangerous in a QA tool because it would have made the app think the wrong card was "current."

Root cause: the same value was being translated back and forth between two coordinate systems at
two different points in the call chain, and the two conversions didn't cancel out the way they were
assumed to. The fix was to settle on **one** convention — pass the raw array index through the
signal untouched, and only convert to scan position at UI-display boundaries — so there was a single
source of truth for "where are we in the file" regardless of scan direction. A follow-up bug in the
same area was found in the SKIPPED-entries logging loop, which was off-by-one and included the
current expected card and the just-scanned card in the "skipped" list — fixed by adjusting the
range bounds so only the cards strictly *between* them were logged.

Lesson to state in an interview: bugs involving two coordinate systems (array index vs. logical
scan position, or similarly, local time vs UTC, 0-indexed vs 1-indexed) are dangerous precisely
because each individual conversion looks locally correct — the bug only appears when you trace the
value through the *entire* path end to end, which is why the fix included adding temporary debug
prints at each conversion point to see the actual numbers at runtime rather than reasoning about it
purely by re-reading the code.

### How did you test reliability?
- **Static analysis / code review pass** across the whole codebase specifically looking for
  concurrency issues, silent `except: pass` blocks, and unvalidated inputs
  (`COMPREHENSIVE_TESTING_REPORT.md`) — this surfaced real issues like race conditions around
  cache writes and command-injection risk in `subprocess` calls using `shell=True` with
  user-supplied IPs, which were then fixed.
- **Manual scenario testing** with real hardware: serial scanners on actual COM ports, UDP scanners
  across multiple physical NICs (to catch the 0.0.0.0 multi-NIC binding conflict), and both heads
  running simultaneously to confirm no cross-head interference.
- **Power-loss / crash simulation**: killing the process mid-scan and mid-cache-write to confirm the
  atomic write (`temp file + fsync + os.replace`) left the cache in a recoverable state and the app
  correctly resumed from `current_card_index` on restart.
- **Direction-specific regression testing**: after the jump bug fix, explicit test cases were run
  for both top-to-bottom and bottom-to-top scanning, near-file-start and near-file-end jumps, and
  large jumps (100+ cards) to make sure the fix didn't regress the already-working direction.

### How did you verify sequence correctness?
- The core algorithm's correctness rests on the O(1) dictionary lookup (`qr_to_index`) being built
  once, deterministically, from the parsed CPD file — so verification focused on making sure the
  dictionary construction matched the card type logic (single/half/quarter positions, rebatch
  splitting) exactly, by cross-checking generated logs and exported CSVs against the source CPD
  file by hand for several representative files (small ones by hand, large ones by scripted diff).
- Three-way status classification (OK / OK (JUMPED) / NOT OK) was tested against constructed
  sequences with known defects: cards scanned in order, cards skipped forward, cards scanned twice,
  cards scanned from the wrong file, and wrong-side scans (e.g., a "right" half-card QR scanned
  when a "left" was expected) — each has to map to the correct status and the correct PLC output
  signal.
- Checksum stripping (0–6 configurable digits) was verified by comparing the "before/after"
  preview shown in the UI directly against what the validation code actually strips, since a
  mismatch there would silently validate against the wrong string.

---

## 6. Likely Follow-Up Traps (be ready)

- **"If UDP can lose packets, how do you guarantee no card gets missed on the line?"**
  Answer honestly: the software guarantees it never *corrupts or drops data it received*; it
  cannot force a lossy network to be lossless. That's a network/hardware reliability concern
  (wired factory Ethernet, short cable runs, no Wi-Fi) outside the app's control, and it's why
  serial is offered as a wired, guaranteed-delivery alternative for links where that matters more
  than UDP's lower latency.
- **"Why not just use TCP and get reliability for free?"**
  TCP's retransmission would reorder/delay a scan relative to the physical card motion — by the
  time a retransmitted packet arrived, the card would already be past the reject gate. For this use
  case, a timely "maybe missed" is more useful operationally than a late "definitely received."
- **"Isn't RSA overkill for a $-value license?"**
  It's proportional to the actual threat: a factory-floor tool distributed as a single .exe with no
  phone-home capability. Asymmetric signing is the standard way to bind a license to hardware
  without needing a license server, and the cost (one verify call at startup) is negligible.
