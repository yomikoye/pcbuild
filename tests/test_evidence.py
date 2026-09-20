"""Network-free parser regressions: extraction must not infer purchase readiness."""
import importlib.util
import pathlib
import unittest

MODULE = pathlib.Path(__file__).parents[1] / 'scripts' / 'collect_evidence.py'


class EvidenceTests(unittest.TestCase):
    def test_parser_retains_product_offer_and_visible_text(self):
        self.assertTrue(MODULE.exists(), 'Direct-HTTP evidence parser is missing')
        spec = importlib.util.spec_from_file_location('collector', MODULE)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        result = mod.parse_html('<title>Example</title><script type="application/ld+json">'
                                '{"@graph":[{"@type":"Product","sku":"EXACT",'
                                '"offers":{"price":"12.34","availability":"OutOfStock"}}]}'
                                '</script><p>Produkt niedostępny</p>')
        self.assertEqual(result['products'][0]['sku'], 'EXACT')
        self.assertEqual(result['products'][0]['offers']['availability'], 'OutOfStock')
        self.assertIn('Produkt niedostępny', result['text'])
        self.assertNotIn('qualified', result)

    def test_malformed_json_is_explicit_not_empty_success(self):
        self.assertTrue(MODULE.exists(), 'Direct-HTTP evidence parser is missing')
        spec = importlib.util.spec_from_file_location('collector', MODULE)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        result = mod.parse_html('<script type="application/ld+json">{bad}</script>')
        self.assertTrue(result['parse_errors'])
        self.assertEqual(result['products'], [])


if __name__ == '__main__':
    unittest.main()
