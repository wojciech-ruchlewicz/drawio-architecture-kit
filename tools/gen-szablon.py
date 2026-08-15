#!/usr/bin/env python3
"""Generuje szablon startowy .drawio oraz bibliotekę kształtów .drawio-library
zgodne ze specyfikacją docs/01-spec-stylu.md"""

import json
import os
import html
from xml.dom import minidom
import xml.etree.ElementTree as ET

# ---------------------------------------------------------------- tokeny stylu

BASE = ("rounded=1;absoluteArcSize=1;arcSize=24;whiteSpace=wrap;html=1;"
        "strokeWidth=1.5;fontFamily=Helvetica;fontSize=14;fontColor=#000000;"
        "align=center;verticalAlign=middle;spacingLeft=8;spacingRight=8;shadow=0;")

S_COMPONENT = BASE + "fillColor=#FFFFFF;strokeColor=#333333;"
S_DATASTORE = BASE + "fillColor=#F0F4F8;strokeColor=#4A6785;"
S_BROKER    = BASE + "fillColor=#F5F0F8;strokeColor=#6E5A85;"
S_EXTERNAL  = BASE + "fillColor=#F5F5F5;strokeColor=#999999;dashed=1;dashPattern=6 4;"
S_HIGHLIGHT = BASE + "fillColor=#FFF6E5;strokeColor=#B37A00;"

CONTAINER = ("rounded=1;absoluteArcSize=1;arcSize=32;whiteSpace=wrap;html=1;"
             "dashed=1;dashPattern=8 4;strokeWidth=1.5;fontFamily=Helvetica;"
             "fontSize=12;fontStyle=1;fontColor=#444444;align=left;verticalAlign=top;"
             "spacingLeft=12;spacingTop=6;shadow=0;container=1;collapsible=0;")

S_GROUP = CONTAINER + "fillColor=#FAFAFA;strokeColor=#BBBBBB;"
S_GREEN = CONTAINER + "fillColor=#F2F7F3;strokeColor=#6FA97F;"
S_RED   = CONTAINER + "fillColor=#FBF3F3;strokeColor=#C08585;"

S_ACTOR = ("shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;"
           "outlineConnect=0;strokeColor=#333333;strokeWidth=1.5;fontFamily=Helvetica;"
           "fontSize=12;fontColor=#000000;")

EDGE_BASE = ("edgeStyle=orthogonalEdgeStyle;rounded=1;arcSize=10;html=1;"
             "strokeWidth=2;jumpStyle=arc;jumpSize=8;fontFamily=Helvetica;"
             "fontSize=10;fontColor=#444444;labelBackgroundColor=#FFFFFF;")

E_SYNC  = EDGE_BASE + "strokeColor=#888888;endArrow=blockThin;endFill=1;endSize=6;"
E_ASYNC = EDGE_BASE + "strokeColor=#888888;endArrow=open;endFill=0;endSize=8;dashed=1;dashPattern=6 4;"
E_DEP   = ("edgeStyle=orthogonalEdgeStyle;rounded=1;arcSize=10;html=1;strokeWidth=1.5;"
           "fontFamily=Helvetica;fontSize=10;fontColor=#444444;labelBackgroundColor=#FFFFFF;"
           "strokeColor=#999999;endArrow=open;endFill=0;endSize=8;dashed=1;dashPattern=1 3;")

T_SECTION = ("text;html=1;align=left;verticalAlign=middle;fontFamily=Helvetica;"
             "fontSize=14;fontStyle=1;fontColor=#444444;")
T_CAPTION = ("text;html=1;align=left;verticalAlign=middle;fontFamily=Helvetica;"
             "fontSize=10;fontColor=#888888;")
T_TITLE = ("text;html=1;align=left;verticalAlign=middle;fontFamily=Helvetica;"
           "fontSize=18;fontStyle=1;fontColor=#000000;")
