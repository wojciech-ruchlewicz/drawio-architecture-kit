#!/usr/bin/env python3
"""
Generuje pliki *.drawio.svg: warstwę graficzną SVG + osadzony edytowalny mxfile
w atrybucie `content`. Jedno źródło prawdy dla stylu – stałe poniżej.

Uruchomienie:  python3 tools/gen.py
Bez zależności zewnętrznych.
"""

import html
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

ROOT = os.environ.get("DIAG_ROOT",
                      os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# ══════════════════════════════════════════════════════════ TOKENY

TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED = "#000000", "#444444", "#888888"
STROKE_BLOCK, STROKE_EDGE = "#333333", "#888888"
STROKE_EXTERNAL, STROKE_AREA, STROKE_AREA_SOLID = "#999999", "#BBBBBB", "#DDDDDD"

# Kolor koduje ZAKRES (jak w C4), nie typ elementu. Typ niesie kształt i tekst.
FILL_DEFAULT = "#FFFFFF"                                  # w zakresie diagramu
FILL_EXTERNAL, STROKE_EXTERNAL_FILL = "#F0F0F0", "#999999"  # poza naszą kontrolą
FILL_HIGHLIGHT, STROKE_HIGHLIGHT = "#FDECEC", "#E60000"     # temat diagramu (czerwień UBS)

# Strefy sieciowe – tylko na diagramach topologii, tylko na kontenerach.
FILL_ZONE_EDGE, STROKE_ZONE_EDGE = "#FFF6E5", "#B37A00"     # strefa brzegowa
FILL_ZONE_CORE, STROKE_ZONE_CORE = "#F0F4F8", "#4A6785"     # strefa wewnętrzna

FS_SMALL, FS_NAME, FS_AREA, FS_TITLE = 11, 14, 12, 18
W, H, H_COMPACT = 200, 80, 50
W_NARROW = 120
H_PIPE, H_PERSON = 60, 110
H_CYL_S, H_PIPE_S, H_PERSON_S = 60, 50, 80
RADIUS, RADIUS_AREA = 12, 16
FONT = "Helvetica, Arial, sans-serif"
SWATCH_CHAR, SWATCH_SIZE = "\u25a0", 15   # ■ U+25A0, powiększony względem 11 px tekstu

# ══════════════════════════════════════════════════════════ STYLE draw.io

_BLOCK = ("rounded=1;absoluteArcSize=1;arcSize=%d;whiteSpace=wrap;html=1;strokeWidth=1.5;"
          "fontFamily=Helvetica;fontSize=%d;fontColor=%s;align=center;verticalAlign=middle;"
          "spacingLeft=6;spacingRight=6;shadow=0;" % (RADIUS * 2, FS_NAME, TEXT_PRIMARY))
_AREA = ("rounded=1;absoluteArcSize=1;arcSize=%d;whiteSpace=wrap;html=1;strokeWidth=1.5;"
         "fontFamily=Helvetica;fontSize=%d;fontStyle=1;fontColor=%s;align=left;verticalAlign=top;"
         "spacingLeft=12;spacingTop=4;shadow=0;container=1;collapsible=0;"
         % (RADIUS_AREA * 2, FS_AREA, TEXT_SECONDARY))
_EDGE = ("edgeStyle=orthogonalEdgeStyle;rounded=1;arcSize=10;html=1;jumpStyle=arc;jumpSize=8;"
         "fontFamily=Helvetica;fontSize=%d;fontColor=%s;labelBackgroundColor=%s;"
         % (FS_SMALL, TEXT_SECONDARY, FILL_DEFAULT))


def block_style(fill, stroke, dashed=False):
    s = _BLOCK + "fillColor=%s;strokeColor=%s;" % (fill, stroke)
    return s + "dashed=1;dashPattern=6 4;" if dashed else s


def area_style(fill, stroke, dashed=False):
    s = _AREA + "fillColor=%s;strokeColor=%s;" % (fill, stroke)
    return s + "dashed=1;dashPattern=8 4;" if dashed else s


def edge_style(kind):
    if kind == "sync":
        return _EDGE + "strokeWidth=2;strokeColor=%s;endArrow=blockThin;endFill=1;endSize=6;" % STROKE_EDGE
    if kind == "async":
        return (_EDGE + "strokeWidth=2;strokeColor=%s;endArrow=open;endFill=0;endSize=8;"
                        "dashed=1;dashPattern=6 4;" % STROKE_EDGE)
    return (_EDGE + "strokeWidth=1.5;strokeColor=%s;endArrow=open;endFill=0;endSize=8;"
                    "dashed=1;dashPattern=1 3;" % STROKE_EXTERNAL)


TEXT_STYLE = ("text;html=1;align=%s;verticalAlign=middle;fontFamily=Helvetica;"
              "fontSize=%d;fontColor=%s;%s")
ACTOR_STYLE = ("shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;"
               "outlineConnect=0;strokeColor=%s;strokeWidth=1.5;fontFamily=Helvetica;"
               "fontSize=%d;fontColor=%s;" % (STROKE_BLOCK, FS_SMALL, TEXT_PRIMARY))
_SHAPE_BASE = ("whiteSpace=wrap;html=1;strokeWidth=1.5;fontFamily=Helvetica;fontSize=%d;"
               "fontColor=%s;align=center;verticalAlign=middle;shadow=0;" % (FS_NAME, TEXT_PRIMARY))


def shape_style(shape, fill, stroke):
    """Kształt koduje kategorię: prostokąt / walec / pipe / person."""
    colours = "fillColor=%s;strokeColor=%s;" % (fill, stroke)
    if shape == "cylinder":
        return "shape=cylinder3;boundedLbl=1;backgroundOutline=1;size=10;" + _SHAPE_BASE + colours
    if shape == "pipe":
        return ("shape=cylinder3;boundedLbl=1;backgroundOutline=1;size=10;direction=north;"
                + _SHAPE_BASE + colours)
    if shape == "person":
        return "shape=mxgraph.c4.person;" + _SHAPE_BASE + colours
    return block_style(fill, stroke)


def html_label(stereotype, name, desc=None):
    p = ['<div style="line-height:1.3">',
         '<font style="font-size:%dpx;color:%s">&laquo;%s&raquo;</font><br>' % (FS_SMALL, TEXT_SECONDARY, stereotype),
         '<b style="font-size:%dpx;color:%s">%s</b>' % (FS_NAME, TEXT_PRIMARY, name)]
    if desc:
        p.append('<br><font style="font-size:%dpx;color:%s">%s</font>' % (FS_SMALL, TEXT_SECONDARY, desc))
    p.append("</div>")
    return "".join(p)


# ══════════════════════════════════════════════════════════ MODEL

class Diagram:
    def __init__(self, name):
        self.name, self.items, self._n = name, [], 0

    def _id(self):
        self._n += 1
        return "n%d" % self._n

    def _add(self, **kw):
        kw["id"] = self._id()
        self.items.append(kw)
        return kw["id"]

    def block(self, x, y, stereotype, name, desc=None, fill=FILL_DEFAULT,
              stroke=STROKE_BLOCK, dashed=False, w=W, h=H, parent="1", shape="rect"):
        return self._add(kind="block", shape=shape, x=x, y=y, w=w, h=h, parent=parent,
                         fill=fill, stroke=stroke, dashed=dashed,
                         stereotype=stereotype, name=name, desc=desc,
                         style=shape_style(shape, fill, stroke),
                         value=html_label(stereotype, name, desc))

    def area(self, x, y, w, h, title, fill="none", stroke=STROKE_AREA, dashed=True, parent="1"):
        return self._add(kind="area", x=x, y=y, w=w, h=h, parent=parent, fill=fill,
                         stroke=stroke, dashed=dashed, title=title,
                         style=area_style(fill, stroke, dashed), value=title)

    def actor(self, x, y, name, parent="1"):
        return self._add(kind="actor", x=x, y=y, w=30, h=60, parent=parent, name=name,
                         style=ACTOR_STYLE, value=name)

    def text(self, x, y, w, h, content, size=FS_SMALL, color=TEXT_SECONDARY,
             bold=False, align="left", parent="1"):
        return self._add(kind="text", x=x, y=y, w=w, h=h, parent=parent, content=content,
                         size=size, color=color, bold=bold, align=align,
                         style=TEXT_STYLE % (align, size, color, "fontStyle=1;" if bold else ""),
                         value=SWATCH_RE.sub(
                             lambda m: '<font color="%s" style="font-size:%dpx">%s</font> '
                             % (m.group(1), SWATCH_SIZE, SWATCH_CHAR), content))

    def swatch(self, x, y, w, h, fill, stroke, dashed=False, parent="1", shape="rect"):
        return self._add(kind="swatch", shape=shape, x=x, y=y, w=w, h=h, parent=parent,
                         fill=fill, stroke=stroke, dashed=dashed,
                         style=shape_style(shape, fill, stroke), value="")

    def edge(self, kind, label, source=None, target=None, exit_=None, entry=None,
             p0=None, p1=None):
        return self._add(kind="edge", etype=kind, label=label, source=source, target=target,
                         exit_=exit_, entry=entry, p0=p0, p1=p1,
                         style=edge_style(kind) + (
                             ("exitX=%s;exitY=%s;exitDx=0;exitDy=0;" % exit_) if exit_ else "") + (
                             ("entryX=%s;entryY=%s;entryDx=0;entryDy=0;" % entry) if entry else ""),
                         value=label)


# ══════════════════════════════════════════════════════════ mxfile

def build_mxfile(d):
    mxfile = ET.Element("mxfile", {"host": "app.diagrams.net", "type": "device", "version": "24.7.17"})
    dg = ET.SubElement(mxfile, "diagram", {"id": "d1", "name": d.name})
    model = ET.SubElement(dg, "mxGraphModel", {
        "dx": "1400", "dy": "900", "grid": "1", "gridSize": "10", "guides": "1", "tooltips": "1",
        "connect": "1", "arrows": "1", "fold": "1", "page": "0", "pageScale": "1",
        "pageWidth": "1600", "pageHeight": "1200", "adaptiveColors": "auto", "math": "0", "shadow": "0"})
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})

    by_id = {i["id"]: i for i in d.items if i["kind"] != "edge"}

    def origin(pid):
        p = by_id.get(pid)
        return (p["x"], p["y"]) if p else (0, 0)

    for it in d.items:
        if it["kind"] == "edge":
            a = {"id": it["id"], "value": it["value"], "style": it["style"],
                 "edge": "1", "parent": "1"}
            if it["source"]:
                a["source"] = it["source"]
            if it["target"]:
                a["target"] = it["target"]
            cell = ET.SubElement(root, "mxCell", a)
            geo = ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
            if it["p0"]:
                ET.SubElement(geo, "mxPoint", {"x": str(it["p0"][0]), "y": str(it["p0"][1]),
                                               "as": "sourcePoint"})
                ET.SubElement(geo, "mxPoint", {"x": str(it["p1"][0]), "y": str(it["p1"][1]),
                                               "as": "targetPoint"})
        else:
            cell = ET.SubElement(root, "mxCell", {
                "id": it["id"], "value": it["value"], "style": it["style"],
                "vertex": "1", "parent": it["parent"]})
            ox, oy = origin(it["parent"])
            ET.SubElement(cell, "mxGeometry", {
                "x": str(it["x"] - ox), "y": str(it["y"] - oy),
                "width": str(it["w"]), "height": str(it["h"]), "as": "geometry"})
    return ET.tostring(mxfile, encoding="unicode")


