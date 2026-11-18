# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->

FitFindr helps a shopper decide whether a thrifted find is worth buying. The user types a request in plain language, such as "vintage graphic tee under $30, size M", along with the clothes they already own. The agent searches a set of secondhand listings, picks the best match, and suggests one or two outfits that combine it with pieces from their wardrobe, or general styling advice if the wardrobe is empty. It ends with a short social-media caption for the find. If nothing matches, it stops early and tells the user which filter (keywords, size, or budget) to loosen instead of making up an outfit.


---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:**
     Filters the listings in `data/listings.json` by size and price, then ranks the remaining items by how well their title, description, and style tags match the user's keywords.
- **Inputs:**
     - `description` (str): keywords for what the user wants, e.g. `"vintage graphic tee"`.
     - `size` (str | None): the size the user wants, e.g. `"M"`.
     - `max_price` (float | None): price ceiling in dollars, inclusive, e.g. `30.00`.
- **Returns:**
     A `list[dict]` of listing dicts. Each dict has the keys `id` (str), `title` (str), `description` (str), `category` (str), `style_tags` (list[str]), `size` (str), `condition` (str), `price` (float), `colors` (list[str]), `brand` (str), and `platform` (str).
- **When it has nothing:**
     An empty list `[]`. it never an exception.

### `suggest_outfit`

- **What it does:**
     Combine one listing with pieces the user already owns and suggest one or two outfits.
- **Inputs:**
     - `new_item` (dict): one listing dict, i.e. a single element of `search_listings`' result.
     - `wardrobe` (dict): a dict with an `items` key holding a list of dicts, each with `id` (str), `name` (str), `category` (str, one of tops / bottoms / outerwear / shoes / accessories), `colors` (list[str]), `style_tags` (list[str]), and `notes` (str | None).
- **Returns:**
     A non-empty `str` of one or two outfit suggestions. When the wardrobe has items, the text names specific pieces from it.
- **When it has nothing:**
     If `wardrobe["items"]` is empty, it returns general styling advice for `new_item` as a non-empty string. It does not raise and does not return `""`.

### `create_fit_card`

- **What it does:**
     Writes a short social-media-style caption for the thrifted find, based on the outfit suggestion.
- **Inputs:**
     - `outfit` (str): the string returned by `suggest_outfit`.
     - `new_item` (dict): the same listing dict that was passed to `suggest_outfit`.
- **Returns:**
     A `str` of two to four sentences that reads like a real post, mentions the item, its price, and its platform once each, and gives a specific vibe.
- **When it has nothing:**
     If `outfit` is empty or whitespace, it returns a descriptive message string (e.g. `"No outfit suggestion to write a caption from."`). It does not raise.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, put a message in `session["error"]` that names the filters that were applied and what to loosen (keywords, size, budget), and stop: `suggest_outfit` and `create_fit_card` are never called and `session["fit_card"]` stays `None`. Otherwise take the first result and go to `suggest_outfit`. A second, defensive check follows it: if `suggest_outfit` returns a blank string, set `session["error"]` and stop before `create_fit_card`. (An empty wardrobe is not a branch in the loop; `suggest_outfit` handles it by returning general styling advice.)

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex (`agent.py::_parse_query`), not the model, so it is free, deterministic and testable. `size` is the text after "size" ("size M", "size US 9", "size W28", "size S/M"); `max_price` is a number after under/below/max/up to/less than, or any `$N`; `description` is what remains after removing those and filler words. Known gap: phrasings like "30 dollars" or "size is M" are not recognised.

**What moves through the session:** Each result is written to the session and read back from it for the next call, in this order: `query` → `parsed` → `search_results` → `selected_item` (first result) → `outfit_suggestion` → `fit_card`. `error` is set only when the run stops early, and `wardrobe` is passed in at the start.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask '...'

