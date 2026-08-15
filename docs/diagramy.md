# Diagramy architektoniczne w draw.io
| | |
|---|---|
| **Autor** | Wojtek Ruchlewicz, w uzgodnieniu z zespołem architektów |
| **Status** | Propozycja do konsultacji |
| **Ostatnia aktualizacja** | 2026-08 |

**Problem:**
Diagramy architektoniczne powstawały dotąd w tylu stylach, ilu było autorów. Każdy z nich pozostawał czytelny dla osoby, która go narysowała, i kosztowny w odbiorze dla wszystkich pozostałych. Dyskusja na review regularnie schodziła na konwencję zapisu zamiast na architekturę.

Dokument ustala jedną konwencję dla diagramów komponentów i topologii: format pliku, poziom abstrakcji, zestaw elementów i reguły ich użycia. Zakres jest celowo wąski. Reguła, która nie zwraca się czytelnością, nie została tu ujęta.

**Odstępstwa:**
Reguły opisane niżej pokrywają typowe przypadki, nie wszystkie. Jeżeli któraś nie pasuje do konkretnego diagramu, należy odstąpić od niej świadomie i odnotować powód w opisie merge requesta. Pojedyncze odstępstwo jest dopuszczalne. Powtarzające się odstępstwo tego samego rodzaju oznacza lukę w specyfikacji i powinno skutkować merge requestem na ten plik.

---

## Diagramy draw.io a Mermaid

draw.io i Mermaid nie konkurują ze sobą. Mają rozłączne zastosowania.
| Rodzaj diagramu | Narzędzie | Uzasadnienie |
|---|---|---|
| Sekwencja, flowchart, state machine, ERD | **Mermaid** | Auto-layout jest w tych przypadkach optymalny, a ręczne układanie nie wnosi informacji. Zapis w markdownie, zerowy koszt utrzymania. |
| Komponenty i ich zależności | **draw.io** | Powyżej ośmiu do dziesięciu węzłów auto-layout Mermaida przestaje być czytelny. Znaczenie niesie tu układ przestrzenny: warstwy, grupowanie, kierunek przepływu. |
| Topologia i deployment | **draw.io** | Zagnieżdżenie (subskrypcja, klaster, namespace, workload) oraz granice stref są informacją przestrzenną. |
Kryterium rozstrzygające: jeżeli po wygenerowaniu diagramu w Mermaid pojawia się potrzeba przesunięcia choćby jednego bloczka, diagram należy do draw.io.

---

## Format pliku

Diagramy zapisujemy jako **`*.drawio.svg`**. Plik w tym formacie jest hybrydą. Dla wszystkich narzędzi poza wtyczką draw.io stanowi zwykły obrazek SVG, renderowany w markdownie, GitLabie i MkDocs bez dodatkowego kroku budowania. Po otwarciu we wtyczce jest edytowalnym diagramem. Źródło przechowywane jest w atrybucie `content` elementu `<svg>`.

Wybór SVG zamiast PNG wynika z czterech różnic: rozmiar pliku rzędu 20 do 60 kB zamiast megabajtów, wektor pozostający ostry w każdej skali, tekst wyszukiwalny i dostępny, oraz tekstowy zamiast binarnego blob w gicie. PNG ma jedną przewagę, czyli wizualny diff w merge requeście, i nie równoważy ona pięćdziesięciokrotnego narzutu na rozmiar repozytorium.

**Nazewnictwo i lokalizacja:**

```
docs/diagrams/<obszar>-components.drawio.svg
docs/diagrams/<obszar>-topology.drawio.svg
```

Nazwy po angielsku, kebab-case, bez numerów wersji i dat. Wersjonowanie zapewnia git. Jeden diagram odpowiada jednemu plikowi. Osadzenie w dokumentacji wymaga tekstu alternatywnego:

```markdown
![Order Execution, komponenty logiczne](diagrams/order-execution-components.drawio.svg)
```

**Ustawienia diagramu:**