# ══════════════════════════════════════════════════════════ render SVG

def wrap(text, width_px, size, bold=False):
    per_char = size * (0.58 if bold else 0.54)
    limit = max(1, int((width_px - 14) / per_char))
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if len(trial) <= limit or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


SWATCH_RE = __import__("re").compile(r"\{(#[0-9A-Fa-f]{6})\}")


def esc(s):
    return html.escape(s, quote=False)


def runs(line):
    """Dzieli linię na fragmenty (tekst, kolor|None). {#RRGGBB} staje się kwadratem."""
    out, pos = [], 0
    for m in SWATCH_RE.finditer(line):
        if m.start() > pos:
            out.append((line[pos:m.start()], None))
        out.append((SWATCH_CHAR + " ", m.group(1)))
        pos = m.end()
    if pos < len(line):
        out.append((line[pos:], None))
    return out or [(line, None)]


def rounded_rect(x, y, w, h, r, fill, stroke, dashed, sw=1.5):
    dash = ' stroke-dasharray="6 4"' if dashed else ""
    return ('<rect x="%g" y="%g" width="%g" height="%g" rx="%g" ry="%g" fill="%s" '
            'stroke="%s" stroke-width="%s"%s/>' % (x, y, w, h, r, r, fill, stroke, sw, dash))


