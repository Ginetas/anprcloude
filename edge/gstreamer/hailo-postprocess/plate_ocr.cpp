/**
 * Hailo Post-Processing Plugin: License Plate OCR
 *
 * This plugin processes OCR model outputs using CTC (Connectionist Temporal Classification)
 * decoding to extract license plate text.
 */

#include "hailo_common.hpp"
#include <string>
#include <vector>
#include <algorithm>
#include <cmath>

// Character set for license plates (customize based on your region)
const std::string CHARSET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";
const int BLANK_INDEX = CHARSET.length();  // CTC blank token

struct OCRResult {
    std::string text;
    float confidence;
    std::vector<float> char_confidences;
};

/**
 * CTC Greedy Decoder
 * Decodes CTC output sequence by taking the most likely character at each timestep.
 */
OCRResult ctc_greedy_decode(float* output_data, int timesteps, int num_classes) {
    OCRResult result;
    result.text = "";
    result.char_confidences.clear();

    int prev_char = BLANK_INDEX;
    float total_conf = 0.0f;
    int char_count = 0;

    for (int t = 0; t < timesteps; t++) {
        // Find character with highest probability at this timestep
        int max_idx = 0;
        float max_prob = output_data[t * num_classes];

        for (int c = 1; c < num_classes; c++) {
            float prob = output_data[t * num_classes + c];
            if (prob > max_prob) {
                max_prob = prob;
                max_idx = c;
            }
        }

        // CTC decoding: skip blanks and repeated characters
        if (max_idx != BLANK_INDEX && max_idx != prev_char) {
            if (max_idx < CHARSET.length()) {
                result.text += CHARSET[max_idx];
                result.char_confidences.push_back(max_prob);
                total_conf += max_prob;
                char_count++;
            }
        }

        prev_char = max_idx;
    }

    // Calculate average confidence
    result.confidence = char_count > 0 ? total_conf / char_count : 0.0f;

    return result;
}

/**
 * CTC Beam Search Decoder (more accurate but slower)
 * Considers multiple candidate sequences and returns the most likely one.
 */
OCRResult ctc_beam_search_decode(float* output_data, int timesteps, int num_classes, int beam_width = 5) {
    // Simplified implementation - full beam search would be more complex
    // For production, consider using a library like TensorFlow CTC or similar

    // For now, fall back to greedy decode
    return ctc_greedy_decode(output_data, timesteps, num_classes);
}

/**
 * Post-process and validate plate text
 * Apply regex patterns, length checks, etc.
 */
std::string validate_plate_text(const std::string& text) {
    // Remove any invalid characters
    std::string cleaned;
    for (char c : text) {
        if (CHARSET.find(c) != std::string::npos) {
            cleaned += c;
        }
    }

    // Apply length validation (typical plates: 4-8 characters)
    if (cleaned.length() < 4 || cleaned.length() > 8) {
        return "";  // Invalid plate
    }

    return cleaned;
}

/**
 * Main filter function called by GStreamer hailofilter element.
 *
 * @param output_tensors: OCR model output tensors from Hailo
 * @param roi: Region of interest (cropped plate)
 * @return: Vector of HailoClassification objects with plate text
 */
extern "C" std::vector<HailoClassification> plate_ocr(
    HailoTensorPtr output_tensors,
    HailoROIPtr roi
) {
    std::vector<HailoClassification> results;

    // Configuration
    const float MIN_CONFIDENCE = 0.6f;
    const bool USE_BEAM_SEARCH = false;  // Set to true for better accuracy

    // Get OCR model output tensor
    // Expected format: [timesteps, num_classes]
    // Where num_classes = len(CHARSET) + 1 (blank)
    auto tensor = output_tensors[0];
    float* data = reinterpret_cast<float*>(tensor.data());

    int timesteps = tensor.height();
    int num_classes = tensor.width();

    // Decode CTC output
    OCRResult ocr_result;
    if (USE_BEAM_SEARCH) {
        ocr_result = ctc_beam_search_decode(data, timesteps, num_classes);
    } else {
        ocr_result = ctc_greedy_decode(data, timesteps, num_classes);
    }

    // Validate and clean plate text
    std::string plate_text = validate_plate_text(ocr_result.text);

    if (!plate_text.empty() && ocr_result.confidence >= MIN_CONFIDENCE) {
        HailoClassification classification;
        classification.label = plate_text;
        classification.confidence = ocr_result.confidence;

        // Store per-character confidences in metadata
        classification.metadata["char_confidences"] = ocr_result.char_confidences;
        classification.metadata["raw_text"] = ocr_result.text;

        results.push_back(classification);
    }

    return results;
}