Nowy diagram należy zakładać jako kopię [`templates/blank.drawio.svg`](../templates/blank.drawio.svg). Szablon ma poniższe ustawienia już zapisane.
| Ustawienie | Wartość | Uzasadnienie |
|---|---|---|
| Adaptive Colors | Automatic | draw.io przelicza paletę na tryb ciemny, zachowując odcień i zmieniając jasność. |
| Tło strony | nieustawione | Wymuszenie białego tła wyłącza adaptację i pozostawia jasny prostokąt na ciemnej stronie. |
| Page View | wyłączony | Diagram architektoniczny nie jest formatowany do strony A4. |
| Czcionka | Helvetica | SVG nie osadza fontów, więc krój spoza listy web-safe renderuje się różnie na różnych maszynach. |
| Cień, Math | wyłączone | Szum wizualny, zwiększa rozmiar pliku, psuje część etykiet. |
| Siatka | 10 px | Wyrównanie bez dodatkowego wysiłku. |

---

## Edycja diagramów

Diagramy edytujemy w VS Code przy pomocy wtyczki **Draw.io Integration** (`hediet.vscode-drawio`). Wtyczka jest nieoficjalna, ale rekomendowana przez zespół diagrams.net i zawiera pełną, offline'ową wersję edytora draw.io.

**Tryb offline jest domyślny.** Wtyczka korzysta z wbudowanej kopii edytora, więc treść diagramów nie opuszcza stacji roboczej. Zachowanie to kontroluje ustawienie `hediet.vscode-drawio.offline`, domyślnie `true`, i nie należy go zmieniać.

**Obsługiwane rozszerzenia:** `.drawio`, `.dio`, `.drawio.svg` i `.drawio.png`. Nowy diagram powstaje przez utworzenie pustego pliku o właściwym rozszerzeniu i otwarcie go; konwersję między formatami wykonuje polecenie `Draw.io: Convert To...` z palety poleceń.

**Podgląd źródła.** Ten sam plik można otworzyć równolegle jako XML poleceniem `View: Reopen Editor With...`. Oba widoki są zsynchronizowane, co pozwala użyć wyszukiwania i zamiany VS Code do masowej zmiany nazw lub stylów. Dla plików `.drawio.svg` widok tekstowy pokazuje SVG z osadzonym źródłem w atrybucie `content`.

**Code review w GitLab:** Przy code review w GitLab pliki SVG wyświetlają się jako pliki tekstowe. Istnieje jednak możliwość przełączenia sposobu ich wyświetlania przez włączenie opcji "podgląd".

Wtyczka wspiera także Live Share, co pozwala przeglądać i omawiać diagram wspólnie bez eksportowania go do osobnego pliku.

---

## Poziomy abstrakcji

Z modelu C4 przejmujemy słownictwo i poziomy, bez jego notacji graficznej i narzędzi. C4 rozwiązuje najtrudniejszy problem diagramowania architektury, czyli jednoznaczne określenie poziomu szczegółowości.

| Poziom C4 | Nasza nazwa | Kiedy | Sufiks pliku |
|---|---|---|---|
| L1 System Context | Kontekst | opcjonalnie, gdy otoczenie systemu jest nieoczywiste | `-context` |
| **L2 Container** | **Komponenty logiczne** | domyślnie, najczęściej rysowany poziom | `-components` |
| L3 Component | Wnętrze komponentu | wyłącznie dla nietrywialnych serwisów | `-components-<serwis>` |
| Deployment | **Topologia** | gdy rozmieszczenie fizyczne ma znaczenie | `-topology` |

**Komponenty logiczne** odpowiadają na pytanie, z czego składa się system i które elementy się ze sobą komunikują. Zawierają komponenty wdrażalne, magazyny danych, brokery, systemy zewnętrzne i aktorów. Nie zawierają infrastruktury: nodów, klastrów, sieci, regionów, subskrypcji ani liczby instancji.

