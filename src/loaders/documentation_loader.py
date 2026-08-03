import requests
from bs4 import BeautifulSoup


class DocumentationLoader:
    """
    Downloads documentation and converts it into clean text
    for the QA Brain.

    Current
    -------
    - Single web page

    Future
    ------
    - Multi-page crawler
    - PDF Loader
    - Confluence
    - SharePoint
    - GitHub Wiki
    """

    def load(
        self,
        url: str,
    ) -> str:

        print("\n" + "=" * 80)
        print("DOCUMENTATION LOADER")
        print("=" * 80)
        print(f"URL : {url}")

        response = requests.get(
            url,
            timeout=30,
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        # Remove elements that do not contribute
        # to business understanding.

        for tag in soup(
            [
                "script",
                "style",
                "header",
                "footer",
                "nav",
                "aside",
            ]
        ):
            tag.decompose()

        text = soup.get_text(
            separator="\n",
            strip=True,
        )

        print(
            f"Characters : {len(text):,}"
        )

        return text