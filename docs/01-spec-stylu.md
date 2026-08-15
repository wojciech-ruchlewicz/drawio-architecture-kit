# Specyfikacja stylu diagramów architektonicznych (draw.io)

**Status:** propozycja do konsultacji
**Wersja:** 0.1
**Dotyczy:** diagramów komponentów logicznych i diagramów topologii tworzonych w draw.io
**Nie dotyczy:** diagramów sekwencji, flowchartów, state machine — te zostają w Mermaid

---

## 1. Cel

Ten dokument definiuje **jeden wizualny system** dla diagramów architektonicznych w naszych repozytoriach. Celem jest to, żeby:

- diagram narysowany przez dowolną osobę w zespole wyglądał jak diagram narysowany przez każdą inną,
- czytelnik nie musiał się uczyć nowej notacji przy każdym repo,
- tworzenie diagramu było kwestią kopiowania gotowych bloczków, a nie projektowania od zera.

System jest celowo **mały**. Jeśli reguła nie zarabia na siebie czytelnością, nie ma jej tutaj.

---

## 2. Kiedy draw.io, a kiedy Mermaid

Mermaid i draw.io nie konkurują — mają rozłączne zastosowania.

| Rodzaj diagramu | Narzędzie | Dlaczego |
|---|---|---|
| Sekwencja, przepływ w czasie | **Mermaid** | Auto-layout jest tu optymalny; ręczne układanie nic nie wnosi. Zapis w markdownie, zerowy koszt utrzymania. |
| Flowchart / decyzje / state machine | **Mermaid** | Jw. Struktura liniowa lub drzewiasta, auto-layout sobie radzi. |
| ERD, class diagram | **Mermaid** | Notacja jest ustandaryzowana, layout drugorzędny. |
| **Komponenty logiczne i ich zależności** | **draw.io** | Powyżej ~8 węzłów auto-layout Mermaida produkuje plątaninę. Znaczenie niesie tu *układ przestrzenny* — warstwy, grupowanie, kierunek przepływu — a tego Mermaid nie pozwala kontrolować. |
| **Topologia / deployment** | **draw.io** | Zagnieżdżenie (subskrypcja → klaster → namespace → pod) i granice stref to informacja przestrzenna. Mermaid `subgraph` nie daje nad tym kontroli. |

**Reguła kciuka:** jeśli po wygenerowaniu diagramu w Mermaid chcesz przesunąć choć jeden bloczek — to jest diagram dla draw.io.

---

## 3. Format pliku

### 3.1 SVG jako domyślny format

Diagramy zapisujemy jako **`*.drawio.svg`**.

Plik `*.drawio.svg` jest hybrydą: dla każdego narzędzia poza wtyczką draw.io to zwykły obrazek SVG (renderuje się w markdownie, w GitHubie, w MkDocs, w przeglądarce), a po otwarciu we wtyczce draw.io w VS Code — edytowalny diagram. Źródłowy XML siedzi w atrybucie `content` elementu `<svg>`.

Dlaczego SVG, a nie PNG:

| | `*.drawio.svg` | `*.drawio.png` |
|---|---|---|
| Rozmiar pliku | 20–60 kB | 0.5–5 MB |
| Ostrość | wektor, zawsze ostry przy każdym zoomie i DPI | rozmywa się przy powiększeniu i na ekranach HiDPI |
| Waga w gicie | tekst, przyrostowy | binarny, każda zmiana to nowy pełny blob |
| Tekst | prawdziwy tekst — wyszukiwalny, zaznaczalny, dostępny | rastr |
| Diff w code review | tekstowy, mało czytelny (osadzony XML) | wizualny swipe/onion-skin na GitHubie |

Jedyna realna przewaga PNG to wizualny diff w PR. Nie jest warta 50-krotnego narzutu na rozmiar repo — zmianę i tak weryfikuje się otwierając plik z brancha.

**PNG dopuszczamy wyjątkowo**, gdy diagram trafia do systemu, który nie renderuje SVG (część klientów pocztowych, niektóre wiki, eksport do PowerPointa).

### 3.2 Nazewnictwo i lokalizacja

