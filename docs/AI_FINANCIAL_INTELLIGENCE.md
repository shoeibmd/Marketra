# AI Financial Intelligence & Safety Framework

## Safety & Non-Speculation Directives
- **Zero Investment Advice:** Never output "BUY THIS STOCK", "THIS STOCK WILL DEFINITELY RISE", or "TARGET PRICE WILL BE ₹XXX".
- **Source Fact Preservation:** Every analysis explicitly separates `VERIFIED FACTS`, `AI ANALYSIS`, `POTENTIAL IMPACT`, and `UNCERTAINTIES` ("NOT AVAILABLE FROM SOURCE").
- **Graceful Fallback:** If AI processing fails or times out, the event is saved with `AI_STATUS = PENDING` without losing underlying disclosure data.
