#!/usr/bin/env python3
# check_domains.py
"""
Given lists of prefixes and suffixes, check availability of prefix+suffix.com
using the Verisign RDAP endpoint for .com.

Usage examples:
  python check_domains.py --prefixes p1,p2 --suffixes s1,s2
  python check_domains.py --prefix-file prefixes.txt --suffix-file suffixes.txt
  python check_domains.py --prefixes news,live --suffixes desk,wire --out results.csv
"""

import argparse
import csv
import itertools
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

RDAP_ENDPOINT = "https://rdap.verisign.com/com/v1/domain/{}"

def load_list_arg(list_arg, file_arg, name):
    """
    Load items from:
      - comma-separated CLI arg (optional)
      - newline-separated file (optional)

    Then:
      - strip + lowercase
      - remove blanks and comment lines (#...) from file
      - de-dupe while preserving order
    """
    raw = []

    if list_arg:
        raw.extend([x.strip() for x in list_arg.split(",")])

    if file_arg:
        with open(file_arg, "r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                raw.append(s)

    # normalize + de-dupe while preserving order
    seen = set()
    items = []
    for s in raw:
        s = (s or "").strip().lower()
        if not s:
            continue
        if s in seen:
            continue
        seen.add(s)
        items.append(s)

    if not items:
        print(f"ERROR: no {name} provided.", file=sys.stderr)
        sys.exit(2)

    return items

def to_domain(prefix, suffix, tld):
    # Basic normalization; IDNs are supported via idna encoding later
    label = f"{prefix}{suffix}".strip().lower()
    # remove spaces and illegal chars except hyphen
    allowed = "abcdefghijklmnopqrstuvwxyz0123456789-"
    label = "".join(ch for ch in label if ch in allowed)
    # Ensure label rules (no leading/trailing hyphen, 1..63 chars)
    if not label or len(label) > 63 or label.startswith("-") or label.endswith("-"):
        return None
    domain = f"{label}.{tld}"
    try:
        # Convert to ASCII/Punycode if needed (idna)
        ascii_domain = domain.encode("idna").decode("ascii")
        return ascii_domain
    except Exception:
        return None

def rdap_check(domain, timeout=8, max_retries=3, backoff=0.75):
    """
    Returns tuple (status, http_status, detail)
    status in {"available","registered","unknown","invalid"}
    """
    url = RDAP_ENDPOINT.format(urllib.parse.quote(domain))
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "domain-checker/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                code = resp.getcode()
                body = resp.read()
        except urllib.error.HTTPError as e:
            code = e.code
            body = e.read() or b""
        except urllib.error.URLError as e:
            if attempt < max_retries - 1:
                time.sleep(backoff * (2 ** attempt))
                continue
            return ("unknown", None, f"network error: {e}")
        except Exception as e:
            return ("unknown", None, f"error: {e}")

        # Interpret codes:
        if code == 200:
            try:
                data = json.loads(body.decode("utf-8", errors="replace"))
                # If RDAP returns an object, domain exists (registered)
                return ("registered", 200, data.get("ldhName") or "registered")
            except Exception:
                return ("registered", 200, "registered")
        elif code == 404:
            return ("available", 404, "not found")
        elif code in (400, 422):
            return ("invalid", code, "invalid domain")
        elif code in (429, 500, 502, 503, 504):
            # Retryable; if retries left, loop; else unknown
            if attempt < max_retries - 1:
                time.sleep(backoff * (2 ** attempt))
                continue
            return ("unknown", code, "server/rate limit")
        else:
            return ("unknown", code, f"http {code}")

    return ("unknown", None, "exhausted retries")

def main():
    parser = argparse.ArgumentParser(description="Check availability of prefix+suffix .com domains via RDAP.")
    parser.add_argument("--prefixes", help="Comma-separated prefixes")
    parser.add_argument("--suffixes", help="Comma-separated suffixes")
    parser.add_argument("--prefix-file", help="File with one prefix per line")
    parser.add_argument("--suffix-file", help="File with one suffix per line")
    parser.add_argument("--tld", default="com", help="TLD to check (default: com)")
    parser.add_argument("--out", default="domain_results.csv", help="CSV output filename")
    parser.add_argument("--sleep", type=float, default=0.2, help="Sleep (seconds) between requests to be polite")
    args = parser.parse_args()

    prefixes = load_list_arg(args.prefixes, args.prefix_file, "prefixes")
    suffixes = load_list_arg(args.suffixes, args.suffix_file, "suffixes")

    rows = []
    total = 0
    available = 0
    registered = 0
    invalid = 0
    unknown = 0

    print(f"Checking {len(prefixes)*len(suffixes)} {args.tld} domains via RDAP...\n")
    for pref, suff in itertools.product(prefixes, suffixes):
        domain = to_domain(pref, suff, args.tld)
        if not domain:
            status, http_code, detail = ("invalid", None, "invalid label")
        else:
            status, http_code, detail = rdap_check(domain)
            time.sleep(args.sleep)

        total += 1
        if status == "available":
            available += 1
        elif status == "registered":
            registered += 1
        elif status == "invalid":
            invalid += 1
        else:
            unknown += 1

        print(f"{domain or (pref+suff+'.'+args.tld):35}  -> {status.upper()}  ({detail})")
        rows.append({
            "domain": domain or f"{pref}{suff}.{args.tld}",
            "status": status,
            "http_status": http_code if http_code is not None else "",
            "detail": detail,
            "prefix": pref,
            "suffix": suff,
        })

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["domain", "status", "http_status", "detail", "prefix", "suffix"])
        writer.writeheader()
        writer.writerows(rows)

    print("\nSummary")
    print("-------")
    print(f"Total:      {total}")
    print(f"Available:  {available}")
    print(f"Registered: {registered}")
    print(f"Invalid:    {invalid}")
    print(f"Unknown:    {unknown}")
    print(f"\nSaved CSV:  {args.out}")

if __name__ == "__main__":
    main()
