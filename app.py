from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent / "src"))

from pipeline.pipeline_v2 import AIQEPPipelineV2


def main():

    requirement_file = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "requirements/login_requirement.md"
    )

    print("\n========================================")
    print("               AI-QEP")
    print("========================================")
    print(f"Requirement File : {requirement_file}")
    print("========================================\n")

    pipeline = AIQEPPipelineV2()

    try:
        pipeline.run(requirement_file)

    except FileNotFoundError as ex:

        print("\n========================================")
        print("ERROR")
        print("========================================")
        print(ex)
        print("========================================")


if __name__ == "__main__":
    main()