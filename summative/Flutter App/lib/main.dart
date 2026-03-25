import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

// ── IMPORTANT: Replace with your live Render URL ──────────────────────────
const String kApiBaseUrl = 'https://your-app-name.onrender.com';
// ─────────────────────────────────────────────────────────────────────────

void main() => runApp(const WLBApp());

class WLBApp extends StatelessWidget {
  const WLBApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'WLB Score Predictor',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF2E7D8C),
          brightness: Brightness.light,
        ),
        useMaterial3: true,
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: Colors.grey.shade50,
          contentPadding:
              const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
          errorStyle: const TextStyle(fontSize: 11),
        ),
      ),
      home: const PredictionPage(),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────
// Data model
// ─────────────────────────────────────────────────────────────────────────
class _FieldConfig {
  final String key;
  final String label;
  final String hint;
  final int min;
  final int max;
  final bool isFloat;

  const _FieldConfig({
    required this.key,
    required this.label,
    required this.hint,
    required this.min,
    required this.max,
    this.isFloat = false,
  });
}

const List<_FieldConfig> kFields = [
  _FieldConfig(key: 'FRUITS_VEGGIES',    label: 'Fruits & Veggies',       hint: '0–10 portions/day',        min: 0,  max: 10),
  _FieldConfig(key: 'DAILY_STRESS',      label: 'Daily Stress',           hint: '0–10',                     min: 0,  max: 10, isFloat: true),
  _FieldConfig(key: 'PLACES_VISITED',    label: 'Places Visited/month',   hint: '0–10',                     min: 0,  max: 10),
  _FieldConfig(key: 'CORE_CIRCLE',       label: 'Core Circle Size',       hint: '0–10',                     min: 0,  max: 10),
  _FieldConfig(key: 'SUPPORTING_OTHERS', label: 'Supporting Others',      hint: '0–10 hrs/week',            min: 0,  max: 10),
  _FieldConfig(key: 'SOCIAL_NETWORK',    label: 'Social Network Score',   hint: '0–10',                     min: 0,  max: 10),
  _FieldConfig(key: 'ACHIEVEMENT',       label: 'Achievement Score',      hint: '0–10',                     min: 0,  max: 10),
  _FieldConfig(key: 'DONATION',          label: 'Donation Score',         hint: '0–10',                     min: 0,  max: 10),
  _FieldConfig(key: 'BMI_RANGE',         label: 'BMI Range',              hint: '1=Underweight … 5=Obese',  min: 1,  max: 5),
  _FieldConfig(key: 'TODO_COMPLETED',    label: 'To-Do Completed',        hint: '0–10',                     min: 0,  max: 10),
  _FieldConfig(key: 'FLOW',              label: 'Flow / Focus',           hint: '0–10',                     min: 0,  max: 10),
  _FieldConfig(key: 'DAILY_STEPS',       label: 'Daily Steps',            hint: '0–30000',                  min: 0,  max: 30000),
  _FieldConfig(key: 'LIVE_VISION',       label: 'Life Vision Clarity',    hint: '0–10',                     min: 0,  max: 10),
  _FieldConfig(key: 'SLEEP_HOURS',       label: 'Sleep Hours/night',      hint: '1–12',                     min: 1,  max: 12),
  _FieldConfig(key: 'LOST_VACATION',     label: 'Lost Vacation Days',     hint: '0–10 days',                min: 0,  max: 10),
  _FieldConfig(key: 'DAILY_SHOUTING',    label: 'Daily Shouting',         hint: '0–10 times',               min: 0,  max: 10),
  _FieldConfig(key: 'SUFFICIENT_INCOME', label: 'Sufficient Income',      hint: '1=No, 2=Yes',              min: 1,  max: 2),
  _FieldConfig(key: 'PERSONAL_AWARDS',   label: 'Personal Awards',        hint: '0–10',                     min: 0,  max: 10),
  _FieldConfig(key: 'TIME_FOR_PASSION',  label: 'Time for Passion',       hint: '0–10 hrs/week',            min: 0,  max: 10),
  _FieldConfig(key: 'WEEKLY_MEDITATION', label: 'Weekly Meditation',      hint: '0–10 sessions',            min: 0,  max: 10),
  _FieldConfig(key: 'AGE_51_or_more',    label: 'Age 51 or more?',        hint: '0=No, 1=Yes',              min: 0,  max: 1),
];

// ─────────────────────────────────────────────────────────────────────────
// Main page
// ─────────────────────────────────────────────────────────────────────────
class PredictionPage extends StatefulWidget {
  const PredictionPage({super.key});

  @override
  State<PredictionPage> createState() => _PredictionPageState();
}

class _PredictionPageState extends State<PredictionPage> {
  final _formKey = GlobalKey<FormState>();
  final Map<String, TextEditingController> _controllers = {
    for (final f in kFields) f.key: TextEditingController(),
  };

  bool   _loading     = false;
  String _resultText  = '';
  Color  _resultColor = Colors.black87;
  bool   _hasResult   = false;

