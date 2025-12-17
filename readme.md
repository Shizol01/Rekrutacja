}

# ⏱️ Rejestracja czasu pracy (QR / Tablet)

Aplikacja do rejestrowania czasu pracy pracowników z wykorzystaniem kodów QR
oraz generowania raportów czasu pracy.


* poprawnej architektury backendu,
* rozdzielenia API i warstwy prezentacji (HTML),
* logiki biznesowej (walidacje, raporty, anomalie),
* czytelnego i testowalnego kodu.

---

## 🧠 Architektura projektu

Projekt został podzielony na trzy wyraźne warstwy:

```
time_tracking/
├── api/        → REST API (JSON / CSV)
├── web/        → Widoki HTML (tablet, panel admina)
├── services/   → Logika biznesowa (jedno źródło prawdy)
```

* **API** – Django REST Framework, dane w formacie JSON / CSV
* **Web** – klasyczne widoki Django (render HTML)
* **Services** – walidacja zdarzeń, liczenie czasu pracy, raporty, anomalie

Taki podział umożliwia łatwe rozszerzenie projektu (np. React / mobile app)
bez naruszania logiki biznesowej.

---

## 🛠️ Technologie

### Backend

* Python 3.11+
* Django
* Django REST Framework
* SQLite
* Django Admin
* pytest / pytest-django (testy)

---

## 📋 Funkcjonalności

### 1️⃣ Rejestracja czasu pracy (QR / Tablet)

Obsługiwane zdarzenia:

* `CHECK_IN` – rozpoczęcie pracy
* `CHECK_OUT` – zakończenie pracy
* `BREAK_START` – rozpoczęcie przerwy
* `BREAK_END` – zakończenie przerwy

Każde zdarzenie zapisywane jest z:

* pracownikiem
* typem zdarzenia
* timestampem (generowany po stronie serwera)
* identyfikatorem urządzenia (tablet)

Walidacja logiki:

* brak `CHECK_OUT` bez wcześniejszego `CHECK_IN`
* brak `BREAK_END` bez `BREAK_START`
* brak `BREAK_START` bez aktywnego `CHECK_IN`
* wykrywanie anomalii (np. brak `CHECK_OUT`, wyjście bez wejścia)

Tablet komunikuje się wyłącznie z API – backend **nie przetwarza obrazu QR**,
otrzymuje jedynie token pracownika.

---

### 2️⃣ Grafik pracy (administrator)

Grafik definiowany w **Django Admin**:

* pracownik
* data
* planowany start i koniec
* typ dnia:

  * `WORK`
  * `OFF`
  * `LEAVE`

Dostępne jest API umożliwiające pobranie grafiku:

* dla jednego pracownika
* dla konkretnej daty
* dla zakresu dat

---

### 3️⃣ Raporty czasu pracy

Raport generowany dla wybranego **zakresu dat** (np. tydzień / miesiąc).

Raport per pracownik zawiera:

* planowany czas pracy (z grafiku)
* faktycznie przepracowany czas
* czas przerw
* spóźnienia (konfigurowalny próg)
* absencje (dzień `WORK` bez `CHECK_IN`)
* urlopy
* listę anomalii:

  * brak `CHECK_OUT`
  * przerwa bez zakończenia
  * wyjście bez wejścia
  * praca bez grafiku (`NO_SCHEDULE`)

Dostępne formaty:

* **HTML** (panel administracyjny)
* **JSON**
* **CSV** (eksport)

---

## 🖥️ Interfejs użytkownika (HTML)

Projekt zawiera prosty interfejs oparty o HTML + CSS:

* **Dashboard** – punkt wejścia do systemu
* **Tablet** – ekran skanowania QR i rejestracji zdarzeń
* **Panel live** – podgląd aktualnego statusu pracowników
* **Raporty** – raporty czasu pracy z możliwością eksportu CSV

Z każdego widoku możliwy jest powrót do dashboardu.

---

## 🔌 Endpointy API (przykłady)

### Rejestracja zdarzeń (tablet)

POST `/api/tablet/events/`

```json
{
  "employee_qr_token": "TOKEN_PRACOWNIKA",
  "device_id": "tablet-01",
  "event_type": "CHECK_IN"
}
```

---

### Status pracownika (tablet)

GET `/api/tablet/status/?qr=TOKEN&device=tablet-01`

---

### Grafik pracy

GET `/api/admin/schedules/?from=YYYY-MM-DD&to=YYYY-MM-DD`

---

### Raport czasu pracy

GET `/api/admin/reports/attendance/?from=YYYY-MM-DD&to=YYYY-MM-DD`

CSV:
GET `/api/admin/reports/attendance.csv/?from=YYYY-MM-DD&to=YYYY-MM-DD`

---

## 🧪 Dane testowe

Projekt zawiera skrypt `populate.py`, który generuje **realistyczne dane demo**:

* pracowników
* urządzenia (tablety)
* grafik pracy (WORK / OFF / LEAVE)
* zdarzenia:

  * poprawne dni pracy
  * spóźnienia
  * absencje
  * anomalie
  * praca bez grafiku

Uruchomienie:

```bash
python populate.py
```

---

## 🧪 Testy

Projekt zawiera testy jednostkowe obejmujące:

* walidację sekwencji zdarzeń
* logikę raportów (absencje, anomalie)
* API statusu tabletu

Uruchomienie testów:

```bash
pytest
```

---

## ▶️ Uruchomienie projektu

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Dostępne adresy:

* Dashboard: `http://localhost:8000/`
* Tablet: `http://localhost:8000/api/tablet/`
* Panel admina (live): `http://localhost:8000/api/admin-panel/live/`
* Django Admin: `http://localhost:8000/admin/`
