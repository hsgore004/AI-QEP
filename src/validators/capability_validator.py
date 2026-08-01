class CapabilityValidator:

    def validate(
        self,
        available_keywords: list[str],
        used_keywords: list[str],
    ) -> list[str]:

        available = set(available_keywords)

        missing = []

        for keyword in used_keywords:

            if keyword not in available:
                missing.append(keyword)

        return sorted(missing)