**Topologia** odpowiada na pytanie, gdzie system fizycznie działa i przez jakie granice przechodzi ruch. Zawiera granice hostingu, strefy sieciowe, punkty przejścia oraz komponenty umieszczone wewnątrz tych granic. Rysujemy na niej wyłącznie przejścia przez granice; zależności zamknięte w jednej strefie należą do diagramu komponentów. Stereotypy opisują tu formę wdrożenia, nie technologię: `«AKS Deployment / 3 repliki»`, `«App Service / P2v3»`.

---

## System wizualny

Kompletna paleta znajduje się w jednym pliku, z kodami hex podpisanymi pod każdym elementem. Nie prowadzimy równoległej tabeli tokenów, żeby nie utrzymywać dwóch źródeł prawdy.

![Paleta elementów](../templates/palette.drawio.svg)

Notacja opiera się na trzech niezależnych kanałach. Każdy koduje inny wymiar, dzięki czemu żadna informacja nie jest przekazywana dwukrotnie.

| Kanał | Koduje | Wartości |
|---|---|---|
| **Kształt** | zgrubną kategorię | prostokąt (usługa, aplikacja, komponent, job), stojący walec (magazyn danych), leżący walec (kolejka, topic), person (rola ludzka) |
| **Kolor** | zakres | biały `#FFFFFF` w zakresie diagramu, szary `#F0F0F0` poza naszą kontrolą, obwódka w czerwieni UBS `#E60000` na tle `#FDECEC` dla tematu diagramu |
| **Tekst** | dokładny typ i technologię | `«Microservice / Spring Boot»`, `«Kafka topic»` |

Przypisanie koloru do zakresu jest zgodne z konwencją stosowaną w przykładach C4, gdzie szary oznacza system istniejący lub cudzy. Sam model C4 nie narzuca kolorystyki; wymaga jedynie, aby kodowanie było spójne i udokumentowane. Tę rolę pełni u nas paleta.

---

## Reguły obowiązkowe

Poniższe cztery reguły decydują o poprawności diagramu. Ich złamanie prowadzi czytelnika do błędnych wniosków o systemie.

**Kierunek strzałki oznacza inicjatora wywołania**, nie kierunek przepływu danych. Strzałka od API do bazy oznacza, że to API odpytuje bazę, niezależnie od tego, w którą stronę płyną dane. Strzałki dwukierunkowe są niedopuszczalne, ponieważ zawsze oznaczają nierozstrzygnięcie, kto inicjuje.

**Każda strzałka ma etykietę w formie czasownik plus obiekt**, na przykład `publikuje OrderExecuted` lub `zapisuje stan zamówienia`. Etykiety typu samo `HTTP` czy `dane` oraz ich brak są niedopuszczalne. Protokół w nawiasie tylko wtedy, gdy wnosi informację. Diagram bez etykiet pokazuje wyłącznie topologię połączeń i nie mówi nic o zachowaniu systemu.

**W środku bloczka stoi nazwa logiczna**, czyli ta używana przez zespół w rozmowie, a nie nazwa repozytorium ani identyfikator zasobu. Identyfikator zasobu, jeżeli jest potrzebny, umieszczamy w opisie.

**Jeden poziom abstrakcji na diagram.** Umieszczenie klasy obok subskrypcji chmurowej jest najczęstszą przyczyną, dla której diagram przestaje cokolwiek komunikować.

---

## Reguły zalecane

Poniższe wpływają na spójność wizualną, nie na poprawność. Odstępstwo nie jest podstawą do zablokowania merge requesta.

- **Trzy strefy tekstu w bloczku:** stereotyp w guillemetach na górze, nazwa logiczna w środku, opis odpowiedzialności na dole, do około 60 znaków.
- **Nie więcej niż jeden wyróżniony element na diagram.** Dwa wyróżnienia znoszą się nawzajem.
- **Bloczki tej samej kategorii mają identyczną szerokość.**
- **Kreskowanie i wypełnienie wykluczają się**, co dotyczy obszarów. Obszar kreskowany pozostaje bez wypełnienia, obszar wypełniony ma linię ciągłą. Kreska oznacza granicę umowną, na przykład bounded context lub zakres diagramu; linia ciągła granicę twardą, jak namespace czy klaster.

