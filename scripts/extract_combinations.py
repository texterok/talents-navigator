import os
import re
import json
from pathlib import Path

THEMES_DIR = Path("/Users/i1pl/talents-navigator/cliftonstrengths")
OUTPUT_FILE = Path("/Users/i1pl/talents-navigator/content/combinations.json")

# Official + alternative mappings RU -> EN
RU_TO_EN = {}

_official = {
    "Достижение": "Achiever", "Катализатор": "Activator", "Приспособляемость": "Adaptability",
    "Аналитик": "Analytical", "Организатор": "Arranger", "Убеждение": "Belief",
    "Распорядитель": "Command", "Коммуникация": "Communication", "Конкуренция": "Competition",
    "Взаимосвязанность": "Connectedness", "Последовательность": "Consistency", "Контекст": "Context",
    "Осмотрительность": "Deliberative", "Развитие": "Developer", "Дисциплинированность": "Discipline",
    "Эмпатия": "Empathy", "Сосредоточенность": "Focus", "Будущее": "Futuristic",
    "Гармония": "Harmony", "Генератор идей": "Ideation", "Включенность": "Includer",
    "Индивидуализация": "Individualization", "Вклад": "Input", "Мышление": "Intellection",
    "Ученик": "Learner", "Максимизатор": "Maximizer", "Позитивность": "Positivity",
    "Отношения": "Relator", "Ответственность": "Responsibility", "Восстановление": "Restorative",
    "Уверенность": "Self-Assurance", "Значимость": "Significance", "Стратегия": "Strategic",
    "Обаяние": "Woo",
}
_alternatives = {
    "Командование": "Command", "Вера": "Belief", "Накопление": "Input",
    "Мыслитель": "Intellection", "Обучаемость": "Learner", "Общение": "Relator",
    "Адаптивность": "Adaptability", "Провидец": "Futuristic", "Воспитатель": "Developer",
    "Реставратор": "Restorative", "Дисциплина": "Discipline", "Фокус": "Focus",
    "Активатор": "Activator", "Достигатель": "Achiever", "Самоуверенность": "Self-Assurance",
    "Включение": "Includer", "Взаимосвязь": "Connectedness", "Футурист": "Futuristic",
    "Генерация идей": "Ideation", "Размышление": "Intellection", "Обучение": "Learner",
    "Родство": "Relator", "Коллекционер": "Input",
    # Extra variants found in actual files
    "Стратегическое мышление": "Strategic", "Стратег": "Strategic",
    "Дальновидность": "Futuristic", "Визионер": "Futuristic",
    "Привязанность": "Relator", "Связующий": "Relator",
    "Развитие других": "Developer", "Осмотрительный": "Deliberative",
    "Максималист": "Maximizer", "Уверенность в себе": "Self-Assurance",
    "Идеация": "Ideation", "Аналитика": "Analytical",
    "Убеждённость": "Belief", "Завоевание": "Woo",
    "Командность": "Command", "Перспектива": "Futuristic",
    "Достижитель": "Achiever", "Целеустремлённость": "Achiever",
    "Деятель": "Achiever", "Достигатор": "Achiever",
    "Близкий": "Relator", "Историк": "Context",
    "Коммуникатор": "Communication", "Соревновательность": "Competition",
    "Развиватель": "Developer", "Позитивность": "Positivity",
    "Интеллекция": "Intellection", "Осторожный": "Deliberative",
    "Командный": "Command", "Учёба": "Learner",
    "Максимализм": "Maximizer", "Перспективное мышление": "Futuristic",
    "Достиженчество": "Achiever", "Связанность": "Connectedness",
    "Аранжировщик": "Arranger", "Включатель": "Includer",
}

RU_TO_EN.update(_official)
RU_TO_EN.update(_alternatives)

VALID_EN = {
    "Achiever", "Activator", "Adaptability", "Analytical", "Arranger", "Belief",
    "Command", "Communication", "Competition", "Connectedness", "Consistency", "Context",
    "Deliberative", "Developer", "Discipline", "Empathy", "Focus", "Futuristic",
    "Harmony", "Ideation", "Includer", "Individualization", "Input", "Intellection",
    "Learner", "Maximizer", "Positivity", "Relator", "Responsibility", "Restorative",
    "Self-Assurance", "Significance", "Strategic", "Woo",
}

