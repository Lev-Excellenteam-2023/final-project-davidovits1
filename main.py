import presentation_parser
import openAI_request
import json
import sys
import os
from dotenv import load_dotenv

PATH = "End of course exercise.pptx"


def main(argv=None):
    load_dotenv()
    # Optionally put a presentation in argv
    print(sys.argv)
    if len(sys.argv) == 2:
        path = sys.argv[1]
    else:
        path = PATH

    text_pptx = presentation_parser.extract_text(path)
    if text_pptx == [""]:
        # Error loading the presentation
        return
    print(text_pptx)

    explanation = {}
    print(type(explanation))
    for i in range(len(text_pptx)):
        explanation[i + 1] = text_pptx[i] + ': ' + openAI_request.generate_explanation(text_pptx[i])

    path = path.replace(".pptx", ".json")
    with open(path, 'w') as json_file:
        json.dump(explanation, json_file, indent=4)
    print(explanation)


if __name__ == "__main__":
    main()
