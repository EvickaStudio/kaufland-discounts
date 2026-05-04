# Kaufland Discounts

Kleiner, inoffizieller Python-Client für aktuelle Angebote aus physischen Kaufland-Märkten.

Das Projekt kann als CLI genutzt werden, oder direkt als kleiner API-Wrapper in Python-Code. Es geht hier ausdrücklich um Kaufland-Filialen und deren Angebote, nicht um den Kaufland Online-Marktplatz.

## Was macht das Tool?

- Kaufland-Märkte suchen
- Marktinformationen anzeigen
- aktuelle Angebote für einen Markt laden
- Ausgabe als einfache CLI-Liste

Beispiel:

```bash
uv run main.py Frankfurt --limit 10
```

Beispielausgabe:

```text
Kaufland Frankfurt/Main-Griesheim (DE1483)
Mainzer Landstraße 683, 65933 Frankfurt am Main, DE
50.0998058, 8.5872564
069/5800263-0
Open: Mon, Tue, Wed, Thu, Fri, Sat
Closed: Sun
Offers: 56
  MÜLLER | 0.88 | 2026-04-30 – 2026-05-06
  ZOTT | 2.22 | 2026-04-30 – 2026-05-06
```

## Scope

Dieses Repo enthält bewusst nur den kleinen Teil, der für Markt- und Angebotsdaten benötigt wird.

Nicht enthalten sind z.B.:

- Login-Flows und Nutzer-/Profilverwaltung
- Loyalty-Guthaben, Coupons, Partnerbenefits
- Marktplatz-Funktionen
- Alles was mit Zahlungen zu tun hat
- Einkaufslisten (sync), Scan-Apps / Self-Checkout-Warenkorb
- Angebotsalarme
- ...

Das Projekt ist read-only gedacht.

## Installation

Voraussetzung:

- Python 3.12+
- `uv` oder normales `pip`

Mit `uv`:

```bash
uv sync
```

Oder mit `pip`:

```bash
pip install -e .
```

## Konfiguration

Das Projekt nutzt `pydantic-settings` und lädt optionale Werte aus einer lokalen `.env`.

Erstelle/Kopiere zuerst die `.env` und füge die benötigten Werte ein:

```bash
cp .env.example .env
```

## CLI-Nutzung

Einen Markt suchen und Angebote anzeigen:

```bash
uv run main.py Frankfurt
```

Mehr Angebote anzeigen:

```bash
uv run main.py Frankfurt --limit 20
```

Anderes Land setzen:

```bash
uv run main.py Turek --country PL
```

## Python-Nutzung

```python
from main import Kaufland

with Kaufland() as kaufland:
    store = kaufland.find_store("Frankfurt")
    offers = kaufland.offers(store.store_id)

print(store.title)
print(len(offers))
```

## Hinweise

Das Projekt ist inoffiziell und kann jederzeit nicht mehr funktionieren, wenn Kaufland die App-API oder deren Antwortformat ändert.
Bitte auch nicht aggressiv pollen oder große Mengen Requests automatisiert abfeuern. Das Tool ist für kleine lokale Abfragen gedacht.

## Lizenz

Dieses Projekt ist unter der Apache-2.0 Lizenz lizenziert. Siehe [LICENSE](LICENSE) für Details.