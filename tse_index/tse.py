import requests
import ast
import re
import pandas as pd
from io import StringIO
import datetime
from pathlib import Path
from tse_index import settings
from tse_index.tse_scrapper import TSEClient
from tse_index._utils import (
    RemoteDataError,
    SymbolWarning,
    _init_session,
    _sanitize_dates,
)


class reader:
    """
    Tehran stock exchange daily data

    Returns DataFrame of historical data from the Tehran Stock Exchange
    open data service, over date range, start to end.

    Parameters
    ----------
    symbols : {int, str, List[str], List[int]}
        The symbols can be persian symbol code or instrument id.
        This argument can be obtained from tsetmc.com site.
    start : string, int, date, datetime, Timestamp
        Starting date. Parses many different kind of date
        default value is 5 years ago
        representations (e.g., 'JAN-01-2010', '1/1/10', 'Jan, 1, 1980')
    end : string, int, date, datetime, Timestamp
        Ending date
    retry_count : int, default 3
        Number of times to retry query request.
    pause : float, default 0.1
        Time, in seconds, of the pause between retries.
    session : Session, default None
        requests.sessions.Session instance to be used.
    adjust_price : bool, default False
        If True, adjusts all prices in hist_data ('Open', 'High', 'Low',
        'Close') based on 'Adj Close' and 'Yesterday' price.
    interval: string, d, w, m for daily, weekly, monthly
    """

    def __init__(
        self, retry_count=3, pause=0.1, session=None, chunksize=50,
    ):

        self.symbols = None

        # Ladder up the wait time between subsequent requests to improve
        # probability of a successful retry
        self.pause_multiplier = 2.5
        self.chunksize = max(1, chunksize)

        self.start = None
        self.end = None

        self.adjust_price = False
        self.interval = "d"

        if self.interval not in ["d", "w", "m"]:
            raise ValueError("Invalid interval: valid values are 'd', 'w' and 'm'.")

        self.client = TSEClient
        self.lastPossibleDeven = None
        self.instrumentList = None
        self._history = {}
        self._groups = {}

    def update(self):
        deven = self.client.LastPossibleDeven()
        if self.lastPossibleDeven != deven:
            # TODO update instrument history
            lastDate = deven.split(";")
            if len(lastDate) < 2:
                raise IOError("Last possible date request returned no data")
        return True

    def search(self, search, market=None):
        if market not in ["index", "normal", None]:
            raise ValueError(
                "Invalid instrument market: valid values are 'index' and 'normal'."
            )
        if market == "index":
            market = "ID"
        elif market == "normal":
            market = "NO"
        instruments = self.instruments()
        if instruments is None:
            return None
        search = re.sub(r"\s{2,}", " ", search.strip()).replace(" ", ".*")
        find = instruments[
            instruments.symbol.str.contains(search)
            & ((market is None) | (instruments.market == market))
        ]
        return find

    def indices(self):
        instruments = self.instruments()
        indices = instruments[lambda i: i.type == "I"]
        indices = indices.drop_duplicates("symbol").sort_index().reset_index(drop=True)
        return indices

    def instruments(self, group=None):
        lastDate = (
            0
            if self.instrumentList is None
            else max(self.instrumentList.get("date", [0]))
        )
        today = int(datetime.date.today().strftime("%Y%m%d"))
        if self.instrumentList is None or today > lastDate:
            # update instrument list
            instrumentList = self._replace_arabic(self.client.Instrument(lastDate))
            data = StringIO(instrumentList)
            instruments = pd.read_csv(
                data,
                lineterminator=";",
                sep=",",
                names=settings._TSE_INS_FIELD,
            )
            instruments['group'] = instruments['group'].str.strip()
            # market = ID/NO  Index Market/Normal Market
            # type = I/A  Indice/Normal
            self.instrumentList = (
                pd.concat([instruments, self.instrumentList])
                .drop_duplicates(subset=["id"])
                .sort_values(["symbol", "date"], ascending=[True, False])
                .reset_index(drop=True)
            )
        if group is None or self.instrumentList is None:
            ins = self.instrumentList
        else:
            groups = self.groups()
            group_code = None
            if group in groups.values():
                group_code = list(groups.keys())[list(groups.values()).index(group)]
            ins = self.instrumentList[self.instrumentList.group == group_code]
        return ins

    def to_csv(
        self,
        base_path: str = settings.DATA_BASE_PATH,
    ):
        """store history of instruments into disk"""
        if self._history is not None and len(self._history) > 0:
            Path(base_path).mkdir(parents=True, exist_ok=True)
            for symbol in self._history:
                self._history[symbol].to_csv(
                    f"{base_path}/{symbol}.csv",
                    index=False
                )

    def history(
        self,
        symbols=None,
        start=None,
        end=None,
        retry_count=3,
        pause=0.1,
        adjust_price=False,
        chunksize=50,
        interval="d",
    ):
        """read one data from specified URL"""
        self.symbols = symbols

        # Ladder up the wait time between subsequent requests to improve
        # probability of a successful retry
        self.pause_multiplier = 2.5
        self.chunksize = max(1, chunksize)

        start, end = _sanitize_dates(start or settings.DEFAULT_START_DATE, end)
        self.start = start
        self.end = end

        self.adjust_price = adjust_price
        self.interval = interval

        if self.interval not in ["d", "w", "m"]:
            raise ValueError("Invalid interval: valid values are 'd', 'w' and 'm'.")

        instruments = self.instruments()
        if instruments is None:
            return None

        if type(self.symbols) is str:
            symbols_list = [self.symbols]
        else:
            symbols_list = self.symbols

        today = int(datetime.date.today().strftime("%Y%m%d"))
        if self.lastPossibleDeven is None or today > max(
            map(int, self.lastPossibleDeven.split(";"))
        ):
            self.lastPossibleDeven = self.client.LastPossibleDeven()
        lastDate = self.lastPossibleDeven.split(";")
        if len(lastDate) < 2:
            raise IOError("Last possible date request returned no data")
        normalLastPossibleDeven = int(lastDate[0])
        indexLastPossibleDeven = int(lastDate[1])

        insCodes = []
        insSymbols = []
        insCodesList = []
        for symbol in symbols_list:
            deven = 0
            ins = instruments[instruments.symbol == symbol]
            if len(ins) == 0:
                continue
            if (
                symbol in self._history
                and self._history.get(symbol) is not None
                and len(self._history.get(symbol)) > 0
            ):
                deven = max(self._history.get(symbol).Date)

            if (((ins.market == "NO").any() and
               deven < normalLastPossibleDeven) or
               ((ins.market == "ID").any() and
               deven < indexLastPossibleDeven)):
                # update history
                insCodes += list(ins["id"])
                insSymbols += list(ins["symbol"])
                insCodesList += list(
                    ins.apply(
                        lambda x: f"{x.id},{deven},"
                        + ("1" if x.market == "ID" else "0"),
                        axis=1,
                    )
                )

        chunk = 0
        while chunk < len(insCodesList):
            resp = self.client.DecompressAndGetInsturmentClosingPrice(
                ";".join(insCodesList[chunk : chunk + self.chunksize])
            )
            historyStr = resp.split("@")
            for i, v in enumerate(historyStr):
                data = StringIO(v)
                ohlc = pd.read_csv(
                    data, lineterminator=";", sep=",", names=settings._TSE_FIELD
                )
                ohlc = ohlc[ohlc["Count"] != 0].reset_index(drop=True)[
                    settings._TSE_FIELD_ORDER
                ]
                if insSymbols[chunk + i] in self._history:
                    self._history[insSymbols[chunk + i]] = (
                        pd.concat(
                            [self._history[insSymbols[chunk + i]], ohlc],
                            ignore_index=True, sort=False
                        )
                        .sort_values("Date")
                        .reset_index(drop=True)
                    )
                else:
                    self._history[insSymbols[chunk + i]] = ohlc
            chunk += self.chunksize

        if type(self.symbols) is str:
            return self._adjust({self.symbols: self._history.get(self.symbols, None)})[
                self.symbols
            ]
        else:
            return self._adjust({s: self._history.get(s, None) for s in symbols_list})

    def _adjust(self, idf):
        instruments = self.instruments()
        df = idf
        if type(idf) is pd.DataFrame:
            df = {0: idf}

        for i in df:
            if df[i] is None:
                continue
            ins = instruments[instruments.symbol == i]
            df[i] = df[i].copy()
            if self.adjust_price and not ins.empty and ins.iloc[0].market == "NO":
                df[i] = self._adjust_price(df[i])

            if "Date" in df[i]:
                df[i]["Date"] = pd.to_datetime(df[i]["Date"], format="%Y%m%d")
                df[i] = df[i].set_index("Date")
                df[i] = df[i][self.start : self.end]
                if self.interval == "w":
                    ohlc = df[i]["Close"].resample("w-sat").ohlc()
                    ohlc["Volumne"] = df[i]["Volume"].resample("w-sat").sum()
                    ohlc["Count"] = df[i]["Count"].resample("w-sat").sum()
                    ohlc["Value"] = df[i]["Value"].resample("w-sat").sum()
                    df[i] = ohlc
                elif self.interval == "m":
                    ohlc = df[i]["Close"].resample("m").ohlc()
                    ohlc["Volume"] = df[i]["Volume"].resample("m").sum()
                    ohlc["Count"] = df[i]["Count"].resample("m").sum()
                    ohlc["Value"] = df[i]["Value"].resample("m").sum()
                    df[i] = ohlc

        if type(idf) is pd.DataFrame:
            return df[0]
        else:
            return df

    def _adjust_price(self, hist_data, columns=None):
        """
        Return modifed DataFrame with adjusted prices based on
        'Adj Close' and 'Yesterday'  price
        """
        """
        Adjust historical records of stock

        There is a capital increase/profit sharing,
        if today "Final Close Price" is not equal to next day
        "Yesterday Final Close Price" by using this ratio,
        performance adjustment of stocks is achieved

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame with historical records.
        columns: list
            List of columns to be modifies

        Returns
        -------
        pd.DataFrame
            DataFrame with adjusted historical records.

        Notes
        -----
        DataFrame can not be empty or else it makes runtime error
        Type of DataFrame must be RangeIndex to make proper range of records
        that need to be modified

        diff: list
            list of indexs of the day after capital increase/profit sharing
        ratio_list: List
            List of ratios to adjust historical data of stock
        ratio: Float
            ratio = df.loc[i].adjClose / df.loc[i+1].yesterday

        Description
        -----------
        #Note: adjustment does not include Tenth and twentieth days
        df.index = range(0,101,1)
        #step is 1
        step = df.index.step
        diff = [10,20]
        ratio_list = [0.5, 0.8]
        df.loc[0:10-step, [open,...]] * ratio[0]
        df.loc[10:20-step, [open,...]] * ratio[1]
        """
        if hist_data is None or hist_data.empty:
            return hist_data
        if not isinstance(hist_data.index, pd.core.indexes.range.RangeIndex):
            raise TypeError(
                "Error in adjusting price; index type must be RangeIndex"
            ) from None
        if columns is None:
            columns = ["Open", "High", "Low", "Close", "AdjClose", "Yesterday"]

        data = hist_data.copy()
        step = data.index.step
        diff = list(data.index[data.shift(1).AdjClose != data.Yesterday])
        if len(diff) > 0:
            diff.pop(0)
        ratio = 1
        ratio_list = []
        for i in diff[::-1]:
            ratio *= data.loc[i, "Yesterday"] / data.shift(1).loc[i, "AdjClose"]
            ratio_list.insert(0, ratio)
        for i, k in enumerate(diff):
            if i == 0:
                start = data.index.start
            else:
                start = diff[i - 1]
            end = diff[i] - step
            data.loc[start:end, columns] = round(
                data.loc[start:end, columns] * ratio_list[i]
            )

        return data

    def group_name(self, symbol):
        instruments = self.instruments()
        ins = instruments[instruments.symbol == symbol]
        group_name = None
        if len(ins) > 0:
            group_code = ins.iloc[0].get("group")
            group_name = self.groups().get(group_code, None)
        return group_name

    def groups(self):
        if not self._groups:
            self._groups = self._fetch_groups()
        return self._groups

    def _fetch_groups(self):
        resp = requests.get(settings._TSE_URL_GROUP_LIST)
        groups = {}
        if resp.status_code == 200:
            group_list = self._replace_arabic(resp.text)
            match = re.search(r'var Sectors=\[\[(.*?)\]\]', group_list, re.DOTALL)
            if match:
                sectors_data = match.group(1)
                # Safely parse the string into a list using ast.literal_eval
                try:
                    sectors_list = ast.literal_eval(f'[[{sectors_data}]]')
                except (ValueError, SyntaxError):
                    raise ValueError(
                        "Error parsing Groups data."
                    )
                    sectors_list = []
                # Step 3: Convert the list of lists into a dictionary
                groups = {sector[0]: sector[1] for sector in sectors_list}

        return groups

    def _replace_arabic(self, string: str):
        return string.replace("ك", "ک").replace("ي", "ی")