---

## Układ diagramu

Ręczna kontrola nad układem jest podstawową przewagą draw.io nad Mermaidem i warto ją wykorzystywać świadomie.

- **Jeden kierunek przepływu na diagram**, z lewej do prawej albo z góry na dół.
- **Warstwy jako kolumny:** klienci, brama i API, logika domenowa, dane. Elementy tej samej warstwy wyrównane w jednej linii.
- **Zależność odwzorowana bliskością.** Strzałka przecinająca cały diagram jest sygnałem, że układ wymaga przemyślenia.
- **Górny limit to około piętnastu elementów i trzy poziomy zagnieżdżenia.** Powyżej diagram przestaje być czytelny niezależnie od jakości układu i należy rozbić go na diagram nadrzędny oraz poddiagramy.
- **Strzałki prowadzone pod kątem prostym**, unikanie odcinków skośnych. Przy nieuniknionych przecięciach należy włączyć mostki (`jumpStyle=gap`).
- **Wyrównanie i równomierne rozłożenie przed commitem** przy pomocy panelu Arrange.

---

## Przykłady

Diagram komponentów logicznych. Aktor po lewej, brama, logika domenowa wewnątrz bounded contextu, dane po prawej, system zewnętrzny oznaczony szarym wypełnieniem:

![Order Execution, komponenty logiczne](../examples/components-example.drawio.svg)

Ten sam system w ujęciu topologicznym. Widoczne są wyłącznie przejścia przez granice stref:

![Order Execution, topologia](../examples/topology-example.drawio.svg)

---

## Checklista przed commitem

Pozostałe warunki są spełnione automatycznie przy starcie od `blank.drawio.svg`.

- [ ] Każda strzałka ma etykietę; żadna nie jest dwukierunkowa
- [ ] Wszystkie elementy pochodzą z palety, kolor koduje zakres lub wyróżnienie
- [ ] W bloczkach stoją nazwy logiczne, nie identyfikatory zasobów

---

## Odstępstwa od C4

**Białe bloczki zamiast niebieskich.** C4 w przykładach stosuje wypełnione, nasycone prostokąty z białym tekstem. Przyjęte rozwiązanie daje wyższy kontrast tekstu, lepiej znosi skalowanie, a przede wszystkim zwalnia kolor na kodowanie zakresu.

**Stereotyp nad nazwą, w guillemetach.** C4 umieszcza typ pod nazwą, w nawiasach kwadratowych, w formie `[Container: Spring Boot]`. Pozostaliśmy przy wersji z typem na górze i z dużą nazwą na środku między dwiema mniejszymi liniami, gdzie blok pozostaje symetryczny.

**Ikony Azure na diagramach topologii.** C4 nie odnosi się do ikon. Dopuszczamy je jako element dekoracyjny do 32 px w rogu bloczka, nigdy zamiast bloczka. Ikona obowiązuje wszystkie elementy danego typu albo żadnego.

---

## Pliki w repozytorium

| Plik | Rola |
|---|---|
| [`templates/blank.drawio.svg`](../templates/blank.drawio.svg) | Pusty diagram z gotowymi ustawieniami, punkt startu każdego nowego pliku |
| [`templates/palette.drawio.svg`](../templates/palette.drawio.svg) | Paleta, otwierana obok jako źródło elementów do kopiowania |
| [`examples/components-example.drawio.svg`](../examples/components-example.drawio.svg) | Kompletny diagram komponentów |
| [`examples/topology-example.drawio.svg`](../examples/topology-example.drawio.svg) | Kompletny diagram topologii |
| [`tools/gen.py`](../tools/gen.py) | Generator powyższych plików, jedno źródło prawdy dla stylów |
