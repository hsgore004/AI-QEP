from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent / "src"))

from pipeline.ai_qep_pipeline import AIQEPPipeline


def main():

    pipeline = AIQEPPipeline()

    pipeline.run()


if __name__ == "__main__":
    main()