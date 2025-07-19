import pytesseract
import cv2
import numpy as np
from PIL import Image
import base64
import io
import tempfile
import os
import logging
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

class OCRService:
    """Enhanced OCR service with multiple processing techniques"""
    
    def __init__(self):
        self.supported_formats = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif']
        
    def extract_text_from_base64(self, image_base64: str) -> Dict[str, any]:
        """
        Extract text from base64 encoded image using multiple OCR techniques
        
        Returns:
            Dict containing:
                - extracted_text: Main extracted text
                - confidence_scores: List of confidence scores
                - preprocessing_used: Which preprocessing technique worked best
                - success: Boolean indicating if OCR was successful
        """
        try:
            # Decode base64 image
            image_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_data))
            
            # Convert PIL image to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Try multiple preprocessing techniques
            preprocessing_methods = [
                ("original", cv_image),
                ("grayscale", self._convert_to_grayscale(cv_image)),
                ("threshold", self._apply_threshold(cv_image)),
                ("noise_removal", self._remove_noise(cv_image)),
                ("enhanced", self._enhance_image(cv_image))
            ]
            
            best_result = {
                "extracted_text": "",
                "confidence_scores": [],
                "preprocessing_used": "original",
                "success": False,
                "word_count": 0
            }
            
            for method_name, processed_image in preprocessing_methods:
                try:
                    # Extract text with confidence data
                    data = pytesseract.image_to_data(
                        processed_image, 
                        config='--psm 6 --oem 3',
                        output_type=pytesseract.Output.DICT
                    )
                    
                    # Filter out low confidence and empty text
                    filtered_text = []
                    confidence_scores = []
                    
                    for i, text in enumerate(data['text']):
                        confidence = int(data['conf'][i])
                        if confidence > 30 and text.strip():  # Only include confident detections
                            filtered_text.append(text.strip())
                            confidence_scores.append(confidence)
                    
                    extracted_text = " ".join(filtered_text)
                    word_count = len(filtered_text)
                    
                    # Update best result if this method found more text with good confidence
                    if word_count > best_result["word_count"] and confidence_scores:
                        avg_confidence = sum(confidence_scores) / len(confidence_scores)
                        if avg_confidence > 40:  # Minimum average confidence threshold
                            best_result = {
                                "extracted_text": extracted_text,
                                "confidence_scores": confidence_scores,
                                "preprocessing_used": method_name,
                                "success": True,
                                "word_count": word_count,
                                "average_confidence": avg_confidence
                            }
                    
                    logger.info(f"OCR method '{method_name}': {word_count} words, avg confidence: {avg_confidence if confidence_scores else 0:.1f}")
                    
                except Exception as method_error:
                    logger.warning(f"OCR method '{method_name}' failed: {str(method_error)}")
                    continue
            
            # Fallback: simple text extraction without confidence filtering
            if not best_result["success"]:
                try:
                    simple_text = pytesseract.image_to_string(cv_image, config='--psm 6 --oem 3').strip()
                    if simple_text:
                        best_result = {
                            "extracted_text": simple_text,
                            "confidence_scores": [],
                            "preprocessing_used": "simple_extraction",
                            "success": True,
                            "word_count": len(simple_text.split()),
                            "average_confidence": 0
                        }
                except Exception as fallback_error:
                    logger.error(f"Fallback OCR failed: {str(fallback_error)}")
            
            return best_result
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            return {
                "extracted_text": "",
                "confidence_scores": [],
                "preprocessing_used": "none",
                "success": False,
                "error": str(e)
            }
    
    def _convert_to_grayscale(self, image: np.ndarray) -> np.ndarray:
        """Convert image to grayscale"""
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    def _apply_threshold(self, image: np.ndarray) -> np.ndarray:
        """Apply binary thresholding"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Use Otsu's thresholding
        _, threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return threshold
    
    def _remove_noise(self, image: np.ndarray) -> np.ndarray:
        """Remove noise using morphological operations"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Apply noise removal
        kernel = np.ones((1, 1), np.uint8)
        image = cv2.dilate(image, kernel, iterations=1)
        image = cv2.erode(image, kernel, iterations=1)
        # Apply Gaussian blur
        image = cv2.GaussianBlur(image, (5, 5), 0)
        return image
    
    def _enhance_image(self, image: np.ndarray) -> np.ndarray:
        """Enhance image contrast and sharpness"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Sharpen the image
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        sharpened = cv2.filter2D(enhanced, -1, kernel)
        
        return sharpened
    
    def validate_image(self, image_base64: str) -> Dict[str, any]:
        """
        Validate if the base64 string represents a valid image
        """
        try:
            image_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_data))
            
            return {
                "valid": True,
                "format": image.format.lower() if image.format else "unknown",
                "size": image.size,
                "mode": image.mode
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    def get_text_regions(self, image_base64: str) -> List[Dict]:
        """
        Get text regions with bounding boxes (useful for UI highlighting)
        """
        try:
            image_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_data))
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Get bounding box data
            data = pytesseract.image_to_data(
                cv_image, 
                output_type=pytesseract.Output.DICT
            )
            
            regions = []
            for i, text in enumerate(data['text']):
                confidence = int(data['conf'][i])
                if confidence > 30 and text.strip():
                    regions.append({
                        "text": text.strip(),
                        "confidence": confidence,
                        "bbox": {
                            "x": data['left'][i],
                            "y": data['top'][i],
                            "width": data['width'][i],
                            "height": data['height'][i]
                        }
                    })
            
            return regions
            
        except Exception as e:
            logger.error(f"Error getting text regions: {str(e)}")
            return []