def svg_text(x, y, content, size, color, bold=False, anchor="start"):
    return ('<text x="%g" y="%g" font-family="%s" font-size="%d" fill="%s"%s '
            'text-anchor="%s">%s</text>'
            % (x, y, FONT, size, color, ' font-weight="bold"' if bold else "", anchor, esc(content)))


def shape_outline(it):
    out = []
    x, y, w, h = it["x"], it["y"], it["w"], it["h"]
    if it["shape"] == "pipe":
        rx = 10
        out.append('<path d="M %g %g L %g %g A %g %g 0 0 1 %g %g L %g %g A %g %g 0 0 1 %g %g Z" '
                   'fill="%s" stroke="%s" stroke-width="1.5"/>'
                   % (x + rx, y, x + w - rx, y, rx, h / 2, x + w - rx, y + h,
                      x + rx, y + h, rx, h / 2, x + rx, y, it["fill"], it["stroke"]))
        out.append('<path d="M %g %g A %g %g 0 0 1 %g %g" fill="none" stroke="%s" stroke-width="1.5"/>'
                   % (x + rx, y, rx, h / 2, x + rx, y + h, it["stroke"]))
    elif it["shape"] == "person":
        r = 15
        out.append(rounded_rect(x, y + r + 7, w, h - r - 7, RADIUS, it["fill"], it["stroke"], False))
        out.append('<ellipse cx="%g" cy="%g" rx="%g" ry="%g" fill="%s" stroke="%s" stroke-width="1.5"/>'
                   % (x + w / 2, y + r, r, r, it["fill"], it["stroke"]))
        out.append('<path d="M %g %g A %g %g 0 0 0 %g %g" fill="%s" stroke="none"/>'
                   % (x + w / 2 - 13, y + r + 7, r, r, x + w / 2 + 13, y + r + 7, it["fill"]))
    elif it["shape"] == "cylinder":
        ry = 10
        out.append('<path d="M %g %g L %g %g A %g %g 0 0 0 %g %g L %g %g A %g %g 0 0 0 %g %g Z" '
                   'fill="%s" stroke="%s" stroke-width="1.5"/>'
                   % (x, y + ry, x, y + h - ry, w / 2, ry, x + w, y + h - ry,
                      x + w, y + ry, w / 2, ry, x, y + ry, it["fill"], it["stroke"]))
        out.append('<path d="M %g %g A %g %g 0 0 0 %g %g" fill="none" stroke="%s" stroke-width="1.5"/>'
                   % (x, y + ry, w / 2, ry, x + w, y + ry, it["stroke"]))
    else:
        out.append(rounded_rect(x, y, w, h, RADIUS, it["fill"], it["stroke"], it["dashed"]))
    return out


