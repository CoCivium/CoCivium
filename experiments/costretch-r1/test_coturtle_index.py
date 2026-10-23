"""Provider-free Python tests for the CoTurtleIndex R1 logical-space witness."""
import importlib.util
import pathlib
import random
import unittest

path = pathlib.Path(__file__).with_name('CoTurtleIndex_R1.py')
spec = importlib.util.spec_from_file_location('coturtle_index', path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CoTurtleIndexTests(unittest.TestCase):
    def test_capacity(self):
        self.assertEqual(module.capacity(), 50_164_531_200_000)

    def test_rank_unrank_boundaries(self):
        for value in [0, 1, module.capacity()//2, module.capacity()-2, module.capacity()-1]:
            self.assertEqual(module.rank(module.unrank(value)), value)

    def test_rank_unrank_sample(self):
        rng = random.Random(771)
        for _ in range(1000):
            index = rng.randrange(module.capacity())
            self.assertEqual(module.rank(module.unrank(index)), index)

    def test_reject_out_of_range(self):
        for value in (-1, module.capacity(), module.capacity()+1, True, 1.1):
            with self.subTest(index=value), self.assertRaises(ValueError):
                module.unrank(value)

    def test_reject_missing_dimension(self):
        candidate = module.unrank(0)
        del candidate['role']
        with self.assertRaises(ValueError):
            module.rank(candidate)

    def test_reject_extra_dimension(self):
        candidate = module.unrank(0)
        candidate['surprise'] = 0
        with self.assertRaises(ValueError):
            module.rank(candidate)

    def test_reject_invalid_digit(self):
        for value in (-1, 8, True, 0.0, '2'):
            candidate = module.unrank(0)
            candidate['role'] = value
            with self.subTest(role=value), self.assertRaises(ValueError):
                module.rank(candidate)

    def test_index_description_not_execution(self):
        point = module.unrank(module.capacity()//3)
        self.assertEqual(set(point), {name for name, _ in module.DIMENSIONS})


if __name__ == '__main__':
    unittest.main()
