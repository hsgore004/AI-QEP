import re


class CapabilityValidator:

    NORMALIZATION_MAP = {
        "present": "visible",
        "displayed": "visible",
        "shown": "visible",

        "login": "log in",
        "log-in": "log in",

        "empty": "blank",
    }

    def validate(
        self,
        available_keywords: list[str],
        used_keywords: list[str],
    ) -> list[str]:

        available = {
            self._normalize(keyword)
            for keyword in available_keywords
        }

        missing = []

        for keyword in used_keywords:

            normalized = self._normalize(keyword)

            if normalized not in available:
                missing.append(keyword)

        return sorted(set(missing))

    def _normalize(
        self,
        keyword: str,
    ) -> str:

        keyword = keyword.lower()

        for source, target in self.NORMALIZATION_MAP.items():
            keyword = re.sub(
                rf"\b{re.escape(source)}\b",
                target,
                keyword,
            )

        keyword = re.sub(r"\s+", " ", keyword)

        return keyword.strip()