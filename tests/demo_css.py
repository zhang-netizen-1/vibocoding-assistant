"""Static checks for declarations and token aliases in generated demo layers."""
import re


def selectors(text):
    """Split selector lists while preserving commas inside :is() and :not()."""
    result = []
    start = depth = 0
    for index, character in enumerate(text):
        if character in '([':
            depth += 1
        elif character in ')]':
            depth -= 1
        elif character == ',' and depth == 0:
            result.append(text[start:index].strip())
            start = index + 1
    return [*result, text[start:].strip()]


def declaration(css, selector, property_name):
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    values = []
    for selector_list, body in re.findall(r'([^{}]+)\{([^{}]*)\}', css):
        if selector in selectors(selector_list):
            for value in re.findall(r'(?<![\w-])' + re.escape(property_name) + r':\s*([^;}]+)', body):
                values.append(('!important' in value, len(values), value))
    if not values:
        raise AssertionError(f'Missing {property_name} for {selector}')
    return max(values)[2].replace('!important', '').strip()


def resolve_color(css, value):
    # Host tokens are inherited by descendants. Follow compatibility aliases
    # through the shared spec instead of taking obsolete source-sheet literals.
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    tokens = {}
    for selector_list, body in re.findall(r'([^{}]+)\{([^{}]*)\}', css):
        if ':host' in selectors(selector_list):
            tokens.update(re.findall(r'(--[\w-]+):\s*([^;}]+)', body))
    seen = set()
    while value.startswith('var('):
        name = re.fullmatch(r'var\((--[\w-]+)\)', value)[1]
        if name in seen:
            raise AssertionError(f'Cyclic color alias {name}')
        seen.add(name)
        value = tokens[name].strip()
    if not re.fullmatch(r'#[\da-fA-F]{3}(?:[\da-fA-F]{3})?', value):
        raise AssertionError(f'Unsupported color {value}')
    if len(value) == 4:
        value = '#' + ''.join(character * 2 for character in value[1:])
    return value.upper()


def demo_styles(assets, kind, skin=None):
    names = [f'demo-{kind}.css', 'demo-spec.css', f'demo-skins/_kind-{kind}.css']
    if skin:
        names.append(f'demo-skins/{skin}.css')
    names.append('demo-accessibility.css')
    return '\n'.join((assets / name).read_text() for name in names)
