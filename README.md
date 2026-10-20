# Single Deny Filter

A `logging.Filter` that rejects every record whose logger name contains a
configured substring — a targeted mute for one noisy library.

```python
import logging
from single_deny_filter import SingleDenyFilter

handler = logging.StreamHandler()
handler.addFilter(SingleDenyFilter("urllib3"))

root = logging.getLogger()
root.addHandler(handler)
root.setLevel(logging.INFO)
```

Records emitted by `urllib3`, `urllib3.connection`, or any logger whose name
contains `urllib3` never reach the handler. Everything else passes through.

## Why this exists

The standard library's `logging.Filter` does hierarchical prefix matching: a
filter with `name="urllib3"` matches `urllib3` and its children by dotted
prefix, but *not* `my_urllib3_things`. That is the right default for
structuring log channels, but it is clumsy when the goal is simply "shut up
about this one library".

This filter uses a plain substring (`in`) test instead. The trade-off is
deliberate and documented: `SingleDenyFilter("url")` will also silence
`my_url_helper`, which a prefix filter would not. If you need precise
dotted-prefix behaviour, use `logging.Filter` directly — that is what it is
for. This class exists for the case where a substring is what you actually
want.

## Edge to know about

The match is a raw substring test, case-sensitive. Pick a name specific
enough not to collide with unrelated loggers. `"urllib3"` is fine;
`"http"` almost certainly is not.

Empty and non-string names raise `ValueError` and `TypeError` respectively
at construction.

## Performance

The window keeps a bounded buffer, so `push` is constant time and memory does not
grow with the length of the stream. `peak` and `trough` are linear in the window
size, which is the trade that keeps `push` cheap.