T_META = ("text;html=1;align=left;verticalAlign=middle;fontFamily=Helvetica;"
          "fontSize=10;fontColor=#444444;")


def label(stereotype, name, desc=None):
    """Trójstrefowa etykieta HTML bloczka."""
    parts = ['<div style="line-height:1.4">']
    parts.append(f'<font style="font-size:11px;color:#444444">&laquo;{stereotype}&raquo;</font><br>')
    parts.append(f'<b style="font-size:14px;color:#000000">{name}</b>')
    if desc:
        parts.append(f'<br><font style="font-size:10px;color:#444444">{desc}</font>')
    parts.append('</div>')
    return "".join(parts)


# ---------------------------------------------------------------- budowanie XML

class Page:
    def __init__(self, name):
        self.name = name
        self.cells = []
        self._n = 0

    def _id(self):
        self._n += 1
        return f"{self.name[:3].lower()}-{self._n}"

    def node(self, x, y, w, h, style, value="", parent="1"):
        """x, y podajemy zawsze ABSOLUTNIE; przeliczenie na współrzędne
        względne rodzica robi render_page()."""
        cid = self._id()
        self.cells.append(dict(kind="vertex", id=cid, value=value, style=style,
                               parent=parent, x=x, y=y, w=w, h=h))
        return cid

    def edge(self, style, value="", source=None, target=None,
             sx=None, sy=None, tx=None, ty=None, exit_=None, entry=None):
        cid = self._id()
        st = style
        if exit_:
            st += f"exitX={exit_[0]};exitY={exit_[1]};exitDx=0;exitDy=0;"
        if entry:
            st += f"entryX={entry[0]};entryY={entry[1]};entryDx=0;entryDy=0;"
        self.cells.append(dict(kind="edge", id=cid, value=value, style=st,
                               parent="1", source=source, target=target,
                               sx=sx, sy=sy, tx=tx, ty=ty))
        return cid


def render_page(page):
    model = ET.Element("mxGraphModel", {
        "dx": "1400", "dy": "900", "grid": "1", "gridSize": "10", "guides": "1",
        "tooltips": "1", "connect": "1", "arrows": "1", "fold": "1", "page": "1",
        "pageScale": "1", "pageWidth": "1600", "pageHeight": "1200",
        "background": "#FFFFFF", "math": "0", "shadow": "0",
    })
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})

    by_id = {c["id"]: c for c in page.cells if c["kind"] == "vertex"}

    def origin(cell_id):
        """Absolutny lewy górny róg rodzica (współrzędne w cells są absolutne)."""
        if cell_id == "1" or cell_id not in by_id:
            return 0, 0
        p = by_id[cell_id]
        return p["x"], p["y"]

    for c in page.cells:
        if c["kind"] == "vertex":
            cell = ET.SubElement(root, "mxCell", {
                "id": c["id"], "value": c["value"], "style": c["style"],
                "vertex": "1", "parent": c["parent"],
            })
            ox, oy = origin(c["parent"])
            ET.SubElement(cell, "mxGeometry", {
                "x": str(c["x"] - ox), "y": str(c["y"] - oy),
                "width": str(c["w"]), "height": str(c["h"]), "as": "geometry",
            })
        else:
            attrs = {"id": c["id"], "value": c["value"], "style": c["style"],
                     "edge": "1", "parent": "1"}
            if c["source"]:
                attrs["source"] = c["source"]
            if c["target"]:
                attrs["target"] = c["target"]
            cell = ET.SubElement(root, "mxCell", attrs)
            geo = ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
            if c["sx"] is not None:
                ET.SubElement(geo, "mxPoint", {"x": str(c["sx"]), "y": str(c["sy"]),
                                               "as": "sourcePoint"})
            if c["tx"] is not None:
                ET.SubElement(geo, "mxPoint", {"x": str(c["tx"]), "y": str(c["ty"]),
                                               "as": "targetPoint"})
    return model