```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings as s; print([(x['title'],x['size'],x['price']) for x in s('graphic tee', size='M', max_price=30)]); print(s('xyzzy'))"

[('Y2K Baby Tee — Butterfly Print', 'S/M', 18.0), ('Mesh Long-Sleeve Top — Black', 'S/M', 15.0)]
[]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import *; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"

**Outfit 1: Casual Streetwear**
Pair the vintage Levi's 501 jeans with the **White ribbed tank top** tucked in for a fitted silhouette. Layer the **Oversized grey crewneck sweatshirt** over your shoulders... Step into the **Chunky white sneakers** and accessorize with the **Black crossbody bag**...
(empty wardrobe, get_empty_wardrobe(): returns general advice — "These vintage Levi's 501s are the ultimate wardrobe building block. Look 1: Casual Streetwear...")
```

```
$ python -c "from tools import create_fit_card as c; from utils.data_loader import load_listings as l; [print(c('jeans and white sneakers', l()[0])) for _ in range(3)]; print(c('  ', l()[0]))"

Found the holy grail of vintage Levi's 501 jeans while scrolling on depop today... For just $38.00, these give off the ultimate effortless 90s off-duty model vibe...
Found the holy grail of denim today—these vintage Levi's 501 jeans... Grab them on my depop for just $38.00 before I change my mind...
Found the holy grail of denim today: these broken-in Vintage Levi's 501 Jeans... Can't believe my luck finding them on depop for just $38.00...
No outfit suggestion to write a caption from.
```

Three runs differ (TEMPERATURE 0.9, cache bypassed in this tool). Size match is whole-token: "M" matches "M", "S/M", "M/L", never "XL" or "US 9".

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* I described my loop as a flow (empty search → message and stop; otherwise suggest an outfit, then a fit card, with a message if there is no outfit) and asked Claude to build `run_agent()` in `agent.py` from it.
- *What came back:* A working loop, but I only caught one bug by running it: the query parser read "size W28" as size `"W"`, because the size regex stopped at the first non-letter, so a size like that could never match a listing. Claude also pointed out that the "no outfit" branch can't trigger, because `suggest_outfit` already returns a generic sentence when the model returns blank text.
- *What I changed:* I had the size regex accept letters followed by digits ("W28") and slashes ("S/M"), then re-ran the parser on "size W28", "size S/M", "size US 9" and "size M". I kept the blank-outfit check in the loop as a guard rather than deleting it.

**Moment 2**

- *What I asked for:* I wanted a message to be generated when the search comes back empty. Claude implemented it as a fixed template, not a model call, and I then asked it to read the message as a user who knows nothing about the app and say what they would try next.
- *What came back:* The message names the keywords, size and budget that were applied, so a user knows what to change, but the three suggestions are chained as "Try to … or … or …" and don't say which change is most likely to help. Running a second query ("black boots under $70") also showed that `search_listings` can put unrelated items first (biker shorts ranked above boots), because "black" matches almost every listing.
- *What I changed:* I kept the template, since a fixed message is deterministic and can be tested, and my README states that choice. I have not yet changed the wording of the message or the ranking in `search_listings`; both are open items for unit 4.

**Moment 3 (unit 4)**

- *What I asked for:* After running `run_eval.py --label before`, I asked Claude to score my five criteria from the results file and, for criterion 5 and 4, show me a worked pass/fail example. I then asked it to argue the opposite verdict.
- *What came back:* All five MET. It parsed the results file with a script, for criterion 5 applying the exact-match rule plus a hand-written list of paraphrases for the wardrobe names. Its strongest counter-argument was that criterion 5 passed only because of the 25% allowance (10 of 25 outputs sat exactly at the limit), and that criterion 4 compares different items, which makes distinct openings nearly guaranteed.
- *What I changed:* I picked the criterion 5 weakness as my one improvement and had the `suggest_outfit` prompt require exact titles and names with no tag lists. Unfound items per output fell from 1.32 to 0.08. I kept the criteria as written and did not loosen any.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

