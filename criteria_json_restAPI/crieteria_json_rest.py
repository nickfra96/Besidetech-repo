
from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

try:
    import requests
except ImportError as exc:  # pragma: no cover
    sys.exit("[FATAL] Modulo 'requests' mancante – pip install requests")

# ----------------------------------------------------

def extract_soggetto(df: pd.DataFrame) -> str:
    for idx, cell in enumerate(df.iloc[:, 0].astype(str)):
        if "denominazione" in cell.lower():
            for j in range(idx + 1, len(df)):
                val = str(df.iat[j, 0]).strip()
                if val and val.lower() != "nan":
                    return val
            break
    return "NON SPECIFICATO"


def extract_testo(df: pd.DataFrame) -> Dict[str, str]:
    testi: Dict[str, str] = {}
    current: str | None = None
    rx = re.compile(r"(?i)^criterio\s+([A-Z]\d(?:\.\d)?)")
    for raw in df.iloc[:, 0].astype(str):
        line = raw.strip()
        m = rx.match(line)
        if m:
            current = m.group(1).upper()
            testi[current] = ""
        elif current:
            testi[current] = (testi[current] + " " + line).strip()
    return testi


def extract_descr(df: pd.DataFrame) -> Dict[str, str]:
    descr: Dict[str, str] = {}
    for _, row in df.iterrows():
        k_raw = str(row.iloc[0]).strip()
        if re.fullmatch(r"[A-Z]\d{1,2}", k_raw):
            descr[k_raw.upper()] = str(row.iloc[1]).strip()
    return descr


def rand_id() -> str:
    return f"{random.randint(0, 999_999_999):09d}"


def update_json(template: Dict[str, Any], testi: Dict[str, str], descr: Dict[str, str], soggetto: str) -> Dict[str, Any]:
    out = json.loads(json.dumps(template))  
    out["soggetto"] = soggetto
    out["idDomanda"] = rand_id()
    for code, node in out["userCriteria"].items():
        node["testo"] = testi.get(code.upper(), "NON FORNITO")
        group = code.split(".")[0].upper()
        if group in descr:
            node["descrizione"] = descr[group]
    return out

# -----------------------------------------------------------

def post_json(data: Dict[str, Any], endpoint: str, token: str, verbose: bool = False) -> None:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token.strip()}" if not token.lower().startswith("bearer ") else token,
    }
    try:
        resp = requests.post(endpoint, json=data, headers=headers, timeout=30)
    except requests.RequestException as exc:
        print(f"[ERRORE] POST fallita: {exc}")
        return

    snippet = (resp.text or "")[:300]
    if resp.ok:
        print(f"  → POST OK {resp.status_code}: {snippet}")
    else:
        print(f"  → POST ERRORE {resp.status_code}: {snippet}")
        if verbose:
            print(f"    URL: {endpoint}\n    Headers: {headers}\n    Payload preview: {json.dumps(data)[:200]}…")

# ------------------------------------------------------------
# Main


def load_template(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def find_sheet(xl: pd.ExcelFile, keys: List[str], fallback_index: int) -> str:
    return next((n for n in xl.sheet_names if all(k in n.lower() for k in keys)), xl.sheet_names[fallback_index])


def process_excel(xlsx: Path, template: Dict[str, Any], verbose: bool) -> Dict[str, Any]:
    if verbose:
        print(f"    Leggo {xlsx.name}…")
    xl = pd.ExcelFile(xlsx, engine="openpyxl")

    sh_anag = find_sheet(xl, ["anagraf"], 0)
    sh_prop = find_sheet(xl, ["proposta", "criter"], 1)
    sh_crit = find_sheet(xl, ["criter", "valut"], -1)

    soggetto = extract_soggetto(pd.read_excel(xlsx, sheet_name=sh_anag, header=None, engine="openpyxl"))
    testi = extract_testo(pd.read_excel(xlsx, sheet_name=sh_prop, header=None, engine="openpyxl"))
    descr = extract_descr(pd.read_excel(xlsx, sheet_name=sh_crit, header=None, engine="openpyxl"))

    return update_json(template, testi, descr, soggetto)


def main():
    p = argparse.ArgumentParser(description="Genera JSON da Excel e facoltativamente li invia via REST")
    p.add_argument("--excel-dir", required=True)
    p.add_argument("--template", required=True)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--endpoint")
    p.add_argument("--token")
    p.add_argument("--verbose", action="store_true", help="Log dettagliato")
    args = p.parse_args()

    token = args.token or os.getenv("API_TOKEN")
    if args.endpoint and not token:
        sys.exit("[FATAL] --endpoint fornito ma manca il token (CLI --token o env API_TOKEN)")

    excel_dir = Path(args.excel_dir).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.verbose:
        print(f"[DEBUG] Excel dir: {excel_dir}\n[DEBUG] Output dir: {out_dir}\n[DEBUG] Template: {args.template}")
    template_json = load_template(Path(args.template))

    excel_files = list(excel_dir.glob("*.xls*"))
    if not excel_files:
        print(f"[WARN] Nessun file .xls* trovato in {excel_dir}")
        sys.exit(0)

    for file in excel_files:
        print(f"[INFO] {file.name}")
        enriched = process_excel(file, template_json, args.verbose)

        out_path = out_dir / f"{file.stem}.json"
        with open(out_path, "w", encoding="utf-8") as fout:
            json.dump(enriched, fout, ensure_ascii=False, indent=4)
        print(f"  ↳ salvato {out_path.name} (idDomanda {enriched['idDomanda']})")

        if args.endpoint:
            if args.verbose:
                print(f"  → POST a {args.endpoint}…")
            post_json(enriched, args.endpoint, token, args.verbose)

    print("\n[FINE] Elaborazione completata.")


if __name__ == "__main__":
    main()
