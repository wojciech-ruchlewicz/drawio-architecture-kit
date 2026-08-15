# Diagramy architektoniczne w draw.io

Mieliśmy kilkanaście diagramów w kilkunastu stylach. Każdy czytelny dla autora, żaden dla reszty. Na review schodziło na to, dlaczego jeden bloczek jest zielony, a drugi niebieski, zamiast na to, czy architektura ma sens. Ten dokument opisuje jeden sposób rysowania, żeby ta rozmowa się już nie odbywała.

Zasady są celowo krótkie. Jeśli reguła nie zarabia na siebie czytelnością, nie ma jej tutaj.

> Spisał: **Wojtek Ruchlewicz**, na podstawie ustaleń z zespołem architektów.
> Ostatnia zmiana: 2026-08.
>
> **Jeśli reguła nie pasuje do twojego przypadku, zrób po swojemu i napisz o tym w merge requeście.** Jeden wyjątek to wyjątek. Drugi taki sam oznacza, że to specyfikacja jest do poprawy, nie ty. Zgłoś się wtedy do mnie albo od razu otwórz MR na ten plik.

---

## Kiedy draw.io, a kiedy Mermaid

Nie konkurują. Mają rozłączne zastosowania.

| Diagram | Narzędzie | Dlaczego |
|---|---|---|
| Sekwencja, flowchart, state machine, ERD | **Mermaid** | Auto-layout jest tu optymalny, ręczne układanie nic nie wnosi. Zero kosztu utrzymania, kod siedzi w markdownie. |
| Komponenty i ich zależności | **draw.io** | Powyżej mniej więcej ośmiu węzłów auto-layout Mermaida produkuje plątaninę. Znaczenie niesie tu układ przestrzenny: warstwy, grupowanie, kierunek przepływu. |
| Topologia i deployment | **draw.io** | Zagnieżdżenie (subskrypcja, klaster, namespace, pod) i granice stref to informacja przestrzenna. |

Jeśli po wygenerowaniu diagramu w Mermaid chcesz przesunąć choć jeden bloczek, to jest diagram dla draw.io.

---

## Jak wygląda plik

Zapisujemy jako **`*.drawio.svg`**. Taki plik jest hybrydą: dla wszystkiego poza wtyczką draw.io to zwykły obrazek SVG, który renderuje się w markdownie, GitLabie i MkDocs bez żadnego build-stepu. Po otwarciu we wtyczce w VS Code to edytowalny diagram. Źródło siedzi w atrybucie `content` elementu `<svg>`.

SVG, a nie PNG: 20 do 60 kB zamiast megabajtów, wektor zawsze ostry, tekst wyszukiwalny, w gicie tekst zamiast binarnego bloba. PNG ma jedną przewagę, wizualny diff w merge requeście, i nie jest ona warta pięćdziesięciokrotnego narzutu na repozytorium.

```
docs/diagrams/<obszar>-components.drawio.svg
docs/diagrams/<obszar>-topology.drawio.svg
```

Nazwy po angielsku, kebab-case, bez wersji i dat w nazwie. Od tego jest git. Jeden diagram to jeden plik. W dokumentacji osadzamy z tekstem alternatywnym:

```markdown
![Order Execution, komponenty logiczne](diagrams/order-execution-components.drawio.svg)
```

**Nowy diagram zaczynaj od kopii [`templates/blank.drawio.svg`](../templates/blank.drawio.svg).** Ma już ustawione wszystko, co poniżej, więc nie musisz o tym pamiętać:

- **Adaptive Colors: Automatic.** draw.io sam przelicza paletę na tryb ciemny, zachowując odcień. Dlatego **nie ustawiamy tła strony na białe**, bo wymuszenie tła psuje adaptację i diagram zostaje jasnym prostokątem na ciemnej stronie.
- **Page View wyłączony.** Diagram architektoniczny nie jest kartką A4.
- **Czcionka Helvetica.** SVG nie osadza fontów, więc font spoza web-safe rozjedzie się na innej maszynie.
- Cień wyłączony, siatka 10 px.

---

## Na jakim poziomie rysujemy

