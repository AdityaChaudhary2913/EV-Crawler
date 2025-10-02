import unittest

from crawler.relevance import content_score


class TestRelevance(unittest.TestCase):
    def test_ev_sentence_scores_high(self):
        text = "The new Ather electric scooter gets better battery swap options and fast charging."
        score = content_score(
            text,
            keywords=["ev scooter", "electric", "battery", "charging"],
            brand_terms=["Ather", "Ola"],
            policy_terms=["FAME"],
            brand_bonus=0.7,
            policy_bonus=0.4,
        )
        self.assertGreater(score, 2.0)


if __name__ == "__main__":
    unittest.main()
