# Personal Finance Statement Analyser

## Background

Singapore banks (DBS, OCBC, UOB) do not provide transaction-level or spending data through
SGFinDex. SGFinDex only returns month-end balance snapshots — useful for a net worth overview
but not for spend tracking or trend analysis.

Third-party apps like Seedly and Planner Bee claim to solve this, but in practice they rely on
screen scraping via a third-party aggregator (Salt Edge) rather than true bank API integrations.
This approach is fragile — DBS sync has been broken on Seedly indefinitely, and UOB/OCBC syncs
fail regularly. Users are also required to hand over their banking credentials to a third party.

This project takes a fully offline, privacy-first approach. No data leaves your machine. Bank
statement PDFs are parsed locally, merged into a unified ledger, and output as a formatted Excel
workbook with month-over-month expense and credit trend charts.

---

## Why Not an API Approach

- **SGFinDex** only returns month-end balance summaries — no individual transactions or spend data.
- **DBS, OCBC, UOB developer APIs** exist but are gated behind formal partnership/approval
  processes and are primarily corporate-facing. Transaction-level data for consumer apps requires
  going through a screening or onboarding process with each bank.
- **Screen scraping** (Seedly/Planner Bee approach) is fragile, legally grey, and requires
  sharing banking credentials with third parties.
- **PDF parsing** is the most practical path for an individual developer — fully offline,
  no credentials shared, no partnership required.

---

## Why Python Over Go

Go was considered but ruled out for this weekend project for one key reason: `monopoly-core`,
the open source library that handles DBS, OCBC, and UOB PDF parsing, is Python-only. Reimplementing
the PDF parsing layer in Go would consume most of the weekend. The Go PDF ecosystem is also thinner
than Python's for this use case.

Python is the right choice here. The full stack — parsing, aggregation, Excel generation — is
well-served by mature, well-documented libraries.

---

## User Stories

**As a user, I want to:**

1. Drop one or more Singapore bank statement PDFs (DBS, OCBC, UOB) into a folder and have them
   automatically parsed into structured transaction data, so that I don't have to manually
   copy-paste from PDFs.

2. Have transactions from multiple banks merged into a single unified ledger, so that I can see
   my complete financial picture across all my accounts in one place.

3. Have transactions automatically categorised by keyword (e.g. GRAB → Transport, FAIRPRICE →
   Groceries), so that I can analyse my spending by category without manual tagging.

4. Be able to correct miscategorised transactions in an editable Category Map tab, and have those
   corrections applied the next time I run the script, so that categorisation improves over time.

5. See a month-over-month expense trend chart showing total spend per category per month, so that
   I can identify where my money is going and how it changes over time.

6. See a month-over-month credit trend chart showing total inflows per month, so that I can track
   my income and any irregular credits.

7. See a net cash flow view per month (credits minus debits), so that I can quickly assess whether
   I am saving or overspending each month.

8. Have each month's raw transactions available in its own dedicated tab, so that I can drill
   down into a specific month's detail when needed.

9. Have the output automatically adjust to however many months and banks are present in the PDFs
   I provide, so that I don't need to reconfigure anything when adding new statements.

10. Have the entire workbook regenerated fresh each run, with my Category Map edits carried
    forward, so that the output is always consistent and up to date.

---

## Acceptance Criteria

- Works fully offline — no data uploaded anywhere
- Handles password-protected PDFs (Singapore bank e-statements typically use NRIC + date of birth)
- Supports multiple PDFs from multiple banks in a single run
- Output is a single `.xlsx` file openable in Excel or LibreOffice
- Re-running the script with additional PDFs produces an updated workbook without losing
  category map edits

---

## Workbook Structure

The generated Excel file has the following tab layout:

| Tab | Type | Description |
|---|---|---|
| All Transactions | Fixed | Full merged ledger across all banks and months |
| Monthly Summary | Fixed | Pivot table — rows = months, cols = categories |
| Expense Trend | Fixed | Bar chart of monthly spend by category |
| Credit Trend | Fixed | Line chart of monthly inflows |
| Net Cash Flow | Fixed | Monthly credits minus debits |
| YYYY-MM (repeating) | Dynamic | One tab per month of raw transactions |
| Category Map | Fixed | Editable keyword → category mapping table |

The dynamic month tabs are generated automatically based on whatever months exist in the
uploaded PDFs — no hardcoding required.

---

## Libraries & Dependencies

### Core

| Library | Purpose |
|---|---|
| `monopoly-core` | Parsing DBS, OCBC, UOB PDF statements into CSV |
| `pandas` | Merging CSVs, aggregation, pivot tables, groupby month/category |
| `openpyxl` | Generating and reading back the `.xlsx` workbook and charts |
| `python-dateutil` | Normalising date formats across different bank statements |
| `pathlib` | Clean file and folder path handling |
| `re` | Keyword matching for transaction categorisation |

### Optional

| Library | Purpose |
|---|---|
| `click` or `argparse` | CLI interface for specifying input folder and output file |
| `colorama` | Coloured terminal output for progress and errors |
| `pytest` | Testing categorisation logic and parsing pipeline |

### Installing monopoly

```bash
# Requires system dependencies first
brew install gcc@11 pkg-config poppler ocrmypdf   # macOS
# or
apt-get install build-essential libpoppler-cpp-dev pkg-config ocrmypdf  # Linux

# Then install
pipx install monopoly-core

# With OCR support for scanned PDFs
pipx install 'monopoly-core[ocr]'
```

---

## Key Design Decisions

**openpyxl over xlsxwriter** — openpyxl supports both reading and writing `.xlsx` files,
enabling the Category Map round-trip (read user edits → regenerate workbook with corrections
applied). xlsxwriter is write-only and cannot support this workflow.

**Regenerate on every run** — the workbook is not the source of truth. The parsed CSVs are.
Each run regenerates the full workbook fresh, with only the Category Map edits read back and
carried forward. This avoids chart corruption and keeps the output consistent.

**Category Map as editable tab** — rather than hardcoding categories in the script, the
keyword-to-category mapping lives in the workbook itself. The user edits it in Excel, and the
next run picks up their changes. This makes categorisation iterative without requiring code edits.

---

## Suggested Weekend Split

### Saturday — Data Pipeline
- Install and validate `monopoly-core` against a real statement
- Parse multiple PDFs and merge into a single pandas DataFrame
- Normalise dates into year-month periods
- Build keyword-to-category mapping and apply categorisation
- Compute monthly aggregations: total debits, credits, net flow, spend by category

### Sunday — Output & Polish
- Generate Excel workbook with `openpyxl`
- Write fixed summary tabs and dynamic month tabs
- Add bar chart (expense trend) and line chart (credit trend)
- Implement Category Map read-back before regeneration
- End-to-end test with real statements from multiple banks
- Add CLI argument for input folder and output file path