Run: `python run_eval.py --label before` (2026-10-14 20:58, caching off, temperature 0.9). Raw output: `results/run_2026-10-14_2058_before.md`.

Criteria 3, 4 and 5 are each "5 different queries / items", so Try N of those rows is the Nth of the five queries in `scenarios.py` (`_FIVE_ITEM_QUERIES`) — a try passes only if its query passes.

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. The item search found is the item the next tool received | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Different items get different fit card openings | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. suggest_outfit only names items that exist | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Real output from one try**, produced by `agent.py::run_agent` (messages by `agent.py::_no_results_message`, text by `tools.py::suggest_outfit` / `create_fit_card`):

Criterion 1 — `vintage graphic tee under $30`, try 1. Selected `Vintage Band Tee — Faded Grey ($19.0, depop)`; fit card:

```
Found this faded grey vintage band tee on depop for just $19 and I'm literally obsessed. Perfect for channeling the ultimate 90s grunge vibe with baggy denim and combat boots, or keeping it chill with wide-leg trousers. Grab it before I change my mind and keep it for myself!
```

Criterion 2 — `designer ballgown size XXS under $5`, try 1. Trace ended at step 2 (`search_listings (via MCP)` returned `[]`, "branch: empty, stopping before suggest_outfit"); `session["error"]`:

```
Nothing matched "designer ballgown", size XXS, under $5. Try to use fewer or different keywords (e.g. just the item type, like "jacket"), or drop the size or try a neighbouring one, or raise the $5 budget.
```

Criterion 3 — try 1 (`vintage levi's 501 jeans`): trace step 3 `select_item` returned `Vintage Levi's 501 Jeans — Medium Wash ($38.0, depop)`, the first of the search results.

Criterion 4 — try 1, the five fit-card opening sentences (lowercased), all different:

```
found these dream medium wash vintage levi's 501s and i'm obsessed.
not over me crying over this y2k butterfly baby tee 😭 it's giving total early 2000s streetwear energy, especially paired with baggy denim and a zip hoodie.
still kicking myself for finding this light wash cropped denim jacket on poshmark for just $42.
found my ultimate 90s streetwear holy grail on depop for $55 and i'm literally never taking these black patent platform mary janes off.
still screaming about finding this gorgeous little tan leather mini shoulder bag on poshmark for just $38!
```

Criterion 5 — try 1, `y2k butterfly baby tee`, `tools.py::suggest_outfit`:

```
**Outfit 1 (Y2K Streetwear):**
Pair the baby tee with the **Baggy straight-leg jeans, dark wash**. Layer the **Black cropped zip hoodie** over top (left unzipped to show the butterfly graphic). Finish the look with the **Chunky white sneakers** and the **Black crossbody bag**. 

**Outfit 2 (Casual Contrast):**
Combine the baby tee with the **Wide-leg khaki trousers**, cinched at the waist with the **Brown leather belt**. Throw the **Vintage black denim jacket** over your shoulders and wear the **Black combat boots** to ground the soft pink and purple tones with a touch of edge.
```

---

## Verdicts and Diagnoses

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Matching query completes all three tools | 4 of 5 | MET (5/5) | All 5 tries returned a fit card; `stopped early: no` in every one. |
| 2 | Impossible query stops before tool 2 | 5 of 5 | MET (5/5) | All 5 tries ended at the search step with the same message naming what to change; no `suggest_outfit` step in any trace. |
| 3 | Item passed on = item search returned | 5 of 5 | MET (5/5) | `agent.py::run_agent` sets `selected_item = search_results[0]` and nothing edits it before `suggest_outfit`, so it is the same dict. Traces confirm the selected title is the top search hit for all 5 queries. |
| 4 | Different openings across 5 categories | 5 of 5 | MET (5/5) | Split each card at the first `.`/`!`/`?` followed by a space, lowercased: 5 distinct openings in each of the 5 tries. |
| 5 | suggest_outfit only names real items | 5 of 5 | MET (5/5) | Applied the rule literally (exact match on `new_item["title"]` or wardrobe `name`, allowance = max(1, floor(25% of items named))). Every output passed, but only because of the allowance: the unfound items were always paraphrases, never inventions. |