# Sort RU keys by length descending for greedy matching
_ru_keys_sorted = sorted(RU_TO_EN.keys(), key=len, reverse=True)

CATEGORY_MAP = {
    "усиливающ": "synergy",
    "усиливают": "synergy",
    "продуктивн": "productive_tension",
    "компенсирующ": "compensating",
    "статистическ": "statistical",
    "дополняющ": "complementary",
    "наиболее вероятн": "statistical",
    "наиболее редк": "statistical_rare",
    "статистически вероятн": "statistical",
    "статистически редк": "statistical_rare",
    "маловероятн": "statistical_rare",
    "взаимодополняющ": "complementary",
    "взаимодополн": "complementary",
    "друг": "synergy",
    "умеряющ": "moderating",
    "умеряют": "moderating",
    "слабая совместимость": "low_compatibility",
    "смягчающ": "moderating",
    "естественн": "synergy",
    "без исполнительск": "synergy",
}


def normalize_theme(name: str) -> str | None:
    name = name.strip()
    if not name:
        return None
    if name in VALID_EN:
        return name
    if name in RU_TO_EN:
        return RU_TO_EN[name]
    for ru, en in RU_TO_EN.items():
        if ru.lower() == name.lower():
            return en
    for en in VALID_EN:
        if en.lower() == name.lower():
            return en
    return None


def find_themes_in_text(text: str) -> list[str]:
    """Find all theme names (EN or RU) in a text string. Returns list of EN names."""
    found = []
    # Check English names first (word boundary)
    for en in sorted(VALID_EN, key=len, reverse=True):
        if re.search(r'\b' + re.escape(en) + r'\b', text):
            if en not in found:
                found.append(en)

    # Check Russian names (longest first to avoid partial matches)
    remaining = text
    for ru in _ru_keys_sorted:
        if ru in remaining:
            en = RU_TO_EN[ru]
            if en not in found:
                found.append(en)
    return found


