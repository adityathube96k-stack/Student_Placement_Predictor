import os
import PyPDF2


def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF resume.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        str: Extracted resume text.
    """

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(
            f"Resume file not found: {pdf_path}"
        )

    if not pdf_path.lower().endswith(".pdf"):
        raise ValueError(
            "Only PDF resume files are supported."
        )

    extracted_text = []

    try:
        with open(pdf_path, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)

            if not reader.pages:
                raise ValueError(
                    "The PDF does not contain any pages."
                )

            for page in reader.pages:
                text = page.extract_text()

                if text:
                    extracted_text.append(text)

        final_text = "\n".join(extracted_text).strip()

        if not final_text:
            raise ValueError(
                "No readable text was found in the PDF."
            )

        return final_text

    except Exception as error:
        raise RuntimeError(
            f"Unable to extract text from PDF: {error}"
        )


if __name__ == "__main__":
    print("==========================================")
    print("RESUME TEXT EXTRACTION MODULE")
    print("==========================================")
    print("Module loaded successfully.")
    print("Use extract_text_from_pdf() to extract")
    print("text from a PDF resume.")
    print("==========================================")