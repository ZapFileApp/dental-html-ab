# ab_process — Alberta Combined & Cleaned Dental URL List

## Purpose
Merge all per-city scraped CSVs from `ab/Canada_cities/` (335 files) into a single
deduped, cleaned list of real Alberta dental-practice website URLs, with government
sites, directories, and unrelated businesses (mis-matched Google Maps results)
stripped out.

## Source
Copied from `../ab/Canada_cities/` (the completed Alberta scrape, 335 city files,
1,933 unique URLs at time of copy — see `../repos.md` for the scrape run history).
The original folder was deleted from `ab_process/` after merging since the source
in `../ab/Canada_cities/` remains the backup.

## Pipeline (run in this order)
1. **`combine_csv.py`** — merged all 335 `Canada_cities/*.csv` files into one
   `ab_combined.csv` (same header: `url,name,address,city,state,phone`).
   Result: 7,451 raw rows (before dedup).
2. **`dedupe_csv.py`** — removed duplicate rows by exact `url` match (first
   occurrence kept). Result: 7,451 → **1,933 rows**. High duplication rate is
   expected: Alberta has hundreds of small towns close together, and Google Maps
   returns nearby-region businesses for small-town searches, so the same practice
   gets rediscovered under many different city searches.
3. **`filter_csv.py`** (pass 1) — removed rows whose domain matched an explicit
   blocklist: government sites, directories/professional associations, and social
   media. Result: 1,933 → 1,867 (**66 removed**).
4. **`strip_params.py`** — stripped query strings (e.g. `?utm_source=...`) from
   every URL, then re-deduped (stripping params collapses some previously-distinct
   rows into the same URL). Result: 1,867 → **1,861 rows** (556 URLs had params
   stripped, 6 new duplicates removed).
5. **`filter_csv.py`** (pass 2) — added finance/insurance domains to the blocklist
   (`sunlife.ca`, `westernfinancialgroup.ca`, etc.) per explicit request. Result:
   1,861 → **1,852 rows** (9 removed).
6. **`filter_csv.py`** (pass 3, deep cleanup) — after spotting an unrelated
   meditation-center URL (`karuna.dhamma.org`) in the data, did a full domain-level
   audit of every URL that didn't contain a dental-related keyword, cross-checked
   against the (mostly unreliable — usually just "Results") `name` field. Expanded
   the blocklist to cover 8 more categories (see below). Result: 1,852 → 1,547
   (**305 removed**), then a second confirmation sub-pass found ~26 more
   confirmed-junk domains via name-field matches (dental associations, more
   pharmacies/health orgs, municipal town sites, a funeral home, restaurants,
   etc.). Result: 1,547 → **1,516** (**31 removed**).
7. **Manual spot-check** — one row (`adcosv.net`, address in Santa Clara, CA) was
   an out-of-province/country mismatch, removed directly. Result: 1,516 →
   **1,515 rows (final)**.

## Final Result
**1,515 rows** in `ab_combined.csv` — down from 7,451 raw scraped rows
(9,336 raw → deduped → 1,933 unique URLs → 1,515 after removing non-dental
junk, a total of **418 junk rows removed** across all filter passes).

