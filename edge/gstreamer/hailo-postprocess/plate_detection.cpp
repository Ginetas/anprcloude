/**
 * Hailo Post-Processing Plugin: License Plate Detection
 *
 * This plugin processes YOLO detection model outputs and extracts
 * license plate bounding boxes with confidence scores.
 */

#include "hailo_common.hpp"
#include <algorithm>
#include <cmath>
#include <vector>

struct Detection {
    float x, y, width, height;
    float confidence;
    int class_id;
};

/**
 * Non-Maximum Suppression (NMS)
 * Filters overlapping detections, keeping only the highest confidence ones.
 */
std::vector<Detection> apply_nms(std::vector<Detection>& detections, float iou_threshold = 0.45) {
    std::vector<Detection> result;

    // Sort by confidence (descending)
    std::sort(detections.begin(), detections.end(),
              [](const Detection& a, const Detection& b) {
                  return a.confidence > b.confidence;
              });

    std::vector<bool> suppressed(detections.size(), false);

    for (size_t i = 0; i < detections.size(); i++) {
        if (suppressed[i]) continue;

        result.push_back(detections[i]);

        // Suppress overlapping boxes
        for (size_t j = i + 1; j < detections.size(); j++) {
            if (suppressed[j]) continue;

            float iou = compute_iou(detections[i], detections[j]);
            if (iou > iou_threshold) {
                suppressed[j] = true;
            }
        }
    }

    return result;
}

/**
 * Compute Intersection over Union (IoU)
 */
float compute_iou(const Detection& a, const Detection& b) {
    float x1 = std::max(a.x, b.x);
    float y1 = std::max(a.y, b.y);
    float x2 = std::min(a.x + a.width, b.x + b.width);
    float y2 = std::min(a.y + a.height, b.y + b.height);

    if (x2 < x1 || y2 < y1) return 0.0f;

    float intersection = (x2 - x1) * (y2 - y1);
    float area_a = a.width * a.height;
    float area_b = b.width * b.height;
    float union_area = area_a + area_b - intersection;

    return intersection / union_area;
}

/**
 * Main filter function called by GStreamer hailofilter element.
 *
 * @param output_tensors: YOLO model output tensors from Hailo
 * @param roi: Region of interest for processing
 * @return: Vector of HailoDetection objects
 */
extern "C" std::vector<HailoDetection> plate_detection(
    HailoTensorPtr output_tensors,
    HailoROIPtr roi
) {
    // Configuration
    const float CONFIDENCE_THRESHOLD = 0.5f;
    const float NMS_THRESHOLD = 0.45f;
    const int NUM_CLASSES = 1;  // Only "license_plate" class

    std::vector<Detection> raw_detections;

    // Parse YOLO output format (depends on model architecture)
    // Assuming YOLOv8 format: [batch, 84, 8400]
    // 84 = 4 (bbox) + 80 (classes) -> simplified to 4 + 1 for single class

    auto tensor = output_tensors[0];
    float* data = reinterpret_cast<float*>(tensor.data());

    int num_detections = tensor.width();  // e.g., 8400
    int stride = tensor.height();         // e.g., 84 or 5

    for (int i = 0; i < num_detections; i++) {
        // Extract bbox coordinates (center x, center y, width, height)
        float cx = data[i * stride + 0];
        float cy = data[i * stride + 1];
        float w = data[i * stride + 2];
        float h = data[i * stride + 3];
        float conf = data[i * stride + 4];  // objectness * class score

        if (conf >= CONFIDENCE_THRESHOLD) {
            Detection det;
            det.x = cx - w / 2.0f;
            det.y = cy - h / 2.0f;
            det.width = w;
            det.height = h;
            det.confidence = conf;
            det.class_id = 0;  // license_plate

            raw_detections.push_back(det);
        }
    }

    // Apply NMS
    std::vector<Detection> filtered = apply_nms(raw_detections, NMS_THRESHOLD);

    // Convert to Hailo format
    std::vector<HailoDetection> hailo_detections;
    for (const auto& det : filtered) {
        HailoDetection hdet;
        hdet.bbox = HailoBBox(det.x, det.y, det.width, det.height);
        hdet.confidence = det.confidence;
        hdet.class_id = det.class_id;
        hdet.label = "license_plate";

        hailo_detections.push_back(hdet);
    }

    return hailo_detections;
}
