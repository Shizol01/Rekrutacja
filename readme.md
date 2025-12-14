# ⏱️ Rejestracja czasu pracy (QR / Tablet)

Prosta aplikacja do rejestracji czasu pracy pracowników z wykorzystaniem kodów QR oraz generowania raportów czasu pracy.

Projekt został wykonany jako **zadanie rekrutacyjne** i skupia się na poprawnej logice backendowej, architekturze oraz czytelnym API.

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

### Rejestracja czasu pracy (tablet / QR)

* CHECK_IN / CHECK_OUT
* BREAK_START / BREAK_END
* rejestracja zdarzeń przez API
* walidacja logiki zdarzeń
* wykrywanie anomalii (np. brak CHECK_OUT)

### Grafik pracy (administrator)

* zarządzanie grafikiem przez Django Admin
* typy dni: WORK / OFF / LEAVE
* endpoint API do pobierania grafiku z filtrowaniem

### Raporty czasu pracy

* raport JSON dla wybranego zakresu dat
* eksport do CSV
* raport zawiera:

  * planowany czas pracy
  * faktycznie przepracowany czas
  * czas przerw
  * spóźnienia
  * absencje
  * anomalie

---

## 📱 Model działania QR / Tablet

* Każdy pracownik posiada **swój indywidualny kod QR** (token)
* Tablet skanuje QR pracownika
* Tablet wysyła do API:

  * token pracownika
  * identyfikator urządzenia
  * typ zdarzenia
* Backend zapisuje zdarzenie i waliduje logikę

> QR code jest nośnikiem tokenu pracownika.
> Backend nie przetwarza obrazu QR – otrzymuje wyłącznie dane.

---

## 🔌 Endpointy API

### Rejestracja zdarzeń (tablet)

```
POST /api/tablet/events/
```

Przykładowy request:

```json
{
  "employee_qr_token": "UUID_PRACOWNIKA",
  "device_id": "tablet-01",
  "event_type": "CHECK_IN"
}
```

---

### Grafik pracy (read-only)

```
GET /api/admin/schedules/
```

Parametry:

* employee_id
* date
* from / to

---

### Raport czasu pracy

```
GET /api/admin/reports/attendance/?from=YYYY-MM-DD&to=YYYY-MM-DD
```

CSV:

```
GET /api/admin/reports/attendance.csv/?from=YYYY-MM-DD&to=YYYY-MM-DD
```

---

## 🧪 Dane testowe

Projekt zawiera skrypt `populate.py`, który generuje:

* pracowników
* urządzenia (tablety)
* grafik pracy
* zdarzenia czasu pracy (w tym anomalie)

Uruchomienie:

```bash
python populate.py
```

---

## ▶️ Uruchomienie

### Backend

```bash
python manage.py migrate
python manage.py runserver
```

Admin:

```
http://localhost:8000/admin/
```

### Frontend

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

W wersji demo:

* endpointy raportowe i grafiku są dostępne bez autoryzacji
* Django Admin pozostaje zabezpieczony

W środowisku produkcyjnym endpointy API powinny być chronione.

---

## ✅ Podsumowanie

Projekt spełnia wszystkie wymagania zadania rekrutacyjnego:

* poprawna rejestracja czasu pracy
* obsługa QR / tablet
* logika raportów i anomalii
* czytelna architektura backendu
* prosty frontend prezentacyjny
