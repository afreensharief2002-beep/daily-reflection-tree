# Write-Up: Daily Reflection Tree — Design Rationale

**DT Fellowship Assignment · Afreen B. Sharief**

---

## Why These Questions

The hardest constraint in this assignment is also the most important one: **no free text**. Every question must offer pre-defined options that genuinely capture a spectrum — not leading the user toward the "right" answer, not collapsing nuance into a binary.

For Axis 1 (Locus), I started from a concrete behavioral signal rather than an abstract attitude. Rotter's original LOC scale asks people to endorse statements about beliefs; that works for research, but it's too meta for an end-of-day conversation. Instead, I asked: *what did you actually do when things went sideways?* The options — "I looked for what I could still control" vs "I waited to see what others would do" — describe recognizable behaviors, not self-assessments. The employee doesn't need to know anything about locus of control theory. They just pick what happened.

For Axis 2 (Orientation), the challenge was making entitlement visible without triggering defensiveness. Entitlement is invisible to the person holding it (Campbell et al., 2004) — that's its defining feature. So I used an indirect approach: first, ask about the *interaction itself* ("what was your role?"), then ask about the *feeling underneath it* ("what's the feeling about input vs return?"). The entitlement branch question ("I gave a lot and it wasn't acknowledged") is honest, not accusatory. It names a real feeling without labeling the person.

For Axis 3 (Radius), I drew on Batson's (2011) distinction between sympathy and perspective-taking. The question isn't "did you feel bad for someone?" — it's "who was in the frame when you were thinking about your own hardest moment?" That's a cognitive act, not an emotional one, and it maps directly to Maslow's self-transcendence: the shift from *what do I need?* to *what does this situation need?*

---

## Branching Design and Trade-offs

The tree uses a **two-layer branching architecture** per axis:

1. **Surface layer** — an opening question that routes the employee into a "high" or "low" branch based on their day's tone
2. **Signal layer** — one or two follow-up questions that accumulate axis signals, driving the final reflection at the summary

This means a single tough answer doesn't condemn the employee to the "victim" track. Someone who said "Draining" at the start can still accumulate internal-locus signals from later questions, producing a more nuanced summary. The axes are about *dominant patterns*, not single data points.

**Trade-off I made:** The tree uses 10 question nodes — slightly above the 8-node minimum — to give each axis room to breathe. The alternative was shorter (fewer questions per axis) but would have made the signal tallies brittle; one question deciding an entire axis felt too thin to be trustworthy.

**What I deliberately avoided:** Asking employees to *rate* themselves ("on a scale of 1–5..."). Scales feel like surveys. The questions in this tree are narrative — they ask about moments, actions, feelings. That's the difference between a questionnaire and a conversation.

---

## Psychological Sources

| Axis | Primary Source | Design Implication |
|------|---------------|-------------------|
| Locus | Rotter (1954), *Locus of Control* | Behavioral options, not attitude endorsements |
| Locus | Dweck (2006), *Mindset* | Adaptation framing — did you adjust, or attribute? |
| Orientation | Campbell et al. (2004), *Psychological Entitlement* | Indirect questions; name the feeling, not the trait |
| Orientation | Organ (1988), *OCB* | "What wasn't required" as the contribution signal |
| Radius | Maslow (1969), *Theory of Metamotivation* | "Who was in the frame" as transcendence proxy |
| Radius | Batson (2011), *Altruism in Humans* | Perspective-taking as a cognitive act, not emotional |

---

## What I'd Improve With More Time

**1. More branching depth in the middle paths.** Currently, the "Mixed" day answer routes into the same "high" branch as "Productive." A better design would have a dedicated "Mixed" path — acknowledging ambivalence explicitly before asking what drove the outcomes.

**2. Temporal interpolation in reflections.** The tree references `{A1_OPEN.answer}` but could do more — e.g., noting patterns across days if the tool ran over multiple sessions. "Last Tuesday you also said Draining. What's different this week?" That would require persistence, but it's the natural evolution.

**3. Testing against more personas.** I walked through the tree as 8 distinct answer patterns (all combinations of the three binary axes) to verify the reflection-summary pairs made sense. But real employees would find edges I didn't — questions where two options feel identical, or where the framing assumes a certain kind of work.

**4. A "pause" or "skip" option.** Some evenings, an employee genuinely can't answer a question — too tired, too raw. A graceful skip mechanism that flags the question as unanswered (rather than forcing a pick) would make the tool more honest.

---

*The tree is the product. The code walks it. The questions are what matter.*
