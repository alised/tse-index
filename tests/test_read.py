import unittest
import tse_index as tse


class TestFetchSymbolHistory(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_fetch_instruments(self) -> None:
        symbol = "نوری"
        expected_index = 19040514831923530
        index = tse.reader()
        instruments = index.instruments()
        ins = instruments[instruments.symbol == symbol]
        if len(ins) > 0:
            index = ins.iloc[0].get("id").item()
        self.assertEqual(index, expected_index)

    def test_search(self) -> None:
        symbol = "شاخص کل6"
        index = tse.reader()
        instruments = index.search(symbol, market="index")
        self.assertEqual(len(instruments), 2)

    def test_fetch_history(self) -> None:
        symbol = "شاخص کل6"
        index = tse.reader()
        ohlc_d = index.history(symbol, start=1399, end=1400, interval="d")
        ohlc_w = index.history(symbol, start=1399, end=1400, interval="w")
        ohlc_m = index.history(symbol, start=2020, end=2021, interval="m")
        self.assertEqual(len(ohlc_d), 243)
        self.assertEqual(len(ohlc_w), 52)
        self.assertEqual(len(ohlc_m), 12)
