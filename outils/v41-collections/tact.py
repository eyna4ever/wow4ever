#!/usr/bin/env python3
"""Minimal read-only TACT/CASC client for the official Blizzard CDN (product wowf = WoW Forever).
Downloads only what is needed, caches everything under ../cache. No account, no credentials."""
import os, sys, struct, zlib, hashlib, json, concurrent.futures as cf, urllib.request, time
from pathlib import Path
HERE = Path(__file__).resolve().parent.parent
CACHE = HERE / "cache"; CACHE.mkdir(exist_ok=True)
HOSTS = ["https://us.cdn.blizzard.com/tpr/wow", "https://level3.ssl.blizzard.com/tpr/wow"]

def http(path, rng=None, tries=4):
    last = None
    for t in range(tries):
        for h in HOSTS:
            try:
                req = urllib.request.Request(f"{h}/{path}")
                if rng: req.add_header("Range", f"bytes={rng[0]}-{rng[0]+rng[1]-1}")
                with urllib.request.urlopen(req, timeout=60) as r:
                    return r.read()
            except Exception as e:
                last = e
        time.sleep(1 + t)
    raise RuntimeError(f"fetch failed {path}: {last}")

def kp(h): return f"{h[:2]}/{h[2:4]}/{h}"

def cached(kind, h, suffix=""):
    p = CACHE / kind / f"{h}{suffix}"
    if p.exists(): return p.read_bytes()
    d = http(f"{kind}/{kp(h)}{suffix}")
    p.parent.mkdir(exist_ok=True, parents=True); p.write_bytes(d); return d

def parse_cfg(txt):
    out = {}
    for line in txt.splitlines():
        if " = " in line and not line.startswith("#"):
            k, v = line.split(" = ", 1); out[k] = v.split()
    return out

class EncryptedError(Exception): pass

ZERO_FILL = True
def blte(data):
    assert data[:4] == b"BLTE", data[:4]
    hs = struct.unpack(">I", data[4:8])[0]
    if hs == 0:
        chunks = [(len(data) - 8, None)]; pos = 8
    else:
        n = struct.unpack(">I", data[8:12])[0] & 0xFFFFFF
        chunks = []
        for i in range(n):
            o = 12 + i * 24
            es, ds = struct.unpack(">II", data[o:o+8]); chunks.append((es, ds))
        pos = hs
    out = bytearray()
    for es, ds in chunks:
        c = data[pos:pos+es]; pos += es
        m = c[:1]
        if m == b"N": out += c[1:]
        elif m == b"Z": out += zlib.decompress(c[1:])
        elif m == b"E":
            if ZERO_FILL and ds: out += b"\0" * ds
            else: raise EncryptedError("encrypted chunk")
        else: raise ValueError(f"mode {m}")
    return bytes(out)