  // ── API call ────────────────────────────────────────────────────────────
  Future<void> _predict() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _loading    = true;
      _hasResult  = false;
      _resultText = '';
    });

    // Build JSON body
    final Map<String, dynamic> body = {};
    for (final f in kFields) {
      final raw = _controllers[f.key]!.text.trim();
      body[f.key] = f.isFloat ? double.parse(raw) : int.parse(raw);
    }

    try {
      final response = await http
          .post(
            Uri.parse('$kApiBaseUrl/predict'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode(body),
          )
          .timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final double score = (data['predicted_work_life_balance_score'] as num).toDouble();
        final String interp = data['interpretation'] as String;

        Color c;
        if (score >= 700)      c = const Color(0xFF2E7D32); // green
        else if (score >= 620) c = const Color(0xFF1565C0); // blue
        else if (score >= 540) c = const Color(0xFFE65100); // orange
        else                   c = const Color(0xFFC62828); // red

        setState(() {
          _resultText  = '🎯 Predicted Score: ${score.toStringAsFixed(2)}\n\n$interp';
          _resultColor = c;
          _hasResult   = true;
        });
      } else {
        final err = jsonDecode(response.body);
        setState(() {
          _resultText  = '⚠️ Error ${response.statusCode}: ${err['detail'] ?? 'Unknown error'}';
          _resultColor = Colors.red.shade700;
          _hasResult   = true;
        });
      }
    } catch (e) {
      setState(() {
        _resultText  = '❌ Network error: $e\n\nCheck your API URL and internet connection.';
        _resultColor = Colors.red.shade700;
        _hasResult   = true;
      });
    } finally {
      setState(() => _loading = false);
    }
  }

  void _resetForm() {
    for (final c in _controllers.values) c.clear();
    setState(() {
      _hasResult  = false;
      _resultText = '';
    });
  }

  // ── Validation ──────────────────────────────────────────────────────────
  String? _validate(String? value, _FieldConfig f) {
    if (value == null || value.trim().isEmpty) return 'Required';
    final num? n = num.tryParse(value.trim());
    if (n == null) return 'Must be a number';
    if (n < f.min || n > f.max) return 'Range: ${f.min}–${f.max}';
    return null;
  }

  // ── UI ───────────────────────────────────────────────────────────────────
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: const Color(0xFFF0F4F5),
      appBar: AppBar(
        backgroundColor: const Color(0xFF2E7D8C),
        foregroundColor: Colors.white,
        title: const Text(
          'Work-Life Balance Predictor',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 17),
        ),
        centerTitle: true,
        elevation: 3,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 20),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // ── Header card ──────────────────────────────────────────
              Card(
                color: const Color(0xFF2E7D8C).withOpacity(0.08),
                elevation: 0,
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12)),
                child: const Padding(
                  padding: EdgeInsets.all(14),
                  child: Text(
                    'Enter your lifestyle data below to predict your '
                    'Work-Life Balance Score (range: 480–820).',
                    style: TextStyle(fontSize: 13.5, color: Color(0xFF37474F)),
                    textAlign: TextAlign.center,
                  ),
                ),
              ),
              const SizedBox(height: 20),

              // ── Input fields ─────────────────────────────────────────
              ...kFields.map((f) => Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          f.label,
                          style: TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w600,
                            color: theme.colorScheme.primary,
                          ),
                        ),
                        const SizedBox(height: 4),
                        TextFormField(
                          controller: _controllers[f.key],
                          keyboardType: f.isFloat
                              ? const TextInputType.numberWithOptions(decimal: true)
                              : TextInputType.number,
                          decoration: InputDecoration(
                            hintText: f.hint,
                            hintStyle: TextStyle(
                                fontSize: 12, color: Colors.grey.shade500),
                          ),
                          validator: (v) => _validate(v, f),
                        ),
                      ],
                    ),
                  )),

              const SizedBox(height: 8),

              // ── Predict button ────────────────────────────────────────
              SizedBox(
                height: 52,
                child: ElevatedButton(
                  onPressed: _loading ? null : _predict,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2E7D8C),
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12)),
                    elevation: 2,
                  ),
                  child: _loading
                      ? const SizedBox(
                          height: 22,
                          width: 22,
                          child: CircularProgressIndicator(
                              color: Colors.white, strokeWidth: 2.5),
                        )
                      : const Text(
                          'Predict',
                          style: TextStyle(
                              fontSize: 16, fontWeight: FontWeight.bold),
                        ),
                ),
              ),
              const SizedBox(height: 10),

              // ── Reset button ─────────────────────────────────────────
              TextButton(
                onPressed: _resetForm,
                child: const Text('Reset Fields',
                    style: TextStyle(color: Color(0xFF607D8B))),
              ),
              const SizedBox(height: 14),

              // ── Result display area ───────────────────────────────────
              AnimatedSwitcher(
                duration: const Duration(milliseconds: 300),
                child: _hasResult
                    ? Card(
                        key: const ValueKey('result'),
                        color: _resultColor.withOpacity(0.08),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                          side: BorderSide(color: _resultColor, width: 1.4),
                        ),
                        child: Padding(
                          padding: const EdgeInsets.all(18),
                          child: Text(
                            _resultText,
                            style: TextStyle(
                              color: _resultColor,
                              fontSize: 15,
                              fontWeight: FontWeight.w600,
                              height: 1.5,
                            ),
                            textAlign: TextAlign.center,
                          ),
                        ),
                      )
                    : const SizedBox.shrink(key: ValueKey('empty')),
              ),
              const SizedBox(height: 30),
            ],
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    for (final c in _controllers.values) c.dispose();
    super.dispose();
  }
}