import asyncio
from datetime import datetime
from pathlib import Path

from openai import OpenAI

from config import settings

from llm.providers.openai_provider import OpenAIProvider
from llm.service import LLMService

from planning.documentation_knowledge_builder import (
    DocumentationKnowledgeBuilder,
)

from planning.qa_knowledge_builder import (
    QAKnowledgeBuilder,
)

from qabrain.entity_discovery import (
    EntityDiscovery,
)

from planning.knowledge_extractor import (
    KnowledgeExtractor,
)

from planning.entity_extractor import (
    EntityExtractor,
)

from planning.test_case_generator import (
    TestCaseGenerator,
)


from utils.test_case_markdown_writer import (
    TestCaseMarkdownWriter,
)

from executors.execution_factory import (
    create_execution_runner,
)

class AIQEPPipelineV3:
    """
    AI-QEP V3

    Stage 1
        Documentation Builder
                │
                ▼
        documentation.json

    Stage 2
        Knowledge Extractor
                │
                ▼
        knowledge.json

    Stage 3
        Entity Discovery
                │
                ▼
        entities.json
    """

    # --------------------------------------------------
    # Constructor
    # --------------------------------------------------

    def __init__(self):

        self.run_id = None
        self.output_dir = None

        #
        # Shared LLM
        #



        self.max_parallel_requests = 5

        self.semaphore = asyncio.Semaphore(
            self.max_parallel_requests,
        )


        client = OpenAI(

            api_key=settings.OPENAI_API_KEY,

        )

        provider = OpenAIProvider(
            client,
        )

        self.llm_service = LLMService(
            provider,
        )

    # --------------------------------------------------
    # Run
    # --------------------------------------------------
    
    async def run(
        self,
        documentation_url: str,
    ):
        if settings.TEST_CASE_FILE is None:

            self._create_run_folder()

        else:

            self.output_dir = Path(
                settings.TEST_CASE_FILE,
            ).parent

            self.run_id = self.output_dir.name

        self._print_banner()

        print()
        print("=" * 80)
        print("PIPELINE STARTED")
        print("=" * 80)
        print(f"Documentation : {documentation_url}")
        print(f"Run ID        : {self.run_id}")
        print(f"Output Folder : {self.output_dir}")


        #
        # Skip pipeline if an existing test case file is supplied
        #

        skip_generation = (
            settings.TEST_CASE_FILE is not None
        )

        #
        # --------------------------------------------------
        # Stage 1
        # --------------------------------------------------
        #
        if skip_generation:

            print()
            print("=" * 80)
            print("Stage 1 : Documentation Builder")
            print("=" * 80)
            print("Skipping stage (using existing test_cases.json).")

        else:
            documentation_builder = DocumentationKnowledgeBuilder()

            await self._execute_stage(

                stage_name="Stage 1 : Documentation Builder",

                stage_callable=documentation_builder.run,

                expected_output="documentation.json",

                documentation_url=documentation_url,

                output_dir=self.output_dir,

            )

        #
        # Stage 2
        #
        if skip_generation:

            print()
            print("=" * 80)
            print("Stage 2 : QA Knowledge Builder")
            print("=" * 80)
            print("Skipping stage (using existing test_cases.json).")

        else:
            qa_knowledge_builder = QAKnowledgeBuilder()

            await self._execute_stage(

                stage_name="Stage 2 : QA Knowledge Builder",

                stage_callable=qa_knowledge_builder.run,

                expected_output="qa_knowledge.json",

                documentation_file=self.output_dir / "documentation.json",

                output_dir=self.output_dir,

            )

        #
        # Stage 3
        #

        print()
        print("=" * 80)
        print("Stage 3 : Knowledge Extractor")
        print("=" * 80)
        if skip_generation:

            print("Skipping stage (using existing test_cases.json).")

        else:
            knowledge_extractor = KnowledgeExtractor(
                self.llm_service,
            )

            qa_knowledge = self._read_json(
                self.output_dir / "qa_knowledge.json",
            )


    #==========================
            for page_index, page in enumerate(
                qa_knowledge["pages"],
                start=1,
            ):

                print()
                print(
                    f"Page {page_index}/{len(qa_knowledge['pages'])} : "
                    f"{page['title']}"
                )

                await self._process_page(

                    page,

                    knowledge_extractor,

                )


    #============================

            knowledge_file = (
                self.output_dir
                / "knowledge.json"
            )

            self._write_json(
                knowledge_file,
                qa_knowledge,
            )

            print()
            print("[OK]")
            print(f"Output : {knowledge_file}")


        #
        # Stage 4
        #

        print()
        print("=" * 80)
        print("Stage 4 : Entity Extractor")
        print("=" * 80)
        if skip_generation:

            print("Skipping stage (using existing test_cases.json).")

        else:
            entity_extractor = EntityExtractor(
                self.llm_service,
            )

            knowledge = self._read_json(
                self.output_dir / "knowledge.json",
            )

            for page_index, page in enumerate(
                knowledge["pages"],
                start=1,
            ):

                print()
                print(
                    f"Page {page_index}/{len(knowledge['pages'])} : "
                    f"{page['title']}"
                )

                await self._process_page(

                    page,

                    entity_extractor,

                )

            entities_file = (
                self.output_dir
                / "entities.json"
            )

            self._write_json(

                entities_file,

                knowledge,

            )

            print()
            print("[OK]")
            print(f"Output : {entities_file}")


        #
        # Stage 5
        #

        print()
        print("=" * 80)
        print("Stage 5 : Test Case Generator")
        print("=" * 80)
        if skip_generation:

            print("Skipping stage (using existing test_cases.json).")
            test_cases_file = Path(
                settings.TEST_CASE_FILE,
            )
        else:
            test_case_generator = TestCaseGenerator(
                self.llm_service,
            )

            entities = self._read_json(
                self.output_dir / "entities.json",
            )

            for page_index, page in enumerate(
                entities["pages"],
                start=1,
            ):

                print()
                print(
                    f"Page {page_index}/{len(entities['pages'])} : "
                    f"{page['title']}"
                )

                await self._process_page(

                    page,

                    test_case_generator,

                )

            test_cases_file = (
                self.output_dir
                / "test_cases.json"
            )

            self._write_json(

                test_cases_file,

                entities,

            )

            print()
            print("[OK]")
            print(f"Output : {test_cases_file}")



            total_pages = len(entities["pages"])

            total_chunks = 0
            total_test_cases = 0

            for page in entities["pages"]:

                total_chunks += len(page["chunks"])

                for chunk in page["chunks"]:

                    total_test_cases += len(
                        chunk.get(
                            "test_cases",
                            [],
                        )
                    )

            print()
            print("=" * 80)
            print("TEST CASE GENERATION SUMMARY")
            print("=" * 80)
            print(f"Pages       : {total_pages}")
            print(f"Chunks      : {total_chunks}")
            print(f"Test Cases  : {total_test_cases}")
            print("=" * 80)

            test_cases_file = (
                self.output_dir
                / "test_cases.json"
            )

            self._write_json(

                test_cases_file,

                entities,

            )

            #
            # Markdown
            #

            writer = TestCaseMarkdownWriter()

            writer.write(

                input_file=test_cases_file,

                output_file=self.output_dir / "test_cases.md",

            )

            print()
            print("[OK]")
            print(f"Output : {test_cases_file}")



        #
        # Stage 6
        #

        print()
        print("=" * 80)
        print("Stage 6 : Test Case Execution")
        print("=" * 80)

        execution_runner = create_execution_runner()

        await execution_runner.execute(

            output_dir=self.output_dir,

        )

        print()
        print("[OK]")
        print("Execution completed.")