**Diagnoses**

No criterion was missed in this run, so there is no miss to diagnose. These are the weak spots I can see in the data, none of which crossed a target:

- **Criterion 5 passes on the allowance, not on exact matching.** The model never names `new_item["title"]` verbatim ("the baby tee", "the mini shoulder bag"), and drops ", dark wash" from the jeans. That is 1–2 unfound items per output, and 2 is the limit for outputs naming 8–9 items. 10 of 25 outputs sat exactly at the limit. Nothing invented was named in any of the 25 outputs. In "cropped denim jacket" try 4 the model also leaked tag lists into the text ("(dark blue, indigo)", "(white, sneakers, chunky, streetwear)"), a prompt/output problem in `tools.py::suggest_outfit` that this criterion doesn't catch.
- **Criterion 4 passes because the items differ, not because the model varies.** Across categories the openings are distinct, but for one item across tries they repeat: "still not over finding these (black) patent platform mary janes on depop" opens tries 1 and 4 of the criterion-3 runs and tries 4 and 5 of the criterion-4 runs, and "still … finding" is a template for many openings. The criterion as written can't see this.
- **Criterion 1 never exercised its excuse.** `suggest_outfit` never returned empty in 5 tries, so the 4-of-5 allowance was not used.

---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path** — `python run_eval.py --label after`, "matching query completes", try 1 (`vintage graphic tee under $30`). Step 2 is the MCP call.

```
[1] parse_query
      in:  vintage graphic tee under $30
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Vintage Band Tee — Faded Grey, Graphic Tee — 2003 Tour Bootleg Style, Y2K Baby Tee — Butterfly Print … +7 more
[3] select_item
      in:  first of search_results
      out: Vintage Band Tee — Faded Grey ($19.0, depop)
[4] suggest_outfit
      in:  Vintage Band Tee — Faded Grey + wardrobe of 10 items
      out: **Outfit 1:** Pair the **Vintage Band Tee — Faded Grey** with the **Baggy straight-leg jeans, dark wash**, **B…
[5] create_fit_card
      in:  outfit + Vintage Band Tee — Faded Grey
      out: Found the holy grail faded grey vintage band tee on depop for just $19.00 and I’m literally never taking it of…
```

**Empty search** — "impossible query stops early", try 1 (`designer ballgown size XXS under $5`). Two steps instead of five; it stops at the branch.

```
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
      →    branch: empty, stopping before suggest_outfit
```

**On the MCP move:** `search_listings` is registered as a tool in `mcp_server.py`. In `agent.py::run_agent` I replaced the direct call `search_listings(description, size=..., max_price=...)` with `mcp_client.call_tool("search_listings", {"description", "size", "max_price"})`; `suggest_outfit` and `create_fit_card` are still called directly. The agent works the same through MCP: every matching-query try in both run logs returned results, the traces show the same top hit for the same query, and the empty case still returns `[]` and stops. I did not diff the MCP result against the old direct result field by field, so I can't say nothing differs, only that nothing I measured did.

**The three failure modes:** the empty-search message is shown above and in the run log. The empty-wardrobe run is in `results/run_2026-10-14_2058_before.md` ("empty wardrobe", `denim jacket under $50`): it returned general styling advice and a fit card, no crash. The model-unavailable handler is `agent.py::_model_unavailable_message` (it names the missing connection and says to check `GEMINI_API_KEY` in `.env` and the network, then re-run). <!-- TODO (author): paste the exact text you saw when you broke the key, if you ran it; it is not in the eval logs. -->

---

## The Improvement

