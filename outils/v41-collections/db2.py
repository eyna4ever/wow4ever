#!/usr/bin/env python3
"""WDC3/4/5 DB2 reader using WoWDBDefs layouts. Read-only; encrypted sections are skipped."""
import struct, re
from pathlib import Path
DBD = Path(__file__).resolve().parent.parent / "cache" / "dbd" / "definitions"

def parse_dbd(name, layout_hash):
    txt = (DBD / f"{name}.dbd").read_text()
    cols = {}
    blocks = txt.split("\n\n")
    head = blocks[0]
    for line in head.splitlines()[1:]:
        m = re.match(r"(\w+)(?:<[^>]*>)?\s+(\w+)", line)
        if m: cols[m.group(2)] = m.group(1)
    for b in blocks[1:]:
        lines = b.strip().splitlines()
        lay = [l for l in lines if l.startswith("LAYOUT")]
        if not lay or layout_hash.upper() not in lay[0].upper(): continue
        out = []
        for l in lines:
            if l.startswith(("LAYOUT", "BUILD", "COMMENT", "//")): continue
            m = re.match(r"(\$[^$]*\$)?([\w]+)(?:<(u?)(\d+)>)?(?:\[(\d+)\])?", l)
            if not m: continue
            ann = m.group(1) or ""; nm = m.group(2)
            out.append(dict(name=nm, type=cols.get(nm, "int"), noninline="noninline" in ann, id="$id" in ann or ",id" in ann,
                            relation="relation" in ann, unsigned=m.group(3) == "u", bits=int(m.group(4)) if m.group(4) else 32,
                            arr=int(m.group(5)) if m.group(5) else 1))
        return out
    raise KeyError(f"layout {layout_hash} not in {name}")

def bits(data, off_bits, nbits):
    b0 = off_bits >> 3; sh = off_bits & 7
    v = int.from_bytes(data[b0:b0 + ((sh + nbits + 7) >> 3)], "little")
    return (v >> sh) & ((1 << nbits) - 1)

