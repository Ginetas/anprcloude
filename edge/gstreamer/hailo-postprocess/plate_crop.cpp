/**
 * Hailo Cropper Plugin: License Plate Cropping
 *
 * This plugin crops detected license plate regions and prepares them
 * for the OCR model.
 */

#include "hailo_common.hpp"
#include <vector>

/**
 * Main cropper function called by GStreamer hailocropper element.
 *
 * @param image: Input image buffer
 * @param detections: List of detected plates
 * @return: Vector of cropped plate images
 */
extern "C" std::vector<HailoCroppedImage> crop_plates(
    HailoImagePtr image,
    std::vector<HailoDetection> detections
) {
    std::vector<HailoCroppedImage> cropped_plates;

    // OCR model input size (adjust based on your model)
    const int OCR_WIDTH = 200;
    const int OCR_HEIGHT = 64;

    for (const auto& det : detections) {
        // Get detection bounding box
        int x = static_cast<int>(det.bbox.x * image->width);
        int y = static_cast<int>(det.bbox.y * image->height);
        int w = static_cast<int>(det.bbox.width * image->width);
        int h = static_cast<int>(det.bbox.height * image->height);

        // Clamp to image boundaries
        x = std::max(0, std::min(x, image->width - 1));
        y = std::max(0, std::min(y, image->height - 1));
        w = std::min(w, image->width - x);
        h = std::min(h, image->height - y);

        // Skip invalid crops
        if (w <= 0 || h <= 0) continue;

        // Crop and resize for OCR
        HailoCroppedImage crop;
        crop.bbox = HailoBBox(x, y, w, h);
        crop.target_width = OCR_WIDTH;
        crop.target_height = OCR_HEIGHT;
        crop.detection = det;

        cropped_plates.push_back(crop);
    }

    return cropped_plates;
}