def render_block(it):
    out = shape_outline(it)
    x, y, w, h = it["x"], it["y"], it["w"], it["h"]
    lines = [("«%s»" % it["stereotype"], FS_SMALL, TEXT_SECONDARY, False),
             (it["name"], FS_NAME, TEXT_PRIMARY, True)]
    if it["desc"]:
        for ln in wrap(it["desc"], w - (24 if it["shape"] == "pipe" else 0), FS_SMALL):
            lines.append((ln, FS_SMALL, TEXT_SECONDARY, False))
    total = sum(s * 1.35 for _, s, _, _ in lines)
    top, height = y, h
    if it["shape"] == "person":
        top, height = y + 22, h - 22
    cy = top + (height - total) / 2
    if it["shape"] == "cylinder":
        cy += 5
    for txt, size, color, bold in lines:
        cy += size * 1.35
        out.append(svg_text(x + w / 2, cy - size * 0.32, txt, size, color, bold, "middle"))
    return out


def render_area(it):
    return [rounded_rect(it["x"], it["y"], it["w"], it["h"], RADIUS_AREA,
                         it["fill"], it["stroke"], it["dashed"]),
            svg_text(it["x"] + 12, it["y"] + 20, it["title"], FS_AREA, TEXT_SECONDARY, True)]


def render_actor(it):
    x, y, w, h = it["x"], it["y"], it["w"], it["h"]
    s = STROKE_BLOCK
    out = ['<ellipse cx="%g" cy="%g" rx="%g" ry="%g" fill="none" stroke="%s" stroke-width="1.5"/>'
           % (x + w / 2, y + h / 8, w / 4, h / 8, s),
           '<path d="M %g %g L %g %g M %g %g L %g %g M %g %g L %g %g M %g %g L %g %g" '
           'fill="none" stroke="%s" stroke-width="1.5"/>'
           % (x + w / 2, y + h / 4, x + w / 2, y + 2 * h / 3,
              x, y + h / 3, x + w, y + h / 3,
              x + w / 2, y + 2 * h / 3, x, y + h,
              x + w / 2, y + 2 * h / 3, x + w, y + h, s)]
    out.append(svg_text(x + w / 2, y + h + 13, it["name"], FS_SMALL, TEXT_PRIMARY, False, "middle"))
    return out


def render_text(it):
    anchor = {"left": "start", "center": "middle", "right": "end"}[it["align"]]
    tx = it["x"] if it["align"] == "left" else (
        it["x"] + it["w"] / 2 if it["align"] == "center" else it["x"] + it["w"])
    lines = it["content"].split("<br>")
    out, cy = [], it["y"] + (it["h"] - len(lines) * it["size"] * 1.35) / 2
    for ln in lines:
        cy += it["size"] * 1.35
        parts = runs(ln)
        if len(parts) == 1 and parts[0][1] is None:
            out.append(svg_text(tx, cy - it["size"] * 0.32, ln, it["size"], it["color"],
                                it["bold"], anchor))
        else:
            spans = "".join(
                ('<tspan fill="%s" font-size="%d">%s</tspan>' % (col, SWATCH_SIZE, esc(txt)))
                if col else esc(txt)
                for txt, col in parts)
            out.append('<text x="%g" y="%g" font-family="%s" font-size="%d" fill="%s"%s '
                       'text-anchor="%s">%s</text>'
                       % (tx, cy - it["size"] * 0.32, FONT, it["size"], it["color"],
                          ' font-weight="bold"' if it["bold"] else "", anchor, spans))
    return out


def anchor_point(it, frac):
    return (it["x"] + float(frac[0]) * it["w"], it["y"] + float(frac[1]) * it["h"])


def route(p0, p1, exit_, entry):
    """Prosty router ortogonalny – L lub Z, jak draw.io dla prostych przypadków."""
    if exit_ is None:
        return [p0, p1]
    horiz_out = float(exit_[0]) in (0.0, 1.0)
    horiz_in = entry is not None and float(entry[0]) in (0.0, 1.0)
    if horiz_out and horiz_in:
        if abs(p0[1] - p1[1]) < 1:
            return [p0, p1]
        mx = (p0[0] + p1[0]) / 2
        return [p0, (mx, p0[1]), (mx, p1[1]), p1]
    if not horiz_out and not horiz_in:
        if abs(p0[0] - p1[0]) < 1:
            return [p0, p1]
        my = (p0[1] + p1[1]) / 2
        return [p0, (p0[0], my), (p1[0], my), p1]
    if horiz_out:
        return [p0, (p1[0], p0[1]), p1]
    return [p0, (p0[0], p1[1]), p1]


