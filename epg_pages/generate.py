#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合并多个 XMLTV EPG 源，生成单一 e.xml 供 GitHub Pages 托管。"""
import urllib.request, gzip, re, sys, os, io
import xml.etree.ElementTree as ET

SOURCES = [
    "http://epg.51zmt.top:8000/e.xml",
    "https://epg.pw/xmltv/epg_CN.xml",
    "https://live.fanmingming.com/e.xml",
    "https://epg.v1.mk/fy.xml",
]

OUT_DIR = "output"
CNAME = "tingbao.cc.cd"

def fetch(url, timeout=90):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (EPG-Bot; +https://github.com/zengzifeng520/IPTV)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
    if data[:2] == b"\x1f\x8b":  # gzip magic
        data = gzip.decompress(data)
    return data

def normalize(name):
    if not name:
        return ""
    s = name.lower()
    s = re.sub(r"[\s\-_+·•.()（）【】\[\]：:、,，/\\]+", "", s)
    s = s.replace("高清", "").replace("标清", "").replace("4k", "").replace("8k", "")
    return s

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    all_channels = {}   # norm -> {"id": canon_id, "names": set, "icons": set}
    seen_prog = set()   # (norm, start, title) 去重
    prog_list = []      # 收集 programme 元素

    for url in SOURCES:
        try:
            data = fetch(url)
        except Exception as e:
            print(f"[skip] 下载失败 {url}: {e}", file=sys.stderr)
            continue

        try:
            root = ET.fromstring(data)
        except Exception as e:
            print(f"[skip] 解析失败 {url}: {e}", file=sys.stderr)
            continue

        n_ch = n_prog = 0
        id_to_norm = {}
        for ch in root.findall("channel"):
            cid = ch.get("id", "")
            names = [n.text.strip() for n in ch.findall("display-name") if n.text and n.text.strip()]
            if not names:
                names = [cid] if cid else ["unknown"]
            norm = normalize(names[0])
            if not norm:
                continue
            id_to_norm[cid] = norm
            if norm not in all_channels:
                all_channels[norm] = {"id": names[0], "names": set(), "icons": set()}
            all_channels[norm]["names"].update(names)
            for ic in ch.findall("icon"):
                src = ic.get("src")
                if src:
                    all_channels[norm]["icons"].add(src)
            n_ch += 1

        for p in root.findall("programme"):
            src_cid = p.get("channel", "")
            norm = id_to_norm.get(src_cid) or normalize(src_cid)
            start = p.get("start", "")
            t = p.find("title")
            title = (t.text or "").strip() if t is not None else ""
            key = (norm, start, title)
            if key in seen_prog:
                continue
            seen_prog.add(key)
            canon = all_channels.get(norm, {}).get("id", src_cid)
            p.set("channel", canon)
            prog_list.append(p)
            n_prog += 1

        print(f"[ok] {url}: channels={n_ch}, programmes={n_prog}", file=sys.stderr)

    # 组装输出
    tv = ET.Element("tv")
    for norm in sorted(all_channels):
        info = all_channels[norm]
        ch = ET.SubElement(tv, "channel")
        ch.set("id", info["id"])
        for dn in sorted(info["names"]):
            e = ET.SubElement(ch, "display-name")
            e.text = dn
        for src in sorted(info["icons"]):
            ic = ET.SubElement(ch, "icon")
            ic.set("src", src)
    for p in prog_list:
        tv.append(p)

    ET.indent(tv, space="  ")
    xml_bytes = ET.tostring(tv, encoding="utf-8", xml_declaration=True)

    with open(os.path.join(OUT_DIR, "e.xml"), "wb") as f:
        f.write(xml_bytes)
    with open(os.path.join(OUT_DIR, "e.xml.gz"), "wb") as f:
        f.write(gzip.compress(xml_bytes, 6))
    with open(os.path.join(OUT_DIR, "CNAME"), "w") as f:
        f.write(CNAME + "\n")
    with open(os.path.join(OUT_DIR, ".nojekyll"), "w") as f:
        f.write("")

    size = os.path.getsize(os.path.join(OUT_DIR, "e.xml"))
    print(f"DONE: channels={len(all_channels)}, programmes={len(prog_list)}, e.xml={size/1024/1024:.1f}MB", file=sys.stderr)

if __name__ == "__main__":
    main()