def render_file(pages):
    mxfile = ET.Element("mxfile", {"host": "Electron", "type": "device", "version": "24.7.17"})
    for i, p in enumerate(pages):
        d = ET.SubElement(mxfile, "diagram", {"id": f"page-{i+1}", "name": p.name})
        d.append(render_page(p))
    raw = ET.tostring(mxfile, encoding="unicode")
    return minidom.parseString(raw).toprettyxml(indent="  ")


# ---------------------------------------------------------------- strona: Paleta

pal = Page("Paleta")

pal.node(60, 40, 800, 30, T_TITLE, "Paleta — system diagramów architektonicznych")
pal.node(60, 70, 900, 20, T_META,
         "Kopiuj bloczki z tej strony do swojego diagramu. Style zgodne z docs/01-spec-stylu.md v0.1")

# --- bloczki
pal.node(60, 130, 400, 24, T_SECTION, "1 &middot; Bloczki komponentów &mdash; 240 &times; 100")

blocks = [
    (60,   S_COMPONENT, label("Microservice &middot; .NET 8", "Order Processor",
                              "Waliduje i utrwala zamówienia"), "Komponent (domyślny)"),
    (360,  S_DATASTORE, label("Azure SQL", "Orders DB",
                              "Stan zamówień, źródło prawdy"), "Magazyn danych"),
    (660,  S_BROKER,    label("Service Bus Topic", "order-events",
                              "Rozgłasza zdarzenia domenowe"), "Broker / kolejka"),
    (960,  S_EXTERNAL,  label("External System", "Payment Provider",
                              "Autoryzacja i rozliczanie płatności"), "System zewnętrzny"),
    (1260, S_HIGHLIGHT, label("Microservice &middot; .NET 8", "Shipment Planner",
                              "Element będący tematem diagramu"), "Wyróżnienie"),
]
for x, style, val, cap in blocks:
    pal.node(x, 170, 240, 100, style, val)
    pal.node(x, 275, 240, 16, T_CAPTION, cap)

# --- warianty
pal.node(60, 330, 400, 24, T_SECTION, "2 &middot; Warianty")

pal.node(60, 370, 240, 60, S_COMPONENT, label("API", "Order API"))
pal.node(60, 435, 240, 16, T_CAPTION, "Bloczek kompaktowy — 240 × 60, bez opisu")

pal.node(390, 370, 30, 60, S_ACTOR, "Operator magazynu")
pal.node(360, 435, 240, 16, T_CAPTION, "Aktor")

# --- obszary
pal.node(60, 490, 400, 24, T_SECTION, "3 &middot; Obszary (kontenery)")

g1 = pal.node(60, 530, 300, 160, S_GROUP, "Bounded Context: Ordering")
pal.node(80, 570, 260, 60, S_COMPONENT, label("Microservice", "Order Processor"), parent=g1)
pal.node(60, 695, 300, 16, T_CAPTION, "Obszar neutralny (grupa logiczna)")

g2 = pal.node(400, 530, 300, 160, S_GREEN, "Green Zone")
pal.node(420, 570, 260, 60, S_COMPONENT, label("AKS Deployment", "Order Processor"), parent=g2)
pal.node(400, 695, 300, 16, T_CAPTION, "Green Zone")

g3 = pal.node(740, 530, 300, 160, S_RED, "Red Zone")
pal.node(760, 570, 260, 60, S_COMPONENT, label("App Service", "Public Gateway"), parent=g3)
pal.node(740, 695, 300, 16, T_CAPTION, "Red Zone")

# --- strzałki
pal.node(60, 750, 400, 24, T_SECTION, "4 &middot; Strzałki")

pal.edge(E_SYNC, "pobiera profil klienta (HTTPS/JSON)", sx=80, sy=810, tx=440, ty=810)
pal.node(60, 825, 400, 16, T_CAPTION, "Wywołanie synchroniczne — linia ciągła, grot wypełniony")