def read(path, name):
    d = Path(path).read_bytes() if not isinstance(path, (bytes, bytearray)) else path
    magic = d[:4]; assert magic in (b"WDC3", b"WDC4", b"WDC5"), magic
    pos = 4
    if magic == b"WDC5":
        pos += 4 + 128
    (rc, fc, rs, sts, th, lh, minid, maxid, loc, flags, idx_index, tfc, bpo, lcc, fsis, cds, pds, sc) = struct.unpack("<IIIIIIIIIHHIIIIIII", d[pos:pos+68])
    pos += 68
    secs = []
    for i in range(sc):
        secs.append(struct.unpack("<QIIIIIIII", d[pos:pos+40])); pos += 40
    fields = [struct.unpack("<hH", d[pos+i*4:pos+i*4+4]) for i in range(tfc)]; pos += 4 * tfc
    fsi = [struct.unpack("<HHIIIII", d[pos+i*24:pos+i*24+24]) for i in range(fsis // 24)]; pos += fsis
    pallet = d[pos:pos+pds]; pos += pds
    common_raw = d[pos:pos+cds]; pos += cds
    # common maps
    commons = []; po = 0; co = 0; pallet_off = []
    for (fob, fsb, ads, st, v1, v2, v3) in fsi:
        if st == 2:
            m = {}
            for j in range(ads // 8):
                k, v = struct.unpack("<II", common_raw[co + j*8: co + j*8 + 8]); m[k] = v
            commons.append(m); co += ads
        else: commons.append(None)
        if st in (3, 4): pallet_off.append(po); po += ads
        else: pallet_off.append(None)
    cols = parse_dbd(name, f"{lh:08X}")
    inline = [c for c in cols if not c["noninline"]]
    idcol = next((c for c in cols if c["id"]), None)
    relcol = next((c for c in cols if c["relation"] and c["noninline"]), None)
    assert len(inline) == len(fsi), (name, len(inline), len(fsi))
    rows = {}
    total_records = sum(s[2] for s in secs)
    str_tables = {}; prev = 0; rec_base = 0
    allstr = b"".join(d[s_[1] + s_[2]*rs : s_[1] + s_[2]*rs + s_[3]] for s_ in secs)
    gidx = 0
    for (tkh, fo, src, sst, ore, ils, rds, omc, ctc) in secs:
        if flags & 1:
            gidx += src
            if tkh != 0: 
                # may be encrypted (zero-filled)
                pass
            p2 = ore
            ids = struct.unpack(f"<{ils//4}I", d[p2:p2+ils]) if ils else None; p2 += ils
            copies = [struct.unpack("<II", d[p2+j*8:p2+j*8+8]) for j in range(ctc)]; p2 += ctc * 8
            omap = [struct.unpack("<IH", d[p2+j*6:p2+j*6+6]) for j in range(omc)]; p2 += omc * 6
            p2 += rds
            omids = struct.unpack(f"<{omc}I", d[p2:p2+4*omc]) if omc else ()
            for j, (off, size) in enumerate(omap):
                rb = d[off:off+size]
                if not rb or rb.count(0) == len(rb): continue
                o = 0; row = {}
                for c in inline:
                    vals = []
                    for k in range(c["arr"]):
                        if c["type"] in ("string", "locstring"):
                            e = rb.find(b"\0", o); vals.append(rb[o:e].decode("utf-8", "replace")); o = e + 1
                        elif c["type"] == "float":
                            vals.append(struct.unpack("<f", rb[o:o+4])[0]); o += 4
                        else:
                            nb = c["bits"] // 8 or 4
                            v = int.from_bytes(rb[o:o+nb], "little", signed=not c["unsigned"]); o += nb; vals.append(v)
                    row[c["name"]] = vals if c["arr"] > 1 else vals[0]
                rid = ids[j] if ids else (omids[j] if omids else None)
                if idcol: row[idcol["name"]] = rid
                rows[rid] = row
            for nid, cid in copies:
                if cid in rows:
                    r = dict(rows[cid]); r[idcol["name"]] = nid; rows[nid] = r
            continue
        recs = d[fo:fo + src * rs]
        st_start = fo + src * rs
        strtab = d[st_start:st_start + sst]
        p2 = st_start + sst
        ids = struct.unpack(f"<{ils//4}I", d[p2:p2+ils]) if ils else None; p2 += ils
        copies = [struct.unpack("<II", d[p2+j*8:p2+j*8+8]) for j in range(ctc)]; p2 += ctc * 8
        p2 += omc * 6
        rel = {}
        if rds:
            ne, rmin, rmax = struct.unpack("<III", d[p2:p2+12])
            for j in range(ne):
                fk, ri = struct.unpack("<II", d[p2+12+j*8:p2+20+j*8]); rel[ri] = fk
            p2 += rds
        encrypted = tkh != 0 and (recs.count(0) == len(recs))
        for ri in range(src):
            if encrypted: break
            rb = recs[ri*rs:(ri+1)*rs]
            if tkh != 0 and rb.count(0) == len(rb): continue
            row = {}
            for ci, (c, (fob, fsb, ads, st, v1, v2, v3)) in enumerate(zip(inline, fsi)):
                if st == 0:
                    n = c["arr"]; size = fsb // n if n else fsb
                    vals = []
                    for k in range(n):
                        bo = fob + k * size
                        if c["type"] in ("string", "locstring"):
                            v = struct.unpack("<I", rb[bo//8:bo//8+4])[0]
                            if v == 0: vals.append(""); continue
                            a = (gidx + ri) * rs + bo // 8 + v - total_records * rs
                            e = allstr.find(b"\0", a)
                            try: vals.append(allstr[a:e].decode("utf-8"))
                            except Exception: vals.append(allstr[a:e].decode("latin-1"))
                        elif c["type"] == "float":
                            vals.append(struct.unpack("<f", rb[bo//8:bo//8+4])[0])
                        else:
                            v = bits(rb, bo, size)
                            if not c["unsigned"] and size and v >= 1 << (size - 1): v -= 1 << size
                            vals.append(v)
                    val = vals if n > 1 else vals[0]
                elif st in (1, 5):
                    v = bits(rb, fob, fsb)
                    if st == 5 and v >= 1 << (fsb - 1): v -= 1 << fsb
                    val = v
                elif st == 2:
                    val = None  # filled after id
                elif st == 3:
                    i2 = bits(rb, fob, fsb); o = pallet_off[ci] + i2 * 4
                    val = struct.unpack("<I", pallet[o:o+4])[0]
                    if c["type"] == "float": val = struct.unpack("<f", pallet[o:o+4])[0]
                elif st == 4:
                    i2 = bits(rb, fob, fsb); o = pallet_off[ci] + i2 * 4 * v3
                    val = list(struct.unpack(f"<{v3}I", pallet[o:o+4*v3]))
                if c["type"] == "int" and isinstance(val, int) and st in (3,) and not c["unsigned"] and c["bits"] == 32 and val >= 1 << 31: val -= 1 << 32
                row[c["name"]] = val
            rid = ids[ri] if ids else row.get(inline[idx_index]["name"]) if idcol and not idcol["noninline"] else None
            if idcol: row[idcol["name"]] = rid
            for ci, (c, f) in enumerate(zip(inline, fsi)):
                if f[3] == 2: row[c["name"]] = commons[ci].get(rid, f[4])
            if relcol: row[relcol["name"]] = rel.get(ri)
            rows[rid] = row
        gidx += src
        for nid, cid in copies:
            if cid in rows:
                r = dict(rows[cid]); r[idcol["name"]] = nid; rows[nid] = r
    return rows
