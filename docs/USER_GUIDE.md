# User Guide — GWP2 Investment Intelligence

No finance or coding background needed. Read this once and you can use everything.

## Home page
Overview of the platform, the "How to use" table, the disclaimer, and the developer profile with contact links.

## 1. Market Overview
- **What you see:** the seven assets' price history, a statistics table (annual return, volatility, Sharpe ratio, skewness, kurtosis), and a correlation heatmap.
- **How to read it:** return = how much a stock made per year on average; volatility = how bumpy the ride was; correlation near 1 = moves together (bad for diversification), near 0 = independent (good).
- **Trust check:** the green banner shows exactly when data was last fetched.

## 2. Quantitative Analysis
- Shows the three optimized portfolios: long-only, capped at 20% per asset, and short-selling allowed — computed by real optimization, not simulation.
- **How to read it:** the bar chart compares weights; the table gives expected return/volatility/Sharpe per strategy. Capping lowers both return and risk. Short-selling raises the modelled Sharpe but is only realistic for professional mandates.

## 3. Predictive Analytics
- **Bootstrap forecast:** a range (5th–95th percentile) for next-year portfolio returns plus the probability of a loss. Treat the range, never the midpoint, as the message.
- **ML regime probability:** the chance a stock's next quarter is positive, with its measured accuracy. If accuracy hovers near 50%, that is the model honestly telling you it has little edge.

## 4. Investor Insights
Three tabs (retail / institutional / corporate). Every BUY/HOLD/SELL tag is produced by a fixed, published scoring rule — the rule is printed on the page. Download the signals as CSV.

## 5. Risk Analysis
Daily VaR ("on a bad day — the worst 5% — you lose about this much"), CVaR ("and if that bad day happens, the average loss is this"), max drawdown, and a live risk-free rate from FRED when available.

## 6. Research Methodology
The original university study, what was changed and why, and the caveats for every method.

## FAQ
- **Is this investment advice?** No. Research output from statistical models on delayed data.
- **Why do numbers differ from the PDF report?** The app uses dividend-adjusted prices and computes weights by true optimization (the report's Step 2 weight table contains a transcription error — see `docs/PROJECT_ANALYSIS.md`).
- **Why is a page empty or showing an error?** The data source was unreachable. The app never invents data; retry in a few minutes.
