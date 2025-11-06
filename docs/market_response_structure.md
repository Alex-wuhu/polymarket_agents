# Gamma Market Response Structure

The Gamma `GET /markets` endpoint returns an array of market objects. Each market record captures the tradeable contract plus a lightweight summary of its parent event. The sections below document every field observed in the sample response inside `docs/Gamma_LLM.md`.

## Market Object Fields

Unless noted otherwise, numeric performance metrics are expressed in USD and may arrive as strings to preserve precision.

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | Unique identifier for the market. |
| `question` | string | Market question presented to traders. |
| `slug` | string | Slug used for `/markets/slug/{slug}` routes. |
| `category` | string | Category label for filtering (for example `US-current-affairs`). |
| `description` | string | Full market description detailing settlement rules. |
| `conditionId` | string | Conditional Tokens condition identifier tied to the market. |
| `marketMakerAddress` | string | Address of the fixed product market maker contract. |
| `marketType` | string | Market topology, such as `normal` or categorical variants. |
| `liquidity` | string (decimal) | Total liquidity committed to the market, returned as a decimal string. |
| `liquidityNum` | number | Parsed numeric form of `liquidity`. |
| `volume` | string (decimal) | Lifetime traded volume. |
| `volumeNum` | number | Convenience numeric representation of `volume`. |
| `volume24hr` | number | Volume traded during the last 24 hours. |
| `volume1wk` | number | Trailing seven-day volume. |
| `volume1wkAmm` | number | Seven-day volume sourced from the AMM. |
| `volume1wkClob` | number | Seven-day volume sourced from the central limit order book. |
| `volume1mo` | number | Trailing thirty-day volume. |
| `volume1moAmm` | number | Thirty-day AMM volume. |
| `volume1moClob` | number | Thirty-day CLOB volume. |
| `volume1yr` | number | Trailing twelve-month volume. |
| `volume1yrAmm` | number | Twelve-month AMM volume. |
| `volume1yrClob` | number | Twelve-month CLOB volume. |
| `spread` | number | Bid–ask spread percentage. |
| `bestBid` | number | Highest active bid price on the CLOB. |
| `bestAsk` | number | Lowest active ask price on the CLOB. |
| `lastTradePrice` | number | Most recent execution price. |
| `outcomes` | stringified JSON | JSON string array of outcome labels (e.g. `["Yes","No"]`). |
| `outcomePrices` | stringified JSON | JSON string array of binary outcome prices (0–1 scale). |
| `clobTokenIds` | stringified JSON | JSON string array of token IDs backing CLOB trading. |
| `umaResolutionStatuses` | stringified JSON | JSON string array tracking UMA integration status. |
| `endDate` | string (ISO 8601) | Scheduled closing time for the market. |
| `endDateIso` | string (YYYY-MM-DD) | Date-only representation of `endDate`. |
| `closedTime` | string (ISO 8601) | Timestamp when the market was marked closed. |
| `createdAt` | string (ISO 8601) | Creation timestamp for the market record. |
| `updatedAt` | string (ISO 8601) | Last update timestamp. |
| `updatedBy` | number | Internal user ID for the last editor. |
| `twitterCardImage` | string | URL to the social preview card used on Twitter/X. |
| `image` | string | Primary market artwork URL. |
| `icon` | string | Icon-sized artwork URL. |
| `mailchimpTag` | string | Identifier used for Mailchimp marketing automations. |
| `creator` | string | Address or identifier of the original market submitter. |
| `approved` | boolean | Market approved by moderators. |
| `active` | boolean | True if the market is accepting new orders. |
| `closed` | boolean | True once the market stops trading. |
| `archived` | boolean | Hidden from standard discovery surfaces. |
| `restricted` | boolean | Geo-fenced or otherwise restricted. |
| `cyom` | boolean | Indicates markets created via “Create Your Own Market”. |
| `funded` | boolean | Market funding objective met flag. |
| `ready` | boolean | Internal gate signalling that the market passed review. |
| `readyForCron` | boolean | Eligible for scheduled background jobs. |
| `hasReviewedDates` | boolean | Moderators confirmed the event timing; helps suppress date warnings. |
| `pendingDeployment` | boolean | Configuration staged but not yet deployed on-chain. |
| `deploying` | boolean | Deployment currently in progress. |
| `fpmmLive` | boolean | Fixed product market maker contract deployed and active. |
| `clearBookOnStart` | boolean | Order book should be cleared once the market starts trading. |
| `manualActivation` | boolean | Market activation must be triggered manually. |
| `pagerDutyNotificationEnabled` | boolean | Operations alerts enabled for this market. |
| `rfqEnabled` | boolean | RFQ (request for quote) flow enabled. |
| `holdingRewardsEnabled` | boolean | Holding rewards accrual activated. |
| `feesEnabled` | boolean | Extra fee mechanics enabled beyond base fees. |
| `negRiskOther` | boolean | Market participates in a negative-risk bundle outside the main neg-risk set. |
| `competitive` | number | Promotional weighting applied to the market. |
| `oneDayPriceChange` | number | Price delta over the last 24 hours. |
| `oneHourPriceChange` | number | Price delta over the last hour. |
| `oneWeekPriceChange` | number | Price delta over the last seven days. |
| `oneMonthPriceChange` | number | Price delta over the last thirty days. |
| `oneYearPriceChange` | number | Price delta over the last 365 days. |
| `rewardsMinSize` | number | Minimum position size eligible for rewards. |
| `rewardsMaxSpread` | number | Maximum spread allowed while earning rewards. |
| `question` | string | Alternate label identical to `title` in event records. |
| `events` | array\<EventSummary\> | Parent event(s) associated with the market. |

