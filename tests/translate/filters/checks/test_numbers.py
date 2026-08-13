"""Tests for the numbers check, including language specific digits."""

from tests.translate.filters.checks.helpers import fails, passes
from translate.filters import checks


def test_numbers() -> None:
    """Test numbers."""
    stdchecker = checks.StandardChecker()
    assert passes(
        stdchecker.numbers,
        "Netscape 4 was not as good as Netscape 7.",
        "Netscape 4 was nie so goed soos Netscape 7 nie.",
    )
    # Check for correct detection of degree.  Also check that we aren't getting confused with 1 and 2 byte UTF-8 characters
    assert fails(stdchecker.numbers, "180° turn", "180 turn")
    assert passes(stdchecker.numbers, "180° turn", "180° turn")
    assert fails(stdchecker.numbers, "180° turn", "360 turn")
    assert fails(stdchecker.numbers, "180° turn", "360° turn")
    assert passes(stdchecker.numbers, "180~ turn", "180 turn")
    assert passes(stdchecker.numbers, "180¶ turn", "180 turn")
    # Numbers with multiple decimal points
    assert passes(stdchecker.numbers, "12.34.56", "12.34.56")
    assert fails(stdchecker.numbers, "12.34.56", "98.76.54")
    # Currency
    # FIXME we should probably be able to handle currency checking with locale inteligence
    assert passes(stdchecker.numbers, "R57.60", "R57.60")
    # FIXME - again locale intelligence should allow us to use other decimal seperators
    assert fails(stdchecker.numbers, "R57.60", "R57,60")
    assert fails(stdchecker.numbers, "1,000.00", "1 000,00")
    # You should be able to reorder numbers
    assert passes(
        stdchecker.numbers,
        "40-bit RC2 encryption with RSA and an MD5",
        "Umbhalo ocashile i-RC2 onamabhithi angu-40 one-RSA ne-MD5",
    )
    # Don't fail the numbers check if the entry is a dialogsize entry
    mozillachecker = checks.MozillaChecker()
    assert passes(mozillachecker.numbers, "width: 12em;", "width: 20em;")


def test_persian_numbers() -> None:
    """Test non latin numbers for Persian (RTL)."""
    fa_checker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="fa"))
    assert passes(fa_checker.numbers, "&حرکت آهسته (۰.۵×)", "&Slow Motion (0.5×)")
    assert passes(fa_checker.numbers, "&حرکت آهسته (0.5×)", "&Slow Motion (0.5×)")
    assert passes(
        fa_checker.numbers, '<img alt="١۰" width="10" />', '<img alt="10" width="10" />'
    )
    assert passes(
        fa_checker.numbers, '<img alt="10" width="10" />', '<img alt="10" width="10" />'
    )
    assert passes(
        fa_checker.numbers, "دسترسی مسدود شده است (۴۰۳)", "Access denied (403)"
    )
    assert passes(fa_checker.numbers, "کتاب موزیلا، ۱۵:۱", "The Book of Mozilla, 15:1")
    assert passes(
        fa_checker.numbers,
        "<p>نشانی درخواست مشخصا(به عنوان مثال<q>mozilla.org:80</q>برای درگاه ۸۰ بر روی  mozilla.org)  ازدرگاهی استفاده می کندکه در حالت عادی به عنوان کاربردی <em>به غیر</em> از وبگردی استفاده می شود.مرورگر برای حفاظت و امنیت شما این درخواست را لغوکرد.</p>",
        "<p>The requested address specified a port (e.g. <q>mozilla.org:80</q> for port 80 on mozilla.org) normally used for purposes <em>other</em> than Web browsing. The browser has canceled the request for your protection and security.</p>",
    )
    assert passes(
        fa_checker.numbers,
        "دستور پردازشی <?%1$S?> دیگر تأثیری خارج از prolog ندارد (برای اطلاعات بیشتر، اشکال ۳۶۰۱۱۹ را مشاهده کنید).",
        "<?%1$S?> processing instruction does not have any effect outside the prolog anymore (see bug 360119).",
    )
    assert passes(
        fa_checker.numbers,
        "encoding حروف این سند بسیار دیرتر از آنکه مورد اثر واقع شود شناسایی شد.encoding فایل برای شناسایی باید به ۱۰۲۴ بایت اول فایل برای شناسایی منتقل شود.",
        "The character encoding declaration of document was found too late for it to take effect. The encoding declaration needs to be moved to be within the first 1024 bytes of the file.",
    )
    assert passes(
        fa_checker.numbers,
        "ویدئو یا صدا در این صفحه نرم‌افزار DRMای احتیاج دارد که نسخه ۶۴ بیتی از %1$S از آن پیشتیبانی نمی‌کند. %2$S",
        "The audio or video on this page requires DRM software that this 64-bit build of %1$S does not support. %2$S",
    )
    assert passes(
        fa_checker.numbers,
        "شما اندازه خیلی بزرگی برای حداقل اندازه قلم انتخاب کرده‌اید (بیش از ۲۴ پیکسل). این ممکن است باعث شود پیکربندی صفحاتی مانند این سخت یا غیرممکن بشود.",
        "You have selected a very large minimum font size (more than 24 pixels). This may make it difficult or impossible to use some important configuration pages like this one.",
    )


