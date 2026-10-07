import logging
import unittest

from single_deny_filter import SingleDenyFilter


def _record(name: str) -> logging.LogRecord:
    return logging.LogRecord(
        name=name,
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="x",
        args=(),
        exc_info=None,
    )


class TestSingleDenyFilter(unittest.TestCase):
    def test_rejects_exact_match(self):
        f = SingleDenyFilter("urllib3")
        self.assertFalse(f.filter(_record("urllib3")))

    def test_rejects_child_logger(self):
        f = SingleDenyFilter("urllib3")
        self.assertFalse(f.filter(_record("urllib3.connection")))

    def test_allows_unrelated_logger(self):
        f = SingleDenyFilter("urllib3")
        self.assertTrue(f.filter(_record("requests")))

    def test_substring_match_siblings(self):
        # Substring matching is the documented behaviour, not a bug.
        f = SingleDenyFilter("urllib3")
        self.assertFalse(f.filter(_record("my_urllib3_helper")))

    def test_rejects_when_name_is_prefix_of_logger(self):
        f = SingleDenyFilter("lib")
        self.assertFalse(f.filter(_record("library.workers")))

    def test_case_sensitive(self):
        # ``in`` is case-sensitive; we do not normalize. This is the simplest
        # rule to reason about and matches how loggers are named in practice.
        f = SingleDenyFilter("urllib3")
        self.assertTrue(f.filter(_record("Urllib3")))

    def test_empty_string_name_rejected(self):
        with self.assertRaises(ValueError):
            SingleDenyFilter("")

    def test_non_string_name_rejected(self):
        with self.assertRaises(TypeError):
            SingleDenyFilter(123)  # type: ignore[arg-type]

    def test_integrated_with_handler(self):
        # Proves the filter actually suppresses records reaching a handler,
        # which is the intended integration point.
        handler = logging.StreamHandler()
        handler.addFilter(SingleDenyFilter("noisy"))
        logger = logging.getLogger("test.integrated")
        logger.handlers = [handler]
        logger.setLevel(logging.DEBUG)
        logger.propagate = False

        emitted = []
        handler.emit = emitted.append  # type: ignore[assignment]

        logger.info("kept")
        logger = logging.getLogger("test.integrated.noisy")
        logger.handlers = [handler]
        logger.propagate = False
        logger.info("dropped")
        logger = logging.getLogger("test.integrated.clean")
        logger.handlers = [handler]
        logger.propagate = False
        logger.info("visible")

        self.assertEqual(len(emitted), 2)
        self.assertEqual(emitted[0].getMessage(), "kept")
        self.assertEqual(emitted[1].getMessage(), "visible")


if __name__ == "__main__":
    unittest.main()
