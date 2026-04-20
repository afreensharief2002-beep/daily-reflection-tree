#!/usr/bin/env python3
"""
Daily Reflection Tree — Deterministic CLI Agent
Part B of the DT Fellowship Assignment

Loads the tree from reflection-tree.json and walks it deterministically.
No LLM calls at runtime. No randomness. Same answers → same path, every time.

Usage:
    python agent.py
    python agent.py --tree ../tree/reflection-tree.json
"""

import json
import sys
import os
import time
import argparse
from datetime import datetime


# ─── Colours for terminal output ──────────────────────────────────────────────
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    CYAN    = "\033[36m"
    GREEN   = "\033[32m"
    YELLOW  = "\033[33m"
    MAGENTA = "\033[35m"
    WHITE   = "\033[97m"
    BLUE    = "\033[34m"


def clear_line():
    print()


def slow_print(text, delay=0.018, colour=C.WHITE):
    """Print text character by character for a conversational feel."""
    print(colour, end="", flush=True)
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print(C.RESET)


def print_divider():
    print(f"\n{C.DIM}{'─' * 60}{C.RESET}\n")


# ─── Tree Loader ──────────────────────────────────────────────────────────────

def load_tree(filepath: str) -> dict:
    """Load the tree JSON and index nodes by id."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    node_map = {}
    for node in data["nodes"]:
        node_map[node["id"]] = node

    return data, node_map


# ─── State Manager ────────────────────────────────────────────────────────────

class SessionState:
    """Tracks answers, signal tallies, and axis dominance."""

    def __init__(self):
        self.answers: dict[str, str] = {}       # node_id → selected answer
        self.signals: dict[str, int] = {        # signal_tag → count
            "axis1:internal": 0,
            "axis1:external": 0,
            "axis2:contribution": 0,
            "axis2:entitlement": 0,
            "axis3:other": 0,
            "axis3:self": 0,
        }
        self.path: list[str] = []               # sequence of visited node ids

    def record_answer(self, node_id: str, answer: str):
        self.answers[node_id] = answer

    def record_signal(self, signal: str):
        if signal and signal in self.signals:
            self.signals[signal] += 1

    def dominant(self, axis: str) -> str:
        """Return the dominant pole for a given axis prefix."""
        candidates = {k: v for k, v in self.signals.items() if k.startswith(axis)}
        if not candidates:
            return "unknown"
        return max(candidates, key=candidates.get).split(":")[1]

    def summary_key(self) -> str:
        a1 = self.dominant("axis1")
        a2 = self.dominant("axis2")
        a3 = self.dominant("axis3")
        return f"{a1}+{a2}+{a3}"


# ─── Text Interpolation ───────────────────────────────────────────────────────

def interpolate(text: str, state: SessionState, summary_templates: dict = None) -> str:
    """Replace {NODE_ID.answer} placeholders and axis summary tokens."""
    if not text:
        return text

    # Replace answer references: {A1_OPEN.answer}
    import re
    for match in re.findall(r"\{([A-Z0-9_]+)\.answer\}", text):
        value = state.answers.get(match, "")
        text = text.replace("{" + match + ".answer}", value)

    if summary_templates:
        # Axis dominant labels
        for axis_key in ["axis1", "axis2", "axis3"]:
            dom = state.dominant(axis_key)
            label = summary_templates.get(axis_key, {}).get(dom, dom)
            text = text.replace("{" + axis_key + ".dominant}", dom)
            text = text.replace("{" + axis_key + ".summary}", label)

        # Closing reflection
        key = state.summary_key()
        closing = summary_templates.get("closingReflections", {}).get(
            key,
            "Take what you noticed into tomorrow."
        )
        text = text.replace("{closing_reflection}", closing)

    return text


# ─── Decision Router ─────────────────────────────────────────────────────────

def resolve_decision(node: dict, state: SessionState) -> str:
    """
    Evaluate a decision node's routing rules and return the next node id.

    Two rule formats supported:
      answer=VALUE1|VALUE2:TARGET_NODE_ID
      signal=POLE1>POLE2:TARGET_NODE_ID   (dominant pole comparison)
    """
    rules = node.get("options") or []

    for rule in rules:
        condition, target = rule.split(":")
        key, value_str = condition.split("=")

        if key == "answer":
            # Find the most recent answer to route from
            # Walk the path backwards to find the last question answer
            values = value_str.split("|")
            # Get the parent node id
            parent_id = node.get("parentId")
            if parent_id and parent_id in state.answers:
                if state.answers[parent_id] in values:
                    return target
            else:
                # Check all recent answers
                for v in values:
                    if v in state.answers.values():
                        return target

        elif key == "signal":
            # Format: axis1:internal>axis1:external or axis1.dominant=internal
            parts = value_str.split(">")
            if len(parts) == 2:
                left_tag, right_tag = parts[0], parts[1]
                left_count = state.signals.get(left_tag, 0)
                right_count = state.signals.get(right_tag, 0)
                if left_count > right_count:
                    return target
            elif ">=" in value_str:
                parts = value_str.split(">=")
                left_tag, right_tag = parts[0], parts[1]
                left_count = state.signals.get(left_tag, 0)
                right_count = state.signals.get(right_tag, 0)
                if left_count >= right_count:
                    return target

    # Fallback: return last rule's target
    if rules:
        return rules[-1].split(":")[1]
    return None


# ─── Node Handlers ────────────────────────────────────────────────────────────

def handle_start(node: dict, state: SessionState):
    clear_line()
    print(f"{C.CYAN}{C.BOLD}{'═' * 60}{C.RESET}")
    print(f"{C.CYAN}{C.BOLD}   Daily Reflection{C.RESET}")
    print(f"{C.DIM}   {datetime.now().strftime('%A, %d %B %Y  ·  %H:%M')}{C.RESET}")
    print(f"{C.CYAN}{C.BOLD}{'═' * 60}{C.RESET}\n")
    time.sleep(0.3)
    slow_print(node["text"], colour=C.WHITE)
    clear_line()
    input(f"  {C.DIM}[ Press Enter to begin ]{C.RESET}")


def handle_question(node: dict, state: SessionState) -> str:
    """Display question, collect answer. Returns chosen option text."""
    print_divider()
    slow_print(node["text"], colour=C.BOLD + C.WHITE)
    clear_line()

    options = node["options"]
    for i, opt in enumerate(options, 1):
        print(f"  {C.CYAN}{i}{C.RESET}  {opt}")

    clear_line()
    while True:
        raw = input(f"  {C.DIM}Your choice (1–{len(options)}): {C.RESET}").strip()
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                chosen = options[idx]
                print(f"\n  {C.GREEN}✓  {chosen}{C.RESET}")
                return chosen
        print(f"  {C.YELLOW}Please enter a number between 1 and {len(options)}.{C.RESET}")


def handle_reflection(node: dict, state: SessionState, summary_templates=None):
    print_divider()
    text = interpolate(node["text"], state, summary_templates)
    print(f"  {C.MAGENTA}╔{'═' * 56}╗{C.RESET}")
    # Word-wrap to fit inside box
    words = text.split()
    line = "  "
    lines = []
    for word in words:
        if len(line) + len(word) + 1 > 56:
            lines.append(line)
            line = "  " + word
        else:
            line += (" " if line.strip() else "") + word
    if line.strip():
        lines.append(line)
    for l in lines:
        print(f"  {C.MAGENTA}║{C.RESET}  {C.WHITE}{l:<54}{C.RESET}  {C.MAGENTA}║{C.RESET}")
    print(f"  {C.MAGENTA}╚{'═' * 56}╝{C.RESET}\n")
    input(f"  {C.DIM}[ Continue ]{C.RESET}")


def handle_bridge(node: dict, state: SessionState):
    print_divider()
    slow_print(f"  {node['text']}", colour=C.DIM + C.CYAN)
    time.sleep(0.8)


def handle_summary(node: dict, state: SessionState, summary_templates: dict):
    print_divider()
    print(f"{C.BLUE}{C.BOLD}  Today's Reflection{C.RESET}\n")
    text = interpolate(node["text"], state, summary_templates)
    for paragraph in text.strip().split("\n\n"):
        slow_print("  " + paragraph.strip(), colour=C.WHITE)
        clear_line()
    time.sleep(0.5)


def handle_end(node: dict, state: SessionState):
    print_divider()
    slow_print(node["text"], colour=C.DIM + C.CYAN)
    clear_line()
    print(f"{C.DIM}  Session path: {' → '.join(state.path)}{C.RESET}\n")


# ─── Tree Walker ─────────────────────────────────────────────────────────────

def walk_tree(node_map: dict, state: SessionState, summary_templates: dict):
    """Main loop — traverse from START to END following the tree."""
    current_id = "START"

    while current_id:
        node = node_map.get(current_id)
        if not node:
            print(f"\n[ERROR] Node '{current_id}' not found in tree.")
            break

        state.path.append(current_id)
        node_type = node["type"]

        if node_type == "start":
            handle_start(node, state)
            current_id = node.get("target") or _first_child(node_map, current_id)

        elif node_type == "question":
            answer = handle_question(node, state)
            state.record_answer(current_id, answer)
            if node.get("signal"):
                state.record_signal(node["signal"])
            current_id = _first_child(node_map, current_id)

        elif node_type == "decision":
            next_id = resolve_decision(node, state)
            current_id = next_id

        elif node_type == "reflection":
            handle_reflection(node, state, summary_templates)
            if node.get("signal"):
                state.record_signal(node["signal"])
            current_id = node.get("target") or _first_child(node_map, current_id)

        elif node_type == "bridge":
            handle_bridge(node, state)
            current_id = node.get("target") or _first_child(node_map, current_id)

        elif node_type == "summary":
            handle_summary(node, state, summary_templates)
            current_id = node.get("target") or _first_child(node_map, current_id)

        elif node_type == "end":
            handle_end(node, state)
            break

        else:
            # Unknown node type — skip
            current_id = node.get("target") or _first_child(node_map, current_id)


def _first_child(node_map: dict, parent_id: str) -> str | None:
    """Return the first node whose parentId matches parent_id."""
    for nid, node in node_map.items():
        if node.get("parentId") == parent_id:
            return nid
    return None


# ─── Entry Point ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Daily Reflection Tree — Deterministic Agent")
    parser.add_argument(
        "--tree",
        default=os.path.join(os.path.dirname(__file__), "../tree/reflection-tree.json"),
        help="Path to the reflection-tree.json file"
    )
    args = parser.parse_args()

    tree_path = os.path.abspath(args.tree)
    if not os.path.exists(tree_path):
        print(f"[ERROR] Tree file not found: {tree_path}")
        sys.exit(1)

    data, node_map = load_tree(tree_path)

    # Extract summary templates from the SUMMARY node
    summary_node = node_map.get("SUMMARY", {})
    summary_templates = summary_node.get("summaryTemplates", {})

    state = SessionState()

    try:
        walk_tree(node_map, state, summary_templates)
    except KeyboardInterrupt:
        print(f"\n\n{C.DIM}Session ended early. See you tomorrow.{C.RESET}\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
