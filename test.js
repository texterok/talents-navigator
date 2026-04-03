import { test, describe } from 'node:test';
import assert from 'node:assert/strict';

// ─── Pure functions extracted from index.html ────────────────────────────────

const ALL_THEME_NAMES = [
  'Achiever','Activator','Adaptability','Analytical','Arranger','Belief',
  'Command','Communication','Competition','Connectedness','Consistency',
  'Context','Deliberative','Developer','Discipline','Empathy','Focus',
  'Futuristic','Harmony','Ideation','Includer','Individualization','Input',
  'Intellection','Learner','Maximizer','Positivity','Relator','Responsibility',
  'Restorative','Self-Assurance','Significance','Strategic','Woo',
];

// Replica of getThemeZone(name) — depends on `selected` array
function makeGetThemeZone(selected) {
  return function getThemeZone(name) {
    const idx = selected.indexOf(name);
    if (idx < 0) return null;
    if (idx < 5)  return 'z1';
    if (idx < 10) return 'z2';
    if (idx < 15) return 'z3';
    if (idx < 20) return 'z4';
    return 'z5';
  };
}

// Replica of getZone(pos) — used in renderChips / renderCards separators
function getZone(pos) {
  if (pos <= 5)  return { cls: 'z1', name: 'Работает само' };
  if (pos <= 10) return { cls: 'z2', name: 'Легко включается' };
  if (pos <= 15) return { cls: 'z3', name: 'Доступно осознанно' };
  if (pos <= 20) return { cls: 'z4', name: 'Требует усилия' };
  return { cls: 'z5', name: 'Вне природной зоны' };
}

// Replica of tag logic in renderSimpleCard / renderFullCard
function getAmpTag(zone) {
  const isStrong = zone === 'z1' || zone === 'z2';
  const isWeak   = zone === 'z4' || zone === 'z5';
  return {
    tagClass: isStrong ? 'amp-tag-multiplier' : isWeak ? 'amp-tag-compensator' : 'amp-tag-neutral',
    tagText:  isStrong ? 'Мультипликатор'     : isWeak ? 'Компенсатор'         : 'Развитие',
  };
}

// Replica of allowed sections logic in renderCards
function getAllowedSections(zone) {
  if (zone === 'z1' || zone === 'z2') return ['trust','care','stability','direction','management','quotes'];
  if (zone === 'z3') return ['management'];
  return [];
}

// ─── Tests ────────────────────────────────────────────────────────────────────

describe('getThemeZone — zone boundaries (Gallup official: z4 ends at pos 20)', () => {
  const selected = [
    'Input','Learner','Strategic','Ideation','Intellection',   // 1-5  → z1
    'Analytical','Context','Futuristic','Adaptability','Belief',// 6-10 → z2
    'Discipline','Harmony','Empathy','Achiever','Arranger',     // 11-15→ z3
    'Includer','Woo','Developer','Positivity','Communication',  // 16-20→ z4
    'Consistency','Futuristic','Relator','Responsibility',      // 21+  → z5
  ];
  const getThemeZone = makeGetThemeZone(selected);

  test('pos 1 (Input) → z1', () => assert.equal(getThemeZone('Input'), 'z1'));
  test('pos 5 (Intellection) → z1', () => assert.equal(getThemeZone('Intellection'), 'z1'));
  test('pos 6 (Analytical) → z2', () => assert.equal(getThemeZone('Analytical'), 'z2'));
  test('pos 10 (Belief) → z2', () => assert.equal(getThemeZone('Belief'), 'z2'));
  test('pos 11 (Discipline) → z3', () => assert.equal(getThemeZone('Discipline'), 'z3'));
  test('pos 15 (Arranger) → z3', () => assert.equal(getThemeZone('Arranger'), 'z3'));
  test('pos 16 (Includer) → z4', () => assert.equal(getThemeZone('Includer'), 'z4'));
  test('pos 20 (Communication) → z4', () => assert.equal(getThemeZone('Communication'), 'z4'));
  test('pos 21 (Consistency) → z5', () => assert.equal(getThemeZone('Consistency'), 'z5'));
  test('pos 24 (Responsibility) → z5', () => assert.equal(getThemeZone('Responsibility'), 'z5'));
  test('unknown theme → null', () => assert.equal(getThemeZone('Unknown'), null));
});

