# Trading Wing — Cipher Ops

## 5 Agent Teams
1. **Analyst Team** - Fundamental, Technical, Sentiment, News agents
2. **Researcher Team** - Bullish vs Bearish debate before every trade
3. **Trader Agents** - Execute buy/sell via exchange APIs
4. **Risk Management** - Sharpe Ratio + Max Drawdown hard limits
5. **Fund Manager** - Final approval on all decisions

## Stack
- Google AI Ultra + PydanticAI
- Qdrant vector DB on KVM8
- Celery + Redis pipeline
- Exchange APIs: [ADD YOUR KEYS IN .env]

## Risk Rules
- Never exceed Max Drawdown threshold
- Sharpe Ratio must be positive before any trade
- All decisions logged to legacy-foundation/memory/episodic/
