from django import template
from string import punctuation

register = template.Library()

censor_list = [
    'редиска',
    'заголовок',
    'radish',
]

def clear_str(word: str) -> str:
    new_word = map(lambda x: x if x not in punctuation else "", word)
    result = ''.join(new_word)
    return result.lower()

@register.filter()
def censor(text_in):
    words_list = text_in.split()
    if isinstance(text_in, str):
        for word in words_list:
            if clear_str(word) in censor_list:
                text_in = text_in.replace(word[1:], '*' * (len(word) - 2) + word[-1])
    return text_in

@register.filter()
def split(value: str, delimiter: str = '\n') -> list:
    """Фильтр преобразующий аргумент типа str в list для дальнейшего использования в цикле в html."""
    return value.split(delimiter)
