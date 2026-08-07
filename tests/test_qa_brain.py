from qabrain.qa_brain import QABrain


def main():

    brain = QABrain()

    brain.build(
        knowledge_file="src/crawl_output/qa_knowledge.json",
        output_file="src/crawl_output/qa_brain.json",
    )


if __name__ == "__main__":
    main()