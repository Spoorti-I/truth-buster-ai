import io
import math
import struct
from typing import Dict, Any, List, Tuple
from PIL import Image, ImageChops, ImageEnhance, ImageFilter, ImageStat

class ImageForensicsAnalyzer:
    """
    Advanced image forensics engine with AI-generated image detection.
    Uses multi-signal analysis: smoothness, noise patterns, entropy,
    color uniformity, gradient analysis, EXIF checks, and ELA.
    """

    def __init__(self):
        pass

    def analyze_image(self, image_bytes: bytes, filename: str) -> Dict[str, Any]:
        try:
            img = Image.open(io.BytesIO(image_bytes))
            width, height = img.size
            format_type = img.format or "UNKNOWN"
            rgb_img = img.convert('RGB')

            # 1. EXIF Metadata Check
            exif_data = None
            try:
                exif_data = img._getexif() if hasattr(img, '_getexif') else None
            except Exception:
                exif_data = None
            has_exif = bool(exif_data)
            camera_make = exif_data.get(271, "Not Specified") if exif_data else "Unknown / Stripped"

            # 2. Error Level Analysis (ELA)
            ela_score = self._compute_ela(rgb_img)

            # 3. AI-Generation Detection Signals
            smoothness_score = self._detect_ai_smoothness(rgb_img)
            noise_uniformity = self._analyze_noise_pattern(rgb_img)
            entropy_score = self._compute_entropy(rgb_img)
            gradient_score = self._analyze_gradient_smoothness(rgb_img)
            color_band_score = self._detect_color_banding(rgb_img)
            texture_score = self._analyze_texture_complexity(rgb_img)

            # 4. File size vs resolution ratio (AI images have specific compression ratios)
            file_size_kb = len(image_bytes) / 1024
            pixel_count = width * height
            bytes_per_pixel = len(image_bytes) / max(pixel_count, 1)
            size_ratio_suspicious = bytes_per_pixel < 0.4  # AI images tend to be very compressed

            # ══════════════════════════════════════════
            # AI DETECTION SCORING (0-100, higher = more likely AI)
            # ══════════════════════════════════════════
            ai_signals = []
            ai_risk_score = 0.0

            # Signal 1: Too smooth (AI images are unnaturally smooth)
            if smoothness_score > 65:
                ai_risk_score += 22
                ai_signals.append(f"🤖 Unnaturally smooth texture detected (Smoothness: {smoothness_score:.0f}/100). AI models produce over-smoothed skin and surfaces.")
            elif smoothness_score > 45:
                ai_risk_score += 10
                ai_signals.append(f"⚠️ Above-average smoothness detected ({smoothness_score:.0f}/100). May indicate AI enhancement or generation.")

            # Signal 2: Uniform noise (real photos have varied sensor noise)
            if noise_uniformity > 70:
                ai_risk_score += 18
                ai_signals.append(f"🤖 Noise pattern is too uniform ({noise_uniformity:.0f}/100). Real cameras produce varying noise across regions.")
            elif noise_uniformity > 50:
                ai_risk_score += 8

            # Signal 3: Low entropy (AI images have predictable pixel patterns)
            if entropy_score < 35:
                ai_risk_score += 15
                ai_signals.append(f"🤖 Low image entropy ({entropy_score:.0f}/100). AI-generated images show predictable color transitions.")
            elif entropy_score < 50:
                ai_risk_score += 6

            # Signal 4: Too-smooth gradients (AI creates perfect gradients)
            if gradient_score > 60:
                ai_risk_score += 15
                ai_signals.append(f"🤖 Suspiciously smooth gradients detected ({gradient_score:.0f}/100). Natural photos have micro-texture in gradient areas.")
            elif gradient_score > 40:
                ai_risk_score += 6

            # Signal 5: Color banding (AI models create subtle color bands)
            if color_band_score > 55:
                ai_risk_score += 10
                ai_signals.append(f"⚠️ Color banding artifacts detected ({color_band_score:.0f}/100). Common in AI-rendered images.")

            # Signal 6: Low texture complexity
            if texture_score < 30:
                ai_risk_score += 12
                ai_signals.append(f"🤖 Low texture complexity ({texture_score:.0f}/100). AI images lack fine-grained natural detail.")
            elif texture_score < 45:
                ai_risk_score += 5

            # Signal 7: No EXIF = strong AI indicator
            if not has_exif:
                ai_risk_score += 12
                ai_signals.append("🤖 No EXIF metadata found. AI-generated images never contain camera data.")
            else:
                ai_risk_score -= 10  # Real camera = bonus
                ai_signals.append(f"✅ EXIF data present (Camera: {camera_make}). Suggests a real camera capture.")

            # Signal 8: File size ratio
            if size_ratio_suspicious:
                ai_risk_score += 5
                ai_signals.append(f"⚠️ Unusually small file for resolution ({file_size_kb:.0f}KB for {width}x{height}px). AI outputs are often highly compressed.")

            # Signal 9: ELA check
            if ela_score < 15:
                ai_risk_score += 8
                ai_signals.append(f"🤖 Very low ELA variance ({ela_score:.1f}/100). AI-generated images compress uniformly without editing traces.")
            elif ela_score > 50:
                ai_signals.append(f"⚠️ High ELA variance ({ela_score:.1f}/100). Image may have been locally edited or composited.")

            # Clamp AI risk
            ai_risk_score = max(0.0, min(100.0, ai_risk_score))

            # ══════════════════════════════════════════
            # AUTHENTICITY SCORE (inverse of AI risk)
            # ══════════════════════════════════════════
            authenticity_score = round(max(3.0, min(97.0, 100.0 - ai_risk_score)), 1)

            # Classification
            if authenticity_score <= 25:
                status = "🤖 HIGH RISK — AI GENERATED / HEAVILY MANIPULATED"
                status_color = "#dc3545"
            elif authenticity_score <= 45:
                status = "⚠️ LIKELY AI GENERATED OR EDITED"
                status_color = "#fd7e14"
            elif authenticity_score <= 65:
                status = "⚠️ SUSPICIOUS — POSSIBLE AI / EDITS"
                status_color = "#ffc107"
            elif authenticity_score <= 80:
                status = "MOSTLY AUTHENTIC — MINOR CONCERNS"
                status_color = "#28a745"
            else:
                status = "✅ AUTHENTIC MEDIA"
                status_color = "#28a745"

            # Add forensic metadata flags
            if width < 500 or height < 500:
                ai_signals.append(f"📐 Low resolution ({width}x{height}px). Small images are harder to verify.")

            if not ai_signals:
                ai_signals.append("Standard image analysis complete.")

            return {
                "authenticity_score": authenticity_score,
                "status": status,
                "status_color": status_color,
                "ela_score": round(ela_score, 1),
                "ai_risk_score": round(ai_risk_score, 1),
                "smoothness": round(smoothness_score, 1),
                "noise_uniformity": round(noise_uniformity, 1),
                "entropy": round(entropy_score, 1),
                "resolution": f"{width} x {height} px",
                "format": format_type,
                "has_exif": has_exif,
                "flags": ai_signals
            }

        except Exception as e:
            return {
                "authenticity_score": 50.0,
                "status": "PROCESSING ERROR",
                "status_color": "#ffc107",
                "ela_score": 0.0,
                "ai_risk_score": 0.0,
                "smoothness": 0.0,
                "noise_uniformity": 0.0,
                "entropy": 0.0,
                "resolution": "Unknown",
                "format": "Unknown",
                "has_exif": False,
                "flags": [f"Could not process image: {str(e)}"]
            }

    # ═══════════════════════════════════════════════
    # DETECTION METHODS
    # ═══════════════════════════════════════════════

    def _compute_ela(self, rgb_img: Image.Image, quality: int = 90) -> float:
        """Error Level Analysis — re-compress and measure difference."""
        try:
            buf = io.BytesIO()
            rgb_img.save(buf, 'JPEG', quality=quality)
            buf.seek(0)
            compressed = Image.open(buf)

            diff = ImageChops.difference(rgb_img, compressed)
            stat_obj = ImageStat.Stat(diff)
            mean_diff = sum(stat_obj.mean) / 3.0
            ela_score = min(100.0, mean_diff * 10.0)
            return ela_score
        except Exception:
            return 25.0

    def _detect_ai_smoothness(self, img: Image.Image) -> float:
        """
        Detects unnatural smoothness in images.
        AI images have extremely smooth skin/surfaces compared to real photos.
        Uses high-pass filter to measure fine detail presence.
        """
        try:
            small = img.resize((256, 256))

            # Apply edge detection (high-pass) — real photos have more edges
            edges = small.filter(ImageFilter.FIND_EDGES)
            edge_stat = ImageStat.Stat(edges)
            edge_mean = sum(edge_stat.mean) / 3.0

            # Apply detail filter — measures micro-texture
            detail = small.filter(ImageFilter.DETAIL)
            diff = ImageChops.difference(small, detail)
            detail_stat = ImageStat.Stat(diff)
            detail_mean = sum(detail_stat.mean) / 3.0

            # Lower edge + detail = smoother = more likely AI
            # Real photos: edge_mean typically 15-50, detail_mean 3-15
            # AI images: edge_mean typically 5-20, detail_mean 1-5
            smoothness = 100.0 - (edge_mean * 1.8 + detail_mean * 5.0)
            return max(0.0, min(100.0, smoothness))
        except Exception:
            return 50.0

    def _analyze_noise_pattern(self, img: Image.Image) -> float:
        """
        Analyzes noise distribution uniformity.
        Real cameras produce varying noise; AI images have uniform noise.
        Splits image into quadrants and compares noise levels.
        """
        try:
            small = img.resize((256, 256))
            w, h = small.size
            hw, hh = w // 2, h // 2

            # Split into 4 quadrants
            quads = [
                small.crop((0, 0, hw, hh)),
                small.crop((hw, 0, w, hh)),
                small.crop((0, hh, hw, h)),
                small.crop((hw, hh, w, h))
            ]

            # Measure noise in each quadrant (edge intensity as proxy)
            noise_levels = []
            for q in quads:
                blurred = q.filter(ImageFilter.GaussianBlur(radius=2))
                diff = ImageChops.difference(q, blurred)
                stat_obj = ImageStat.Stat(diff)
                noise_levels.append(sum(stat_obj.mean) / 3.0)

            if not noise_levels:
                return 50.0

            # Uniform noise = high score = suspicious
            mean_noise = sum(noise_levels) / len(noise_levels)
            if mean_noise < 0.01:
                return 85.0  # Extremely smooth = very suspicious

            variance = sum((n - mean_noise) ** 2 for n in noise_levels) / len(noise_levels)
            coefficient_of_variation = math.sqrt(variance) / max(mean_noise, 0.01)

            # Low variation = uniform noise = AI-like
            # Real photos have CoV typically 0.15-0.6
            # AI images have CoV typically 0.02-0.12
            uniformity = max(0.0, min(100.0, 100.0 - (coefficient_of_variation * 200)))
            return uniformity
        except Exception:
            return 50.0

    def _compute_entropy(self, img: Image.Image) -> float:
        """
        Computes Shannon entropy of the image.
        Higher entropy = more random/complex = more likely real photo.
        AI images tend to have lower entropy (more predictable patterns).
        """
        try:
            gray = img.convert('L').resize((256, 256))
            hist = gray.histogram()
            total = sum(hist)
            if total == 0:
                return 50.0

            entropy = 0.0
            for count in hist:
                if count > 0:
                    p = count / total
                    entropy -= p * math.log2(p)

            # Max possible entropy for 8-bit = 8.0
            # Real photos: typically 6.5-7.8
            # AI images: typically 5.5-7.0
            # Normalize to 0-100
            normalized = (entropy / 8.0) * 100.0
            return max(0.0, min(100.0, normalized))
        except Exception:
            return 50.0

    def _analyze_gradient_smoothness(self, img: Image.Image) -> float:
        """
        Detects unnaturally smooth gradients.
        AI models create perfect color transitions that lack micro-noise.
        """
        try:
            small = img.convert('L').resize((128, 128))
            pixels = list(small.getdata())
            w = 128

            # Measure local gradient smoothness across horizontal lines
            smooth_count = 0
            total_checks = 0

            for y in range(0, 128, 4):
                for x in range(1, 127):
                    idx = y * w + x
                    prev_val = pixels[idx - 1]
                    curr_val = pixels[idx]
                    next_val = pixels[idx + 1]

                    # Check if pixel is perfectly interpolated (AI signature)
                    expected = (prev_val + next_val) / 2.0
                    diff = abs(curr_val - expected)

                    total_checks += 1
                    if diff < 1.5:  # Very close to perfect interpolation
                        smooth_count += 1

            if total_checks == 0:
                return 50.0

            ratio = (smooth_count / total_checks) * 100.0
            # Real photos: 30-55% smooth interpolation
            # AI images: 55-80% smooth interpolation
            # Shift so that >55% triggers detection
            score = max(0.0, min(100.0, (ratio - 30.0) * 2.0))
            return score
        except Exception:
            return 50.0

    def _detect_color_banding(self, img: Image.Image) -> float:
        """
        Detects color banding artifacts common in AI-generated images.
        AI models sometimes produce subtle bands of similar colors.
        """
        try:
            small = img.convert('L').resize((256, 256))
            pixels = list(small.getdata())
            w = 256

            # Count consecutive pixels with identical or near-identical values
            band_count = 0
            total_pairs = 0

            for y in range(0, 256, 2):
                run_length = 1
                for x in range(1, 256):
                    idx = y * w + x
                    prev_idx = y * w + x - 1
                    total_pairs += 1

                    if abs(pixels[idx] - pixels[prev_idx]) <= 1:
                        run_length += 1
                    else:
                        if run_length >= 8:  # Long run of identical colors
                            band_count += run_length
                        run_length = 1

                if run_length >= 8:
                    band_count += run_length

            if total_pairs == 0:
                return 50.0

            ratio = (band_count / total_pairs) * 100.0
            return max(0.0, min(100.0, ratio * 2.0))
        except Exception:
            return 40.0

    def _analyze_texture_complexity(self, img: Image.Image) -> float:
        """
        Measures overall texture complexity using Laplacian variance.
        Real photos have complex, varied textures. AI images are simpler.
        """
        try:
            gray = img.convert('L').resize((256, 256))

            # Laplacian-like sharpness via edge detection
            edges = gray.filter(ImageFilter.Kernel(
                size=(3, 3),
                kernel=[0, 1, 0, 1, -4, 1, 0, 1, 0],
                scale=1,
                offset=128
            ))

            stat_obj = ImageStat.Stat(edges)
            # Variance of Laplacian — higher = more texture
            variance = stat_obj.var[0]

            # Real photos: variance typically 200-2000+
            # AI images: variance typically 50-400
            normalized = min(100.0, (variance / 800.0) * 100.0)
            return max(0.0, normalized)
        except Exception:
            return 50.0