def clean_text(text: str) -> str:
    text = re.sub(r'\*\*', '', text)
    text = re.sub(r'\*', '', text)
    text = re.sub(r'\[S\d+(?:,\s*S\d+)*\]', '', text)
    text = re.sub(r'>\s*"', '', text)
    text = re.sub(r'"\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def extract_frequency(text: str) -> str | None:
    m = re.search(r'(\d+)\s*%', text)
    if m:
        return m.group(1) + "%"
    return None


def detect_category(header: str) -> str:
    h = header.lower()
    for key, cat in sorted(CATEGORY_MAP.items(), key=lambda x: -len(x[0])):
        if key in h:
            return cat
    return "synergy"


def is_category_header(line: str, file_theme_en: str) -> bool:
    """Check if a line is a category/section header (not a combination entry)."""
    # Must be H3 or bold text
    if not (line.startswith('###') or line.startswith('**')):
        return False
    # If it contains "+", it's likely a combination
    if '+' in line:
        return False
    # If it contains a theme name other than file theme, it might be a single-theme combo header
    themes = find_themes_in_text(line)
    other_themes = [t for t in themes if t != file_theme_en]
    if other_themes:
        return False
    # Check for known category keywords
    h = line.lower()
    category_keywords = [
        "усиливающ", "усиливают", "продуктивн", "компенсирующ", "статистическ",
        "дополняющ", "наиболее", "маловероятн", "взаимодополняющ",
        "друг", "сочетан", "комбинац", "пар", "редк", "частые партнёр",
        "умеряющ", "умеряют", "слабая совместимость", "смягчающ",
        "взаимодополн", "естественн", "таланты,", "партнёрств",
        "без исполнительск",
    ]
    for kw in category_keywords:
        if kw in h:
            return True
    return False


def extract_pair_from_line(line: str, file_theme_en: str):
    """Try to extract a theme pair from a line. Returns (theme_a, theme_b) or None."""
    # Strip leading bullet
    clean_line = re.sub(r'^[-*]\s+', '', line)

    # Bullet list format: - **ThemeName (EN):** description
    bullet_bold = re.match(r'^[-*]\s+\*\*([^*]+)\*\*', line)
    if bullet_bold:
        content = bullet_bold.group(1).strip().rstrip(':')
        themes = find_themes_in_text(content)
        other = [t for t in themes if t != file_theme_en]
        if other:
            return file_theme_en, other[0]

    # Strategy: find all theme references in the line
    # If "+" is present, try to split on it
    if '+' in clean_line:
        # Find text around "+"
        # Pattern: something + something
        plus_match = re.search(r'([^+|]{2,})\+([^+|]{2,})', clean_line)
        if plus_match:
            left = plus_match.group(1).strip().strip('*# |')
            right = plus_match.group(2).strip().strip('*# |')
            # Clean parenthetical
            left = re.sub(r'\([^)]*\)\s*$', '', left).strip()
            right = re.sub(r'\([^)]*\)\s*$', '', right).strip()
            right = re.sub(r'\s*[:—].*$', '', right).strip()

            a_en = normalize_theme(left)
            b_en = normalize_theme(right)
            if a_en and b_en:
                return a_en, b_en

            # Try finding themes in each side
            left_themes = find_themes_in_text(plus_match.group(1))
            right_themes = find_themes_in_text(plus_match.group(2))
            if left_themes and right_themes:
                return left_themes[0], right_themes[0]

    # Table row: | **ThemeName (RU)** | description |
    table_match = re.match(r'\|\s*\*?\*?(.+?)\*?\*?\s*\|(.+)\|', line)
    if table_match:
        cell = table_match.group(1).strip()
        themes = find_themes_in_text(cell)
        other = [t for t in themes if t != file_theme_en]
        if other:
            return file_theme_en, other[0]

    # Bold single theme: **ThemeName** (description)  or **ThemeName** (EN — desc):
    bold_match = re.match(r'^\*\*([^*]+)\*\*', line)
    if bold_match:
        content = bold_match.group(1).strip()
        themes = find_themes_in_text(content)
        other = [t for t in themes if t != file_theme_en]
        if other:
            return file_theme_en, other[0]

    # H3 with theme name: ### ThemeRU (ThemeEN)
    h3_match = re.match(r'^###\s+(.+)', line)
    if h3_match:
        content = h3_match.group(1).strip()
        themes = find_themes_in_text(content)
        if len(themes) >= 2:
            return themes[0], themes[1]
        other = [t for t in themes if t != file_theme_en]
        if other:
            return file_theme_en, other[0]

    return None


def get_section7(lines: list[str]) -> list[str]:
    start = None
    end = None
    for i, line in enumerate(lines):
        if re.match(r'^## 7[\.\s]', line):
            start = i
        elif start is not None and re.match(r'^## \d', line) and not re.match(r'^## 7', line):
            end = i
            break
    if start is None:
        return []
    if end is None:
        end = len(lines)
    # Trim trailing source footnotes and separators
    while end > start and (not lines[end - 1].strip() or lines[end - 1].strip().startswith('*Источник') or lines[end - 1].strip().startswith('*Составлен') or lines[end - 1].strip().startswith('*Методолог') or lines[end - 1].strip() == '---'):
        end -= 1
    return lines[start:end]


def parse_combinations(filepath: Path, file_theme_en: str):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    section7 = get_section7([l.rstrip('\n') for l in lines])
    if not section7:
        print(f"  WARNING: No section 7 found in {filepath.name}")
        return []

    results = []
    current_category = "synergy"
    current_entry = None
    current_text_lines = []

    def flush_entry():
        nonlocal current_entry, current_text_lines
        if current_entry:
            text = clean_text('\n'.join(current_text_lines))
            freq = extract_frequency(text)
            current_entry['text'] = text
            current_entry['frequency'] = freq
            results.append(current_entry)
        current_entry = None
        current_text_lines = []

    for line in section7:
        stripped = line.strip()

        # Skip section header
        if re.match(r'^## 7', line):
            continue

        # Skip empty lines
        if not stripped:
            continue

        # Skip table separator
        if re.match(r'^\|[-\s|]+\|$', stripped):
            continue

        # Skip table header with column names
        if re.match(r'^\|\s*(Партнёрский|Сочетание|Партнёр)', stripped):
            continue

        # Skip source footnotes
        if re.match(r'^\*Источник', stripped) or re.match(r'^\*Составлен', stripped) or re.match(r'^\*Методолог', stripped):
            continue

        # Skip --- separator
        if re.match(r'^---', stripped):
            continue

        # Skip blockquotes (these are supporting quotes, not entries)
        if stripped.startswith('>'):
            if current_entry:
                current_text_lines.append(stripped.lstrip('> ').strip('"'))
            continue

        # Skip "Итоговый фрейм" or similar concluding headers
        if re.match(r'^##\s+Итог', stripped):
            flush_entry()
            break

        # Check if this is a category header
        if is_category_header(stripped, file_theme_en):
            flush_entry()
            current_category = detect_category(stripped)
            continue

        # Try to extract a theme pair
        pair = extract_pair_from_line(stripped, file_theme_en)

        if pair:
            flush_entry()
            theme_a, theme_b = pair

            # Extract description text from the line
            text_part = stripped
            # Remove H3 prefix
            text_part = re.sub(r'^###\s+', '', text_part)
            # For table rows, extract the description cell
            if '|' in text_part and not text_part.startswith('**'):
                parts = text_part.split('|')
                # Usually: | theme | description |
                if len(parts) >= 3:
                    text_part = parts[2].strip()
                else:
                    text_part = parts[-1].strip()
            else:
                # Remove the bold theme pair part
                # Try to remove everything up to the closing ** or ) followed by : or —
                text_part = re.sub(r'^\*\*[^*]+\*\*\s*', '', text_part)
                text_part = re.sub(r'^\([^)]+\)\s*', '', text_part)
            # Remove leading separators
            text_part = re.sub(r'^[\s—:]+', '', text_part).strip()

            current_entry = {
                'theme_a': theme_a,
                'theme_b': theme_b,
                'category': current_category,
            }
            if text_part:
                current_text_lines = [text_part]
            else:
                current_text_lines = []
        elif current_entry:
            # Continuation text for current entry
            if stripped:
                current_text_lines.append(stripped)

    flush_entry()
    return results


def main():
    all_entries = []
    files = sorted(THEMES_DIR.glob("*_ru.md"))
    print(f"Found {len(files)} files\n")

    # Map filenames to English theme names
    name_map = {}
    for en in VALID_EN:
        name_map[en.lower().replace('-', '')] = en

    for filepath in files:
        stem = filepath.stem.replace('_ru', '')
        key = stem.lower().replace('-', '')
        theme_en = name_map.get(key)
        if not theme_en:
            print(f"  WARNING: Cannot map filename {filepath.name} to English theme")
            continue

        entries = parse_combinations(filepath, theme_en)
        print(f"  {filepath.name}: {len(entries)} combinations (theme: {theme_en})")
        all_entries.append((theme_en, entries))

    # Build merged dictionary
    combinations = {}
    for file_theme, entries in all_entries:
        for entry in entries:
            a, b = entry['theme_a'], entry['theme_b']
            if a == b:
                continue
            key = '|'.join(sorted([a, b]))

            if key not in combinations:
                combinations[key] = {
                    'category': entry['category'],
                    'text': entry['text'],
                    'frequency': entry['frequency'],
                }
            else:
                existing = combinations[key]
                if entry['text'] and entry['text'] not in existing['text']:
                    if existing['text']:
                        existing['text'] += '\n\n---\n\n' + entry['text']
                    else:
                        existing['text'] = entry['text']
                if entry['frequency'] and not existing['frequency']:
                    existing['frequency'] = entry['frequency']
                if existing['category'] == 'synergy' and entry['category'] != 'synergy':
                    existing['category'] = entry['category']

    combinations = dict(sorted(combinations.items()))

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(combinations, f, ensure_ascii=False, indent=2)

    total = len(combinations)
    with_freq = sum(1 for v in combinations.values() if v['frequency'])
    by_category = {}
    for v in combinations.values():
        cat = v['category']
        by_category[cat] = by_category.get(cat, 0) + 1

    print(f"\n{'='*50}")
    print(f"Total unique pairs: {total}")
    print(f"Pairs with frequency data: {with_freq}")
    print(f"\nPairs by category:")
    for cat, count in sorted(by_category.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")
    print(f"\nOutput written to: {OUTPUT_FILE}")


if __name__ == '__main__':
    main()
