DATE_FORMAT = "%Y%m%d"
DEFAULT_START_DATE = 20010321
DATA_BASE_PATH = "tickers_data"

_TSE_URL_GROUP_LIST = "http://old.tsetmc.com/tsev2/res/loader.aspx?t=g&_555"

_TSE_INS_FIELD = [
    "id",
    "code",
    "enSymbol",
    "enName",
    "enNameCode",
    "symbol",
    "name",
    "coCode",
    "date",
    "flow",
    "coName",
    "type",
    "board",
    "market",
    "d",
    "group",
    "subgroup",
    "cat",
]

_TSE_FIELD = [
    "ID",
    "Date",
    "AdjClose",
    "Close",
    "Count",
    "Volume",
    "Value",
    "Low",
    "High",
    "Yesterday",
    "Open",
]

_TSE_FIELD_ORDER = [
    "Date",
    "Open",
    "High",
    "Low",
    "Close",
    "Count",
    "Volume",
    "Value",
    "AdjClose",
    "Yesterday",
]
