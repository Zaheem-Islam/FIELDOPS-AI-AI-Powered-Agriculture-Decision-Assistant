import unittest
from unittest.mock import patch

from i18n import localize_irrigation, localize_result, translate_text
from voice_utils import pick_preferred_voice


class BilingualUiTests(unittest.TestCase):
    def test_localize_result_urdu(self):
        result = {
            "field_status": "Water Stress Risk — HIGH",
            "recommendation": "Irrigation is recommended for the wheat field.",
            "confidence": "Medium",
            "crop_health": {"finding": "Low soil moisture", "confidence": "High"},
            "soil": {"finding": "Low soil moisture", "confidence": "High"},
            "weather": {"finding": "Limited rainfall", "confidence": "High"},
            "vision": {"observation": "No image was provided.", "limitation": "Upload a crop image."},
            "validation": {"issues": ["Required field information is missing."]},
            "next_actions": ["Review the irrigation recommendation."]
        }

        with patch("i18n._translate_urdu_online", return_value=None):
            localized = localize_result(result, "ur")

        self.assertIn("پانی کی کمی کا خطرہ", localized["field_status"])
        self.assertIn("مشورہ", localized["recommendation"])
        self.assertNotIn("سفارش", localized["recommendation"])
        self.assertIn("مٹی میں پانی کم ہے", localized["soil"]["finding"])
        self.assertIn("کم بارش", localized["weather"]["finding"])
        self.assertIn("مطلوبہ معلومات", localized["validation"]["issues"][0])
        self.assertIn("دوبارہ جائزہ", localized["next_actions"][0])

    def test_localize_irrigation_urdu(self):
        irrigation = {"recommendation": "Recommended", "method": "Controlled demo rule: low soil moisture + limited rainfall"}

        localized = localize_irrigation(irrigation, "ur")

        self.assertEqual(localized["recommendation"], "تجویز شدہ")
        self.assertIn("مٹی میں پانی کم", localized["method"])

    def test_urdu_localization_translates_unmapped_ai_text(self):
        source = "The crop needs closer monitoring during the current stage."
        expected = "موجودہ مرحلے کے دوران فصل کی زیادہ نگرانی کی ضرورت ہے۔"

        with patch("i18n._translate_urdu_online", return_value=expected):
            self.assertEqual(translate_text(source, "ur"), expected)

    def test_fallback_recommendation_is_fully_urdu_without_network(self):
        source = (
            "Irrigation is recommended for the Wheat field because soil moisture is low, "
            "recent/expected rainfall is limited, and the crop is at the Germination stage."
        )

        with patch("i18n._translate_urdu_online", return_value=None):
            localized = translate_text(source, "ur")

        self.assertIn("گندم", localized)
        self.assertIn("مشورہ", localized)
        self.assertNotIn("سفارش", localized)
        self.assertNotIn("Irrigation", localized)
        self.assertNotIn("Germination", localized)

    def test_fixed_rag_text_is_fully_urdu_without_network(self):
        source = (
            "When recent and expected rainfall are limited, irrigation decisions should "
            "consider crop stage and current soil moisture together."
        )

        with patch("i18n._translate_urdu_online", return_value=None):
            localized = translate_text(source, "ur")

        self.assertNotIn("rainfall", localized.lower())
        self.assertNotIn("irrigation", localized.lower())

    def test_pick_preferred_voice_prefers_urdu_for_urdu_language(self):
        voices = [
            {"name": "Microsoft David Desktop - English (United States)", "lang": "en-US"},
            {"name": "Microsoft Urdu - Pakistan", "lang": "ur-PK"},
            {"name": "Google UK English Female", "lang": "en-GB"},
        ]

        self.assertEqual(pick_preferred_voice("ur", voices)["lang"], "ur-PK")

    def test_pick_preferred_voice_english_falls_back_to_any_supported_voice(self):
        voices = [{"name": "Generic Voice", "lang": "fr-FR"}, {"name": "Windows English", "lang": "en-US"}]

        self.assertEqual(pick_preferred_voice("en", voices)["lang"], "en-US")


if __name__ == "__main__":
    unittest.main()
