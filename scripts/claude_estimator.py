"""
Claude Estimator — Independent AI probability assessment for Polymarket signals.

Uses Claude claude-sonnet-4-20250514 to generate an independent probability estimate for each
market question, then blends with the 7-factor model to produce a combined edge
and signal strength rating.

Requires ANTHROPIC_API_KEY in environment.
"""

import os
import json
import re

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None


# Confidence weight for edge blending
CONFIDENCE_WEIGHTS = {
    "low": 0.15,
    "medium": 0.35,
    "high": 0.50,
}

MODEL_ID = "claude-sonnet-4-20250514"


class ClaudeEstimator:
    """Calls Claude API for an independent probability estimate on a prediction market."""

    def __init__(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in environment")
        if Anthropic is None:
            raise ImportError("anthropic package not installed — run: pip install anthropic")
        self.client = Anthropic(api_key=api_key)

    def estimate(self, question, yes_odds, category, resolution_date,
                 model_prob, model_edge):
        """
        Get Claude's independent probability estimate for a market question.

        Args:
            question: The market question (e.g. "Will BTC hit $100K by June?")
            yes_odds: Current YES price on Polymarket (0.0-1.0)
            category: Market category (crypto, politics, sports, etc.)
            resolution_date: When the market resolves
            model_prob: Our 7-factor model's probability estimate
            model_edge: Our model's calculated edge over market

        Returns:
            dict with: claude_probability, confidence, reasoning, direction,
                       claude_edge, agrees_with_model, combined_edge, signal_strength
        """
        prompt = self._build_prompt(question, yes_odds, category,
                                    resolution_date, model_prob, model_edge)

        try:
            response = self.client.messages.create(
                model=MODEL_ID,
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = response.content[0].text
            parsed = self._parse_response(raw)
        except Exception as e:
            # Fallback: return neutral estimate that doesn't affect scoring
            return self._fallback(str(e), model_prob, model_edge, yes_odds)

        # Derive additional fields
        claude_prob = parsed["claude_probability"]
        confidence = parsed["confidence"]

        # Direction: does Claude lean YES or NO?
        direction = "YES" if claude_prob > 0.5 else "NO"

        # Claude's edge vs market
        if claude_prob > yes_odds:
            claude_edge = claude_prob - yes_odds
        else:
            claude_edge = (1 - claude_prob) - (1 - yes_odds)

        # Does Claude agree with our model's direction?
        model_direction = "YES" if model_prob > yes_odds else "NO"
        agrees = (direction == model_direction)

        # Combined edge blending
        weight = CONFIDENCE_WEIGHTS.get(confidence, 0.15)
        if agrees:
            # Blend: model edge boosted by Claude's confidence-weighted edge
            combined_edge = model_edge * (1 - weight) + max(model_edge, claude_edge) * weight
        else:
            # Disagree: penalize model edge
            combined_edge = model_edge * (1 - weight)

        # Signal strength rating
        signal_strength = self._rate_signal_strength(
            agrees, confidence, combined_edge
        )

        return {
            "claude_probability": round(claude_prob, 4),
            "confidence": confidence,
            "reasoning": parsed["reasoning"],
            "direction": direction,
            "claude_edge": round(claude_edge, 4),
            "agrees_with_model": agrees,
            "combined_edge": round(combined_edge, 4),
            "signal_strength": signal_strength,
            "error": None,
        }

    def _build_prompt(self, question, yes_odds, category, resolution_date,
                      model_prob, model_edge):
        return f"""You are a prediction market analyst. Give your independent probability estimate for this market.

Market Question: {question}
Category: {category}
Current YES odds: {yes_odds * 100:.1f}%
Resolution Date: {resolution_date}
Our model estimates: {model_prob * 100:.1f}% (edge: +{model_edge * 100:.1f}%)

Respond in EXACTLY this JSON format, nothing else:
{{
  "claude_probability": <float 0.0-1.0>,
  "confidence": "<low|medium|high>",
  "reasoning": "<1-2 sentence reasoning>"
}}

Rules:
- Be independent. Do not anchor to the model estimate or market odds.
- Consider base rates, current events, and category-specific factors.
- confidence = how sure you are in YOUR estimate (low/medium/high).
- Return ONLY the JSON object, no markdown fences or extra text."""

    def _parse_response(self, raw):
        """Parse Claude's JSON response, handling common formatting issues."""
        text = raw.strip()
        # Strip markdown code fences if present
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        text = text.strip()

        data = json.loads(text)

        prob = float(data["claude_probability"])
        prob = max(0.01, min(0.99, prob))

        confidence = data.get("confidence", "low").lower()
        if confidence not in ("low", "medium", "high"):
            confidence = "low"

        reasoning = data.get("reasoning", "No reasoning provided.")

        return {
            "claude_probability": prob,
            "confidence": confidence,
            "reasoning": reasoning,
        }

    def _fallback(self, error_msg, model_prob, model_edge, yes_odds):
        """Return neutral fallback when API call fails."""
        return {
            "claude_probability": round(yes_odds, 4),
            "confidence": "low",
            "reasoning": f"Claude estimate unavailable: {error_msg}",
            "direction": "YES" if yes_odds > 0.5 else "NO",
            "claude_edge": 0.0,
            "agrees_with_model": True,
            "combined_edge": round(model_edge, 4),
            "signal_strength": "weak",
            "error": error_msg,
        }

    def _rate_signal_strength(self, agrees, confidence, combined_edge):
        """Rate overall signal strength from Claude + model agreement."""
        if agrees and confidence == "high" and combined_edge > 0.07:
            return "strong"
        if agrees and combined_edge > 0.04:
            return "moderate"
        if not agrees and confidence == "high":
            return "conflict"
        return "weak"
