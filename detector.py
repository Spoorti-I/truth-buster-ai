import re
import math
from typing import Dict, Any, Optional

SENSATIONAL_WORDS = {
    'shocking', 'unbelievable', 'secret', 'miracle', 'banned', 'disaster', 
    'hidden truth', 'conspiracy', 'illuminati', 'exposed', 'they don\'t want you to know',
    'doctors hate', 'instant cure', 'guaranteed', 'mind blowing', 'jaw dropping',
    'breaking', 'urgent', 'disaster', 'bombshell', 'scandal', 'leaked'
}

CREDIBLE_SOURCES = {
    'reuters', 'ap news', 'associated press', 'bbc', 'bloomberg', 'nature',
    'science', 'afp', 'nytimes', 'washingtonpost', 'wsj', 'nasa', 'who', 'cdc'
}

UNRELIABLE_DOMAINS = {
    'realrawnews', 'infowars', 'naturalnews', 'worldnewsdailyreport', 'newsbiscuit'
}

class FakeNewsDetector:
    def __init__(self):
        pass

    def analyze_text(self, text: str, headline: str = "", domain: str = "") -> Dict[str, Any]:
        """
        Analyzes raw text or scraped article text and returns comprehensive metrics.
        """
        combined_text = f"{headline} {text}".strip()
        if not combined_text:
            return {
                "truth_score": 50,
                "status": "UNVERIFIED",
                "badge_color": "#ffc107",
                "sensationalism_score": 0,
                "clickbait_score": 0,
                "linguistic_score": 0,
                "source_credibility": 50,
                "reasons": ["No content provided for analysis."]
            }

        # 1. Sensationalism Score (0-100)
        sensationalism_score, sensational_found = self._calc_sensationalism(combined_text)

        # 2. Clickbait Index (0-100)
        clickbait_score, clickbait_reasons = self._calc_clickbait(headline or text[:120])

        # 3. Linguistic & Syntax Score (0-100)
        linguistic_score, linguistic_flags = self._calc_linguistic_quality(combined_text)

        # 4. Source & Domain Credibility (0-100)
        source_score, source_notes = self._calc_source_credibility(domain, combined_text)

        # 5. Calculate Weighted Truth Score
        # High sensationalism and high clickbait lower the truth score.
        # High linguistic quality and credible source boost truth score.
        
        penalty = (sensationalism_score * 0.35) + (clickbait_score * 0.30) + ((100 - linguistic_score) * 0.15)
        bonus = (source_score * 0.20)
        
        raw_truth = 100 - penalty + bonus
        truth_score = round(max(5.0, min(98.0, raw_truth)), 1)

        # Classification Status
        if truth_score >= 75:
            status = "VERIFIED AUTHENTIC"
            badge_color = "#28a745" # Green
        elif truth_score >= 50:
            status = "MISLEADING / UNVERIFIED"
            badge_color = "#ffc107" # Yellow / Orange
        elif truth_score >= 30:
            status = "LIKELY FAKE NEWS"
            badge_color = "#fd7e14" # Orange-Red
        else:
            status = "HIGH RISK - CONFIRMED FAKE"
            badge_color = "#dc3545" # Red

        # Construct key risk flags
        reasons = []
        if sensational_found:
            reasons.append(f"Trigger words detected: {', '.join(sensational_found[:4])}")
        if clickbait_reasons:
            reasons.extend(clickbait_reasons)
        if linguistic_flags:
            reasons.extend(linguistic_flags)
        if source_notes:
            reasons.extend(source_notes)
        if not reasons:
            reasons.append("Standard neutral linguistic style detected.")

        return {
            "truth_score": truth_score,
            "status": status,
            "badge_color": badge_color,
            "sensationalism_score": round(sensationalism_score, 1),
            "clickbait_score": round(clickbait_score, 1),
            "linguistic_score": round(linguistic_score, 1),
            "source_credibility": round(source_score, 1),
            "reasons": reasons
        }

    def _calc_sensationalism(self, text: str):
        words = re.findall(r'\w+', text.lower())
        total_words = max(len(words), 1)
        
        found = []
        for word in words:
            if word in SENSATIONAL_WORDS and word not in found:
                found.append(word)

        # Check multi-word triggers
        text_lower = text.lower()
        for phrase in ['they don\'t want you to know', 'doctors hate', 'hidden truth', 'instant cure']:
            if phrase in text_lower and phrase not in found:
                found.append(phrase)

        ratio = (len(found) * 3) / (math.sqrt(total_words) + 1) * 35
        # Caps ratio
        caps_words = [w for w in re.findall(r'\b[A-Z]{2,}\b', text) if w.lower() not in {'usa', 'uk', 'fbi', 'cia', 'nasa', 'ai', 'url', 'pdf'}]
        caps_ratio = (len(caps_words) / total_words) * 100
        
        excl_count = text.count('!')
        excl_ratio = min(excl_count * 10, 30)

        score = min(100.0, ratio + (caps_ratio * 2.5) + excl_ratio)
        return score, found

    def _calc_clickbait(self, text: str):
        reasons = []
        score = 0
        text_lower = text.lower()

        # Questions or exaggerated hooks
        if text.strip().endswith('?'):
            score += 15
            reasons.append("Headline ends with a rhetorical question.")

        if re.search(r'\b(you won\'t believe|this is why|here\'s what|will shock you|number \d+)\b', text_lower):
            score += 40
            reasons.append("Contains classic clickbait phrasing pattern.")

        if re.search(r'\b\d+\s+(reasons|ways|things|secrets|facts)\b', text_lower):
            score += 25
            reasons.append("Listicle clickbait headline pattern detected.")

        return min(100.0, score), reasons

    def _calc_linguistic_quality(self, text: str):
        flags = []
        score = 70.0  # baseline

        words = text.split()
        if len(words) < 15:
            score -= 20
            flags.append("Text is extremely short, reducing statistical certainty.")

        # Check for citation/quote indicators
        quote_count = text.count('"') + text.count('“') + text.count('”')
        if quote_count >= 2:
            score += 15
        else:
            flags.append("Lacks direct quotes or attributed statements.")

        # Check for numeric evidence
        if re.search(r'\b\d+(\.\d+)?%\b|\b\d{4}\b|\b\$\d+', text):
            score += 10

        return max(10.0, min(95.0, score)), flags

    def _calc_source_credibility(self, domain: str, text: str):
        notes = []
        score = 50.0

        if domain:
            domain_clean = domain.lower().replace("www.", "")
            if any(credible in domain_clean for credible in CREDIBLE_SOURCES):
                score = 92.0
                notes.append(f"Domain '{domain_clean}' is a recognized top-tier credible news organization.")
            elif domain_clean.endswith(".gov") or domain_clean.endswith(".edu"):
                score = 96.0
                notes.append("Official government or educational institutional domain.")
            elif any(unreliable in domain_clean for unreliable in UNRELIABLE_DOMAINS):
                score = 10.0
                notes.append(f"Domain '{domain_clean}' is listed in unverified / satire media databases.")

        # Check text mentions of recognized news agencies
        text_lower = text.lower()
        for source in CREDIBLE_SOURCES:
            if source in text_lower and not notes:
                score += 15
                notes.append(f"References established reporting source: '{source.upper()}'")
                break

        return min(100.0, score), notes
