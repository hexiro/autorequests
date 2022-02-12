from __future__ import annotations

import re

fix_snake_case_regexp = re.compile("_{2,}")
leading_integer_regexp = re.compile("^[0-9]+")