**What I changed:** one edit to the prompt in `tools.py::suggest_outfit` (non-empty-wardrobe branch only). The old closing instruction was "Name the wardrobe pieces exactly as listed." The new one tells the model to refer to the new piece by its exact title, word for word (the real title is filled into the prompt), to refer to each wardrobe piece by its exact name as listed including words after a comma, and not to describe pieces with colors, tags or parenthetical lists. The empty-wardrobe prompt, the fallback sentence, the 120-word limit and the temperature are unchanged. Nothing else in the repo changed between the two runs.

**Which failure it was meant to fix:** the weak spot in criterion 5 (model output, `suggest_outfit`). Before, the model never named the new item by its exact title and dropped ", dark wash" from the jeans, so every output had 1–2 unfound items, and it passed only because of the 25% allowance (10 of 25 outputs sat exactly at the limit). One output also leaked tag lists in parentheses.

### Run Log — After

Run: `python run_eval.py --label after`. Raw output: `results/run_2026-10-14_2257_after.md`. Same scenarios, 5 tries, caching off.

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. The item search found is the item the next tool received | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. Different items get different fit card openings | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. suggest_outfit only names items that exist | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

Criterion 5, measured on the 25 outputs (5 queries x 5 tries), same literal exact-match rule and allowance both times:

| Measure | Before | After |
|---|---|---|
| Average unfound items per output | 1.32 | 0.08 |
| Outputs sitting exactly at the allowance limit | 10 of 25 | 1 of 25 |
| Outputs with a parenthetical tag list | 1 | 0 |
| Outputs over the limit (fail) | 0 | 0 |

Example, "cropped denim jacket" try 1 after the change (`tools.py::suggest_outfit`):

```
Outfit 1: Pair the **Denim Jacket — Light Wash, Cropped** with the **White ribbed tank top** and the **Baggy straight-leg jeans, dark wash**. Add the **Chunky white sneakers** and the **Black crossbody bag** to complete a street-style denim-on-denim look.
```

**Did it help, and how do I know:** Yes, on the thing I targeted. The pass/fail verdicts did not change (all five were MET before and after, so they could not show an improvement). The measured difference is in how close criterion 5 sat to failing: unfound items per output fell from 1.32 to 0.08, and only 1 of 25 outputs is at the limit instead of 10. The one parenthetical leak is gone. Caveats: this is one 5-try run of each, and the model is random, so a small difference could be noise, but a drop this large across 25 outputs is unlikely to be. Cost: the text now repeats the full listing title ("Denim Jacket — Light Wash, Cropped") instead of "the jacket", so it reads stiffer, and some outputs lost their "Outfit 1" headings. Criteria 4 and 1–3 were not targeted and did not move.

---

## What's Still Broken

No criterion is currently missed, in either run, so there is nothing to fix for a miss. This is what I think is still weak, and why I stopped.

- **Criterion 5 passes on a loose rule.** After the change, unfound items average 0.08 per output, but the criterion still counts a paraphrase as an unfound item and then forgives it with a 25% allowance, and "items named" is partly my own judgment (I used a hand-written list of paraphrases). I would make the check automatic by having the model return the items it used as a list and comparing that list to the wardrobe. I stopped because the brief limits this unit to one improvement.
- **Criterion 4 can't see repetition for one item.** Openings differ across items, but the same item gets "still not over finding these…" across tries. I would add a check that runs the same item five times and compares those openings. I did not rewrite the `create_fit_card` prompt because no criterion failed, and it would have been a second change.
- **Criterion 3 passes by construction.** The agent takes `search_results[0]` and nothing edits it. I did not log a real dict-equality check.
- **Criterion 1's 4-of-5 allowance was never used.** `suggest_outfit` never returned empty in 10 tries, so I haven't seen the third-tool branch fire in a real run.
- **Open from unit 3:** `search_listings` ranking puts unrelated items first when a broad word like "black" matches almost everything ("black boots under $70" ranked biker shorts above boots), and the empty-search message chains "Try to … or … or" without saying which change helps most. Not in any of my five criteria, so left alone.
- **Tests were one run each.** Each log is one 5-try run at temperature 0.9. A second run could differ by a try or two.

