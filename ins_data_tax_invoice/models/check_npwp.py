import re


def _check_npwp(npwp, f_name='npwp'):
    """ custom function to check npwp """
    # return empty if the field is not filled
    if not npwp:
        return {}

    # set default warning message
    warning = {
        'title': 'Bad NPWP format !',
        'message': "Valid NPWP:'01.855.081.4-005.000' or '018550814005000'"
    }

    # if the length is not 15 or 20, return a warning, reset
    # check if the length is 15 and is integer
    id_len = len(npwp)
    vals = {}
    check_len = id_len not in (15, 20)
    check_digit = id_len == 15 and not npwp.isdigit()
    if check_len or check_digit:
        return {
            'warning': warning,
            'value': {f_name: False}
        }
    elif id_len == 15:  # length is 15 then we have to reformat
        parse = re.findall(r'(\d{2})(\d{3})(\d{3})(\d{1})(\d{3})(\d{3})', npwp)
        if parse:  # there is result, update the view
            out = '%s.%s.%s.%s-%s.%s' % parse[0]
            vals = {f_name: out}
            return {'value': vals}
        else:
            return {
                'warning': warning,
                'value': {f_name: False}
            }
    elif id_len == 20:  # length is 20 then we have to match
        pattern = r'(\d{2}).(\d{3}).(\d{3}).(\d{1})-(\d{3}).(\d{3})'
        match = re.match(pattern, npwp)
        if not match:  # no result, then wrong
            return {
                'warning': warning,
                'value': {f_name: False}
            }
    # just return empty dictionary if it is valid
    return {'value': vals}
