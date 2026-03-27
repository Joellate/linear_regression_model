import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Rwanda Crop Yield Predictor',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF2E7D32)),
        useMaterial3: true,
      ),
      home: const PredictionPage(),
    );
  }
}

class PredictionPage extends StatefulWidget {
  const PredictionPage({super.key});

  @override
  State<PredictionPage> createState() => _PredictionPageState();
}

class _PredictionPageState extends State<PredictionPage> {
  final _formKey = GlobalKey<FormState>();

  final _soilQualityController      = TextEditingController();
  final _seedVarietyController      = TextEditingController();
  final _fertilizerController       = TextEditingController();
  final _sunnyDaysController        = TextEditingController();
  final _rainfallController         = TextEditingController();
  final _irrigationController       = TextEditingController();

  String _result = '';
  bool _isLoading = false;

  @override
  void dispose() {
    _soilQualityController.dispose();
    _seedVarietyController.dispose();
    _fertilizerController.dispose();
    _sunnyDaysController.dispose();
    _rainfallController.dispose();
    _irrigationController.dispose();
    super.dispose();
  }

  Future<void> _predict() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
      _result = '';
    });

    try {
      final body = jsonEncode({
        'soil_quality':         double.parse(_soilQualityController.text.trim()),
        'seed_variety':         int.parse(_seedVarietyController.text.trim()),
        'fertilizer_kg_per_ha': double.parse(_fertilizerController.text.trim()),
        'sunny_days':           double.parse(_sunnyDaysController.text.trim()),
        'rainfall_mm':          double.parse(_rainfallController.text.trim()),
        'irrigation_schedule':  int.parse(_irrigationController.text.trim()),
      });

      debugPrint('REQUEST BODY: $body');

      final response = await http.post(
        Uri.parse('https://rwanda-yield-api.onrender.com/predict'),
        headers: {'Content-Type': 'application/json'},
        body: body,
      ).timeout(const Duration(seconds: 60));

      debugPrint('STATUS: ${response.statusCode}');
      debugPrint('RESPONSE: ${response.body}');

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _result = '🌾 Predicted Yield: ${data['predicted_yield_kg_per_hectare']} kg/hectare';
        });
      } else {
        setState(() {
          _result = '❌ Status ${response.statusCode}: ${response.body}';
        });
      }
    } on TimeoutException {
      setState(() {
        _result = '⏳ Server timed out. Open https://rwanda-yield-api.onrender.com/docs in browser first to wake it up, then try again.';
      });
    } catch (e) {
      debugPrint('EXCEPTION: $e');
      setState(() {
        _result = '❌ Exception: $e';
      });
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Widget _buildField({
    required String label,
    required String hint,
    required TextEditingController controller,
    required String validatorHint,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: TextFormField(
        controller: controller,
        keyboardType: const TextInputType.numberWithOptions(decimal: true),
        decoration: InputDecoration(
          labelText: label,
          hintText: hint,
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
          filled: true,
          fillColor: Colors.grey.shade50,
        ),
        validator: (value) {
          if (value == null || value.trim().isEmpty) {
            return 'Please enter $label';
          }
          if (double.tryParse(value) == null) {
            return 'Enter a valid number';
          }
          return null;
        },
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade100,
      appBar: AppBar(
        backgroundColor: const Color(0xFF2E7D32),
        title: const Text(
          '🌾 Rwanda Crop Yield Predictor',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Text(
                  'Enter farming details to predict crop yield',
                  style: TextStyle(fontSize: 15, color: Colors.black54),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 20),
                _buildField(
                  label: 'Soil Quality',
                  hint: '50 – 100',
                  controller: _soilQualityController,
                  validatorHint: '50–100',
                ),
                _buildField(
                  label: 'Seed Variety',
                  hint: '0 = Traditional, 1 = Improved',
                  controller: _seedVarietyController,
                  validatorHint: '0 or 1',
                ),
                _buildField(
                  label: 'Fertilizer (kg/hectare)',
                  hint: '0 – 300',
                  controller: _fertilizerController,
                  validatorHint: '0–300',
                ),
                _buildField(
                  label: 'Sunny Days',
                  hint: '0 – 365',
                  controller: _sunnyDaysController,
                  validatorHint: '0–365',
                ),
                _buildField(
                  label: 'Rainfall (mm)',
                  hint: '0 – 3000',
                  controller: _rainfallController,
                  validatorHint: '0–3000',
                ),
                _buildField(
                  label: 'Irrigation Schedule',
                  hint: '0 – 15',
                  controller: _irrigationController,
                  validatorHint: '0–15',
                ),
                const SizedBox(height: 10),
                ElevatedButton(
                  onPressed: _isLoading ? null : _predict,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF2E7D32),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                  child: _isLoading
                      ? const SizedBox(
                          height: 22,
                          width: 22,
                          child: CircularProgressIndicator(
                            color: Colors.white,
                            strokeWidth: 2.5,
                          ),
                        )
                      : const Text(
                          'Predict',
                          style: TextStyle(fontSize: 17, fontWeight: FontWeight.bold),
                        ),
                ),
                const SizedBox(height: 24),
                if (_result.isNotEmpty)
                  Container(
                    padding: const EdgeInsets.all(18),
                    decoration: BoxDecoration(
                      color: _result.startsWith('🌾')
                          ? const Color(0xFFE8F5E9)
                          : const Color(0xFFFFEBEE),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: _result.startsWith('🌾')
                            ? const Color(0xFF2E7D32)
                            : Colors.redAccent,
                      ),
                    ),
                    child: Text(
                      _result,
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: _result.startsWith('🌾')
                            ? const Color(0xFF2E7D32)
                            : Colors.redAccent,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
