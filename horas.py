
"""
Irania Aguinaga Muñoz 

Este fichero contiene la función normalizaHoras(), que lee un fichero
de texto, identifica expresiones horarias mediante expresiones regulares
y escribe otro fichero con las horas válidas en el formato HH:MM.
"""

import re


def _formatea_hora(hora, minuto):
    """
    Devuelve una hora con el formato HH:MM.
    """
    return f'{hora:02d}:{minuto:02d}'


def _convierte_periodo(hora, periodo):
    """
    Convierte una hora expresada con un periodo del día al formato
    de 24 horas. Devuelve None cuando la expresión no es válida.
    """
    if not 1 <= hora <= 12:
        return None

    if periodo == 'de la mañana':
        return hora if 4 <= hora <= 12 else None

    if periodo in ('del mediodía', 'del mediodia'):
        if hora == 12:
            return 12
        return hora + 12 if 1 <= hora <= 3 else None

    if periodo == 'de la tarde':
        return hora + 12 if 3 <= hora <= 8 else None

    if periodo == 'de la noche':
        if 8 <= hora <= 11:
            return hora + 12
        if hora == 12:
            return 0
        return hora if 1 <= hora <= 4 else None

    if periodo == 'de la madrugada':
        return hora if 1 <= hora <= 6 else None

    return None


def _aplica_modificador(hora, modificador):
    """
    Aplica expresiones como 'en punto', 'y cuarto', 'y media'
    o 'menos cuarto'.
    """
    if modificador in (None, 'en punto'):
        return hora, 0

    if modificador == 'y cuarto':
        return hora, 15

    if modificador == 'y media':
        return hora, 30

    if modificador == 'menos cuarto':
        return (hora - 1) % 24, 45

    return hora, 0


def _normaliza_con_periodo(coincidencia):
    """
    Normaliza expresiones como '4 y media de la tarde'.
    """
    hora = int(coincidencia.group('hora'))
    modificador = coincidencia.group('modificador')
    periodo = coincidencia.group('periodo')

    hora_convertida = _convierte_periodo(hora, periodo)

    if hora_convertida is None:
        return coincidencia.group(0)

    hora_convertida, minuto = _aplica_modificador(
        hora_convertida,
        modificador
    )

    return _formatea_hora(hora_convertida, minuto)


def _normaliza_horas_h_con_periodo(coincidencia):
    """
    Normaliza expresiones como '7h de la mañana'.
    """
    hora = int(coincidencia.group('hora'))
    minuto = int(coincidencia.group('minuto') or 0)
    periodo = coincidencia.group('periodo')

    hora_convertida = _convierte_periodo(hora, periodo)

    if hora_convertida is None or minuto > 59:
        return coincidencia.group(0)

    return _formatea_hora(hora_convertida, minuto)


def _normaliza_formato_h(coincidencia):
    """
    Normaliza expresiones como '18h30m', '17h5m' o '8h'.
    """
    hora = int(coincidencia.group('hora'))
    minuto = int(coincidencia.group('minuto') or 0)

    if hora > 23 or minuto > 59:
        return coincidencia.group(0)

    return _formatea_hora(hora, minuto)


def _normaliza_formato_estandar(coincidencia):
    """
    Normaliza expresiones como '8:05' o '18:30'.
    """
    hora = int(coincidencia.group('hora'))
    minuto = int(coincidencia.group('minuto'))

    if hora > 23 or minuto > 59:
        return coincidencia.group(0)

    return _formatea_hora(hora, minuto)


def _normaliza_sin_periodo(coincidencia):
    """
    Normaliza expresiones como '8 en punto', '8 y media'
    o '5 menos cuarto'.
    """
    hora = int(coincidencia.group('hora'))
    modificador = coincidencia.group('modificador')

    if not 1 <= hora <= 12:
        return coincidencia.group(0)

    hora %= 12
    hora, minuto = _aplica_modificador(hora, modificador)

    return _formatea_hora(hora, minuto)


def normalizaHoras(ficText, ficNorm):
    """
    Lee el fichero ficText, normaliza sus expresiones horarias válidas
    y escribe el resultado en el fichero ficNorm.
    """
    periodos = (
        r'de la mañana|del mediod[ií]a|de la tarde|'
        r'de la noche|de la madrugada'
    )

    patron_h_con_periodo = re.compile(
        rf'(?<!\w)(?P<hora>\d{{1,2}})h'
        rf'(?:(?P<minuto>\d{{1,2}})m)?\s+'
        rf'(?P<periodo>{periodos})(?!\w)'
    )

    patron_con_periodo = re.compile(
        rf'(?<!\w)(?P<hora>\d{{1,2}})\s+'
        rf'(?:(?P<modificador>'
        rf'en punto|y cuarto|y media|menos cuarto)\s+)?'
        rf'(?P<periodo>{periodos})(?!\w)'
    )

    patron_h = re.compile(
        rf'(?<!\w)(?P<hora>\d{{1,2}})h'
        rf'(?:(?P<minuto>\d{{1,2}})m)?'
        rf'(?!\w)(?!\s+(?:{periodos}))'
    )

    patron_estandar = re.compile(
        r'(?<![\w:])(?P<hora>\d{1,2}):'
        r'(?P<minuto>\d{2})(?![\d:])'
    )

    patron_sin_periodo = re.compile(
        r'(?<!\w)(?P<hora>\d{1,2})\s+'
        r'(?P<modificador>en punto|y cuarto|y media|menos cuarto)'
        r'(?!\w)'
    )

    with open(ficText, 'r', encoding='utf-8') as fichero_entrada:
        texto = fichero_entrada.read()

    texto = patron_h_con_periodo.sub(
        _normaliza_horas_h_con_periodo,
        texto
    )

    texto = patron_con_periodo.sub(
        _normaliza_con_periodo,
        texto
    )

    texto = patron_h.sub(
        _normaliza_formato_h,
        texto
    )

    texto = patron_estandar.sub(
        _normaliza_formato_estandar,
        texto
    )

    texto = patron_sin_periodo.sub(
        _normaliza_sin_periodo,
        texto
    )

    with open(ficNorm, 'w', encoding='utf-8') as fichero_salida:
        fichero_salida.write(texto)

