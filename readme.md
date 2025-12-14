# ⏱️ Rejestracja czasu pracy (QR / Tablet)

Aplikacja do rejestrowania czasu pracy pracowników z wykorzystaniem kodów QR
oraz generowania raportów czasu pracy.

Projekt wykonany jako **zadanie rekrutacyjne** – celem jest pokazanie poprawnej
architektury backendu, logiki biznesowej oraz czytelnego API.

---

## 🛠️ Technologie

### Backend

* Python 3.11+
* Django
* Django REST Framework
* SQLite
* Django Admin

### Frontend (demo)

* Vue 3

---

## 📋 Funkcjonalności

### Rejestracja czasu pracy (QR / Tablet)

Obsługiwane zdarzenia:

* CHECK_IN
* CHECK_OUT
* BREAK_START
* BREAK_END

Każde zdarzenie zawiera:

* pracownika
* typ zdarzenia
* timestamp (generowany po stronie backendu)
* identyfikator urządzenia (tablet)

Walidacja logiki:

* brak CHECK_OUT bez wcześniejszego CHECK_IN
* brak BREAK_END bez BREAK_START
* brak BREAK_START bez aktywnego CHECK_IN
* wykrywanie wielokrotnego CHECK_IN (anomalia)

---

### Grafik pracy (administrator)

Grafik definiowany w Django Admin:

* pracownik
* data
* planowany start i koniec
* typ dnia:

  * WORK
  * OFF
  * LEAVE

Możliwości:

* tworzenie / edycja / usuwanie grafiku
* API do pobierania grafiku:

  * dla jednego pracownika
  * dla konkretnej daty
  * dla zakresu dat

---

### Raporty czasu pracy

Raport generowany dla zakresu dat.

Raport per pracownik zawiera:

* planowany czas pracy
* faktycznie przepracowany czas
* czas przerw
* spóźnienia
* absencje
* listę anomalii

Formaty:

* JSON
* CSV

---

## 📱 Model działania QR / Tablet

* Każdy pracownik posiada **własny kod QR**
* Kod QR zawiera **token pracownika**
* Tablet skanuje kod QR
* Tablet wysyła do API:

  * token pracownika
  * identyfikator urządzenia
  * typ zdarzenia
* Backend zapisuje zdarzenie i wykonuje walidację

Backend **nie przetwarza obrazu QR** – otrzymuje wyłącznie dane.

---

## 🔌 Endpointy API

### Rejestracja zdarzeń (tablet)

POST `/api/tablet/events/`

```json
{
  "employee_qr_token": "UUID_PRACOWNIKA",
  "device_id": "tablet-01",
  "event_type": "CHECK_IN"
}
```

---

### Grafik pracy

GET `/api/admin/schedules/`

Parametry:

* employee_id
* date
* from
* to

---

### Raport czasu pracy

GET `/api/admin/reports/attendance/?from=YYYY-MM-DD&to=YYYY-MM-DD`

CSV:
GET `/api/admin/reports/attendance.csv/?from=YYYY-MM-DD&to=YYYY-MM-DD`

---

## 🧪 Dane testowe

Projekt zawiera plik `populate.py`, który generuje:

* pracowników
* urządzenia (tablety)
* grafik pracy
* zdarzenia (w tym anomalie)

Uruchomienie:

```bash
python populate.py
```

---

## ▶️ Uruchomienie projektu

### Backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Panel admina:

```
http://localhost:8000/admin/
```

---

### Frontend (demo)

```bash
cd frontend
npm install
npm run dev
```

Frontend:

```
http://localhost:5173
```

---

## 🔐 Uwaga

W wersji demonstracyjnej:

* endpointy raportów i grafiku są dostępne bez autoryzacji
* Django Admin pozostaje zabezpieczony

W środowisku produkcyjnym endpointy API powinny być chronione.

---

## ✅ Podsumowanie

Projekt spełnia wymagania zadania rekrutacyjnego:

* rejestracja czasu pracy przez QR / tablet
* walidacja logiki zdarzeń
* obsługa grafiku pracy
* generowanie raportów
* czytelna architektura backendu
* prosty frontend prezentacyjny
