import os
import io
import math
from typing import Dict, Any
from PIL import Image, ImageChops, ImageEnhance

class ImageForensicsAnalyzer:
    def __init__(self):
        pass

    def analyze_image(self, image_bytes: bytes, filename: str) -> Dict[str, Any]:
        """
        Analyzes image for digital manipulation, ELA anomalies, EXIF data, and visual metrics.
        """
        try:
            img = Image.open(io.BytesIO(image_bytes))
            width, height = img.size
            format_type = img.format or "UNKNOWN"
            mode = img.mode

            # 1. EXIF Metadata Check
            exif_data = img._getexif() if hasattr(img, '_getexif') and img._getexif() else {}
            has_exif = bool(exif_data)
            camera_make = exif_data.get(271, "Not Specified") if exif_data else "Unknown / Stripped"

            # 2. Simulated Error Level Analysis (ELA)
            ela_score, ela_im = self._compute_ela(img)

            # 3. Compression & Resolution Integrity
            resolution_score = min(100, (width * height) / (1920 * 1080) * 80 + 20)
            
            # 4. Color Spectrum & Noise Consistency
            color_variance_score = self._compute_color_variance(img)

            # Overall Forensic Risk & Authenticity Index
            forensic_authenticity_score = round((100 - ela_score) * 0.5 + (resolution_score * 0.3) + (color_variance_score * 0.2), 1)
            forensic_authenticity_score = max(10.0, min(99.0, forensic_authenticity_score))

            if forensic_authenticity_score >= 75:
                status = "AUTHENTIC MEDIA"
                status_color = "#28a745"
            elif forensic_authenticity_score >= 45:
                status = "POSSIBLE EDITS / LOW RES"
                status_color = "#ffc107"
            else:
                status = "HIGH MANIPULATION / AI GENERATED RISK"
                status_color = "#dc3545"

            flags = []
            if ela_score > 40:
                flags.append(f"High compression variance detected (ELA score: {round(ela_score,1)}/100). Possible localized photo editing.")
            if not has_exif:
                flags.append("EXIF metadata stripped (Common in social media re-uploads or web graphics).")
            else:
                flags.append(f"EXIF Metadata found (Camera: {camera_make}).")

            if width < 500 or height < 500:
                flags.append("Low resolution image detected (Under 500px).")

            return {
                "authenticity_score": forensic_authenticity_score,
                "status": status,
                "status_color": status_color,
                "ela_score": round(ela_score, 1),
                "resolution": f"{width} x {height} px",
                "format": format_type,
                "has_exif": has_exif,
                "flags": flags
            }

        except Exception as e:
            return {
                "authenticity_score": 50.0,
                "status": "PROCESSING ERROR",
                "status_color": "#ffc107",
                "ela_score": 0.0,
                "resolution": "Unknown",
                "format": "Unknown",
                "has_exif": False,
                "flags": [f"Could not analyze image format: {str(e)}"]
            }

    def _compute_ela(self, orig_img: Image.Image, quality: int = 90):
        """
        Performs Error Level Analysis (ELA) by re-saving at standard JPEG compression 
        and analyzing pixel difference scale.
        """
        try:
            # Convert to RGB if PNG/RGBA
            rgb_img = orig_img.convert('RGB')
            
            # Save temporary compressed buffer
            buf = io.BytesIO()
            rgb_img.save(buf, 'JPEG', quality=quality)
            buf.seek(0)
            compressed = Image.open(buf)

            # Compute difference
            diff = ImageChops.difference(rgb_img, compressed)
            extrema = diff.getextrema()

            max_diff = max([ex[1] for ex in extrema])
            if max_diff == 0:
                max_diff = 1

            scale = 255.0 / max_diff
            diff_enhanced = ImageEnhance.Brightness(diff).enhance(scale)
            
            # Calculate mean difference intensity
            stat = diff.histogram()
            total_pixels = rgb_img.width * rgb_img.height
            mean_intensity = sum(i * stat[i] for i in range(len(stat))) / (total_pixels * 3)

            ela_score = min(100.0, mean_intensity * 12.0)
            return ela_score, diff_enhanced
        except Exception:
            return 25.0, orig_img

    def _compute_color_variance(self, img: Image.Image):
        try:
            small = img.convert('RGB').resize((64, 64))
            pixels = list(small.getdata())
            r = [p[0] for p in pixels]
            g = [p[1] for p in pixels]
            b = [p[2] for p in pixels]
            
            def var(lst):
                m = sum(lst) / len(lst)
                return sum((x - m) ** 2 for x in lst) / len(lst)

            total_var = (var(r) + var(g) + var(b)) / 3.0
            score = min(100.0, math.sqrt(total_var) * 1.2)
            return score
        except Exception:
            return 70.0