---

<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**

---

## Capstone

**What This Extends**

FitFindr (Project 2: the three-tool agent with `search_listings` on MCP, from units 3 and 4). What's new is an operational layer around the existing agent: the `serve.py` HTTP wrapper gets structured logging and timing, a documented single-command local run, and a measured cost per run. The agent logic in `agent.py` and `tools.py` is not changed by this unit's build.

**The Shape**

Shape A: deploy and instrument. I'm adding a JSON-lines request log to `serve.py` (timestamp, query, outcome, error, per-run duration, model calls and tokens), a run path on Path B (local with logs), and a cost measurement taken from that log. Failed and rejected requests also leave a record.

Out of scope, considered and cut:
- No change to the planning loop, the three tools, or the listings data. The ranking weakness noted in unit 4 stays as it is.
- No hosted deployment (Path A). The MCP call spawns a subprocess per tool call and the host has 512 MB, so I'm running locally with a committed log.
- No new tool, no retry-with-looser-constraints, and no web UI.

**Running It**

Path B, local with logs. Start command and environment are in [RUNNING.md](RUNNING.md): `AI201_CACHE=0 python serve.py`.

**Instrumentation**

`serve.py::ask` appends one JSON line per request to `logs/requests.jsonl`: `ts`, `id`, `query`, `http_status`, `outcome` (completed / stopped / rejected / crashed), `error`, `output`, `found_item`, `duration_ms` (agent run only, excluding lock wait), `model_calls`, `tokens`, `waited_ms`. Below are all 12 entries from the measurement session (`output` truncated to 70 characters here; the full text is in `logs/requests.jsonl`). The failed paths are the `rejected` entry (empty body, 400) and the `stopped` entries (no listings matched). I did not trigger a `crashed` entry.

