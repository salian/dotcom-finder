# dotcom-finder

A fast, scriptable utility to bulk-check `.com` domain availability by generating prefix+suffix combinations and querying the official Verisign RDAP endpoint.

This tool is ideal for founders, marketers, and developers who want to explore brandable domain ideas at scale and export clean results for further analysis.

---

## Features

- 🔎 Checks real `.com` availability using **Verisign RDAP**
- 🔀 Generates all combinations of prefixes × suffixes
- 📁 Supports inline lists or text files for inputs
- 📊 Exports results to CSV
- 🧪 Classifies domains as:
  - Available
  - Registered
  - Invalid
  - Unknown (network / RDAP edge cases)
- ⚡ Lightweight, no external dependencies

---

## How It Works

1. Accepts prefixes and suffixes (via CLI or files)
2. Generates combinations like `prefix + suffix + .com`
3. Queries Verisign’s RDAP service
4. Interprets responses to determine availability
5. Saves results and prints a summary


---

## Example: Using an LLM to Generate Prefix & Suffix Lists

You can use any LLM (ChatGPT, Claude, Gemini, etc.) to quickly generate high-quality prefix and suffix lists for domain discovery.

### Recommended Prompt

Copy–paste the prompt below into your preferred LLM:

```
You are helping me generate brandable domain names.

Task:
Generate two separate lists:

Prefixes

Suffixes

Rules:

Each item must be lowercase

Use only a–z characters

No hyphens, numbers, or special characters

Each word should be 2–6 characters long

Avoid real brand names or trademarks

Avoid offensive or sensitive terms

Optimized for .com domain names

Output must be plain text only

One word per line

No explanations or commentary

Context:
The domains will be formed as:
<prefix><suffix>.com

Theme:
[DESCRIBE YOUR THEME HERE — e.g. fintech, AI tools, creator economy, health, gaming, productivity]

Output format exactly as follows:

PREFIXES:
word1
word2
word3
...

SUFFIXES:
word1
word2
word3
...
```

## Example Theme Inputs

- “AI-powered SaaS tools for developers”
- “Modern fintech products for global users”
- “Short, punchy names for creator tools”
- “Trustworthy healthcare technology brands”
- “Playful but premium consumer internet brands”

---

## Using the Output

1. Copy the `PREFIXES` list into `prefixes.txt`
2. Copy the `SUFFIXES` list into `suffixes.txt`
3. Run.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/dotcom-finder.git
cd dotcom-finder
```
---

Ensure you’re running Python 3.8+:
```
python --version
```

No additional dependencies required.

## Usage
Basic usage (inline lists)
```
python check_domains.py \
  --prefixes news,live \
  --suffixes desk,wire
```
Using files
```
python check_domains.py \
  --prefix-file prefixes.txt \
  --suffix-file suffixes.txt
```

Each file should contain one entry per line.

Export results to CSV
```
python check_domains.py \
  --prefixes quick,smart \
  --suffixes pay,bank \
  --out results.csv
```
## Output

The CSV contains:

Column	Description
domain	Full domain name (example.com)
status	available / registered / invalid / unknown
rdap_source	RDAP endpoint used
raw_response	Parsed RDAP metadata (JSON)

The script also prints a terminal summary:
```
Summary
-------
Total:      120
Available:  37
Registered: 78
Invalid:    3
Unknown:    2
Saved CSV:  results.csv
```
## Why RDAP?

RDAP is the modern, standardized replacement for WHOIS.
Using Verisign’s RDAP endpoint ensures:

Accurate .com registry data

No scraping

Better structured responses

## Use Cases

Startup & SaaS naming

Brand/domain research

Marketing campaign domains

Automated domain ideation pipelines

Bulk validation before registrar checks

## Limitations

Only checks .com domains

Rate-limited by the RDAP service

Availability ≠ registrar price or premium status

## Roadmap (Ideas)

- Multi-TLD support (.io, .ai, .dev)

- Parallel / async requests

- Registrar price lookup

- JSON / Parquet output

- GitHub Actions workflow for batch runs

## License

MIT License — use freely, attribution appreciated.

## Disclaimer

This tool checks registry availability only.
Final availability and pricing should always be confirmed with a domain registrar.