```
docs/
  diagrams/
    <obszar>-components.drawio.svg     # diagram komponentów logicznych
    <obszar>-topology.drawio.svg       # diagram topologii / deployment
    <obszar>-components-<detal>.drawio.svg   # rozbicie na poddiagram
```

- `<obszar>` — nazwa domeny/systemu, kebab-case, po angielsku (`order-management`, `identity`).
- Bez wersji i dat w nazwie — od tego jest git.
- Jeden diagram = jeden plik = jedna strona. Nie używamy wielostronicowych `.drawio` jako diagramów produkcyjnych (wielostronicowy jest tylko szablon startowy).

### 3.3 Osadzanie w dokumentacji

```markdown
![Order Management — komponenty logiczne](diagrams/order-management-components.drawio.svg)
```

Tekst alternatywny jest obowiązkowy i opisuje diagram, nie plik.

### 3.4 Ustawienia, które trzeba ustawić raz

| Ustawienie | Wartość | Powód |
|---|---|---|
| Tło strony (`File → Page Setup → Background`) | `#FFFFFF` | Przezroczyste tło + czarny tekst = diagram niewidoczny w dark mode GitHuba i MkDocs. To najczęstszy błąd. |
| Czcionka | **Helvetica** (fallback Arial) | SVG nie osadza fontów. Font spoza listy web-safe rozjedzie się na innej maszynie. |
| Siatka | 10 px, snap włączony | Wyrównanie bez wysiłku. |
| Cień (`Shadow`) | wyłączony | Szum wizualny, powiększa SVG. |
| `Math typesetting` | wyłączone | Psuje renderowanie niektórych etykiet. |

---

## 4. Model pojęciowy — lekki C4

Pożyczamy **słownictwo i poziomy abstrakcji z modelu C4**, ale nie jego notację graficzną ani narzędzia. Powód: C4 jest szeroko znany, dobrze uzasadniony i rozwiązuje najtrudniejszy problem diagramów — *na jakim poziomie szczegółowości jesteśmy*. Nie ma sensu wymyślać tego od nowa.

| Poziom C4 | Nasza nazwa | Kiedy rysujemy | Plik |
|---|---|---|---|
| L1 System Context | Kontekst | opcjonalnie, gdy system ma nietrywialne otoczenie | `-context` |
| **L2 Container** | **Komponenty logiczne** | **domyślnie — to jest diagram, który robimy najczęściej** | `-components` |
| L3 Component | Wnętrze komponentu | tylko dla nietrywialnych serwisów | `-components-<serwis>` |
| Deployment | **Topologia** | **gdy rozmieszczenie fizyczne ma znaczenie** | `-topology` |

### Odstępstwa od C4 (świadome)

1. **Odwracamy kolorystykę.** C4 rysuje wypełnione, nasycone niebieskie prostokąty z białym tekstem. My rysujemy **białe bloczki z ciemną obwódką**. Powody: lepszy kontrast tekstu, czytelność w druku i w skali, brak konkurencji z kolorem użytym semantycznie (strefy, wyróżnienia), spójność z jasnym tłem dokumentacji.
2. **Nie używamy oficjalnej terminologii „Container"** w etykietach — jest myląca w kontekście, w którym „container" znaczy Docker. Warstwę techniczną opisujemy stereotypem (`«Microservice · .NET 8»`).
3. **Legenda jest opcjonalna**, jeśli diagram jest monochromatyczny. Obowiązkowa, gdy używamy koloru semantycznie.

---

## 5. Tokeny wizualne

Wszystko poniżej jest normatywne. Nie improwizujemy kolorów ani rozmiarów.

### 5.1 Kolory tekstu

Tylko dwa poziomy. Trzeci by wprowadził hierarchię, której czytelnik nie odczyta.

| Token | Hex | Zastosowanie |
|---|---|---|
| `text.primary` | `#000000` | nazwa logiczna komponentu |
| `text.secondary` | `#444444` | stereotyp technologiczny, opis, etykiety strzałek, tytuły kontenerów |

### 5.2 Linie