```json
{"ts": "2026-11-18T23:14:06.003+00:00", "id": "74aab0c7", "query": "vintage graphic tee under $30", "http_status": 200, "outcome": "completed", "error": null, "output": "Obsessed with how perfectly worn-in this vintage band tee in faded gre…", "found_item": "Vintage Band Tee — Faded Grey", "duration_ms": 3717, "model_calls": 2, "tokens": 717, "waited_ms": 0}
{"ts": "2026-11-18T23:14:08.560+00:00", "id": "c597d299", "query": "black boots under $70", "http_status": 200, "outcome": "completed", "error": null, "output": "Obsessed with these shiny black biker shorts I just listed on Depop fo…", "found_item": "Biker Shorts — Black, Shiny", "duration_ms": 2555, "model_calls": 2, "tokens": 760, "waited_ms": 0}
{"ts": "2026-11-18T23:14:11.081+00:00", "id": "4332b651", "query": "denim jacket size M", "http_status": 200, "outcome": "completed", "error": null, "output": "Obsessed with this studded medium wash denim vest, but my closet is of…", "found_item": "Denim Vest — Medium Wash, Studded", "duration_ms": 2518, "model_calls": 2, "tokens": 697, "waited_ms": 0}
{"ts": "2026-11-18T23:14:13.336+00:00", "id": "c8d36238", "query": "floral summer dress under $40", "http_status": 200, "outcome": "completed", "error": null, "output": "still not over finding this 90s floral midi slip dress 😭 it’s giving t…", "found_item": "90s Silk Slip Dress — Floral, Midi Length", "duration_ms": 2253, "model_calls": 2, "tokens": 803, "waited_ms": 0}
{"ts": "2026-11-18T23:14:15.550+00:00", "id": "0f18e9ef", "query": "leather belt", "http_status": 200, "outcome": "completed", "error": null, "output": "Obsessed with this braided brown leather belt I just scored on thredUp…", "found_item": "Leather Belt — Brown, Braided", "duration_ms": 2212, "model_calls": 2, "tokens": 604, "waited_ms": 0}
{"ts": "2026-11-18T23:14:15.923+00:00", "id": "a25386cc", "query": "wool sweater size L under $50", "http_status": 200, "outcome": "stopped", "error": "Nothing matched \"wool sweater\", size L, under $50. Try to use fewer or different keywords (e.g. just the item type, like \"jacket\"), or drop the size or try a neighbouring one, or raise the $50 budget.", "output": "Nothing matched \"wool sweater\", size L, under $50. Try to use fewer or…", "found_item": null, "duration_ms": 370, "model_calls": 0, "tokens": 0, "waited_ms": 0}
{"ts": "2026-11-18T23:14:18.122+00:00", "id": "4f7fd1a8", "query": "sneakers size 9", "http_status": 200, "outcome": "completed", "error": null, "output": "Found these off-white low-top canvas sneakers on Poshmark for just $20…", "found_item": "Low-Top Canvas Sneakers — Off-White", "duration_ms": 2198, "model_calls": 2, "tokens": 689, "waited_ms": 0}
{"ts": "2026-11-18T23:14:20.290+00:00", "id": "41cc1f16", "query": "corduroy pants", "http_status": 200, "outcome": "completed", "error": null, "output": "Still not over finding these rust corduroy wide-leg pants on Depop for…", "found_item": "Corduroy Wide-Leg Pants — Rust", "duration_ms": 2166, "model_calls": 2, "tokens": 734, "waited_ms": 0}
{"ts": "2026-11-18T23:15:04.547+00:00", "id": "5f017535", "query": "silk scarf", "http_status": 200, "outcome": "completed", "error": null, "output": "Still can’t believe I scored this sage green silk button-down on Depop…", "found_item": "Silk Button-Down — Sage Green", "duration_ms": 44253, "model_calls": 2, "tokens": 949, "waited_ms": 0}
{"ts": "2026-11-18T23:15:05.055+00:00", "id": "5cc51be7", "query": "linen shirt size S", "http_status": 200, "outcome": "stopped", "error": "Nothing matched \"linen shirt\", size S. Try to use fewer or different keywords (e.g. just the item type, like \"jacket\"), or drop the size or try a neighbouring one.", "output": "Nothing matched \"linen shirt\", size S. Try to use fewer or different k…", "found_item": null, "duration_ms": 500, "model_calls": 0, "tokens": 0, "waited_ms": 0}
{"ts": "2026-11-18T23:15:05.056+00:00", "id": "926293a6", "query": null, "http_status": 400, "outcome": "rejected", "error": "missing or empty 'query'", "output": "", "duration_ms": 0, "model_calls": 0, "tokens": 0, "waited_ms": 0}
{"ts": "2026-11-18T23:15:05.378+00:00", "id": "faccf4d3", "query": "designer ballgown size XXS under $5", "http_status": 200, "outcome": "stopped", "error": "Nothing matched \"designer ballgown\", size XXS, under $5. Try to use fewer or different keywords (e.g. just the item type, like \"jacket\"), or drop the size or try a neighbouring one, or raise the $5 budget.", "output": "Nothing matched \"designer ballgown\", size XXS, under $5. Try to use fe…", "found_item": null, "duration_ms": 322, "model_calls": 0, "tokens": 0, "waited_ms": 0}
```

Gap: requests to unknown paths (404) or wrong methods (405) never reach `ask()`, so they are not logged.

**What It Costs**

Measured from the log above: the 8 completed runs averaged 744 tokens and 2.0 model calls each (range 604-949 tokens). Duration averaged 7.7 s but that is skewed by one 44 s run (likely rate-limit retry waiting in `generate.py`); the other seven ran 2.2-3.7 s. Measured by sending 10 different queries through the Flask test client with the cache off and reading `generate.token_counts()` before and after each run. Two of the ten matched nothing and cost 0 tokens. I did not convert tokens to dollars, since I did not look up the price. For 100 runs a day: 100 x 744 = about 74,400 tokens a day.
