from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SITE_ROOT.parent

AUTHOR = "django-benchmark"
SITENAME = "Django Benchmark"
SITEURL = ""

PATH = str(SITE_ROOT / "content")
OUTPUT_PATH = str(SITE_ROOT / "output")
THEME = str(SITE_ROOT / "theme")
TIMEZONE = "UTC"
DEFAULT_LANG = "en"

ARTICLE_PATHS = []
PAGE_PATHS = []
DIRECT_TEMPLATES = ["index"]

FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
AUTHORS_SAVE_AS = ""
CATEGORIES_SAVE_AS = ""
TAGS_SAVE_AS = ""
ARCHIVES_SAVE_AS = ""

PLUGIN_PATHS = [str(SITE_ROOT / "plugins")]
PLUGINS = ["results"]

BENCHMARK_RESULTS_DIR = REPO_ROOT / "results"
SAMPLE_RESULTS_DIR = SITE_ROOT / "data"

DELETE_OUTPUT_DIRECTORY = True
