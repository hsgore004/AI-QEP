import json
from pathlib import Path


class TestCaseMarkdownWriter:
    """
    Writes generated test cases to a human-readable Markdown document.
    """

    # --------------------------------------------------
    # Write
    # --------------------------------------------------

    def write(
        self,
        input_file,
        output_file,
    ):

        data = json.loads(
            Path(input_file).read_text(
                encoding="utf-8",
            )
        )

        pages = data.get(
            "pages",
            [],
        )

        lines = []

        lines.append("# AI-QEP Generated Test Cases")
        lines.append("")

        if data.get("documentation_url"):
            lines.append(
                f"**Documentation:** {data['documentation_url']}"
            )
            lines.append("")

        total_chunks = 0
        total_test_cases = 0

        # --------------------------------------------------
        # Pages
        # --------------------------------------------------

        for page_index, page in enumerate(
            pages,
            start=1,
        ):

            lines.append("---")
            lines.append("")
            lines.append(
                f"# Page {page_index} : {page.get('title','')}"
            )
            lines.append("")

            chunks = page.get(
                "chunks",
                [],
            )

            # --------------------------------------------------
            # Chunks
            # --------------------------------------------------

            for chunk_index, chunk in enumerate(
                chunks,
                start=1,
            ):

                total_chunks += 1

                lines.append("## ----------------------------------------")
                lines.append(
                    f"## Chunk {chunk_index}"
                )
                lines.append("")

                lines.append(
                    f"**Heading:** {chunk.get('heading','')}"
                )
                lines.append("")

                test_cases = chunk.get(
                    "test_cases",
                    [],
                )

                if not test_cases:

                    lines.append(
                        "_No test cases generated._"
                    )
                    lines.append("")
                    continue

                # --------------------------------------------------
                # Test Cases
                # --------------------------------------------------

                for test_case in test_cases:

                    total_test_cases += 1

                    lines.append(
                        f"### {test_case.get('id','')}"
                    )
                    lines.append("")

                    lines.append(
                        f"**Title:** {test_case.get('title','')}"
                    )
                    lines.append("")

                    lines.append(
                        f"**Objective:** {test_case.get('objective','')}"
                    )
                    lines.append("")

                    lines.append(
                        f"**Priority:** {test_case.get('priority','Medium')}"
                    )
                    lines.append("")

                    #
                    # Preconditions
                    #

                    lines.append("#### Preconditions")

                    preconditions = test_case.get(
                        "preconditions",
                        [],
                    )

                    if preconditions:

                        for item in preconditions:

                            lines.append(
                                f"- {item}"
                            )

                    else:

                        lines.append(
                            "- None"
                        )

                    lines.append("")

                    #
                    # Steps
                    #

                    lines.append("#### Steps")

                    steps = test_case.get(
                        "steps",
                        [],
                    )

                    if steps:

                        for index, step in enumerate(
                            steps,
                            start=1,
                        ):

                            lines.append(
                                f"{index}. {step}"
                            )

                    else:

                        lines.append(
                            "No steps."
                        )

                    lines.append("")

                    #
                    # Expected Results
                    #

                    lines.append(
                        "#### Expected Results"
                    )

                    expected_results = test_case.get(
                        "expected_results",
                        [],
                    )

                    if expected_results:

                        for index, result in enumerate(
                            expected_results,
                            start=1,
                        ):

                            lines.append(
                                f"{index}. {result}"
                            )

                    else:

                        lines.append(
                            "No expected results."
                        )

                    lines.append("")
                    lines.append("---")
                    lines.append("")

        #
        # Summary
        #

        lines.append("")
        lines.append("# Summary")
        lines.append("")
        lines.append(
            f"- Pages : {len(pages)}"
        )
        lines.append(
            f"- Chunks : {total_chunks}"
        )
        lines.append(
            f"- Test Cases : {total_test_cases}"
        )
        lines.append("")

        Path(output_file).write_text(
            "\n".join(lines),
            encoding="utf-8",
        )

        print()
        print("=" * 80)
        print("TEST CASE MARKDOWN CREATED")
        print("=" * 80)
        print(f"Output      : {output_file}")
        print(f"Pages       : {len(pages)}")
        print(f"Chunks      : {total_chunks}")
        print(f"Test Cases  : {total_test_cases}")
        print("=" * 80)