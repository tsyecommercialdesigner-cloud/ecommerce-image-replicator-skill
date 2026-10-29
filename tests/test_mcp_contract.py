"""Offline checks against the installed MCP development package, not a Skill runtime dependency.

All text, IDs and hashes below are synthetic. No business files or credentials are read;
no server or provider is called.
"""
import unittest

from image_replicator.design import (
    CopyValidationError,
    effective_delta,
    resolve_copy,
    resolve_design,
    validate_final_copy,
)


def block(content):
    return {"content": content, "css": "color: #558833;", "box": {
        "x": 10, "y": 20, "width": 500, "height": 100,
    }}


class NativeMcpContract(unittest.TestCase):
    def test_shared_defaults_preserve_attributes_and_merge_color(self):
        context = {"defaults": {"design": {
            "product_attributes": [{"property": "dimensions", "value": "30x30cm",
                                    "source": "synthetic fixture"}],
            "brand_style": {"palette": ["orange", "cream"], "text_color": "#A8441A"},
        }}}
        for _ in range(12):
            delta = effective_delta(context, {})
            self.assertEqual(delta["design"]["product_attributes"][0]["value"], "30x30cm")
        changed = effective_delta(context, {"design": {"brand_style": {"text_color": "#111111"}}})
        self.assertEqual(changed["design"]["brand_style"]["palette"], ["orange", "cream"])

    def test_default_fact_adaptation_does_not_require_literal_rules(self):
        context = {"facts": [{"value": "Dimensions 30x30cm", "source": "synthetic fixture"}],
                   "defaults": {"design": {"product_attributes": [
                       {"property": "dimensions", "value": "30x30cm", "source": "synthetic fixture"},
                   ]}}}
        text = {"texts": [block("Reference dimensions 25x25cm")]}
        plan = resolve_design(
            {"image_id": "SYNTHETIC-ONLY", "source": "synthetic-reference.png", "sha256": "0" * 64,
             "delta": {}}, context, text, {"scene": "Synthetic reference scene"},
        )
        validate_final_copy(plan)
        self.assertEqual(plan["text_role"], "reference_transcription")
        self.assertEqual(plan["text_replacements"], [])
        self.assertEqual(plan["texts"], text["texts"])
        self.assertEqual(plan["product_attributes"][0]["value"], "30x30cm")

    def test_one_evidenced_literal_edit_covers_dimension_forms(self):
        texts = [block("25x25cm"), block("25cm")]
        result = resolve_copy(texts, [{"old": "25", "new": "30", "source": "synthetic dimensions"}])
        self.assertEqual([b["content"] for b in result], ["30x30cm", "30cm"])
        self.assertEqual(result[0]["box"], texts[0]["box"])

    def test_overlap_diagnostic_has_phase_and_rule_indexes(self):
        with self.assertRaises(CopyValidationError) as raised:
            resolve_copy([block("25x25cm 25cm")], [
                {"old": "25x25cm", "new": "30x30cm", "source": "synthetic"},
                {"old": "25cm", "new": "30cm", "source": "synthetic"},
            ])
        self.assertEqual(raised.exception.diagnostic["phase"], "copy_preflight")
        self.assertEqual(raised.exception.diagnostic["error_code"], "copy_replacements_overlap")
        self.assertEqual(raised.exception.diagnostic["replacement_indexes"], [0, 1])

    def test_unmatched_diagnostic_points_to_only_the_missing_rule(self):
        with self.assertRaises(CopyValidationError) as raised:
            resolve_copy([block("green apple")], [
                {"old": "green apple", "new": "orange", "source": "synthetic"},
                {"old": "20 pieces", "new": "30 pieces", "source": "synthetic"},
            ])
        self.assertEqual(raised.exception.diagnostic["error_code"], "copy_replacement_unmatched")
        self.assertEqual(raised.exception.diagnostic["replacement_indexes"], [1])

    def test_default_inheritance_conflict_is_not_a_scene_error(self):
        with self.assertRaises(CopyValidationError) as raised:
            effective_delta({"defaults": {"texts": [block("literal copy")]}}, {
                "text_replacements": [{"old": "old", "new": "new", "source": "synthetic"}],
            })
        self.assertEqual(raised.exception.diagnostic["error_code"], "copy_input_conflict")


if __name__ == "__main__":
    unittest.main()
