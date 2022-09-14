from __future__ import annotations

from .delete import httpbin_method_delete_examples
from .get import httpbin_method_get_examples
from .patch import httpbin_method_patch_examples
from .post import httpbin_method_post_examples
from .put import httpbin_method_put_examples

__all__ = ("httpbin_method_examples",)

httpbin_method_examples = {
    **httpbin_method_delete_examples,
    **httpbin_method_get_examples,
    **httpbin_method_patch_examples,
    **httpbin_method_post_examples,
    **httpbin_method_put_examples,
}
