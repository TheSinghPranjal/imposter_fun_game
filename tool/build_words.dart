// Builds and validates assets/data/imposter_words.json from tool/words/*.txt.
//
//   dart run tool/build_words.dart                 build, validate, write
//   dart run tool/build_words.dart --check <file>  validate an existing pack
//
// Exits non-zero on wrong counts, duplicate IDs or words, empty fields, or a
// hint that contains or spells the word.
import 'dart:convert';
import 'dart:io';

const expectedCounts = {'easy': 400, 'medium': 300, 'hard': 200};
const outputPath = 'assets/data/imposter_words.json';

void main(List<String> args) {
  if (args.length == 2 && args.first == '--check') {
    final raw = jsonDecode(File(args[1]).readAsStringSync()) as List<dynamic>;
    final entries = raw.cast<Map<String, dynamic>>();
    _report(validate(entries));
    stdout.writeln('OK: ${entries.length} entries in ${args[1]}');
    return;
  }
  final entries = <Map<String, dynamic>>[
    for (final difficulty in expectedCounts.keys) ..._parse(difficulty),
  ];
  _report(validate(entries));
  File(outputPath)
    ..createSync(recursive: true)
    ..writeAsStringSync(
      '[\n${entries.map(jsonEncode).join(',\n')}\n]\n',
    );
  stdout.writeln('Wrote ${entries.length} entries to $outputPath');
}

List<Map<String, dynamic>> _parse(String difficulty) {
  final out = <Map<String, dynamic>>[];
  var category = '';
  var categoryTag = '';
  final lines = File('tool/words/$difficulty.txt').readAsLinesSync();
  for (final raw in lines) {
    final line = raw.trim();
    if (line.isEmpty || line.startsWith('# Format')) continue;
    if (line.startsWith('#')) {
      final parts = line.substring(1).trim().split(RegExp(r'\s+'));
      category = parts[0];
      categoryTag = parts.length > 1 ? parts[1] : parts[0];
      continue;
    }
    final fields = line.split('|');
    final number = (out.length + 1).toString().padLeft(3, '0');
    out.add({
      'id': '${difficulty}_$number',
      'difficulty': difficulty,
      'category': category,
      'word': fields[0].trim(),
      'hint': fields.length > 1 ? fields[1].trim() : '',
      'tags': <String>{
        category,
        categoryTag,
        if (fields.length > 2) ...fields[2].split(',').map((t) => t.trim()),
      }.toList(),
    });
  }
  return out;
}

String _letters(String s) =>
    s.toLowerCase().replaceAll(RegExp(r'[^a-z0-9]'), '');

String _sorted(String s) => (s.split('')..sort()).join();

List<String> validate(List<Map<String, dynamic>> entries) {
  final errors = <String>[];
  final counts = <String, int>{};
  final ids = <String>{};
  final words = <String>{};

  for (final e in entries) {
    final id = '${e['id'] ?? ''}';
    final difficulty = '${e['difficulty'] ?? ''}';
    final word = '${e['word'] ?? ''}'.trim();
    final hint = '${e['hint'] ?? ''}'.trim();
    final category = '${e['category'] ?? ''}'.trim();
    final label = id.isEmpty ? word : id;

    counts[difficulty] = (counts[difficulty] ?? 0) + 1;
    if (id.isEmpty) errors.add('empty id for "$word"');
    if (!ids.add(id)) errors.add('duplicate id: $id');
    if (!id.startsWith('${difficulty}_')) {
      errors.add('$label: id does not match difficulty "$difficulty"');
    }
    if (word.isEmpty) errors.add('$label: empty word');
    if (hint.isEmpty) errors.add('$label: empty hint');
    if (category.isEmpty) errors.add('$label: empty category');
    if (e['tags'] is! List || (e['tags'] as List).isEmpty) {
      errors.add('$label: empty tags');
    }
    if (word.isNotEmpty && !words.add(word.toLowerCase())) {
      errors.add('$label: duplicate word "$word"');
    }
    if (word.isEmpty || hint.isEmpty) continue;

    if (hint.split(RegExp(r'\s+')).length > 2) {
      errors.add('$label: hint over 2 words: "$hint"');
    }
    final w = _letters(word);
    final h = _letters(hint);
    if (h.contains(w)) errors.add('$label: hint contains word: "$hint"');
    if (_sorted(h) == _sorted(w)) errors.add('$label: hint spells word: "$hint"');
    for (final part in word.toLowerCase().split(RegExp(r'[^a-z0-9]+'))) {
      if (part.length >= 4 && h.contains(part)) {
        errors.add('$label: hint reuses "$part": "$hint"');
      }
    }
    for (final part in hint.toLowerCase().split(RegExp(r'[^a-z0-9]+'))) {
      if (part.length >= 4 && w.contains(part)) {
        errors.add('$label: word contains hint part "$part": "$word"');
      }
    }
  }

  expectedCounts.forEach((difficulty, expected) {
    final actual = counts[difficulty] ?? 0;
    if (actual != expected) {
      errors.add('$difficulty: expected $expected entries, found $actual');
    }
  });
  for (final d in counts.keys) {
    if (!expectedCounts.containsKey(d)) errors.add('unknown difficulty: "$d"');
  }
  return errors;
}

void _report(List<String> errors) {
  if (errors.isEmpty) return;
  stderr.writeln('Word pack invalid (${errors.length} problems):');
  errors.forEach(stderr.writeln);
  exit(1);
}
