from __future__ import annotations

# Public OpenAI API prices observed for the GPT-5.6 family at hackathon time.
# Values are USD per 1M uncached input tokens / output tokens. The estimate is
# intentionally conservative: cached-input discounts are not subtracted.
MODEL_PRICES_USD_PER_MILLION: dict[str, tuple[float, float]] = {
    "gpt-5.6-luna": (0.20, 1.20),
    "gpt-5.6-terra": (2.00, 12.00),
    "gpt-5.6-sol": (4.00, 20.00),
    "gpt-5.6": (4.00, 20.00),
}


def estimate_cost_usd(model: str, input_tokens: int, output_tokens: int) -> float | None:
    prices = MODEL_PRICES_USD_PER_MILLION.get(model)
    if prices is None:
        return None
    input_price, output_price = prices
    return round(
        (input_tokens / 1_000_000) * input_price
        + (output_tokens / 1_000_000) * output_price,
        6,
    )
