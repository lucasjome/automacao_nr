from datetime import datetime
import json
import trp


def adjust_boudingbox(boundingBox):
    return {'top': boundingBox.top,
            'bottom': boundingBox.top + boundingBox.height,
            'left': boundingBox.left,
            'right': boundingBox.left + boundingBox.width,
            'width': boundingBox.width,
            'height': boundingBox.height
            }


def get_lines_in_boundingbox(page, boundingBox):
    lines = []
    boundingBox = adjust_boudingbox(boundingBox)

    for line in page.lines:
        line_bbox = adjust_boudingbox(line.geometry.boundingBox)

        if (line_bbox['left'] >= boundingBox['left'] and
            line_bbox['left'] <= boundingBox['right'] and
            line_bbox['top'] >= boundingBox['top'] and
                line_bbox['top'] <= boundingBox['bottom']):
            lines.append(line)
    return lines


def get_signer_info(page):
    signature_boudingbox = trp.BoundingBox(height=0.09337568171322341,
                                           width=0.32019598245620723,
                                           top=0.6608583211898804,
                                           left=0.4356914281845093)

    signature_lines = get_lines_in_boundingbox(page, signature_boudingbox)

    if not signature_lines:
        return None

    signer_name = None
    signer_signature = None

    for line in signature_lines:
        # Pegar assinatura
        if 'HANDWRITING' in line.words[0].textType:
            signer_signature = line.text

        # Pegar o nome
        if 'PRINTED' in line.words[0].textType:
            signer_name = line.text

    return {'signer_name': signer_name, 'signer_signature': signer_signature}


def get_person_name(page):
    name_boudingbox = trp.BoundingBox(height=0.07026442140340805,
                                      width=0.6210504174232483,
                                      left=0.24513930827379227,
                                      top=0.2866944015026093)
    person_name = ''

    name_lines = get_lines_in_boundingbox(page, name_boudingbox)

    if not name_lines:
        return None

    for line in name_lines:
        person_name += line.text

    return person_name


def get_course_name(page):
    course_boudingbox = trp.BoundingBox(height=0.1378476420798065,
                                        width=0.6210504174232483,
                                        left=0.24513930827379227,
                                        top=0.42321644498186217)

    course_lines = get_lines_in_boundingbox(page, course_boudingbox)

    if not course_lines:
        return None

    lines_txt = ''
    for line in course_lines:
        lines_txt += f'{line.text} '

    lines_txt = lines_txt.strip()

    # Extrair indexes em lowerCase para evitar problemas com o OCR
    lines_txt_lower = lines_txt.lower()

    course_start_index = lines_txt_lower.find('nr ')
    course_end_index = lines_txt_lower.find(' ministrado pela ')

    course_name = lines_txt[course_start_index:course_end_index]

    # Extrair nome da empresa
    temp = lines_txt_lower.find("pela")
    wordEndIndex = temp + lines_txt_lower[temp:].index(' ')
    course_company = lines_txt[wordEndIndex:].strip()

    return course_name, course_company


MONTHS = {'janeiro': 1,  'fevereiro': 2, u'março': 3,    'abril': 4,
          'maio': 5,     'junho': 6,     'julho': 7,     'agosto': 8,
          'setembro': 9, 'outubro': 10,  'novembro': 11, 'dezembro': 12}


def format_course_date(course_date):
    course_month, course_year = course_date.split(' de ')
    month_number = MONTHS[course_month.lower()]

    course_date = datetime.strptime(
        f'{month_number} - {course_year}',  "%m - %Y")
    return course_date


def get_course_date(page):
    course_total_hours = None
    course_date = None

    for line in page.lines:
        if line.text.startswith('Carga horária'):
            course_total_hours = line.text.split(':')[-1].strip()
        if line.text.startswith('Mês e ano da conclusão'):
            course_date = line.text.split(':')[-1].strip()

    course_date = format_course_date(course_date)
    course_hours = float(course_total_hours.split(' ')[0])

    return course_hours, course_date
