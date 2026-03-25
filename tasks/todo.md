# Fix: Bad Signal Quality + Duplicate Messages + Binance Geo-block

## Duplicate Messages Fix
- [x] SIGTERM handler — old instance stops polling immediately on Railway deploy
- [x] 8-second startup delay — new instance waits for old one to die
- [x] Flush confirmation — confirms offset with Telegram API on startup

## Signal Quality Fix (binance_ta_runner.py — shared by forex_ta_runner.py)
- [x] Only count confluences matching dominant direction (3 bull + 2 bear = count 3, not 5)
- [x] Exclude neutral factors (BB_squeeze, Volume) from confluence count
- [x] Raise threshold from 3 to 4 directional confluences
- [x] Raise confidence levels (6+ for HIGH, 4+ for MEDIUM)
- [x] Reject signals with SL wider than 2x ATR
- [x] Volume check requires vol_avg > 100 (filters CoinGecko zero-volume)
- [x] Staleness guard for CoinGecko candle data
- [x] Added missing contradiction filter to forex load_forex_signals

## Polymarket Scanner Fix
- [x] Use combined_edge instead of raw edge in threshold
- [x] Block signals where Claude explicitly disagrees
- [x] Cap agreement boost BEFORE clamping (prevents 52.5% shifts)

## Binance Geo-block Fix
- [x] Added Bybit as fallback #1 (public API, global, real volume, no auth)
- [x] Bybit uses dual domains (api.bybit.com + api.bytick.com) for resilience
- [x] CoinGecko demoted to fallback #2 (last resort)
- [ ] **USER ACTION:** Change Railway region to EU in Railway dashboard (Settings > Region)

## Verification
- [ ] Deploy to Railway
- [ ] /scan_all — one message, Bybit data source, fewer + stronger signals
- [ ] Check edge values in Polymarket signals are reasonable (< 35%)
