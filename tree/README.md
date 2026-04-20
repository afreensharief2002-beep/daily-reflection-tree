# Daily Reflection Tree
### DT Fellowship Assignment — Afreen B. Sharief

A deterministic end-of-day reflection tool that walks employees through three psychological axes via a structured decision tree. **No LLM at runtime. No free text. Same answers → same path, every time.**

---

## Repository Structure

```
/tree/
  reflection-tree.json      ← Part A: the full tree as structured data
  tree-diagram.md           ← Part A: Mermaid visual of all branches

/agent/
  agent.py                  ← Part B: CLI agent that walks the tree

/transcripts/
  persona-1-victor-contributing-altrocentric.md
  persona-2-victim-entitlement-selfcentric.md

write-up.md                 ← Design rationale (2 pages)
README.md                   ← This file
```

---

## Part A — Reading the Tree

The tree is stored in `tree/reflection-tree.json`. Each node has:

| Field | Purpose |
|-------|---------|
| `id` | Unique node identifier |
| `parentId` | Parent in the tree hierarchy |
| `type` | `start`, `question`, `decision`, `reflection`, `bridge`, `summary`, `end` |
| `text` | What the employee sees. `{NODE_ID.answer}` is replaced at runtime. |
| `options` | For questions: list of choices. For decisions: routing rules. |
| `target` | Override next node (for bridges that jump across subtrees). |
| `signal` | What this node records: e.g. `axis1:internal` increments that counter. |

### Decision Node Routing Format

```
"answer=VALUE1|VALUE2:TARGET_NODE_ID"   — route by prior answer
"signal=axis1:internal>axis1:external:TARGET_NODE_ID"  — route by dominant signal
```

### Tracing a Path Manually

To trace the **internal + contribution + altrocentric** path:

```
START → A1_OPEN (pick "Productive")
→ A1_D_OPEN (routes to A1_Q1_HIGH)
→ A1_Q1_HIGH (pick "I adapted when things shifted")
→ A1_D_Q1_HIGH (routes to A1_Q2_INTERNAL)
→ A1_Q2_INTERNAL (pick "Yes — I see clearly")   [signal: axis1:internal]
→ A1_D_Q2 (internal > external → A1_R_INTERNAL)
→ A1_R_INTERNAL → BRIDGE_1_2 → A2_OPEN
→ A2_OPEN (pick "I contributed something...")
→ A2_D_OPEN (routes to A2_Q1_CONTRIBUTION)
→ A2_Q1_CONTRIBUTION (pick "I helped someone")  [signal: axis2:contribution]
→ A2_Q2_CONTRIBUTION (any option)               [signal: axis2:contribution]
→ A2_D_Q2 (contribution > entitlement → A2_R_CONTRIBUTION)
→ A2_R_CONTRIBUTION → BRIDGE_2_3 → A3_OPEN
→ A3_OPEN (pick "The team — we were all tangled")
→ A3_D_OPEN (routes to A3_Q1_OTHER)
→ A3_Q1_OTHER (pick "I checked in")             [signal: axis3:other]
→ A3_Q2_OTHER (any option)                      [signal: axis3:other]
→ A3_D_Q2 (other > self → A3_R_ALTROCENTRIC)
→ A3_R_ALTROCENTRIC → SUMMARY → END
```

---

## Part B — Running the Agent

**Requirements:** Python 3.10+. No external libraries.

```bash
cd agent
python agent.py
```

To specify a custom tree file:

```bash
python agent.py --tree ../tree/reflection-tree.json
```

**What it does:**
- Loads and indexes `reflection-tree.json`
- Walks the tree node by node
- Waits for numbered input at `question` nodes
- Auto-advances at `start`, `bridge`, `decision` nodes
- Accumulates axis signals as the session progresses
- Interpolates `{NODE_ID.answer}` placeholders in reflection text
- Selects the correct closing reflection from 8 possible `summaryTemplates` keys
- Prints the session path on exit

---

## The Three Axes

| Axis | Spectrum | Psychology |
|------|----------|-----------|
| **Locus** | Victim ↔ Victor | Rotter (1954) LOC; Dweck (2006) Growth Mindset |
| **Orientation** | Entitlement ↔ Contribution | Campbell et al. (2004); Organ (1988) OCB |
| **Radius** | Self-Centric ↔ Altrocentric | Maslow (1969) Self-Transcendence; Batson (2011) |

---

## Tree Stats

- **Total nodes:** 36
- **Question nodes:** 10 (3–4 per axis + opening)
- **Decision nodes:** 7
- **Reflection nodes:** 6 (2 per axis)
- **Bridge nodes:** 2
- **Possible conversation paths:** 8
- **Possible closing reflections:** 8 (one per axis combination)

---

## Design Philosophy

> The questions are the product. A technically perfect tree with shallow questions loses to a rough tree with questions that make someone pause.

See `write-up.md` for full design rationale.
