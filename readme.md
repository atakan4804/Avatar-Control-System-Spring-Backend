# Sensorserver

# Author

Atakan Celik
Bachelor Thesis – Real-Time Avatar Control System


Dieses Projekt implementiert einen Spring-Boot-basierten Sensorserver zur Echtzeitübertragung und Verarbeitung von Sensordaten für die Avatar Steuerung.

Die Kommunikation erfolgt über WebSockets und HTTPS. Zusätzlich wird eine lokale HTML-Seite über einen Python-HTTPS-Server bereitgestellt.

Für die vollständige Funktionalität wird zusätzlich das zugehörige Unity-Projekt inklusive der entsprechenden Avatar-, Netzwerk- und Steuerungsskripte benötigt.

---

# Voraussetzungen

Für das Projekt werden folgende Komponenten benötigt:

- Java 21

- IntelliJ IDEA

- Python 3.14 oder neuer

- Gradle (oder Gradle Wrapper)

- lokale SSL-Zertifikate

- Unity Hub

- Unity Editor

- das zugehörige Unity-Projekt inklusive aller benötigten Skripte

---

# HTTPS-Server starten

Vor der Verwendung muss der lokale HTTPS-Python-Server im Terminal gestartet werden.

Im Projektordner folgenden Befehl ausführen:

```bash
python3 -m http.server 8000 \
  --bind 0.0.0.0 \
  --directory . \
  --tls-cert certs/your-cert.pem \
  --tls-key certs/your-key.pem
```
Hinweis:  
Eigene lokale SSL-Zertifikate müssen im `certs`-Ordner hinterlegt werden.

Der Server läuft anschließend unter:

```text
https://localhost:8000
```

Die HTML-Seite kann geöffnet werden über:

```text
https://localhost:8000/index.html
```