def path_with_corners(pts, r=10):
    d = ["M %g %g" % pts[0]]
    for i in range(1, len(pts) - 1):
        a, b, c = pts[i - 1], pts[i], pts[i + 1]
        v1 = (b[0] - a[0], b[1] - a[1])
        v2 = (c[0] - b[0], c[1] - b[1])
        l1 = max(1e-6, (v1[0] ** 2 + v1[1] ** 2) ** 0.5)
        l2 = max(1e-6, (v2[0] ** 2 + v2[1] ** 2) ** 0.5)
        rr = min(r, l1 / 2, l2 / 2)
        p_in = (b[0] - v1[0] / l1 * rr, b[1] - v1[1] / l1 * rr)
        p_out = (b[0] + v2[0] / l2 * rr, b[1] + v2[1] / l2 * rr)
        d.append("L %g %g" % p_in)
        d.append("Q %g %g %g %g" % (b[0], b[1], p_out[0], p_out[1]))
    d.append("L %g %g" % pts[-1])
    return " ".join(d)


def arrow_head(p_prev, p_end, filled, color, size=8):
    dx, dy = p_end[0] - p_prev[0], p_end[1] - p_prev[1]
    l = max(1e-6, (dx * dx + dy * dy) ** 0.5)
    ux, uy = dx / l, dy / l
    bx, by = p_end[0] - ux * size, p_end[1] - uy * size
    w = size * 0.42
    a = (bx - uy * w, by + ux * w)
    b = (bx + uy * w, by - ux * w)
    if filled:
        return ('<path d="M %g %g L %g %g L %g %g Z" fill="%s" stroke="%s" stroke-width="1"/>'
                % (p_end[0], p_end[1], a[0], a[1], b[0], b[1], color, color))
    return ('<path d="M %g %g L %g %g L %g %g" fill="none" stroke="%s" stroke-width="1.5"/>'
            % (a[0], a[1], p_end[0], p_end[1], b[0], b[1], color))


def render_edge(it, by_id):
    if it["source"]:
        p0 = anchor_point(by_id[it["source"]], it["exit_"] or ("0.5", "0.5"))
        p1 = anchor_point(by_id[it["target"]], it["entry"] or ("0.5", "0.5"))
    else:
        p0, p1 = it["p0"], it["p1"]
    pts = route(p0, p1, it["exit_"], it["entry"])
    color = STROKE_EDGE if it["etype"] in ("sync", "async") else STROKE_EXTERNAL
    width = 2 if it["etype"] in ("sync", "async") else 1.5
    dash = ""
    if it["etype"] == "async":
        dash = ' stroke-dasharray="6 4"'
    elif it["etype"] == "dep":
        dash = ' stroke-dasharray="1 3"'
    out = ['<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linejoin="round"%s/>'
           % (path_with_corners(pts), color, width, dash)]
    out.append(arrow_head(pts[-2], pts[-1], it["etype"] == "sync", color))
    if it["label"]:
        tw = len(it["label"]) * FS_SMALL * 0.54 + 8
        # Etykieta na środku segmentu, który nie wchodzi na żaden bloczek.
        # Przy remisie wygrywa dłuższy segment – tam jest najwięcej powietrza.
        obstacles = [o for o in by_id.values() if o["kind"] in ("block", "swatch", "actor")]

        def collides(cx, cy):
            for o in obstacles:
                if (cx + tw / 2 > o["x"] and cx - tw / 2 < o["x"] + o["w"]
                        and cy + 8 > o["y"] and cy - 8 < o["y"] + o["h"]):
                    return True
            return False

        cands = []
        for i in range(len(pts) - 1):
            cx, cy = (pts[i][0] + pts[i + 1][0]) / 2, (pts[i][1] + pts[i + 1][1]) / 2
            ln = ((pts[i][0] - pts[i + 1][0]) ** 2 + (pts[i][1] - pts[i + 1][1]) ** 2) ** 0.5
            cands.append((collides(cx, cy), -ln, cx, cy))
        _, _, mx_, my_ = min(cands)
        out.append('<rect x="%g" y="%g" width="%g" height="%g" fill="%s"/>'
                   % (mx_ - tw / 2, my_ - 9, tw, 16, FILL_DEFAULT))
        out.append(svg_text(mx_, my_ + 3, it["label"], FS_SMALL, TEXT_SECONDARY, False, "middle"))
    return out


ORDER = {"area": 0, "swatch": 1, "block": 1, "actor": 1, "edge": 2, "text": 3}


