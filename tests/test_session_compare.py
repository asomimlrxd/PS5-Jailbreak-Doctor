import unittest

from session_compare import compare_log_texts


class SessionComparisonTests(unittest.TestCase):
    def test_counts_added_and_removed_lines(self):
        result = compare_log_texts(
            "same line\nold line\n",
            "same line\nnew line\n",
            "before.log",
            "after.log",
        )
        self.assertEqual(result["baseline_lines"], 2)
        self.assertEqual(result["current_lines"], 2)
        self.assertEqual(result["added_count"], 1)
        self.assertEqual(result["removed_count"], 1)
        self.assertEqual(result["added_lines"], ["new line"])
        self.assertEqual(result["removed_lines"], ["old line"])
        self.assertIn("+new line", result["diff"])
        self.assertIn("-old line", result["diff"])

    def test_duplicate_lines_are_counted(self):
        result = compare_log_texts("repeat\nrepeat\n", "repeat\n")
        self.assertEqual(result["removed_count"], 1)
        self.assertEqual(result["added_count"], 0)

    def test_inputs_are_not_mutated(self):
        before = "a\r\nb\r\n"
        after = "a\r\nc\r\n"
        compare_log_texts(before, after)
        self.assertEqual(before, "a\r\nb\r\n")
        self.assertEqual(after, "a\r\nc\r\n")

    def test_line_limit_prevents_excessive_comparison(self):
        huge = ("x\n" * 200_001)
        with self.assertRaises(ValueError):
            compare_log_texts(huge, "normal")


if __name__ == "__main__":
    unittest.main()
