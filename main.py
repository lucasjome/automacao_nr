import boto3
from pdf2image import convert_from_path
from pathlib import Path
import ntpath
import argparse as ap
import trp

from classes import Course, Employee, CompletedCourse
from db_base import session_factory
from datetime import datetime
from ocr_extraction_helper import OcrParser
import json


def populate_db(session):
    nr10 = Course(
        name='NR 10 Básico', hours=40, description='Segurança em Instalações e Serviços em Eletricidade')
    nr35 = Course(name='NR 35 Básico', hours=8,
                  description='Trabalho em Altura')

    f1 = Employee(name="Fernando Souza")
    f2 = Employee(name="Fernando dos Santos Oliveira")
    f3 = Employee(name='Fábio Aurélio de Alencar')

    session.add_all([nr10, nr35, f1, f2, f3])
    session.commit()

# Parse Document and OCR


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


def parse_document(document):
    print("Analisando certificado NR")
    ocr_parser = OcrParser(page=document.pages[0])

    # Criando o Funcionário
    person_name = ocr_parser.get_person_name()

    # Valida existência de nome no certificado
    if person_name == None or person_name['person_name'] == '':
        raise ValueError("Nome não encontrado")

    doc_employee = Employee(name=person_name['person_name'])

    # Criando o Curso
    course_info = ocr_parser.get_course_info()
    if course_info == None:
        raise ValueError("Dados sobre o curso não encontrados")

    course_date_info = ocr_parser.get_course_date()

    doc_course = Course(name=course_info['course_name'],
                        description=course_info['course_description'],
                        company=course_info['course_company'],
                        hours=course_date_info['course_hours'])

    # Dados do assinante responsável
    signer_info = ocr_parser.get_signer_info()
    if signer_info == None:
        raise ValueError("Erro ao buscar dados do Assinante")

    return doc_employee, doc_course, signer_info, course_date_info

# Validation methods


def validate_employee(session, doc_employee):
    # Verifica se o funcionario existe no banco de dados
    employee_query = session.query(Employee).filter(
        Employee.name.ilike(doc_employee.name))

    if employee_query.count() != 1:
        print("Funcionário não encontrado no sistema.")
        return False

    doc_employee = employee_query.first()
    print(f"Nome do funcionário: {doc_employee.name}")
    return True


def validate_course(session, doc_course, course_date_info):
    # Verifica e valida o curso no banco de dados
    course_query = session.query(Course).filter(
        Course.name.ilike(doc_course.name))
    if course_query.count() == 1:
        course = course_query.first()
        donein = course_date_info['course_date'].strftime('%m/%Y')

        print(f"Curso: {doc_course.name} - {doc_course.description}")
        print(
            f" - Data de término: {donein}")

        if doc_course.hours >= course.hours:
            print(
                f" - Carga horária: Aprovada ({doc_course.hours}h de {course.hours}h)")
            return True
        else:
            print(
                f" - Carga horária: Mínimo não obtido ({doc_course.hours}h de {course.hours}h)")
            return False


def validate_signer(signer_info):
    # Verifica a existência de assinatura
    signer_name = signer_info['signer_name']
    signer_signature = signer_info['signer_signature']

    print(f"Responsável pelo curso: {signer_name}")
    if signer_signature == None:
        print(" - Documento não assinado!")
        return False

    print(" - Documento assinado.")
    return True


def validate_certificate(session, doc_employee, doc_course, signer_info, course_date_info):
    print("Validando o certificado\n")
    print("# Dados obtidos:\n")

    # Validação modular dos dados
    v_name = validate_employee(session, doc_employee)
    v_course = validate_course(session, doc_course, course_date_info)
    v_sign = validate_signer(signer_info)

    print()

    # Se tudo está correto, salvar no banco
    if not (v_name and v_course and v_sign):
        print("Documento incompleto, não será salvo no banco de dados.")
        return False

    print("Salvando curso completado no banco de dados")
    doc_completedcourse = CompletedCourse(employee_id=doc_employee.employee_id,
                                          course_id=doc_course.course_id,
                                          donein=course_date_info['course_date'])
    session.add(doc_completedcourse)
    session.commit()
    return True


def main():
    # Criar e adicionar informações ao banco de dados
    session = session_factory()
    populate_db(session)

    # Parse Argument (--help para mais detalhes)
    parser = ap.ArgumentParser(
        description='Extração automática de certificados tipo NR')
    parser.add_argument('--input_pdf', action='store', type=str,
                        required=True, help='Arquivo em PDF contendo o certificado NR')

    # Leitura dos argumentos
    args = parser.parse_args()
    pdf_file = args.input_pdf

    # Checa se o arquivo em PDF existe
    if not Path(pdf_file).exists():
        print("Arquivo não encontrado.")
        return False

    # Converter pdf -> png
    # temp_file = extract_pdf_as_image(pdf_file)
    # aws_textract_response = get_ocr_response(temp_file)

    with open('./temp/teste10.json', 'r') as f:
        teste10_json = json.load(f)

    with open('./temp/teste35.json', 'r') as f:
        teste35_json = json.load(f)
    document = trp.Document(teste10_json)

    # Extrai as informações e cria os objetos
    doc_employee, doc_course, signer_info, course_date_info = parse_document(
        document)

    # Validação com o banco
    validate_certificate(session, doc_employee, doc_course,
                         signer_info, course_date_info)
    session.close()


if __name__ == "__main__":
    main()