def render_svg(d, pad=16):
    by_id = {i["id"]: i for i in d.items if i["kind"] != "edge"}
    body = []
    for it in sorted(d.items, key=lambda i: (ORDER[i["kind"]], d.items.index(i))):
        if it["kind"] == "block":
            body += render_block(it)
        elif it["kind"] == "area":
            body += render_area(it)
        elif it["kind"] == "actor":
            body += render_actor(it)
        elif it["kind"] == "text":
            body += render_text(it)
        elif it["kind"] == "swatch":
            body += shape_outline(it)
        else:
            body += render_edge(it, by_id)

    xs = [i["x"] for i in d.items if i["kind"] != "edge"]
    ys = [i["y"] for i in d.items if i["kind"] != "edge"]
    xe = [i["x"] + i["w"] for i in d.items if i["kind"] != "edge"]
    ye = [i["y"] + i["h"] + (16 if i["kind"] == "actor" else 0) for i in d.items if i["kind"] != "edge"]
    for i in d.items:
        if i["kind"] == "edge" and i["p0"]:
            xs += [i["p0"][0], i["p1"][0]]; xe += [i["p0"][0], i["p1"][0]]
            ys += [i["p0"][1], i["p1"][1]]; ye += [i["p0"][1], i["p1"][1]]
    x0, y0 = min(xs) - pad, min(ys) - pad
    w, h = max(xe) + pad - x0, max(ye) + pad - y0
    return x0, y0, w, h, "\n".join(body)


def write(path, d):
    x0, y0, w, h, body = render_svg(d)
    content = html.escape(build_mxfile(d), quote=True)
    svg = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
           'version="1.1" width="%gpx" height="%gpx" viewBox="%g %g %g %g" content="%s">\n'
           '%s\n</svg>\n' % (w, h, x0, y0, w, h, content, body))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    return len(svg)


# ══════════════════════════════════════════════════════════ PALETTE

p = Diagram("Palette")
p.text(40, 20, 1100, 26, "Architecture diagram palette", FS_TITLE, TEXT_PRIMARY, True)
p.text(40, 48, 1100, 16, "Three independent channels: shape = category, colour = scope, "
                         "text = exact type and technology.")

# --- 1 · kształt
p.text(40, 92, 600, 20, "1 / Shape – what kind of thing it is", FS_NAME, TEXT_SECONDARY, True)
p.block(40, 126, "Microservice / Spring Boot", "Execution Engine", "Routes client orders to venues")
p.text(40, 232, 250, 30, "Rectangle – service, application,<br>component, job", FS_SMALL, TEXT_MUTED)

p.block(300, 126, "PostgreSQL", "Orders DB", shape="cylinder")
p.text(300, 232, 250, 30, "Standing cylinder – data store<br>(database, blob, cache)", FS_SMALL, TEXT_MUTED)

p.block(560, 141, "Kafka topic", "trade-events", shape="pipe", h=H_PIPE)
p.text(560, 232, 250, 30, "Lying cylinder (pipe) – queue,<br>topic, event stream", FS_SMALL, TEXT_MUTED)

p.block(820, 116, "Person", "Sales trader", "Captures client orders",
        shape="person", h=H_PERSON)
p.text(820, 232, 250, 30, "Person – human role<br>(shape=mxgraph.c4.person)", FS_SMALL, TEXT_MUTED)

# --- 2 · warianty rozmiaru
p.text(40, 288, 700, 20, "2 / Variants – same meaning, less room", FS_NAME, TEXT_SECONDARY, True)
p.block(40, 330, "REST API / Spring Boot", "Order Gateway", h=H_COMPACT)
p.text(40, 400, 250, 30, "Compact rectangle – 200 x 50,<br>no description line", FS_SMALL, TEXT_MUTED)

p.block(300, 330, "Adapter", "FIX Adapter", w=W_NARROW, h=H_COMPACT)
p.text(300, 400, 160, 30, "Narrow rectangle – 120 x 50,<br>adapters, gateways, sidecars", FS_SMALL, TEXT_MUTED)

p.block(470, 325, "PostgreSQL", "Orders", shape="cylinder", w=W_NARROW, h=H_CYL_S)
p.text(470, 400, 160, 30, "Small cylinder<br>120 x 60", FS_SMALL, TEXT_MUTED)

p.block(650, 330, "Kafka", "trades", shape="pipe", w=W_NARROW, h=H_PIPE_S)
p.text(650, 400, 160, 30, "Small pipe<br>120 x 50", FS_SMALL, TEXT_MUTED)

p.block(830, 310, "Person", "Trader", shape="person", w=W_NARROW, h=H_PERSON_S)
p.text(830, 400, 160, 30, "Small person<br>120 x 80", FS_SMALL, TEXT_MUTED)

# --- 3 · kolor = zakres
p.text(40, 456, 700, 20, "3 / Colour – how much of it is ours", FS_NAME, TEXT_SECONDARY, True)
p.block(40, 490, "Microservice / Spring Boot", "Execution Engine", "Routes client orders to venues")
p.text(40, 578, 250, 30, "In scope<br>{#FFFFFF}#FFFFFF / {#333333}#333333", FS_SMALL, TEXT_MUTED)

