import zlib
import struct
import base64
import requests
import bs4


class TSEClient:
    def DecompressAndGetInsturmentClosingPrice(insCodesList: str):
        """
        Fetch historical price of stocks and indices

        Parameters
        ----------
        insCodesList : str
            List of instument ids
            InstrumentID,LastStoredRecordDate,0/1;...
            0 = stock
            1 = index
            EX: "2318736941376687,20210901,0;32097828799138957,20210901,1"

        Returns
        -------
        data : str
            Historical price of stocks
        columns:
            long InsCode
            int DEven
            decimal PClosing
            decimal PDrCotVal
            decimal ZTotTran
            decimal QTotTran5J
            decimal QTotCap
            decimal PriceMin
            decimal PriceMax
            decimal PriceYesterday
            decimal PriceFirst

        """
        if not insCodesList:
            return ""

        compressor = zlib.compressobj(wbits=(16 + zlib.MAX_WBITS))
        compressed = base64.b64encode(
            struct.pack("<L", len(insCodesList))
            + compressor.compress(bytes(insCodesList, "ascii"))
            + compressor.flush()
        )

        url = "http://service.tsetmc.com/WebService/TseClient.asmx"

        headers = {
            "User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0; MS Web Services Client Protocol 2.0.50727.9151)",
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": '"http://tsetmc.com/DecompressAndGetInsturmentClosingPrice"',
            "Connection": "close",
        }

        body = '<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><soap:Body><DecompressAndGetInsturmentClosingPrice xmlns="http://tsetmc.com/"><insCodes>{}</insCodes></DecompressAndGetInsturmentClosingPrice></soap:Body></soap:Envelope>'

        response = requests.post(
            url, data=body.format(compressed.decode("ascii")), headers=headers
        )
        data = ""
        if response.status_code == 200:
            soup = bs4.BeautifulSoup(response.text, "xml")
            tag = soup.find("DecompressAndGetInsturmentClosingPriceResult")
            if tag is not None:
                data = tag.text
        return data

    def LastPossibleDeven():
        url = "http://service.tsetmc.com/WebService/TseClient.asmx"

        headers = {
            "User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0; MS Web Services Client Protocol 2.0.50727.9151)",
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": '"http://tsetmc.com/LastPossibleDeven"',
            "Expect": "100-continue",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "close",
        }

        body = '<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><soap:Body><LastPossibleDeven xmlns="http://tsetmc.com/" /></soap:Body></soap:Envelope>'

        response = requests.post(url, data=body, headers=headers)
        if response.status_code == 200:
            soup = bs4.BeautifulSoup(response.text, "xml")
            tag = soup.find("LastPossibleDevenResult")
            data = ""
            if tag is not None:
                data = tag.text
        return data

    def InstrumentAndShare(InsLastDate: str = "0", ShareLastID: int = 0):
        """
        

        Parameters
        ----------
        InsLastDate : str, optional
            DESCRIPTION. The default is "0".
        ShareLastID : int, optional
            DESCRIPTION. The default is 0.

        Returns
        -------
        data : TYPE
            DESCRIPTION.

        ShareInfo Columns:
            long Idn
            long InsCode
            int DEven
            decimal NumberOfShareNew
            decimal NumberOfShareOld
            
        """
        url = "http://service.tsetmc.com/WebService/TseClient.asmx"

        headers = {
            "User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0; MS Web Services Client Protocol 2.0.50727.9151)",
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": '"http://tsetmc.com/InstrumentAndShare"',
            "Expect": "100-continue",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "close",
        }

        body = '<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><soap:Body><InstrumentAndShare xmlns="http://tsetmc.com/"><DEven>{}</DEven><LastID>{}</LastID></InstrumentAndShare></soap:Body></soap:Envelope>'

        response = requests.post(
            url, data=body.format(InsLastDate, ShareLastID), headers=headers
        )
        if response.status_code == 200:
            soup = bs4.BeautifulSoup(response.text, "xml")
            tag = soup.find("InstrumentAndShareResult")
            data = tag.text if tag else ""
        return data

    def Instrument(InsLastDate: str = "0"):
        """
        fetch list of tse instruments

        Parameters
        ----------
        InsLastDate : str, optional
            max value of DEven column. date format is "YYYYMMDD".
            The default is "0".

        Returns
        -------
        data : str
            list of instrumetns that seperated with ";".
        columns:
            long InsCode
            string InstrumentID
            string LatinSymbol
            string LatinName
            string CompanyCode
            string Symbol
            string Name
            string CIsin
            int DEven
            byte Flow
            string LSoc30
            string CGdSVal
            string CGrValCot
            string YMarNSC
            string CComVal
            string CSecVal
            string CSoSecVal
            string YVal

        """
        url = "http://service.tsetmc.com/WebService/TseClient.asmx"

        headers = {
            "User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0; MS Web Services Client Protocol 2.0.50727.9151)",
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": '"http://tsetmc.com/Instrument"',
            "Expect": "100-continue",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "close",
        }

        body = '<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><soap:Body><Instrument xmlns="http://tsetmc.com/"><DEven>{}</DEven></Instrument></soap:Body></soap:Envelope>'

        response = requests.post(url, data=body.format(InsLastDate), headers=headers)
        if response.status_code == 200:
            soup = bs4.BeautifulSoup(response.text, "xml")
            tag = soup.find("InstrumentResult")
            data = tag.text if tag else ""
        return data
