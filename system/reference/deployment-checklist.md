# Deployment Checklist

Użyj przy wdrożeniu projektu u nowego klienta lub na nowym środowisku.

---

## Ogólny checklist (każde wdrożenie)

### 1. Konfiguracja środowiska
- [ ] Credentials / API keys skonfigurowane
- [ ] Zmienne środowiskowe ustawione
- [ ] Endpointy / URLs zaktualizowane (nie stare testowe)
- [ ] Dostępy do zewnętrznych usług (bazy, storage, API) zweryfikowane

### 2. Dane i zasoby
- [ ] Foldery / buckety / tabele utworzone na koncie klienta
- [ ] Identyfikatory zasobów zaktualizowane w konfiguracji
- [ ] Dane testowe usunięte / zastąpione produkcyjnymi

### 3. Test przed go-live
- [ ] Uruchom z jednym przykładem testowym
- [ ] Sprawdź logi — brak błędów
- [ ] Zweryfikuj output w docelowym miejscu
- [ ] Przetestuj edge case: puste dane, nieprawidłowy format

### 4. Po wdrożeniu
- [ ] Aktywuj workflow / uruchom serwis
- [ ] Poinformuj klienta co i jak
- [ ] Udokumentuj w tym pliku co zostało zmienione

---

## [Nazwa procesu / workflow]

### Co zmienić u nowego klienta

| Element | Gdzie | Wartość do zmiany |
|---------|-------|-------------------|
| — | — | — |

### Znane problemy przy wdrożeniu

<!-- edge cases, wymagania środowiskowe, pułapki -->

### Test

1. ...
2. ...

---

## Dodawanie nowego procesu do tego pliku

```
## [Nazwa]
### Co zmienić u nowego klienta
### Znane problemy przy wdrożeniu
### Test
```