def test_bengali_numbers() -> None:
    """Test non latin numbers for Bengali (LTR)."""
    bn_checker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="bn"))
    assert passes(bn_checker.numbers, "উচ্চ গতি (১.৫ গুন)", "&High Speed (1.5×)")
    assert passes(bn_checker.numbers, "উচ্চ গতি (0.5 গুন)", "&Slow Motion (0.5×)")
    assert passes(
        bn_checker.numbers, '<img alt="১০" width="10" />', '<img alt="10" width="10" />'
    )
    assert passes(
        bn_checker.numbers, '<img alt="10" width="10" />', '<img alt="10" width="10" />'
    )
    assert passes(
        bn_checker.numbers,
        "<strong>Mozilla-র বই</strong>১৫: ১ পাতা থেকে সংগৃহীত",
        "from <strong>The Book of Mozilla,</strong> 15:1",
    )
    assert passes(
        bn_checker.numbers,
        "ট্যাগ গুলি ২৫ টি অক্ষরের মধ্যে সীমাবদ্ধ",
        "Tags are limited to 25 characters",
    )
    assert passes(
        bn_checker.numbers,
        "পাসওয়ার্ড অন্তত ৮-টি অক্ষর বিশিষ্ট হওয়া আবশ্যক এবং এই ক্ষেত্রে ব্যবহারকারী অ্যাকাউন্টের নাম অথবা পুনরুদ্ধারের (key) পাসওয়ার্ড রূপে ব্যবহার করা যাবে না।",
        "Your password must be at least 8 characters long.  It cannot be the same as either your user name or your Recovery Key.",
    )


def test_arabic_numbers() -> None:
    """Test non latin numbers for Arabic."""
    ar_checker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="ar"))
    assert passes(
        ar_checker.numbers,
        "أقصى طول للوسم ٢٥ حرفًا",
        "Tags are limited to 25 characters",
    )
    assert passes(ar_checker.numbers, "حركة ب&طيئة (٠٫٥×)", "&Slow Motion (0.5×)")
    assert passes(ar_checker.numbers, "متصفح &٣٦٠ الآمن", "&360 Secure Browser")
    assert passes(
        ar_checker.numbers,
        "من <strong>كتاب موزيلا،</strong> ١٥‏:١",
        "from <strong>The Book of Mozilla,</strong> 15:1",
    )
    assert passes(ar_checker.numbers, "١٧٥٪", "175%")


def test_assamese_numbers() -> None:
    """Test non latin numbers for Assamese."""
    as_checker = checks.StandardChecker(checks.CheckerConfig(targetlanguage="as"))
    assert passes(
        as_checker.numbers,
        "প্ৰতি ৩ ছেকেণ্ডত স্বচালিতভাৱে সতেজ কৰক",
        "Autorefresh every 3 seconds",
    )
    assert passes(
        as_checker.numbers,
        "পৃষ্ঠা পুনৰ ল'ড কৰা হৈছিল, কাৰণ HTML দস্তাবেজৰ আখৰ এনক'ডিং যোষণা ফাইলৰ প্ৰথম ১০২৪ বাইট পূৰ্বস্কেন কৰোতে পোৱা নগল। এনক'ডিং ঘোষণাক ফাইলৰ প্ৰথম ১০২৪ বাইটৰ মাজত স্থানান্তৰ কৰিব লাগিব।",
        "The page was reloaded, because the character encoding declaration of the HTML document was not found when prescanning the first 1024 bytes of the file. The encoding declaration needs to be moved to be within the first 1024 bytes of the file.",
    )
    assert passes(as_checker.numbers, "সংস্কৰণ ৩", "Version 3")
    assert passes(as_checker.numbers, "১৭৫%", "175%")
