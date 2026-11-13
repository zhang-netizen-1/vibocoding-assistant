import re
import unittest
from pathlib import Path

SKINS = Path(__file__).resolve().parents[1] / 'site-src/redesign/demo-skins'


class HintPositionSkinTest(unittest.TestCase):
    """The hint pill position (12px inset + stage border) is owned by demo-spec.css.
    No per-entry or per-kind skin may move it; tests/hint_position_headless.cjs
    checks the rendered position on all 192 entries."""

    def test_no_skin_overrides_hint_position(self):
        offenders = []
        for css in sorted(SKINS.glob('*.css')):
            text = re.sub(r'/\*.*?\*/', '', css.read_text(encoding='utf-8'), flags=re.S)
            for selector, body in re.findall(r'([^{}]+)\{([^{}]*)\}', text):
                if not re.search(r'\.ds-hint(?![\w-])', selector):
                    continue
                if re.search(r'(?<![\w-])(inset|left|right|top|bottom|position|margin|translate|transform)\s*:', body):
                    offenders.append(f'{css.name}: {selector.strip()}')
        self.assertEqual(offenders, [])


if __name__ == '__main__':
    unittest.main()