pal.edge(E_ASYNC, "publikuje OrderCreated", sx=80, sy=880, tx=440, ty=880)
pal.node(60, 895, 400, 16, T_CAPTION, "Komunikacja asynchroniczna — linia przerywana, grot pusty")

pal.edge(E_DEP, "odczytuje konfigurację", sx=80, sy=950, tx=440, ty=950)
pal.node(60, 965, 400, 16, T_CAPTION, "Zależność logiczna — linia kropkowana")

# --- legenda
pal.node(600, 750, 400, 24, T_SECTION, "5 &middot; Legenda (kopiuj do prawego dolnego rogu)")

leg = pal.node(600, 790, 300, 190, S_GROUP, "Legenda")
pal.node(620, 826, 40, 24, S_COMPONENT, "", parent=leg)
pal.node(670, 826, 220, 24, T_META, "Usługa / aplikacja", parent=leg)
pal.node(620, 860, 40, 24, S_DATASTORE, "", parent=leg)
pal.node(670, 860, 220, 24, T_META, "Magazyn danych", parent=leg)
pal.node(620, 894, 40, 24, S_BROKER, "", parent=leg)
pal.node(670, 894, 220, 24, T_META, "Broker / kolejka", parent=leg)
pal.node(620, 928, 40, 24, S_EXTERNAL, "", parent=leg)
pal.node(670, 928, 220, 24, T_META, "System zewnętrzny", parent=leg)

# --- nagłówek diagramu
pal.node(1080, 750, 400, 24, T_SECTION, "6 &middot; Nagłówek diagramu")
pal.node(1080, 790, 460, 28, T_TITLE, "Order Management — komponenty logiczne")
pal.node(1080, 820, 460, 18, T_META,
         "Poziom: C4 L2 &middot; Właściciel: Team Orders &middot; Aktualizacja: 2026-08")


# ------------------------------------------------- strona: przykład komponentów

ex = Page("Przyklad-komponenty")

ex.node(60, 40, 700, 28, T_TITLE, "Order Management — komponenty logiczne")
ex.node(60, 72, 700, 18, T_META,
        "Poziom: C4 L2 &middot; Właściciel: Team Orders &middot; Aktualizacja: 2026-08")

actor = ex.node(90, 250, 30, 60, S_ACTOR, "Klient")

api = ex.node(220, 220, 240, 100, S_COMPONENT,
              label("API &middot; ASP.NET Core", "Order API",
                    "Przyjmuje i waliduje zamówienia"))

ctx = ex.node(520, 130, 620, 400, S_GROUP, "Bounded Context: Ordering")

proc = ex.node(560, 190, 240, 100, S_COMPONENT,
               label("Microservice &middot; .NET 8", "Order Processor",
                     "Realizuje logikę cyklu życia zamówienia"), parent=ctx)
db = ex.node(860, 190, 240, 100, S_DATASTORE,
             label("Azure SQL", "Orders DB", "Źródło prawdy o zamówieniach"), parent=ctx)
bus = ex.node(560, 370, 240, 100, S_BROKER,
              label("Service Bus Topic", "order-events",
                    "Rozgłasza zdarzenia domenowe"), parent=ctx)
ship = ex.node(860, 370, 240, 100, S_COMPONENT,
               label("Microservice &middot; .NET 8", "Shipment Planner",
                     "Planuje wysyłkę po opłaceniu"), parent=ctx)

pay = ex.node(220, 400, 240, 100, S_EXTERNAL,
              label("External System", "Payment Provider",
                    "Autoryzacja i rozliczanie płatności"))

ex.edge(E_SYNC, "składa zamówienie (HTTPS)", source=actor, target=api,
        exit_=("1", "0.5"), entry=("0", "0.5"))
ex.edge(E_SYNC, "przekazuje do realizacji (gRPC)", source=api, target=proc,
        exit_=("1", "0.5"), entry=("0", "0.5"))