###### internal keywords
    def _create_run_folder(self):

        self.run_id = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        self.output_dir = (
            Path("output")
            / self.run_id
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    # --------------------------------------------------
    # Banner
    # --------------------------------------------------

    def _print_banner(self):

        print()
        print("=" * 80)
        print("AI-QEP V3")
        print("=" * 80)

    # --------------------------------------------------
    # Execute Stage
    # --------------------------------------------------

    async def _execute_stage(
        self,
        stage_name: str,
        stage_callable,
        expected_output: str,
        **kwargs,
    ):

        print()
        print("=" * 80)
        print(stage_name)
        print("=" * 80)

        output_file = self.output_dir / expected_output

        #
        # Remove stale output
        #

        if output_file.exists():
            output_file.unlink()

        print("Running...")

        try:

            print("Calling stage...")

            success = await stage_callable(
                **kwargs,
            )

            print(f"Stage returned : {success}")

        except Exception as ex:

            print()
            print("=" * 80)
            print("STAGE FAILED")
            print("=" * 80)
            print(stage_name)
            print()

            raise RuntimeError(
                f"{stage_name} failed.\n{ex}"
            ) from ex

        if not success:

            raise RuntimeError(
                f"{stage_name} returned failure."
            )

        if not output_file.exists():

            raise RuntimeError(
                f"{stage_name} did not create "
                f"{expected_output}"
            )

        print("[OK]")
        print(f"Output : {expected_output}")


    # --------------------------------------------------
    # Read JSON
    # --------------------------------------------------

    def _read_json(
        self,
        file,
    ):

        import json

        return json.loads(

            Path(file).read_text(
                encoding="utf-8",
            )

        )


    # --------------------------------------------------
    # Write JSON
    # --------------------------------------------------

    def _write_json(
        self,
        file,
        data,
    ):

        import json

        Path(file).write_text(

            json.dumps(
                data,
                indent=2,
                ensure_ascii=False,
            ),

            encoding="utf-8",

        )

    # --------------------------------------------------
    # Process Page
    # --------------------------------------------------

    async def _process_page(
        self,
        page,
        knowledge_extractor,
    ):


        async def process_chunk(
            chunk,
        ):

            async with self.semaphore:

                print(
                    f"    [{chunk['chunk_number']}/{chunk['total_chunks']}] "
                    f"{chunk['heading']}"
                )

#===================
                for attempt in range(1, 4):

                    try:

                        return await knowledge_extractor.extract(
                            chunk,
                        )

                    except Exception as ex:

                        print(
                            f"      Retry {attempt}/3 failed : {ex}"
                        )

                        if attempt == 3:

                            raise

                        await asyncio.sleep(
                            attempt * 2,
                        )
#=======================
        tasks = [

            process_chunk(chunk)

            for chunk in page["chunks"]

        ]

        results = await asyncio.gather(
            *tasks,
            return_exceptions=True,
        )

        processed_chunks = []

#====================
        for original_chunk, result in zip(
            page["chunks"],
            results,
        ):

            if isinstance(
                result,
                Exception,
            ):

                print(
                    f"[ERROR] {original_chunk['id']} : {result}"
                )

                original_chunk["knowledge"] = {

                    "facts": [],

                    "definitions": [],

                    "business_rules": [],

                }

                original_chunk["processing"] = {

                    "status": "failed",
                    "attempts": 3,
                    "error": str(result),

                }

                processed_chunks.append(
                    original_chunk,
                )

                continue

            processed_chunks.append(
                result,
            )
#====================
        page["chunks"] = processed_chunks

        return page