import boto3
from pdf2image import convert_from_path


def parse_input_pdf(pdf_file):
    converted_pdf = convert_from_path(pdf_file)


def get_ocr_response(documentName):
    # Read document content
    with open(documentName, 'rb') as document:
        imageBytes = bytearray(document.read())

    # Amazon Textract client
    textract = boto3.client('textract', region_name='us-east-1')

    # Call Amazon Textract
    response_png = textract.detect_document_text(
        Document={'Bytes': imageBytes})

    return response_png


def main():
    print("Inicio")


if __name__ == "__main__":
    main()
