# Kaufland Discounts

Kleiner, inoffizieller Python-Client für aktuelle Angebote aus physischen Kaufland-Märkten.

Das Projekt kann als CLI genutzt werden oder direkt als kleiner API-Wrapper in Python-Code. Es geht hier ausdrücklich um Kaufland-Filialen und deren Angebote, nicht um den Kaufland Online-Marktplatz.

> Dieses Repo enthält keine Zugangsdaten. Benötigte Werte müssen lokal über `.env` bereitgestellt werden.

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
MobilePayment, LoyaltyProgram, LoyaltyPointsProgram, LoyaltyCoupons, AdBanner, PartnerBenefits, KScanDZ, Xtra
Open: Mon, Tue, Wed, Thu, Fri, Sat
Closed: Sun
Offers: 56
  MÜLLER:       Kefir oder Ayran                     |     0.88 | (1 kg = 1.76)      | loyalty    0.79* | 2026-04-30 – 2026-05-06
  ZOTT:         Zottarella Classic-Rolle             |     2.22 | Abtropfgewicht ... | loyalty    1.99* | 2026-04-30 – 2026-05-06
  NESTLÉ ...    Eisgenuss                            |     1.99 | (1 l = 2.37 - 7... | loyalty    1.79* | 2026-04-30 – 2026-05-06
  DOVGAN:       Plombir Eis                          |     2.79 | (1 l = 3.58 - 8... | loyalty    2.49* | 2026-04-30 – 2026-05-06
  YOUCOOK:      Fertiggericht                        |     3.79 | (1 kg = 9.03)      | loyalty    3.49* | 2026-04-30 – 2026-05-06
  POPP:         Feinkostsalat                        |     1.89 | (1 kg = 4.73)      | loyalty    1.69* | 2026-04-30 – 2026-05-06
  MILKA:        Pralinés oder Hauchzarte Herzen      |     1.69 | (1 kg = 13.00 -... | loyalty    1.49* | 2026-04-30 – 2026-05-09
  LAMBERTZ:     Coco-Fleur, Balena oder Divina       |     1.49 | (1 kg = 11.92 -... | loyalty    1.29* | 2026-04-30 – 2026-05-09
  SÖHNLEIN:     Brillant Sekt oder weinhaltiges G... |     2.69 | (1 l = 3.59)       | loyalty    2.49* | 2026-04-30 – 2026-05-09
  BECK'S:       Pils oder Gold                       |    10.99 | (1 l = 1.10)       | loyalty    9.99* | 2026-04-30 – 2026-05-06
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

## Referenzen

Die Implementierung orientiert sich an öffentlich verfügbaren live Client- und Testreferenzen rund um die Kaufland-App-API, unter anderem an einer archivierten SchwarzIT-Referenz:

- [SchwarzIT/iosklbasekit – REST-Testreferenz](https://github.com/SchwarzIT/iosklbasekit/blob/ecee80d2d7f803cbde49a038617a56053752a93e/KLBaseKitTests/REST/TestTests.swift#L28) <!--- Working live Kaufland api test -->

Dieses Repository enthält bewusst keine eingebetteten Auth-Werte.

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

## Inspiration

Inspiriert durch [`torbenpfohl/rewe-discounts`](https://github.com/torbenpfohl/rewe-discounts).

Ich wollte eine kleine Automation bauen, die mir einen Überblick über aktuelle Angebote aus verschiedenen Märkten in meiner Nähe gibt, ohne dafür mehrere unterschiedliche Apps öffnen zu müssen.

Weitere kleine API-Wrapper für andere Märkte, zum Beispiel Edeka, sind geplant beziehungsweise existieren bereits als PoC.

## Hinweise

Das Projekt ist inoffiziell und kann jederzeit nicht mehr funktionieren, wenn Kaufland die App-API oder deren Antwortformat ändert.
Bitte keine großen Mengen Requests automatisiert abfeuern. Das Tool ist für kleine lokale Abfragen gedacht.

## Lizenz

Dieses Projekt ist unter der Apache-2.0 Lizenz lizenziert. Siehe [LICENSE](LICENSE) für Details.