ex.edge(E_SYNC, "zapisuje i odczytuje stan (TDS)", source=proc, target=db,
        exit_=("1", "0.5"), entry=("0", "0.5"))
ex.edge(E_ASYNC, "publikuje OrderCreated", source=proc, target=bus,
        exit_=("0.5", "1"), entry=("0.5", "0"))
ex.edge(E_ASYNC, "subskrybuje OrderPaid", source=bus, target=ship,
        exit_=("1", "0.5"), entry=("0", "0.5"))
ex.edge(E_SYNC, "autoryzuje płatność (HTTPS/JSON)", source=api, target=pay,
        exit_=("0.5", "1"), entry=("0.5", "0"))

exleg = ex.node(1180, 400, 300, 156, S_GROUP, "Legenda")
ex.node(1200, 436, 40, 24, S_COMPONENT, "", parent=exleg)
ex.node(1250, 436, 220, 24, T_META, "Usługa / aplikacja", parent=exleg)
ex.node(1200, 470, 40, 24, S_DATASTORE, "", parent=exleg)
ex.node(1250, 470, 220, 24, T_META, "Magazyn danych", parent=exleg)
ex.node(1200, 504, 40, 24, S_BROKER, "", parent=exleg)
ex.node(1250, 504, 220, 24, T_META, "Broker / kolejka", parent=exleg)


# -------------------------------------------------- strona: przykład topologii

tp = Page("Przyklad-topologia")

tp.node(60, 40, 700, 28, T_TITLE, "Order Management — topologia")
tp.node(60, 72, 700, 18, T_META,
        "Poziom: C4 Deployment &middot; Właściciel: Team Orders &middot; Aktualizacja: 2026-08")

sub = tp.node(60, 130, 1360, 560, S_GROUP, "Subskrypcja: sub-orders-prod (West Europe)")

red = tp.node(100, 190, 380, 460, S_RED, "Red Zone — ruch z internetu", parent=sub)
fd = tp.node(130, 250, 240, 100, S_COMPONENT,
             label("Azure Front Door", "Edge", "Terminacja TLS, WAF, routing"), parent=red)
gw = tp.node(130, 400, 240, 100, S_COMPONENT,
             label("App Service &middot; P2v3", "Public Gateway",
                   "Uwierzytelnia i przepuszcza ruch do Green Zone"), parent=red)

green = tp.node(520, 190, 860, 460, S_GREEN, "Green Zone — sieć prywatna", parent=sub)

aks = tp.node(560, 250, 460, 360, S_GROUP, "AKS: aks-orders-prod &middot; namespace: orders", parent=green)
proc_t = tp.node(590, 310, 240, 100, S_COMPONENT,
                 label("AKS Deployment &middot; 3 repliki", "Order Processor",
                       "HPA 3–10, limit 1 vCPU / 2 GiB"), parent=aks)
tp.node(590, 450, 240, 100, S_COMPONENT,
        label("AKS Deployment &middot; 2 repliki", "Shipment Planner",
              "HPA 2–6, limit 0.5 vCPU / 1 GiB"), parent=aks)

# Na diagramie topologii rysujemy wyłącznie przejścia przez granice stref.
tp.edge(E_SYNC, "kieruje ruch po WAF (HTTPS)", source=fd, target=gw,
        exit_=("0.5", "1"), entry=("0.5", "0"))
tp.edge(E_SYNC, "wywołuje API zamówień (HTTPS, Private Link)", source=gw, target=proc_t,
        exit_=("1", "0.5"), entry=("0", "0.5"))

tp.node(1080, 310, 240, 100, S_DATASTORE,
        label("Azure SQL &middot; Business Critical", "Orders DB",
              "Private Endpoint, geo-replika w North Europe"), parent=green)