Pożyczamy słownictwo i poziomy z modelu C4, bez jego notacji graficznej i narzędzi. C4 rozwiązuje najtrudniejszy problem diagramów, czyli *na jakim poziomie szczegółowości właściwie jesteśmy*, i nie ma sensu wymyślać tego od nowa.

| Poziom C4 | U nas | Kiedy | Sufiks pliku |
|---|---|---|---|
| L1 System Context | Kontekst | opcjonalnie, gdy otoczenie systemu jest nieoczywiste | `-context` |
| **L2 Container** | **Komponenty logiczne** | **domyślnie, to rysujemy najczęściej** | `-components` |
| L3 Component | Wnętrze komponentu | tylko dla nietrywialnych serwisów | `-components-<serwis>` |
| Deployment | **Topologia** | gdy rozmieszczenie fizyczne ma znaczenie | `-topology` |

**Komponenty logiczne** odpowiadają na pytanie *z czego składa się system i kto z kim rozmawia*. Zawierają komponenty wdrażalne, magazyny danych, brokery, systemy zewnętrzne i aktorów. Nie zawierają infrastruktury: nodów, klastrów, sieci, regionów, subskrypcji ani liczby instancji.

**Topologia** odpowiada na pytanie *gdzie to fizycznie działa i co przez co przechodzi*. Zawiera granice hostingu, strefy sieciowe, punkty przejścia i komponenty umieszczone wewnątrz tych granic. Rysujemy na niej wyłącznie przejścia przez granice, bo zależności zamknięte w jednej strefie należą do diagramu komponentów. Stereotypy opisują tu formę wdrożenia, nie technologię: `«AKS Deployment / 3 repliki»`, `«App Service / P2v3»`.

---

## Trzy kanały

Cała paleta jest w jednym pliku, z kodami hex podpisanymi pod każdym elementem. Nie ma osobnej tabeli, która mogłaby się rozjechać.

![Paleta elementów](../templates/palette.drawio.svg)

Każdy kanał niesie inny wymiar, więc nic nie jest zakodowane dwa razy.

| Kanał | Co koduje | Wartości |
|---|---|---|
| **Kształt** | zgrubna kategoria | prostokąt (usługa, aplikacja, komponent, job), stojący walec (magazyn danych), leżący walec (kolejka, topic), person (rola ludzka) |
| **Kolor** | zakres | biały `#FFFFFF` w zakresie, szary `#F0F0F0` poza naszą kontrolą, czerwień UBS `#E60000` na obwódce plus `#FDECEC` dla tematu diagramu |
| **Tekst** | dokładny typ i technologia | `«Microservice / Spring Boot»`, `«Kafka topic»` |

Kolor na osi zakresu to konwencja z przykładów C4, gdzie szary oznacza system już istniejący albo cudzy. Sam model C4 kolorów nie narzuca, wymaga tylko, żeby kodowanie było spójne i udokumentowane. U nas dokumentuje je paleta.

Kształt `person` pochodzi z biblioteki C4 wbudowanej w draw.io. Włącz ją raz przez **More Shapes → Software → C4**. Pozostałe kształty są w rdzeniu draw.io.

---

## Reguły, które mają znaczenie

Te cztery decydują o tym, czy diagram jest poprawny. Złamanie którejkolwiek sprawia, że czytelnik wyciągnie błędny wniosek o systemie.

**Kierunek strzałki oznacza, kto inicjuje**, a nie dokąd płyną dane. Strzałka od API do bazy znaczy „API odpytuje bazę", nawet jeśli dane wracają w drugą stronę. Strzałki dwukierunkowe są zabronione, bo zawsze oznaczają, że autor nie przemyślał, kto inicjuje.

**Każda strzałka ma etykietę w formie czasownik plus obiekt.** `publikuje OrderExecuted`, `zapisuje stan zamówienia`. Nie `HTTP`, nie `dane`, nie pustka. Protokół w nawiasie tylko wtedy, gdy naprawdę coś wnosi. Diagram bez etykiet pokazuje topologię połączeń i nie mówi nic o zachowaniu.

