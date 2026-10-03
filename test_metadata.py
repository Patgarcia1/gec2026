import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from parse import get_meta


class MetadataTests(unittest.TestCase):
    def test_soil_readmes(self):
        soil = get_meta("biogeochem")
        self.assertEqual(len(soil["authors"]), 7)
        self.assertIn("François Guillemette", soil["authors"])
        self.assertEqual(soil["variables"]["BA"]["unit"], "cells/gSoil")
        self.assertEqual(soil["variables"]["SR"]["description"], "spectral slope ratio")
        self.assertEqual(soil["doi"], "")  # Ancillary DOI is not this dataset's DOI.
        biolog = get_meta("biolog")
        self.assertEqual(len(biolog["variables"]), 34)
        self.assertIn("D, L-α-Glycerol Phosphate", biolog["variables"]["C10"]["description"])
        self.assertEqual(biolog["variables"]["C10"]["unit"], "AWCD")
        self.assertEqual(biolog["location"], "Bécancour, Québec, Canada")

    def test_cattle_blocks(self):
        cow = get_meta("cow")
        self.assertEqual(cow["authors"], ["John Cant", "Patricia Kedzierski", "Carolina Reyes"])
        self.assertEqual(cow["doi"], "https://doi.org/10.5683/SP4/MS7XVT")
        self.assertEqual(len(cow["variables"]), 24)
        self.assertIn("date", cow["variables"])
        self.assertIn("HP_Greenfeed", cow["variables"])
        self.assertEqual(cow["variables"]["BWsmth_chg"]["unit"], "kg/d")
        self.assertEqual(cow["variables"]["DIM"]["unit"], "")
        self.assertEqual(cow["variables"]["milk_fat"]["unit"], "%")
        self.assertIn("Notes".lower(), cow["variables"]["milkE"])

    def test_values_are_read_at_call_time(self):
        # Changing the source text must change the result, with no registry/cache.
        with patch.object(Path, "read_text", return_value=(
            "Title of Dataset: A changed title\nName: New Author\n"
            "Variable List:\nBA, updated definition, new-unit\nMissing data codes: NA\n"
        )):
            meta = get_meta("biogeochem")
        self.assertEqual(meta["title"], "A changed title")
        self.assertEqual(meta["authors"], ["New Author"])
        self.assertEqual(meta["variables"]["BA"]["unit"], "new-unit")

    def test_paths_are_independent_of_working_directory(self):
        original = os.getcwd()
        with tempfile.TemporaryDirectory() as directory:
            try:
                os.chdir(directory)
                self.assertTrue(get_meta("cow")["title"])
            finally:
                os.chdir(original)
        self.assertEqual(get_meta("unknown"), {})


if __name__ == "__main__":
    unittest.main()
