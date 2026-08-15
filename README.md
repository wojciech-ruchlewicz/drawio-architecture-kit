# Diagramy architektoniczne

Jeden sposób rysowania diagramów komponentów i topologii, oparty na draw.io i na plikach `*.drawio.svg` trzymanych w repozytorium obok kodu.

## Co to daje

**Diagram żyje w gicie razem z kodem.** Zmiana architektury i zmiana diagramu idą w jednym merge requeście i przechodzą to samo review. Nie ma osobnego miejsca, które trzeba pamiętać, żeby zaktualizować.

**Jeden plik jest jednocześnie obrazkiem i źródłem.** `*.drawio.svg` renderuje się w markdownie, GitLabie i MkDocs bez żadnego kroku budowania, a po kliknięciu otwiera się w edytorze. Żadnego eksportowania, żadnej pary „diagram i jego PNG".

**Edycja w VS Code, offline.** Wtyczka Draw.io Integration ma wbudowany edytor, więc treść diagramów nie opuszcza stacji roboczej.

**Copilot to czyta i potrafi tym operować.** Źródło diagramu jest tekstem osadzonym w pliku, więc asystent widzi nazwy komponentów, opisy i etykiety strzałek. Ponieważ diagram leży obok kodu, można go zapytać, czy jeden nadal odpowiada drugiemu.

**Gotowe elementy zamiast projektowania od zera.** Paleta powyżej zawiera wszystko, czego potrzeba. Rysowanie sprowadza się do kopiowania i podpisywania.

## Jak zacząć

1. Zainstaluj wtyczkę VS Code **Draw.io Integration** (`hediet.vscode-drawio`).
2. Skopiuj [`templates/blank.drawio.svg`](templates/blank.drawio.svg) do `docs/diagrams/<obszar>-components.drawio.svg`. Ustawienia diagramu są już w nim zapisane, zostaje uzupełnić nagłówek.
3. Otwórz obok [`templates/palette.drawio.svg`](templates/palette.drawio.svg) i przeciągaj z niej elementy. `Ctrl+C` i `Ctrl+V` działają między zakładkami draw.io.

Tyle wystarczy na pierwszy diagram. Reszta zasad, wraz z uzasadnieniami, jest w [specyfikacji](docs/diagrams.md).

## Jak to wygląda

![Order Execution, komponenty logiczne](examples/components-example.drawio.svg)

Kolejne przykłady i pełen opis notacji: [`docs/diagrams.md`](docs/diagrams.md).

## Paleta elementów

![Paleta elementów](templates/palette.drawio.svg)

## Zawartość repozytorium

| Ścieżka | Rola |
|---|---|
| [`docs/diagrams.md`](docs/diagrams.md) | Specyfikacja: format pliku, poziomy C4, reguły, układ, checklista |
| [`templates/blank.drawio.svg`](templates/blank.drawio.svg) | Pusty diagram z gotowymi ustawieniami |
| [`templates/palette.drawio.svg`](templates/palette.drawio.svg) | Paleta elementów |
| [`examples/`](examples/) | Kompletne diagramy komponentów i topologii |
| [`tools/gen.py`](tools/gen.py) | Generator palety, szablonu i przykładów |