**W środku bloczka stoi nazwa logiczna**, czyli ta, której zespół używa w rozmowie. Nie nazwa repozytorium, nie nazwa zasobu w Azure. `app-ord-gw-weu-p-01` nie znaczy nic dla nikogo spoza zespołu, który to wdrażał. Nazwa zasobu, jeśli potrzebna, idzie do opisu.

**Jeden poziom abstrakcji na diagram.** Klasa obok subskrypcji Azure to najczęstszy sposób, w jaki diagram przestaje cokolwiek znaczyć.

---

## Rzeczy, o które nie będziemy się kłócić

Te wpływają na estetykę, nie na poprawność. Trzymaj się ich, bo dzięki nim diagramy z różnych zespołów wyglądają jak jedna rodzina, ale nikt nie zablokuje ci merge requesta za odstępstwo.

- **Trzy strefy tekstu w bloczku:** stereotyp w guillemetach na górze, nazwa logiczna w środku, opis odpowiedzialności na dole, do jakichś 60 znaków. Jeśli opis się nie mieści, komponent ma prawdopodobnie za szeroką odpowiedzialność, i to jest wartościowy sygnał z samego rysowania.
- **Walec i pipe niosą tylko stereotyp i nazwę.** Kopuła zjada linię opisu. Jeśli opis jest niezbędny, użyj prostokąta.
- **Jeden wyróżniony element na diagram.** Dwa wyróżnienia to brak wyróżnienia.
- **Bloczki tej samej kategorii mają identyczną szerokość.** Nierówne szerokości są najsilniejszym sygnałem, że diagram robiono w pośpiechu.
- **Kreskowanie i wypełnienie się wykluczają.** Dotyczy obszarów: kreskowany nie ma wypełnienia, wypełniony ma linię ciągłą. Kreska oznacza granicę umowną (bounded context, zakres diagramu), linia ciągła granicę twardą (namespace, klaster). Przy trzech poziomach zagnieżdżenia zawsze ciągła, bo nałożone kreski robią mory.

**Nie rysujemy legend.** C4 wymaga legendy na każdym diagramie, ale w praktyce nikt jej nie utrzymuje, a ten sam blok skopiowany na dwudziestu diagramach to dwadzieścia miejsc do rozjechania się. Legendą jest [paleta](../templates/palette.drawio.svg): jedna, wersjonowana, wspólna. Wystarczy, że diagram używa wyłącznie elementów z niej.

---

## Układ

Layout w draw.io jest ręczny i to jest cała przewaga tego narzędzia nad Mermaidem. Warto ją wykorzystać świadomie.

- **Jeden kierunek przepływu na diagram**, z lewej do prawej albo z góry na dół. Nigdy oba.
- **Warstwy jako kolumny:** klienci, brama i API, logika domenowa, dane. Elementy tej samej warstwy w jednej linii.
- **Zależność to bliskość.** Jeśli strzałka przecina cały diagram, przemyśl układ, zanim ją narysujesz.
- **Mniej więcej piętnaście elementów i trzy poziomy zagnieżdżenia** to sufit. Powyżej diagram przestaje być czytelny niezależnie od jakości układu, więc rozbij go na nadrzędny i poddiagramy.
- **Strzałki pod kątem prostym**, bez skosów. Przy nieuniknionych przecięciach włącz mostki (`jumpStyle=arc`).
- **Podpinaj strzałki do konkretnych krawędzi**, nie do środka bloczka. Inaczej przy pierwszym przesunięciu elementu diagram się rozjedzie.
- **Wyrównaj i rozłóż równomiernie przed commitem** (panel Arrange). Dwadzieścia sekund pracy i największy pojedynczy zysk estetyczny.

---

## Jak to wygląda w praktyce

Diagram komponentów. Aktor po lewej, brama, logika domenowa w bounded contexcie, dane po prawej, system zewnętrzny szary:

![Order Execution, komponenty logiczne](../examples/components-example.drawio.svg)

Ten sam system w ujęciu topologicznym. Widać wyłącznie to, co przechodzi przez granicę strefy:

![Order Execution, topologia](../examples/topology-example.drawio.svg)

### A tak wyglądał ten sam diagram wcześniej

![Ten sam system narysowany bez zasad](../examples/components-antipattern.drawio.svg)

