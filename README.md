# Diagramy architektoniczne — system wizualny

Zestaw zasad i gotowych elementów do tworzenia diagramów architektonicznych w draw.io,
przechowywanych w repozytorium razem z kodem i dokumentacją.

## Zawartość

| Ścieżka | Co to |
|---|---|
| [`docs/01-spec-stylu.md`](docs/01-spec-stylu.md) | Specyfikacja: kiedy draw.io a kiedy Mermaid, tokeny wizualne, katalog elementów, gotowe style do wklejenia, zasady układu, checklista |
| [`templates/szablon-startowy.drawio`](templates/szablon-startowy.drawio) | 3 strony: **Paleta** (bloczki i strzałki do kopiowania), **Przykład — komponenty**, **Przykład — topologia** |
| [`templates/architektura.drawio-library`](templates/architektura.drawio-library) | Biblioteka kształtów (JSON) do wczytania w **app.diagrams.net lub draw.io Desktop** przez `File → Open Library` — elementy lądują jako paleta w lewym panelu. Wtyczka VS Code nie obsługuje otwierania plików bibliotek; tam używaj strony **Paleta** z szablonu |
| [`tools/gen-szablon.py`](tools/gen-szablon.py) | Generator obu plików powyżej. Zmiana stylu = edycja stałych na górze skryptu i `python3 tools/gen-szablon.py` |

## Start w 3 krokach

1. Zainstaluj wtyczkę VS Code **Draw.io Integration** (`hediet.vscode-drawio`).
2. Otwórz `templates/szablon-startowy.drawio`, przejdź na stronę **Paleta**.
3. Utwórz plik `docs/diagrams/<obszar>-components.drawio.svg`, wklej bloczki z palety, ustaw tło strony na `#FFFFFF`.

Jeśli pracujesz w app.diagrams.net albo w draw.io Desktop, zamiast kopiowania z palety możesz wczytać bibliotekę: `File → Open Library` → `templates/architektura.drawio-library`. Kształty pojawią się wtedy na stałe w lewym panelu.

## Dlaczego tak

Diagram w formacie `*.drawio.svg` jest jednocześnie obrazkiem (renderuje się w markdownie, GitHubie, MkDocs — bez żadnego build-stepu) i edytowalnym źródłem (otwiera się we wtyczce draw.io w VS Code). Leży w gicie obok kodu, więc wersjonuje się i review'uje razem ze zmianą, którą opisuje.

Mermaid zostaje tam, gdzie auto-layout jest zaletą: sekwencje, flowcharty, ERD. draw.io wchodzi tam, gdzie znaczenie niesie układ przestrzenny: komponenty i topologia. Szczegóły w [specyfikacji](docs/01-spec-stylu.md#2-kiedy-drawio-a-kiedy-mermaid).