| Token | Hex | Grubość | Zastosowanie |
|---|---|---|---|
| `stroke.block` | `#333333` | 1.5 | obwódka bloczka komponentu |
| `stroke.muted` | `#999999` | 1.5, dashed | obwódka elementu zewnętrznego / poza zakresem |
| `stroke.edge` | `#888888` | 2 | strzałki |
| `stroke.container` | `#BBBBBB` | 1.5, dashed | obwódka obszaru / grupy |

Strzałki są celowo jaśniejsze od bloczków. Bloczki niosą treść, strzałki są infrastrukturą — mają się „gubić" w tle, a nie dominować.

### 5.3 Wypełnienia

Baza jest **monochromatyczna**. Kolor jest zasobem rzadkim.

| Token | Fill | Stroke | Zastosowanie |
|---|---|---|---|
| `fill.default` | `#FFFFFF` | `#333333` | komponent w zakresie diagramu |
| `fill.external` | `#F5F5F5` | `#999999` dashed | system zewnętrzny, third-party, poza naszą kontrolą |
| `fill.group` | `#FAFAFA` | `#BBBBBB` dashed | obszar grupujący bez znaczenia semantycznego |
| `fill.highlight` | `#FFF6E5` | `#B37A00` | **jeden** element będący tematem diagramu / zmieniany w danym PR |

### 5.4 Paleta semantyczna (opcjonalna, do wyboru **jednej osi**)

**Zasada nadrzędna: na jednym diagramie kolor koduje dokładnie jedną oś znaczeniową.** Albo typ elementu, albo strefę bezpieczeństwa — nigdy oba naraz. Jeśli potrzebujesz dwóch osi, drugą koduj kształtem lub zagnieżdżeniem.

**Oś A — typ elementu** (przydatna na diagramach komponentów):

| Typ | Fill | Stroke |
|---|---|---|
| Usługa / aplikacja | `#FFFFFF` | `#333333` |
| Magazyn danych (DB, blob, cache) | `#F0F4F8` | `#4A6785` |
| Broker / kolejka / event bus | `#F5F0F8` | `#6E5A85` |
| System zewnętrzny | `#F5F5F5` | `#999999` dashed |

**Oś B — strefa** (przydatna na diagramach topologii):

| Strefa | Fill | Stroke |
|---|---|---|
| Green Zone | `#F2F7F3` | `#6FA97F` |
| Red Zone | `#FBF3F3` | `#C08585` |
| Strefa neutralna / subskrypcja | `#FAFAFA` | `#BBBBBB` dashed |

Tinty są celowo bardzo jasne (L ≈ 96%). Kolor ma sygnalizować przynależność z odległości metra, a nie krzyczeć.

### 5.5 Typografia

| Element | Rozmiar | Waga | Kolor |
|---|---|---|---|
| Stereotyp (górna linia bloczka) | 11 px | regular | `#444444` |
| Nazwa logiczna (środek) | 14 px | **bold** | `#000000` |
| Opis (dolna linia) | 10 px | regular | `#444444` |
| Etykieta strzałki | 10 px | regular | `#444444` |
| Tytuł kontenera / obszaru | 12 px | **bold** | `#444444` |
| Tytuł diagramu | 18 px | **bold** | `#000000` |

Minimum to 10 px — poniżej diagram przestaje być czytelny po wklejeniu do slajdu.

### 5.6 Wymiary i odstępy

| Token | Wartość |
|---|---|
| Siatka | 10 px |
| Bloczek standardowy | 240 × 100 |
| Bloczek kompaktowy (bez opisu) | 240 × 60 |
| Promień zaokrąglenia bloczka | 12 px |
| Odstęp poziomy między kolumnami | 60 px |
| Odstęp pionowy między wierszami | 40 px |
| Padding wewnątrz kontenera | 20 px z boków i dołu, 40 px z góry (na tytuł) |
| Zaokrąglenie załamań strzałek | 10 px |

Wszystkie współrzędne są wielokrotnościami 10. Wszystkie bloczki tej samej kategorii mają identyczną szerokość — nierówne szerokości są najsilniejszym sygnałem, że diagram robiono w pośpiechu.

---

## 6. Katalog elementów

### 6.1 Bloczek komponentu

Trzy strefy tekstu w jednym prostokącie:

```
┌────────────────────────────────┐
│      «Microservice · .NET 8»   │  ← czym to JEST fizycznie
│                                │
│       Order Processor          │  ← nazwa LOGICZNA (co to robi)
│                                │
│  Waliduje i utrwala zamówienia │  ← opis, jedno–dwa zdania
└────────────────────────────────┘
```

**Reguły treści:**

- **Stereotyp** w guillemetach `« »` (konwencja UML). Format: `«Typ · Technologia»`. Typ z zamkniętej listy: `Microservice`, `Web App`, `API`, `Function`, `Database`, `Blob Storage`, `Queue`, `Topic`, `Cache`, `Job`, `External System`. Technologia opcjonalna, ale bardzo pomaga.
- **Nazwa logiczna** — jak zespół nazywa tę rzecz w rozmowie. Nie nazwa repozytorium, nie nazwa zasobu w Azure.
- **Opis** — odpowiada na pytanie „za co ten komponent odpowiada", maks. ~90 znaków. Jeśli nie potrafisz opisać komponentu w jednym zdaniu, prawdopodobnie ma zbyt szeroką odpowiedzialność — i to jest wartościowy sygnał z samego procesu rysowania.

Opis można pominąć (bloczek kompaktowy 240 × 60), gdy diagram ma > 12 elementów i opisy zaczynają dominować.

### 6.2 Obszar / kontener

