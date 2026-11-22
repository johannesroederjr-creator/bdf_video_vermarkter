# Projekt Sales Intelligence – Erklärvideo (Rundgang)

Das Video wird per Python-Code erzeugt: Die Aufnahme des echten Dashboards (`assets/aufnahme.mp4`) wird zugeschnitten, gezoomt, hervorgehoben und mit Texten versehen. Das Ergebnis ist ein Video ohne Ton im 16:9-Format (1920×1080, 30 Bilder/s).

## Einmalige Einrichtung (Windows)
1. **Python 3.10+** installieren (python.org, beim Setup „Add Python to PATH“ anhaken).
2. **ffmpeg** installieren: in der Eingabeaufforderung `winget install Gyan.FFmpeg`, danach Eingabeaufforderung neu öffnen. Prüfen mit `ffmpeg -version`.
3. Im Projektordner: `pip install -r requirements.txt`

Empfehlung: Projektordner **außerhalb von OneDrive** ablegen (z. B. `C:\Projekte\Sales_Intelligence`). Beim Rendern entstehen mehrere hundert MB Zwischendateien.

## Video erzeugen
| Wunsch | Befehl |
|---|---|
| Nur Standbilder prüfen (schnell) | `python build.py vorschau 1:6.5 3:20.0` (Abschnitt:Sekunde) → `temp/vorschau_*.png` |
| Alles rendern (ca. 4–8 Min.) | `python build.py render` |
| Nur einen Abschnitt neu rendern | `python build.py render 3` |
| Komplettes Video (mit Abfrage + Abspann) | `python build.py zusammenfuegen` → `ausgabe/Sales_Intelligence_Rundgang_komplett.mp4` |
| Version für die Website | `python build.py web` → `ausgabe/sales-intelligence_web.mp4` und `ausgabe/poster.jpg` |

Abschnitte: 0 Einstieg · 1 Cockpit · 2 Kundenbewegungen · 3 Verkaufschancen · 4 Abfrage · 5 Abspann.
Nach Änderungen: den betroffenen Abschnitt rendern, dann `zusammenfuegen` (und ggf. `web`).
Doppelklick-Variante: `render_alles.bat`.

## Was wo geändert wird
- **`inhalt.py`** – alles Inhaltliche:
  - `T`: Texte im Einstieg, Abspann und in der Abfrage (inkl. E-Mail-Adresse, Button-Text, Dankeschön-Satz).
  - `OPTS`: die vier Antwortoptionen.
  - `CL_B`, `CL_C`, `CL_D`: Ausschnitte der Aufnahme (`src` = von/bis in Sekunden der Aufnahme, `out` = Dauer im Video; `out` größer als die Länge = Zeitlupe).
  - `SPEC_B`, `SPEC_C`, `SPEC_D`: die Stationen (`beats`) mit Zeiten, Zoomziel, Rahmen und Blasen-Text. Zeiten (`t0`, `t1`) laufen ab Beginn des jeweiligen Abschnitts.
  - `DAUER`: Länge von Einstieg, Abfrage und Abspann.
- **`engine.py`** – Farben (aus der Website: #0969da, #218bff), Schriften (Instrument Sans, DM Sans), Hintergrund.
- **`build.py`** – Zeichen- und Render-Logik. Nur anfassen, wenn sich das Aussehen der Elemente ändern soll (z. B. Blasenform).
- **`assets/`** – `aufnahme.mp4` (Quelle: Bildschirmaufnahme vom 20.11.), `logo.png` (aus der Website), `fonts/`.

## Neue Aufnahme einsetzen
Neue Datei als `assets/aufnahme.mp4` ablegen. Danach in `inhalt.py` die Zeiten (`src`) und die Rechtecke (`P1`, `P3`, `P4`) anpassen – sie beziehen sich auf Sekunden und Pixel der Aufnahme. Standbilder mit `vorschau` prüfen. Die Aufnahme hat oben und unten je 14 Pixel schwarzen Rand, das ist in den Koordinaten bereits berücksichtigt (`R(...)`).

## Hinweise
- Das Video enthält synthetische Beispieldaten; das steht unten rechts im Bild.
- Die Reihenfolge der Abschnitte und die Zeiten der Aufnahme (z. B. „Klick bei 25,5 s“) sind fest auf die Aufnahme vom 20.11. abgestimmt.
- Der Ablauf ist deterministisch: gleicher Code und gleiche Aufnahme ergeben dasselbe Video.