Sześć bloczków, sześć szerokości i sześć kolorów, z których żaden nic nie znaczy. Strzałki bez etykiet, więc nie wiadomo, co się między tymi pudełkami dzieje. Jedna dwukierunkowa, bo autor nie rozstrzygnął, kto inicjuje. `OrderEntity` to klasa, `sub-etrading-prod` to subskrypcja, a `app-ord-gw-weu-p-01` to nazwa zasobu, więc na jednym obrazku siedzą trzy poziomy abstrakcji naraz. Brak tytułu i właściciela, więc za pół roku nikt nie wie, czy to jest jeszcze aktualne.

Nikt nie narysował tego złośliwie. Tak wychodzi, kiedy nie ma się od czego odbić, i właśnie po to jest paleta.

---

## Zanim wypchniesz zmianę

Cztery rzeczy, reszta wynika ze startu od `blank.drawio.svg`.

- [ ] Każda strzałka ma etykietę „czasownik plus obiekt", żadna nie jest dwukierunkowa
- [ ] Wszystkie elementy pochodzą z palety, kolor koduje wyłącznie zakres
- [ ] W nazwach stoją nazwy logiczne, nie nazwy zasobów
- [ ] Nagłówek uzupełniony: tytuł, poziom C4, właściciel, miesiąc aktualizacji

---

## Gdzie odeszliśmy od C4

**Białe bloczki zamiast niebieskich.** C4 rysuje wypełnione, nasycone prostokąty z białym tekstem. Nasza wersja daje lepszy kontrast tekstu, lepiej znosi skalę i druk, a przede wszystkim zwalnia kolor na kodowanie zakresu.

**Stereotyp nad nazwą, w guillemetach.** C4 stawia typ pod nazwą, w nawiasach kwadratowych: `[Container: Spring Boot]`. Argument za wersją C4 jest mocny, bo nazwa jest najważniejsza, a czyta się od góry. Zostaliśmy przy swojej, bo nazwa jest wtedy optycznie wyśrodkowana między dwiema mniejszymi liniami, blok wychodzi symetryczny, a zespół już tak te diagramy czyta.

**Ikony Azure na topologii.** C4 nic o nich nie mówi. U nas są dopuszczalne jako dekoracja do 32 px w rogu bloczka, nigdy zamiast bloczka. Albo wszystkie elementy danego typu mają ikonę, albo żaden.

**Brak legend**, opisany wyżej.

---

## Co się zmieniało

| Kiedy | Co i dlaczego |
|---|---|
| 2026-08 | Kolor przeszedł z osi typu elementu na oś zakresu. Typ i tak stał w stereotypie, więc kodowaliśmy go dwa razy, a zakres wisiał tylko na kreskowanej obwódce. Magazyny danych i kolejki straciły przy tym swoje tinty i odróżnia je teraz kształt. |
| 2026-08 | Doszły kształty semantyczne: walec dla magazynów danych, pipe dla kolejek, person dla ról ludzkich. Wcześniej wszystko było prostokątem. |
| 2026-08 | Wypadły legendy z diagramów. Rolę legendy przejęła paleta. |
| 2026-08 | Bloczki zmalały z 240x100 do 200x80, a rozmiary czcionek zeszły z pięciu do czterech. |

---

## Pliki

| Plik | Rola |
|---|---|
| [`templates/blank.drawio.svg`](../templates/blank.drawio.svg) | Pusty diagram z gotowymi ustawieniami. Punkt startu każdego nowego pliku |
| [`templates/palette.drawio.svg`](../templates/palette.drawio.svg) | Paleta. Trzymaj otwartą obok i kopiuj z niej elementy |
| [`examples/components-example.drawio.svg`](../examples/components-example.drawio.svg) | Kompletny diagram komponentów |
| [`examples/topology-example.drawio.svg`](../examples/topology-example.drawio.svg) | Kompletny diagram topologii |
| [`examples/components-antipattern.drawio.svg`](../examples/components-antipattern.drawio.svg) | Ten sam system narysowany źle, do porównania |
| [`tools/gen.py`](../tools/gen.py) | Generator powyższych. Jedno źródło prawdy dla stylów |

Wtyczka do VS Code: **Draw.io Integration** (`hediet.vscode-drawio`).
