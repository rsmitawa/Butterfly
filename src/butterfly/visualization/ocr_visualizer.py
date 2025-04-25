import cv2
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Tuple

class OCRVisualizer:
    def __init__(self):
        plt.style.use('ggplot')
        
    def draw_ocr_results(self, 
                       image: np.ndarray,
                       text_regions: List[Tuple[Tuple[int, int, int, int], str]],
                       output_path: str = None):
        """
        Visualize OCR text detection results
        Args:
            image: Input image (BGR or RGB)
            text_regions: List of ((x1,y1,x2,y2), text) tuples
            output_path: Optional path to save visualization
        """
        plt.figure(figsize=(12, 8))
        
        # Convert BGR to RGB if needed
        if image.shape[-1] == 3 and len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
        plt.imshow(image)
        ax = plt.gca()
        
        for (x1, y1, x2, y2), text in text_regions:
            # Draw bounding box
            rect = plt.Rectangle((x1, y1), x2-x1, y2-y1, 
                               fill=False, 
                               linewidth=2,
                               edgecolor='red')
            ax.add_patch(rect)
            
            # Add text label
            plt.text(x1, y1, text, 
                    bbox=dict(facecolor='yellow', alpha=0.8),
                    fontsize=8)
        
        plt.axis('off')
        
        if output_path:
            plt.savefig(output_path, bbox_inches='tight', dpi=300)
        else:
            plt.show()
        plt.close()
