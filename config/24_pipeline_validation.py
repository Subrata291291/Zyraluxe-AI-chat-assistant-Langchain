import importlib.util
from pathlib import Path


CONFIG_FILE = Path(__file__).parent / "18_config.py"
FACTORY_FILE = Path(__file__).parent / "22_rag_service_factory.py"
PIPELINE_FILE = Path(__file__).parent / "23_rag_pipeline.py"


def load_module(name, file_path):

    spec = importlib.util.spec_from_file_location(
        name,
        file_path
    )

    if spec is None or spec.loader is None:
        raise ImportError(
            f"Cannot load {file_path}"
        )

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


TEST_CASES = [

    {
        "question": "How long does a refund take?",
        "expected_keyword": "7-10"
    },

    {
        "question": "Can I return an item?",
        "expected_keyword": "2 hours"
    },

    {
        "question": "Do you sell my personal information?",
        "expected_keyword": "do not sell"
    }
]


def validate():

    config = load_module(
        "zyra_config",
        CONFIG_FILE
    )

    factory = load_module(
        "zyra_factory",
        FACTORY_FILE
    )

    pipeline = load_module(
        "zyra_pipeline",
        PIPELINE_FILE
    )

    components = factory.create_components(config)

    passed = 0

    print("=" * 60)
    print("ZYRA LUXE - PIPELINE VALIDATION")
    print("=" * 60)

    for index, test in enumerate(TEST_CASES, start=1):

        print()
        print("-" * 60)
        print(f"Test {index}")
        print(f"Question: {test['question']}")

        try:

            result = pipeline.run_pipeline(
                test["question"],
                components,
                config
            )

            answer = result["answer"]

            keyword = test["expected_keyword"].lower()

            answer_lower = answer.lower()

            has_keyword = keyword in answer_lower

            has_source = len(result["sources"]) > 0

            success = has_keyword and has_source

            if success:
                passed += 1

            print()
            print("Answer:")
            print(answer)

            print()
            print(f"Keyword Found: {has_keyword}")
            print(f"Sources Found: {has_source}")

            print()

            if success:
                print("Result: PASS")
            else:
                print("Result: FAIL")

        except Exception as error:

            print()
            print("Result: ERROR")
            print(error)

    print()
    print("=" * 60)
    print("FINAL REPORT")
    print("=" * 60)

    print(f"Passed: {passed}/{len(TEST_CASES)}")

    accuracy = passed / len(TEST_CASES) * 100

    print(f"Success Rate: {accuracy:.0f}%")

    print("=" * 60)


if __name__ == "__main__":

    validate()