class Tact:
    def __init__(self, buildcfg, cdncfg):
        self.tag = buildcfg[:8]
        self.b = parse_cfg(cached("config", buildcfg).decode())
        self.c = parse_cfg(cached("config", cdncfg).decode())
        self.idx = None
    def load_indexes(self):
        p = CACHE / f"ekeyindex-{self.tag}.bin"
        if p.exists():
            self.idx = {}
            raw = p.read_bytes()
            arch = self.c["archives"]
            for i in range(0, len(raw), 26):
                k = raw[i:i+16]; a, sz, off = struct.unpack("<HII", raw[i+16:i+26]); self.idx[k] = (arch[a] if a != 0xFFFF else None, sz, off)
            return
        arch = self.c["archives"]
        def get(h):
            return h, cached("data", h, ".index")
        res = {}
        with cf.ThreadPoolExecutor(24) as ex:
            for h, d in ex.map(get, arch): res[h] = d
        idx = {}
        for ai, h in enumerate(arch):
            for k, sz, off in self.parse_index(res[h]): idx[k] = (ai, sz, off)
        # loose files
        fi = self.c.get("file-index", [None])[0]
        if fi:
            for k, sz, off in self.parse_index(cached("data", fi, ".index")): idx.setdefault(k, (0xFFFF, sz, 0))
        buf = bytearray()
        for k, (a, sz, off) in idx.items(): buf += k + struct.pack("<HII", a, sz, off)
        p.write_bytes(bytes(buf)); return self.load_indexes()
    @staticmethod
    def parse_index(d):
        ncs = d[-13]; ks = d[-14]; szb = d[-15]; offb = d[-16]; bkb = d[-17]
        num = struct.unpack("<I", d[-12:-8])[0]
        bs = bkb * 1024; esz = ks + szb + offb; got = 0; pos = 0
        while got < num and pos < len(d):
            block = d[pos:pos+bs]; pos += bs
            for o in range(0, bs - esz + 1, esz):
                k = block[o:o+ks]
                if k == b"\0" * ks or len(k) < ks: break
                sz = int.from_bytes(block[o+ks:o+ks+szb], "big")
                off = int.from_bytes(block[o+ks+szb:o+esz], "big") if offb else 0
                yield k[:16], sz, off; got += 1
                if got >= num: break
    def by_ekey(self, ekey: bytes):
        p = CACHE / "files" / ekey.hex()
        if p.exists(): return p.read_bytes()
        if self.idx is None: self.load_indexes()
        e = self.idx.get(ekey)
        if e is None or e[0] is None:
            d = http(f"data/{kp(ekey.hex())}")
        else:
            a, sz, off = e
            d = http(f"data/{kp(a)}", rng=(off, sz))
        out = blte(d)
        p.parent.mkdir(exist_ok=True); p.write_bytes(out); return out
    def load_encoding(self):
        p = CACHE / f"encoding-{self.tag}.ckmap"
        if p.exists():
            raw = p.read_bytes(); self.enc = {raw[i:i+16]: raw[i+16:i+32] for i in range(0, len(raw), 32)}; return
        ek = bytes.fromhex(self.b["encoding"][1])
        d = blte(http(f"data/{kp(ek.hex())}"))
        assert d[:2] == b"EN"
        hck, hek = d[3], d[4]
        cps = struct.unpack(">H", d[5:7])[0] * 1024
        eps = struct.unpack(">H", d[7:9])[0] * 1024
        cpc = struct.unpack(">I", d[9:13])[0]; epc = struct.unpack(">I", d[13:17])[0]
        ssz = struct.unpack(">I", d[18:22])[0]
        pos = 22 + ssz + cpc * (hck + 16)
        buf = bytearray(); enc = {}
        for pg in range(cpc):
            page = d[pos:pos+cps]; pos += cps; o = 0
            while o + 6 + hck <= len(page):
                kc = page[o]
                if kc == 0: break
                ck = page[o+6:o+6+hck]; e0 = page[o+6+hck:o+6+hck+hek]
                enc[ck] = e0; buf += ck + e0
                o += 6 + hck + hek * kc
        p.write_bytes(bytes(buf)); self.enc = enc
    def load_root(self):
        p = CACHE / f"root-{self.tag}.json"
        if p.exists(): self.root = {int(k): v for k, v in json.loads(p.read_text()).items()}; return
        ck = bytes.fromhex(self.b["root"][0])
        d = self.by_ekey(self.enc[ck])
        root = {}
        if d[:4] == b"TSFM":
            hsz, ver = struct.unpack("<II", d[4:12])
            if hsz > 1000:  # old style header without size/version
                ver = 0; pos = 12
            else:
                pos = hsz
            total, named = (struct.unpack("<II", d[12:20]) if ver else struct.unpack("<II", d[4:12]))
            allow_nameless = named < total
        else:
            raise ValueError("legacy root not handled")
        while pos < len(d):
            n = struct.unpack("<I", d[pos:pos+4])[0]
            if ver >= 2:
                loc, f1, f2 = struct.unpack("<III", d[pos+4:pos+16]); f3 = d[pos+16]; pos += 17
                cflags = f1 | f2 | (f3 << 17)
            else:
                cflags, loc = struct.unpack("<II", d[pos+4:pos+12]); pos += 12
            fids = struct.unpack(f"<{n}i", d[pos:pos+4*n]); pos += 4 * n
            cks = [d[pos+16*i:pos+16*i+16] for i in range(n)]; pos += 16 * n
            if not (allow_nameless and (cflags & 0x10000000)): pos += 8 * n
            fid = -1
            for i in range(n):
                fid = fid + 1 + fids[i]
                if cflags & 0x8000000: continue  # skip encrypted/no-compress? keep anyway below
                root.setdefault(fid, []).append([loc, cks[i].hex()])
        p.write_text(json.dumps(root)); self.root = root
    def file(self, fdid, locale=0x2):
        ents = self.root.get(fdid) or []
        pick = [c for l, c in ents if l & locale] or [c for l, c in ents]
        if not pick: raise KeyError(fdid)
        return self.by_ekey(self.enc[bytes.fromhex(pick[0])])

def open_70862():
    return Tact("5ada954223f7c409ea172361f5c9e565", "55a5dda25b026279080cad451b6cbf73")

def open_eu():
    return Tact("3627b099867bfde3e37a17cf44f69cdc", "96bea67d7d87c3dacb917be74097eaa6")

if __name__ == "__main__":
    t = open_eu(); t.load_encoding(); print("enc", len(t.enc)); t.load_root(); print("root", len(t.root))