> **Note:** Some payloads include duplicate fields with identical semantics (for example `spread`, `restricted`, `updatedAt`). Each field is listed once in the table above.

## Event Summary (`events[]`)

Each market response includes an `events` array describing the parent event in condensed form. These fields correspond to the event schema but omit nested market data.

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | Event identifier joined to the market. |
| `ticker` | string | Short slug for the event. |
| `slug` | string | Full event slug for lookup. |
| `title` | string | Event question. |
| `description` | string | Settlement guidance for the event. |
| `category` | string | Event category tag. |
| `image` | string | Event artwork URL. |
| `icon` | string | Event icon URL. |
| `startDate` | string (ISO 8601) | When the event begins. |
| `endDate` | string (ISO 8601) | Event resolution date. |
| `closedTime` | string (ISO 8601) | Timestamp when the event was closed. |
| `createdAt` | string (ISO 8601) | Creation timestamp within Gamma. |
| `updatedAt` | string (ISO 8601) | Most recent update timestamp. |
| `creationDate` | string (ISO 8601) | Original authored date, pre-database. |
| `published_at` | string (ISO 8601) | Publication timestamp. |
| `volume` | number | Lifetime event trading volume (USD). |
| `volume24hr` | number | Trailing 24-hour volume. |
| `volume1wk` | number | Trailing seven-day volume. |
| `volume1mo` | number | Trailing thirty-day volume. |
| `volume1yr` | number | Trailing twelve-month volume. |
| `liquidity` | number | Aggregate liquidity across constituent markets. |
| `liquidityAmm` | number | Liquidity supplied by the AMM. |
| `liquidityClob` | number | Liquidity supplied by the CLOB. |
| `openInterest` | number | Outstanding open interest across the event. |
| `commentCount` | number | User comment total for the event. |
| `competitive` | number | Promotional weight applied to the event. |
| `active` | boolean | Event currently trading. |
| `closed` | boolean | Event closed to trading. |
| `archived` | boolean | Hidden from regular discovery. |
| `featured` | boolean | Highlighted in the UI. |
| `restricted` | boolean | Access restricted. |
| `cyom` | boolean | “Create Your Own Market” origin flag. |
| `enableNegRisk` | boolean | Event supports negative risk groupings. |
| `negRiskAugmented` | boolean | Event uses augmented negative risk behaviour. |
| `pendingDeployment` | boolean | Event pending deployment to production infrastructure. |
| `deploying` | boolean | Deployment currently underway. |
| `showAllOutcomes` | boolean | UI hint to expand all outcomes. |
| `showMarketImages` | boolean | UI hint to render market artwork. |
| `sortBy` | string | Default ordering for event markets. |
