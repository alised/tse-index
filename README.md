<div dir="rtl">

# دریافت دیتای شاخص کل و صنایع بورس تهران

به راحتی دیتای بروز شاخص ها و سهام بازار بورس و اوراق بهادار تهران را در پایتون دریافت کنید.
این ماژول قادر است دیتای تمامی سهام را بصورت بخش‌های ۵۰ تایی (پیش فرض) با سرعت بالایی دریافت کند و در صورت نیاز به بروزرسانی تنها دیتای روزهای جدید را دریافت می کند

## امکانات
- دریافت تاریخچه قیمتی نمادها و شاخص ها
- دریافت لیست نمادها
- دریافت لیست شاخص‌ها
- جستجو در نام نمادها
- تجمیع خودکار دیتای قدیمی نمادها
- تعدیل عملکردی سابقه قیمتی سهام
  
## نصب
<div dir="ltr">

```bash
pip install tse-index
```

</div>

## نصب آخرین نسخه در حال توسعه
<div dir="ltr">

``` shell
python -m pip install git+https://github.com/alised/tse-index.git
```

</div>

## نحوه استفاده

### دریافت سابقه شاخص یا نماد
<div dir="ltr">

```python
import tse_index as tse
index = tse.reader()
index.history("شاخص کل6", start=1390, end=14000730, adjust_price=False, interval="d")

                 Open       High  ...   AdjClose     Yesterday
Date                              ...                         
2011-03-26    23295.7    23756.6  ...    23756.3  2.329490e+04
2011-03-27    23853.5    24213.2  ...    24199.8  2.375630e+04
2011-03-28    24226.6    24287.8  ...    24287.8  2.419980e+04
2011-03-29    24351.2    24495.9  ...    24486.6  2.428780e+04
2011-03-30    24495.5    24605.0  ...    24486.0  2.448660e+04
              ...        ...  ...        ...           ...
2021-10-12  1454820.0  1454820.0  ...  1418721.1  5.700514e+10
2021-10-13  1417770.0  1417770.0  ...  1397446.4  5.615032e+10
2021-10-16  1406010.0  1437440.0  ...  1437445.4  5.775750e+10
2021-10-17  1444280.0  1445100.0  ...  1436062.0  5.770277e+10
2021-10-18  1435350.0  1436960.0  ...  1436964.1  5.756671e+10
```

</div>

جهت دریافت تاریخچه شاخص کافیست نام آن را وارد نمایید

تاریخ شروع و پایان اختیاری است و می‌تواند شمسی یا میلادی باشد. تاریخ شمسی حتما باید بصورت عددی وارد شود. در صورتی که تنها سال وارد شود یک فروردین آن سال اعمال میشود.

اینترول میتواند d، w و یا m باشد که به ترتیب دیتای روزانه، هفتگی و ماهانه نماد مورد نظر را بر می گرداند. اولین روز هفته شنبه در نظر گرفته شده است. اما در مورد دیتای ماهانه مبنا، ماه‌های میلادی می‌باشد.

برای دریافت سابقه تعدیل شده کافیست آرگومان adjust_price=True را اضافه کنید. این تعدیل از نوع عملکردی است و افزایش سرمایه و تقسیم سود را شامل می شود.
  توجه داشته باشید که در مورد شاخص تعدیل قیمت معنا ندارد و در صورتی که از آرگومان مربوطه استفاده کنید نادیده گرفته می‌شود.

### جستجو در لیست شاخص‌ها و نمادها
<div dir="ltr">

```python
import tse_index as tse
index = tse.reader()
index.search("دارو", "index").symbol

32      43-مواد دارویی6
1039      دارو فرابورس6
```

</div>
در صورتی که نام کامل شاخص یا نمادی را نمی‌دانید کافیست تا آن را جستجو کنید.
برای یافتن نام نمادها بجای 'index' از عبارت 'normal' استفاده کنید.

### دریافت لیست شاخص‌ها
<div dir="ltr">

```python
import tse_index as tse
index = tse.reader()
index.indices().symbol


0               01-زراعت6
1            10-ذغال سنگ6
2           13-کانه فلزی6
3          14-سایر معادن6
4        15-غذا-آشامیدنی6
       ...
106                  چوب6
107     کانی غیرفلزی فرا6
108        کانی فلزی فرا6
109    کل هم وزن فرابورس6
110       کل هم وزن پایه6
```

</div>

### دریافت لیست کامل نمادها
<div dir="ltr">

```python
import tse_index as tse
index = tse.reader()
index.instruments().symbol

0        اعتضاد غدیر
1         کاغذ مراغه
2          (1)کشاورز
3           (12)نوین
4          (2)کشاورز
    ...
2933           گپارس
2934           گکوثر
2935            گکیش
2936           گکیشح
2937           یاقوت
```

</div>

## مشارکت در توسعه برنامه
  اگر مشکلی در برنامه مشاهده می کنید از سربرگ Issues موضوع را با تگ باگ و در صورتی که پیشنهادی دارید با تگ بهبود مطرح نمایید.

  در صورت تمایل به مشارکت در توسعه پروژه [آموزش مشارکت](https://github.com/firstcontributions/first-contributions/blob/master/translations/README.fa.md) را مطالعه فرمایید.

</div>