tp.node(1080, 450, 240, 100, S_BROKER,
        label("Service Bus &middot; Premium", "order-events",
              "Private Endpoint, 1 jednostka komunikatów"), parent=green)

tpleg = tp.node(60, 720, 460, 122, S_GROUP, "Legenda")
tp.node(80, 756, 40, 24, S_RED.replace("container=1;collapsible=0;", ""), "", parent=tpleg)
tp.node(130, 756, 380, 24, T_META, "Red Zone — ekspozycja na ruch publiczny", parent=tpleg)
tp.node(80, 790, 40, 24, S_GREEN.replace("container=1;collapsible=0;", ""), "", parent=tpleg)
tp.node(130, 790, 380, 24, T_META, "Green Zone — sieć prywatna, brak dostępu z internetu", parent=tpleg)


# ---------------------------------------------------------------- zapis plików

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "templates")

with open(f"{OUT}/szablon-startowy.drawio", "w", encoding="utf-8") as f:
    f.write(render_file([pal, ex, tp]))

# --- biblioteka kształtów

def lib_entry(title, style, w, h, value=""):
    xml = (f'<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/>'
           f'<mxCell id="2" value="{html.escape(value, quote=True)}" '
           f'style="{html.escape(style, quote=True)}" vertex="1" parent="1">'
           f'<mxGeometry width="{w}" height="{h}" as="geometry"/></mxCell></root></mxGraphModel>')
    return {"xml": xml, "w": w, "h": h, "title": title, "aspect": "fixed"}


def lib_edge(title, style, value=""):
    xml = (f'<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/>'
           f'<mxCell id="2" value="{html.escape(value, quote=True)}" '
           f'style="{html.escape(style, quote=True)}" edge="1" parent="1">'
           f'<mxGeometry relative="1" as="geometry">'
           f'<mxPoint x="0" y="0" as="sourcePoint"/>'
           f'<mxPoint x="160" y="0" as="targetPoint"/>'
           f'</mxGeometry></mxCell></root></mxGraphModel>')
    return {"xml": xml, "w": 160, "h": 20, "title": title}


library = [
    lib_entry("Komponent", S_COMPONENT, 240, 100,
              label("Microservice &middot; .NET 8", "Nazwa komponentu", "Za co odpowiada")),
    lib_entry("Komponent (kompaktowy)", S_COMPONENT, 240, 60,
              label("API", "Nazwa komponentu")),
    lib_entry("Magazyn danych", S_DATASTORE, 240, 100,
              label("Azure SQL", "Nazwa bazy", "Co przechowuje")),
    lib_entry("Broker / kolejka", S_BROKER, 240, 100,
              label("Service Bus Topic", "nazwa-topicu", "Jakie zdarzenia niesie")),
    lib_entry("System zewnętrzny", S_EXTERNAL, 240, 100,
              label("External System", "Nazwa systemu", "Za co odpowiada")),
    lib_entry("Wyróżnienie", S_HIGHLIGHT, 240, 100,
              label("Microservice &middot; .NET 8", "Temat diagramu", "Za co odpowiada")),
    lib_entry("Aktor", S_ACTOR, 30, 60, "Rola użytkownika"),
    lib_entry("Obszar (neutralny)", S_GROUP, 400, 240, "Bounded Context: nazwa"),
    lib_entry("Green Zone", S_GREEN, 400, 240, "Green Zone"),
    lib_entry("Red Zone", S_RED, 400, 240, "Red Zone"),
    lib_edge("Wywołanie synchroniczne", E_SYNC, "czasownik + obiekt (HTTPS)"),
    lib_edge("Komunikacja asynchroniczna", E_ASYNC, "publikuje ZdarzenieX"),
    lib_edge("Zależność logiczna", E_DEP, "odczytuje konfigurację"),
]

with open(f"{OUT}/architektura.drawio-library", "w", encoding="utf-8") as f:
    f.write(json.dumps(library, ensure_ascii=False, indent=2))

print("ok")