p.block(300, 490, "External System", "Reference Data", "Instrument and counterparty master",
        fill=FILL_EXTERNAL, stroke=STROKE_EXTERNAL_FILL)
p.text(300, 578, 250, 30, "Out of scope, third party<br>{#F0F0F0}#F0F0F0 / {#999999}#999999",
       FS_SMALL, TEXT_MUTED)

p.block(560, 490, "Microservice / Python", "Position Keeper", "The subject of this diagram",
        fill=FILL_HIGHLIGHT, stroke=STROKE_HIGHLIGHT)
p.text(560, 578, 250, 30, "Highlight, at most one per diagram<br>{#FDECEC}#FDECEC / {#E60000}#E60000",
       FS_SMALL, TEXT_MUTED)

# --- 4 · obszary
p.text(40, 634, 700, 20, "4 / Areas (containers)", FS_NAME, TEXT_SECONDARY, True)
_areas = [
    (40, "none", STROKE_AREA, True, "Bounded Context: Order Execution",
     "Soft boundary – dashed, no fill<br>{#BBBBBB}#BBBBBB"),
    (360, "none", STROKE_AREA_SOLID, False, "Namespace: execution",
     "Hard boundary – solid, no fill<br>{#DDDDDD}#DDDDDD"),
    (680, FILL_ZONE_EDGE, STROKE_ZONE_EDGE, False, "Perimeter zone",
     "Network zone, topology only<br>{#FFF6E5}#FFF6E5 / {#B37A00}#B37A00"),
    (1000, FILL_ZONE_CORE, STROKE_ZONE_CORE, False, "Internal zone",
     "Network zone, topology only<br>{#F0F4F8}#F0F4F8 / {#4A6785}#4A6785"),
]
for x, fill, stroke, dashed, title, cap in _areas:
    a = p.area(x, 668, 280, 130, title, fill=fill, stroke=stroke, dashed=dashed)
    p.block(x + 40, 718, "AKS Deployment", "Component", h=H_COMPACT, parent=a)
    p.text(x, 808, 280, 30, cap, FS_SMALL, TEXT_MUTED)

# --- 5 · strzałki
p.text(40, 864, 600, 20, "5 / Connectors", FS_NAME, TEXT_SECONDARY, True)
for i, (kind, lbl, cap) in enumerate([
    ("sync", "fetches instrument data", "Synchronous call – solid, filled head / {#888888}#888888, 2px"),
    ("async", "publishes OrderExecuted", "Asynchronous message – dashed, open head"),
    ("dep", "reads configuration", "Logical dependency – dotted / {#999999}#999999, 1.5px"),
]):
    y = 912 + i * 56
    p.edge(kind, lbl, p0=(60, y), p1=(400, y))
    p.text(40, y + 12, 480, 16, cap, FS_SMALL, TEXT_MUTED)

# --- 6 · tokeny
p.text(560, 864, 400, 20, "6 / Type", FS_NAME, TEXT_SECONDARY, True)
ty = p.area(560, 902, 380, 150, "Four sizes, two colours",
            fill="none", stroke=STROKE_AREA_SOLID, dashed=False)
p.text(580, 936, 340, 100,
       "18 bold – diagram title / {#000000}#000000<br>"
       "14 bold – element name / {#000000}#000000<br>"
       "12 bold – area title / {#444444}#444444<br>"
       "11 – everything else / {#444444}#444444<br>"
       "Helvetica, no other family", FS_SMALL, TEXT_SECONDARY, parent=ty)

p.text(980, 864, 400, 20, "7 / Geometry", FS_NAME, TEXT_SECONDARY, True)
gm = p.area(980, 902, 380, 150, "Grid 10, everything snaps",
            fill="none", stroke=STROKE_AREA_SOLID, dashed=False)
p.text(1000, 936, 340, 100,
       "rectangle 200 x 80, compact 200 x 50<br>"
       "narrow 120 x 50, pipe 200 x 60<br>"
       "person 200 x 110, area radius 16<br>"
       "corner radius 12, stroke 1.5<br>"
       "gaps 60 horizontal, 40 vertical", FS_SMALL, TEXT_SECONDARY, parent=gm)

p.text(560, 1064, 800, 16,
       "Cylinder and pipe carry name + «type» only – the domed cap eats the description line.",
       FS_SMALL, TEXT_MUTED)


# ══════════════════════════════════════════════════════════ EXAMPLE: COMPONENTS

c = Diagram("Components")
c.text(40, 24, 800, 26, "Order Execution – logical components", FS_TITLE, TEXT_PRIMARY, True)
c.text(40, 52, 800, 16, "Level: C4 L2 | Owner: Electronic Trading | Updated: 2026-08")

b_trader = c.block(40, 200, "Person", "Sales trader", "Captures client orders",
                   shape="person", w=180, h=H_PERSON)