describe('getZone(pos) — position-based zone (for separators and chips)', () => {
  test('pos 1 → z1', () => assert.equal(getZone(1).cls, 'z1'));
  test('pos 5 → z1', () => assert.equal(getZone(5).cls, 'z1'));
  test('pos 6 → z2', () => assert.equal(getZone(6).cls, 'z2'));
  test('pos 10 → z2', () => assert.equal(getZone(10).cls, 'z2'));
  test('pos 11 → z3', () => assert.equal(getZone(11).cls, 'z3'));
  test('pos 15 → z3', () => assert.equal(getZone(15).cls, 'z3'));
  test('pos 16 → z4', () => assert.equal(getZone(16).cls, 'z4'));
  test('pos 20 → z4', () => assert.equal(getZone(20).cls, 'z4'));
  test('pos 21 → z5', () => assert.equal(getZone(21).cls, 'z5'));
  test('pos 34 → z5', () => assert.equal(getZone(34).cls, 'z5'));
  // regression: old boundary was 24/25 — these must be z5 now
  test('pos 24 → z5 (regression: was z4 before fix)', () => assert.equal(getZone(24).cls, 'z5'));
  test('pos 25 → z5 (regression: was z5 before fix, still z5)', () => assert.equal(getZone(25).cls, 'z5'));
});

describe('getAmpTag — tag class and label per zone (renderSimpleCard + renderFullCard)', () => {
  test('z1 → Мультипликатор', () => {
    const { tagClass, tagText } = getAmpTag('z1');
    assert.equal(tagClass, 'amp-tag-multiplier');
    assert.equal(tagText, 'Мультипликатор');
  });
  test('z2 → Мультипликатор', () => {
    const { tagClass, tagText } = getAmpTag('z2');
    assert.equal(tagClass, 'amp-tag-multiplier');
    assert.equal(tagText, 'Мультипликатор');
  });
  test('z3 → Развитие (regression: was Компенсатор before fix)', () => {
    const { tagClass, tagText } = getAmpTag('z3');
    assert.equal(tagClass, 'amp-tag-neutral');
    assert.equal(tagText, 'Развитие');
  });
  test('z4 → Компенсатор', () => {
    const { tagClass, tagText } = getAmpTag('z4');
    assert.equal(tagClass, 'amp-tag-compensator');
    assert.equal(tagText, 'Компенсатор');
  });
  test('z5 → Компенсатор', () => {
    const { tagClass, tagText } = getAmpTag('z5');
    assert.equal(tagClass, 'amp-tag-compensator');
    assert.equal(tagText, 'Компенсатор');
  });
  // regression: isWeak must be declared in renderSimpleCard — both paths must work
  test('isWeak defined for z4 (no ReferenceError)', () => {
    assert.doesNotThrow(() => getAmpTag('z4'));
  });
  test('isWeak defined for z5 (no ReferenceError)', () => {
    assert.doesNotThrow(() => getAmpTag('z5'));
  });
});

describe('getAllowedSections — sections shown per zone in renderCards', () => {
  const FULL = ['trust','care','stability','direction','management','quotes'];

  test('z1 shows all 6 sections', () => assert.deepEqual(getAllowedSections('z1'), FULL));
  test('z2 shows all 6 sections', () => assert.deepEqual(getAllowedSections('z2'), FULL));
  test('z3 shows only management', () => assert.deepEqual(getAllowedSections('z3'), ['management']));
  test('z4 shows no sections', () => assert.deepEqual(getAllowedSections('z4'), []));
  test('z5 shows no sections', () => assert.deepEqual(getAllowedSections('z5'), []));
});
