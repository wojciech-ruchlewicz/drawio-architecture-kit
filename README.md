# Diagramy architektoniczne – system wizualny

Zasady i gotowe elementy do rysowania diagramów architektonicznych w draw.io, trzymanych w repozytorium razem z kodem i dokumentacją.

| Ścieżka | Co to |
|---|---|
| [`docs/01-spec-stylu.md`](docs/01-spec-stylu.md) | Zasady: kiedy draw.io a kiedy Mermaid, format pliku, poziomy C4, reguły wizualne, układ, checklista |
| [`templates/palette.drawio.svg`](templates/palette.drawio.svg) | Paleta – wszystkie elementy z podpisanymi kolorami i wymiarami |
| [`examples/components-example.drawio.svg`](examples/components-example.drawio.svg) | Kompletny diagram komponentów |
| [`examples/topology-example.drawio.svg`](examples/topology-example.drawio.svg) | Kompletny diagram topologii |
| [`tools/gen.py`](tools/gen.py) | Generator wszystkich trzech plików. Zmiana stylu = edycja stałych na górze skryptu i `python3 tools/gen.py`. Bez zależności. |

## Jak zacząć

1. Zainstaluj wtyczkę VS Code **Draw.io Integration** (`hediet.vscode-drawio`).
2. Skopiuj `templates/palette.drawio.svg` do `docs/diagrams/<obszar>-components.drawio.svg`, otwórz i wyczyść kanwę – dostajesz plik z już poprawnymi ustawieniami diagramu.
3. Trzymaj paletę otwartą w drugiej zakładce i kopiuj z niej elementy (`Ctrl+C` / `Ctrl+V` działa między zakładkami draw.io).

Nie używamy bibliotek kształtów ani Scratchpada: Scratchpad żyje w `localStorage` przeglądarki i nie da się go współdzielić przez repo, a biblioteki wymagają konfiguracji per-workspace. Paleta w pliku jest prostsza i wersjonuje się razem z resztą.

## Dlaczego tak

Plik `*.drawio.svg` jest jednocześnie obrazkiem (renderuje się w markdownie, GitLabie, MkDocs – bez build-stepu) i edytowalnym źródłem (otwiera się we wtyczce draw.io w VS Code). Leży w gicie obok kodu, więc wersjonuje się i przechodzi review razem ze zmianą, którą opisuje.

Mermaid zostaje tam, gdzie auto-layout jest zaletą: sekwencje, flowcharty, ERD. draw.io wchodzi tam, gdzie znaczenie niesie układ przestrzenny: komponenty i topologia.

Diagramy mają `adaptiveColors="auto"`, więc ten sam plik wygląda dobrze w jasnym i ciemnym motywie – nie ustawiamy tła strony.