b_gw = c.block(300, 215, "REST API / Spring Boot", "Order Gateway",
               "Validates and enriches client orders")
ctx = c.area(640, 110, 640, 370, "Bounded Context: Order Execution")
b_exec = c.block(680, 170, "Microservice / Spring Boot", "Execution Engine",
                 "Routes orders to trading venues", parent=ctx)
b_db = c.block(1020, 170, "PostgreSQL", "Orders DB", shape="cylinder", parent=ctx)
b_bus = c.block(680, 330, "Kafka topic", "trade-events", shape="pipe", h=H_PIPE, parent=ctx)
b_pos = c.block(1020, 320, "Microservice / Python", "Position Keeper",
                "Maintains intraday positions", parent=ctx)
b_ref = c.block(300, 375, "External System", "Reference Data",
                "Instrument and counterparty master",
                fill=FILL_EXTERNAL, stroke=STROKE_EXTERNAL_FILL)

c.edge("sync", "submits client order", b_trader, b_gw, ("1", "0.5"), ("0", "0.5"))
c.edge("sync", "forwards order (REST)", b_gw, b_exec, ("1", "0.5"), ("0", "0.5"))
c.edge("sync", "reads / writes order state", b_exec, b_db, ("1", "0.5"), ("0", "0.5"))
c.edge("async", "publishes OrderExecuted", b_exec, b_bus, ("0.5", "1"), ("0.5", "0"))
c.edge("async", "subscribes OrderExecuted", b_bus, b_pos, ("1", "0.5"), ("0", "0.5"))
c.edge("sync", "fetches instrument data (REST)", b_gw, b_ref, ("0.5", "1"), ("0.5", "0"))


# ══════════════════════════════════════════════════════════ EXAMPLE: TOPOLOGY

t = Diagram("Topology")
t.text(40, 24, 800, 26, "Order Execution – topology", FS_TITLE, TEXT_PRIMARY, True)
t.text(40, 52, 800, 16, "Level: C4 Deployment | Owner: Electronic Trading | Updated: 2026-08")

sub = t.area(40, 110, 1120, 480, "Subscription: sub-etrading-prod (West Europe)")
edge_z = t.area(80, 170, 320, 400, "Perimeter zone – partner connectivity",
                fill=FILL_ZONE_EDGE, stroke=STROKE_ZONE_EDGE, dashed=False, parent=sub)
t_fd = t.block(110, 240, "Azure Front Door", "Edge", "TLS termination, WAF, routing", parent=edge_z)
t_gw = t.block(110, 390, "App Service / P2v3", "Order Gateway",
               "Authenticates partner traffic", parent=edge_z)

core = t.area(440, 170, 680, 400, "Internal zone – trading network",
              fill=FILL_ZONE_CORE, stroke=STROKE_ZONE_CORE, dashed=False, parent=sub)
aks = t.area(480, 230, 380, 300, "AKS: aks-etrading-prod | namespace: execution",
             fill="none", stroke=STROKE_AREA_SOLID, dashed=False, parent=core)
t_exec = t.block(510, 290, "AKS Deployment / 3 replicas", "Execution Engine",
                 "HPA 3-10, limit 1 vCPU / 2 GiB", parent=aks)
t.block(510, 410, "AKS Deployment / 2 replicas", "Position Keeper",
        "HPA 2-6, limit 0.5 vCPU / 1 GiB", parent=aks)
t.block(900, 290, "Azure PostgreSQL", "Orders DB",
        shape="cylinder", parent=core)
t.block(900, 420, "Event Hubs / Kafka", "trade-events", shape="pipe", h=H_PIPE, parent=core)

t.edge("sync", "routes traffic after WAF", t_fd, t_gw, ("0.5", "1"), ("0.5", "0"))
t.edge("sync", "calls order API (Private Link)", t_gw, t_exec, ("1", "0.5"), ("0", "0.5"))

t.text(40, 630, 900, 16,
       "Only zone crossings are drawn. Dependencies that stay inside one zone belong "
       "on the component diagram.", FS_SMALL, TEXT_MUTED)


# ══════════════════════════════════════════════════════════ BLANK

# Pusty diagram z komplet ustawień (adaptiveColors, page=0, brak tła, siatka 10).
# Zostaje tylko nagłówek, bo wymaga go checklista – nadpisz i rysuj.
b = Diagram("Diagram")
b.text(40, 24, 800, 26, "Area – diagram type", FS_TITLE, TEXT_PRIMARY, True)
b.text(40, 52, 800, 16, "Level: C4 L2 | Owner: Team | Updated: YYYY-MM")


# ══════════════════════════════════════════════════════════ ZAPIS

for path, diagram in [
    ("templates/blank.drawio.svg", b),
    ("templates/palette.drawio.svg", p),
    ("examples/components-example.drawio.svg", c),
    ("examples/topology-example.drawio.svg", t),
]:
    n = write(os.path.join(ROOT, path), diagram)
    print("%-46s %6d B" % (path, n))