## Removed Categories (full list of blocked domains lives in `filter_csv.py`'s `BLOCKED_DOMAINS`)
| Category | Examples |
|---|---|
| Government | albertahealthservices.ca, canada.ca, servicecanada.gc.ca, rcmp-grc.gc.ca, ualberta.ca, atb.com, and 10 municipal town sites (falher.ca, westlock.ca, stavely.ca, etc.) |
| Directories / professional associations | albertadentalassociation.ca, dentaltown.ca, abrda.ca (College of Alberta Dental Assistants), cdsab.ca (College of Dental Surgeons of Alberta), camrosedirectory.ca |
| Social media | facebook.com, m.facebook.com, instagram.com, fb.com |
| Finance / insurance | sunlife.ca, westernfinancialgroup.ca, dyckinsurance.ca, awarefinancial.ca, stoneins.ca, acera.ca, moneygram.com, brokerlink.ca, branches.fairstone.ca, kowalrealty.ca, sandstonelaw.ca |
| Veterinary / pet | 50+ domains — ardrossanvet.ca, bowrivervet.com, petsmart.ca, store.petvalu.ca, sturgeoncountykennels.ca, cochranehumane.ca, etc. |
| Pharmacy | pharmasave.com, guardian-ida-remedysrx.ca, shoppersdrugmart.ca, pharmachoice.com, rexall.ca, medigroup.ca (Dave Hill Pharmacy), and 8 more local pharmacies |
| Physio / chiropractic | 13 domains — bowriverchiropractic.ca, medicinehatphysio.ca, etc. |
| Eye care / optometry | acuityeyecare.ca, specsavers.ca, sherwoodparkoptometry.ca, etc. |
| General medical / health / PCN | arrowwoodmedical.ca, reddeerpcn.com, radiushealth.ca, covenanthealth.ca, doctorsplus.ca, and 20+ more clinics/health orgs |
| Beauty / spa / wellness | altitudespa.ca, modernaesthetics.ca, mmccosmeticlaser.com, horizoncosmetic.ca, etc. |
| Hotels / restaurants / retail / gas | homehardware.ca, canadiantire.ca, petro-canada.ca, sobeys.com, wyndhamhotels.com, and 30+ more |
| Schools / libraries / municipal / misc institutions | nait.ca, several `*library.ab.ca` sites, co-op grocery chains, gopherholemuseum.org, connelly-mckinley.com (funeral home), khs.btps.ca (high school) |
| Clearly unrelated / mis-scraped | karuna.dhamma.org (Vipassana meditation centre — the original find that triggered this whole cleanup pass), sabir.organicbaghbani.com (unrelated foreign gardening site), tripca.cyou (spam-looking domain), ldsanctuary.com (wildlife sanctuary), fmspca.ca (SPCA), adcosv.net (out-of-province mismatch) |

## Kept — false negatives recovered during the audit
These looked non-dental by keyword but were confirmed as real dental practices
(mostly via abbreviation patterns — `dh` = dental hygiene, `pd` = pediatric
dental, `OS`/`OMS` = oral (maxillofacial) surgery — or via the `name` field):
`brushforkids.com`, `completedh.com`, `delburnedh.ca`, `harkerchan.com`,
`hucalandedwards.com`, `kidssayahh.com`, `kingswayos.com`, `medhatomspeds.ca`,
`mmdh.ca`, `mountainvalleys.org`, `mypdltd.com`, `nhdblackfalds.com`,
`nu-gendh.ca`, `ofdc.ca`, `onthewaymobiledh.com`, `pcmdh.ca`, `pearlsofwisdom.ca`,
`process.can1.intiveo.com` (Intiveo = dental patient-communication software),
`rcdedmonton.ca`, `sdh20103.wixsite.com`, `smylesdh.ca`, `totherootdh.ca`,
`ceratechlab.com` (dental ceramics lab).

## Left in file — genuinely uncertain (24 domains)
No confident domain/name signal either way (all are legitimate Alberta business/
office-suite addresses, just no dental indicator in the name or URL). Left as-is
rather than guessing on real business data — flag for manual review if desired:
`abcpd.ca`, `arcnetwork.ca`, `book.squareup.com`, `cvcyeg.com`,
`diamondelite.services`, `feathandelemi.com`, `ffmc.ca`,
`freshperspectivemobile.com`, `gmobileunit.com`, `hmmyeg.com`, `kapown.ca`,
`lcdcare.ca`, `llbcl.ca`, `llmc.ca`, `lwdd.ca`, `magathan.com`, `panaram.ca`,
`pppd.ca`, `rogerejohnsonenterprises.ca`, `sardp.ca`, `thriveservicescentre.ca`,
`timetocare.ca`, `wbsah.com`, `x-ray.ca`.

## Scripts (run in order to reproduce from scratch)
1. `combine_csv.py` — merges `Canada_cities/*.csv` → `ab_combined.csv`
2. `dedupe_csv.py` — dedupes by exact URL
3. `filter_csv.py` — removes all `BLOCKED_DOMAINS` (edit this list to adjust scope)
4. `strip_params.py` — strips query params, re-dedupes
