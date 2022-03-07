from tempfile import tempdir
import boto3
from pdf2image import convert_from_path
from pathlib import Path
import ntpath
import argparse as ap


def extract_pdf_as_image(pdf_file):
    print("Convertendo o PDF para PNG")
    # Extrai o nome do arquivo de pdf
    pdf_filename = ntpath.basename(pdf_file)

    # Cria pasta temporária se preciso
    temp_dir = Path(__file__).parent.absolute() / 'temp'
    Path(temp_dir).mkdir(exist_ok=True)

    # Converte para png
    converted_pdf = convert_from_path(pdf_file)

    # Pela simplicidade, eu assumo que a primeira página sempre é a Frente do certificado.
    temp_output = f"{temp_dir}/{pdf_filename.split('.')[0]}.png"
    converted_pdf[0].save(temp_output, 'PNG')
    return temp_output


def get_ocr_response(documentName):
    print("Processando OCR com AWS Textract")
    # Abre a imagem do certificado
    with open(documentName, 'rb') as document:
        imageBytes = bytearray(document.read())

    # Cliente Amazon Textract
    textract = boto3.client('textract', region_name='us-east-1')

    # Chama o Amazon Textract
    response_png = textract.detect_document_text(
        Document={'Bytes': imageBytes})

    return response_png


def main():
    # Parse Argument (--help para mais detalhes)
    parser = ap.ArgumentParser(
        description='Extração automática de certificados tipo NR')
    parser.add_argument('--input_pdf', action='store', type=str,
                        required=True, help='Arquivo em PDF contendo o certificado NR')

    # Leitura dos argumentos
    args = parser.parse_args()
    pdf_file = args.input_pdf

    # Converte pdf -> png
    temp_file = extract_pdf_as_image(pdf_file)
    aws_textract_response = get_ocr_response(temp_file)


if __name__ == "__main__":
    main()
