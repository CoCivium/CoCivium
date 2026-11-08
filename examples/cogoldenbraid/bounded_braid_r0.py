"""Bounded, pure CoGoldenBraid R0 relation evaluator. No runtime authority."""
from dataclasses import dataclass
from typing import Tuple

@dataclass(frozen=True)
class Braid:
    key: str
    refs: Tuple[str, ...]
    supply: float
    demand: float
    future: float

def evaluate(items, root, depth_limit=8, node_budget=100):
    """Return bounded reachable IDs, cycles and truncation; never execute effects."""
    if depth_limit < 0 or node_budget < 1:
        raise ValueError("invalid bounds")
    by_id = {b.key: b for b in items}
    if len(by_id) != len(items):
        raise ValueError("duplicate braid identity")
    visited, active, cycles = set(), set(), set()
    ordered = []
    truncated = False
    def walk(key, depth):
        nonlocal truncated
        if key in active:
            cycles.add(key)
            return
        if key in visited:
            return
        if depth > depth_limit or len(visited) >= node_budget:
            truncated = True
            return
        if key not in by_id:
            raise ValueError("unresolved reference: " + key)
        visited.add(key)
        active.add(key)
        ordered.append(key)
        for child in sorted(by_id[key].refs):
            walk(child, depth + 1)
        active.remove(key)
    walk(root, 0)
    return {"reachable": ordered, "cycles": sorted(cycles),
            "truncated": truncated, "effects": 0}

if __name__ == "__main__":
    import unittest
    class Checks(unittest.TestCase):
        def test_recursive_cycle(self):
            items = [Braid("a", ("b",), 1, 0, 0),
                     Braid("b", ("a",), 0, 1, 1)]
            r = evaluate(items, "a")
            self.assertEqual(r["cycles"], ["a"])
            self.assertEqual(r["reachable"], ["a", "b"])
            self.assertEqual(r["effects"], 0)
        def test_budget(self):
            items = [Braid(str(i), (str(i+1),) if i < 10 else (), 0, 0, 0) for i in range(11)]
            r = evaluate(items, "0", node_budget=3)
            self.assertTrue(r["truncated"])
            self.assertEqual(len(r["reachable"]), 3)
        def test_replay(self):
            items = [Braid("a", ("b",), 1, 2, 3), Braid("b", (), 2, 3, 4)]
            self.assertEqual(evaluate(items, "a"), evaluate(list(reversed(items)), "a"))
        def test_invalid(self):
            with self.assertRaises(ValueError):
                evaluate([Braid("a", ("missing",), 0, 0, 0)], "a")
            with self.assertRaises(ValueError):
                evaluate([Braid("a", (), 0, 0, 0)]*2, "a")
    unittest.main()
