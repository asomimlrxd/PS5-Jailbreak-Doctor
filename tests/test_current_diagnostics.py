import unittest

import doctor_core
from doctor_core import analyze_logs


class CurrentShadowMountDiagnosticsTests(unittest.TestCase):
    def test_release_version(self):
        self.assertEqual(doctor_core.APP_VERSION, "1.04")

    def test_api_listener_stall_rule_is_matched(self):
        log = "[API] HTTP/JSON listener on port 10101 silently dies and refuses connections"
        findings = analyze_logs(log)
        ids = {finding.rule_id for finding in findings}
        self.assertIn("SHADOW_API_LISTENER_STALL", ids)

    def test_scan_queued_after_exit_rule_is_matched(self):
        log = (
            "[GAME] process exited, awaiting same-app handoff: PPSA99203 pid=299\n"
            "[SCAN] scan queued until the prepared game is closed\n"
        )
        findings = analyze_logs(log)
        ids = {finding.rule_id for finding in findings}
        self.assertIn("SHADOW_SCAN_QUEUED_AFTER_GAME_EXIT", ids)

    def test_open_pull_request_is_not_recorded_as_a_released_fix(self):
        rule = next(r for r in doctor_core.KNOWLEDGE_BASE["rules"] if r["id"] == "SHADOW_SCAN_QUEUED_AFTER_GAME_EXIT")
        self.assertEqual(rule["evidence_status"], "relato_comunitario_aberto")
        self.assertTrue(any("pull/163" in url for url in rule["sources"]))
        self.assertIn("não", rule["fix_summary"].casefold())


if __name__ == "__main__":
    unittest.main()