Prostokąt z przerywaną obwódką, tytuł **wyrównany do lewej u góry** (w przeciwieństwie do bloczków, gdzie tekst jest wyśrodkowany — ten kontrast sam w sobie komunikuje „to jest pojemnik, nie element").

Zastosowanie: granica systemu, subskrypcja, klaster, namespace, strefa bezpieczeństwa, warstwa logiczna.

Zagnieżdżenie maksymalnie **3 poziomy**. Głębiej — dziel na osobny diagram.

Tytuł kontenera zawiera typ granicy: `Subskrypcja: prod-weu`, `AKS: aks-prod-weu`, `Namespace: orders`, `Green Zone`.

### 6.3 Aktor

Prosty piktogram postaci + podpis pod spodem. Tylko na diagramach kontekstu i komponentów. Bez stereotypu, bez opisu — aktor to `Operator magazynu`, a nie `«Human» Operator`.

### 6.4 Strzałki

Kierunek strzałki oznacza **kto inicjuje**, nie kierunek przepływu danych. To najczęstsze nieporozumienie — strzałka od `API` do `Database` oznacza „API odpytuje bazę", nawet jeśli dane płyną w drugą stronę.

| Semantyka | Linia | Grot |
|---|---|---|
| Wywołanie synchroniczne (HTTP, gRPC, SQL) | ciągła | wypełniony |
| Komunikacja asynchroniczna (event, message) | przerywana | pusty |
| Zależność logiczna / konfiguracyjna | kropkowana | pusty, cienki |

**Etykiety:** czasownik w 3. osobie + obiekt, opcjonalnie protokół w nawiasie.

- ✅ `pobiera profil klienta (HTTPS/JSON)`
- ✅ `publikuje OrderCreated`
- ❌ `HTTP`, `dane`, `→`, brak etykiety

Etykieta ma białe tło (`labelBackgroundColor=#FFFFFF`), żeby nie zlewała się z przecinającymi liniami.

Strzałki dwukierunkowe są **zabronione** — zawsze oznaczają, że autor nie przemyślał, kto inicjuje. Narysuj dwie strzałki albo jedną z etykietą opisującą oba kierunki.

Przy nieuniknionych przecięciach włącz `jumpStyle=arc` (mostki na skrzyżowaniach).

### 6.5 Legenda

Prawy dolny róg, w ramce `fill.group`. Obowiązkowa, jeśli diagram używa koloru semantycznie lub więcej niż jednego typu strzałki. Zawiera wyłącznie te elementy, które faktycznie występują na diagramie.

### 6.6 Tytuł i metryka

Lewy górny róg, poza obszarem treści:

```
Order Management — komponenty logiczne
Poziom: C4 L2 · Właściciel: Team Orders · Aktualizacja: 2026-08
```

Data aktualizacji w tekście jest redundantna wobec gita, ale czytelnik oglądający wyeksportowany obrazek gita nie ma. Wystarczy dokładność do miesiąca.

---

## 7. Gotowe style draw.io

Wklejane przez `Ctrl+E` (Edit Style) na zaznaczonym elemencie. To jest normatywne źródło prawdy dla sekcji 5.

### Bloczek komponentu (standardowy)

```
rounded=1;absoluteArcSize=1;arcSize=24;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#333333;strokeWidth=1.5;fontFamily=Helvetica;fontSize=14;fontColor=#000000;align=center;verticalAlign=middle;spacingLeft=8;spacingRight=8;shadow=0;
```

Etykieta (HTML, wklejana przez `F2`):

```html
<div style="line-height:1.4">
<font style="font-size:11px;color:#444444">«Microservice · .NET 8»</font><br>
<b style="font-size:14px;color:#000000">Order Processor</b><br>
<font style="font-size:10px;color:#444444">Waliduje i utrwala zamówienia</font>
</div>
```

### Magazyn danych

```
rounded=1;absoluteArcSize=1;arcSize=24;whiteSpace=wrap;html=1;fillColor=#F0F4F8;strokeColor=#4A6785;strokeWidth=1.5;fontFamily=Helvetica;fontSize=14;fontColor=#000000;align=center;verticalAlign=middle;spacingLeft=8;spacingRight=8;shadow=0;
```

### Broker / kolejka

```
rounded=1;absoluteArcSize=1;arcSize=24;whiteSpace=wrap;html=1;fillColor=#F5F0F8;strokeColor=#6E5A85;strokeWidth=1.5;fontFamily=Helvetica;fontSize=14;fontColor=#000000;align=center;verticalAlign=middle;spacingLeft=8;spacingRight=8;shadow=0;
```

### System zewnętrzny

```
rounded=1;absoluteArcSize=1;arcSize=24;whiteSpace=wrap;html=1;dashed=1;dashPattern=6 4;fillColor=#F5F5F5;strokeColor=#999999;strokeWidth=1.5;fontFamily=Helvetica;fontSize=14;fontColor=#000000;align=center;verticalAlign=middle;spacingLeft=8;spacingRight=8;shadow=0;
```

### Wyróżnienie (temat diagramu)

```
rounded=1;absoluteArcSize=1;arcSize=24;whiteSpace=wrap;html=1;fillColor=#FFF6E5;strokeColor=#B37A00;strokeWidth=1.5;fontFamily=Helvetica;fontSize=14;fontColor=#000000;align=center;verticalAlign=middle;spacingLeft=8;spacingRight=8;shadow=0;
```

### Obszar / kontener (neutralny)

```
rounded=1;absoluteArcSize=1;arcSize=32;whiteSpace=wrap;html=1;dashed=1;dashPattern=8 4;fillColor=#FAFAFA;strokeColor=#BBBBBB;strokeWidth=1.5;fontFamily=Helvetica;fontSize=12;fontStyle=1;fontColor=#444444;align=left;verticalAlign=top;spacingLeft=12;spacingTop=6;shadow=0;container=1;collapsible=0;
```

### Obszar — Green Zone

```
rounded=1;absoluteArcSize=1;arcSize=32;whiteSpace=wrap;html=1;dashed=1;dashPattern=8 4;fillColor=#F2F7F3;strokeColor=#6FA97F;strokeWidth=1.5;fontFamily=Helvetica;fontSize=12;fontStyle=1;fontColor=#444444;align=left;verticalAlign=top;spacingLeft=12;spacingTop=6;shadow=0;container=1;collapsible=0;
```

### Obszar — Red Zone

```
rounded=1;absoluteArcSize=1;arcSize=32;whiteSpace=wrap;html=1;dashed=1;dashPattern=8 4;fillColor=#FBF3F3;strokeColor=#C08585;strokeWidth=1.5;fontFamily=Helvetica;fontSize=12;fontStyle=1;fontColor=#444444;align=left;verticalAlign=top;spacingLeft=12;spacingTop=6;shadow=0;container=1;collapsible=0;
```

### Strzałka — wywołanie synchroniczne

```
edgeStyle=orthogonalEdgeStyle;rounded=1;arcSize=10;html=1;strokeColor=#888888;strokeWidth=2;endArrow=blockThin;endFill=1;endSize=6;jumpStyle=arc;jumpSize=8;fontFamily=Helvetica;fontSize=10;fontColor=#444444;labelBackgroundColor=#FFFFFF;
```

### Strzałka — komunikacja asynchroniczna

```
edgeStyle=orthogonalEdgeStyle;rounded=1;arcSize=10;html=1;dashed=1;dashPattern=6 4;strokeColor=#888888;strokeWidth=2;endArrow=open;endFill=0;endSize=8;jumpStyle=arc;jumpSize=8;fontFamily=Helvetica;fontSize=10;fontColor=#444444;labelBackgroundColor=#FFFFFF;
```

### Strzałka — zależność logiczna

```
edgeStyle=orthogonalEdgeStyle;rounded=1;arcSize=10;html=1;dashed=1;dashPattern=1 3;strokeColor=#999999;strokeWidth=1.5;endArrow=open;endFill=0;endSize=8;fontFamily=Helvetica;fontSize=10;fontColor=#444444;labelBackgroundColor=#FFFFFF;
```

> **Uwaga techniczna:** `absoluteArcSize=1;arcSize=24` daje promień **12 px**. W mxGraph przy `absoluteArcSize=1` promień to `arcSize / 2` — dlatego wartość jest podwojona. Bez `absoluteArcSize=1` `arcSize` jest procentem krótszego boku i zaokrąglenie skaluje się z rozmiarem bloczka, co psuje spójność.

---

## 8. Zasady układu

Layout jest w draw.io ręczny — to jest cała przewaga tego narzędzia. Warto ją wykorzystać świadomie.

1. **Jeden kierunek przepływu na diagram.** Ruch użytkownika/żądań: z lewej do prawej albo z góry na dół. Nigdy oba naraz.
2. **Warstwy jako kolumny (lub wiersze).** Klienci → brama/API → logika domenowa → dane. Elementy tej samej warstwy wyrównane w jednej linii.
3. **Zależność = bliskość.** Komponenty, które ze sobą intensywnie rozmawiają, stoją obok siebie. Jeśli strzałka przecina cały diagram, przemyśl układ, zanim ją narysujesz.
4. **Limit ~15 elementów.** Powyżej diagram przestaje być czytelny niezależnie od jakości układu. Rozbij na diagram nadrzędny + poddiagramy.
5. **Zero przecięć, jeśli się da.** Gdy się nie da — mostki (`jumpStyle=arc`).
6. **Strzałki pod kątem prostym** (`orthogonalEdgeStyle`). Bez skosów, bez krzywych.
7. **Punkty zaczepienia stałe.** Podpinaj strzałki do konkretnych krawędzi (fixed connection points), nie do środka bloczka — inaczej przy przesunięciu elementu strzałki przeskakują i diagram się rozjeżdża.
8. **Wyrównanie i rozkład.** `Ctrl+Shift+A` / panel Arrange — wyrównaj i rozłóż równomiernie przed każdym commitem. To 20 sekund pracy i największy pojedynczy zysk estetyczny.
9. **Białe światło.** Nie upychaj. Odstęp 60/40 px jest minimum, nie celem.

---

## 9. Diagram komponentów logicznych

**Odpowiada na pytanie:** z czego składa się system i kto z kim rozmawia.

**Zawiera:** komponenty wdrażalne (serwisy, aplikacje, funkcje), magazyny danych, brokery, systemy zewnętrzne, aktorów. Zależności między nimi z etykietami.

**Nie zawiera:** infrastruktury (nody, klastry, sieci), regionów, subskrypcji, szczegółów wdrożenia, liczby instancji.

**Grupowanie:** kontenery neutralne (`fill.group`) reprezentują granice logiczne — bounded context, domenę, granicę systemu. Nie strefy sieciowe.

**Typowy układ:** aktorzy po lewej, wejście (API Gateway / BFF) w drugiej kolumnie, logika domenowa w środku, dane po prawej, systemy zewnętrzne w prawej skrajnej kolumnie lub pod spodem.

---

## 10. Diagram topologii

**Odpowiada na pytanie:** gdzie to fizycznie działa i co przez co przechodzi.

**Zawiera:** granice hostingu (subskrypcja, resource group, klaster AKS, namespace, App Service Plan), strefy bezpieczeństwa (Green/Red Zone), sieci i punkty przejścia (Front Door, App Gateway, Private Endpoint), oraz komponenty z diagramu komponentów **umieszczone wewnątrz** tych granic.

**Nie zawiera:** logiki biznesowej, szczegółów kontraktów, wewnętrznych zależności, które nie przekraczają żadnej granicy.

**Zagnieżdżenie:** `Subskrypcja → Resource Group / Klaster → Namespace → Workload`. Maks. 3 poziomy widoczne naraz.

**Stereotypy** na tym diagramie opisują formę wdrożenia, nie technologię:
`«AKS Deployment · 3 repliki»`, `«Azure Blob Container»`, `«Service Bus Topic»`, `«App Service · P2v3»`.

**Ikony Azure:** na diagramach topologii dopuszczamy oficjalną bibliotekę kształtów Azure (`More Shapes → Networking → Azure`). Zasady:

- ikona jako **element dekoracyjny w lewym górnym rogu bloczka**, nie zamiast bloczka — bloczek nadal ma stereotyp, nazwę i opis,
- maks. 32 × 32 px,
- albo wszystkie elementy danego typu mają ikonę, albo żaden — mieszanka wygląda na niedokończoną,
- ikona nie zwalnia z podpisania elementu.

Na diagramach komponentów logicznych **ikon nie używamy** — tam liczy się abstrakcja od technologii.

---

## 11. Checklista przed commitem

- [ ] Tło strony ustawione na `#FFFFFF` (sprawdź w dark mode)
- [ ] Wszystkie czcionki to Helvetica/Arial
- [ ] Wszystkie bloczki tej samej kategorii mają tę samą szerokość
- [ ] Elementy wyrównane do siatki 10 px, kolumny/wiersze wyrównane
- [ ] Każda strzałka ma etykietę w formie „czasownik + obiekt"
- [ ] Brak strzałek dwukierunkowych
- [ ] Kierunek strzałek = kto inicjuje
- [ ] Kolor koduje **jedną** oś znaczeniową; legenda obecna, jeśli kolor jest semantyczny
- [ ] ≤ 15 elementów, ≤ 3 poziomy zagnieżdżenia
- [ ] Tytuł, poziom C4, właściciel i miesiąc aktualizacji obecne
- [ ] Diagram osadzony w markdownie z sensownym tekstem alternatywnym
- [ ] Plik ma rozszerzenie `.drawio.svg` i waży < 200 kB

---

## 12. Antywzorce

| Antywzorzec | Dlaczego szkodzi | Zamiast tego |
|---|---|---|
| Diagram „wszystko naraz" | Nikt go nie czyta, nikt nie aktualizuje | Kilka diagramów po jednym pytaniu każdy |
| Strzałki bez etykiet | Diagram pokazuje topologię połączeń, ale nie mówi nic o zachowaniu | Czasownik + obiekt na każdej strzałce |
| Kolor „bo ładnie" | Czytelnik szuka znaczenia, którego nie ma | Monochrom + kolor tylko semantycznie |
| Mieszanie warstw abstrakcji | Klasa obok subskrypcji Azure na jednym diagramie | Trzymaj się jednego poziomu C4 |
| Nazwy zasobów zamiast nazw logicznych | `app-ord-proc-weu-prod-01` nic nie znaczy dla czytelnika | Nazwa logiczna w środku, nazwa zasobu w opisie, jeśli potrzebna |
| Duplikowanie diagramu w slajdach | Rozjeżdża się z repo w ciągu tygodnia | Eksport/link do wersji z repo |
| Diagram jako obraz bez źródła | Nie da się edytować, ktoś rysuje od nowa | Zawsze `.drawio.svg` |

---

## 13. Materiały

- Szablon startowy z paletą: [`templates/szablon-startowy.drawio`](../templates/szablon-startowy.drawio)
- Biblioteka kształtów: [`templates/architektura.drawio-library`](../templates/architektura.drawio-library)
- Wtyczka VS Code: `hediet.vscode-drawio` (Draw.io Integration)
