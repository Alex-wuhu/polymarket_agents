# Gamma Event Response Structure

The Gamma `GET /events` endpoint returns an array of event objects. Each event combines question-level metadata with a list of market summaries plus optional series and tag records. The tables below describe every field observed in the sample response from `docs/Gamma_LLM.md`.

## Event Object Fields

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | Unique event identifier used by Gamma. |
| `ticker` | string | Short, URL-safe identifier for the event, reused across related resources. |
| `slug` | string | Full slug suitable for building `/events/slug/{slug}` URLs. |
| `title` | string | Human-readable event question shown in the UI. |
| `description` | string | Markdown-capable event description clarifying settlement criteria. |
| `resolutionSource` | string | URL pointing to the official data source for adjudicating the event. |
| `category` | string | High-level categorisation (for example `Sports`). |
| `image` | string | URL for the event hero image. |
| `icon` | string | URL for a smaller icon rendition of the event artwork. |
| `startDate` | string (ISO 8601) | When the event becomes relevant or trading opens. |
| `creationDate` | string (ISO 8601) | Original authored date; often matches `startDate` for legacy data. |
| `endDate` | string (ISO 8601) | Scheduled resolution time for the underlying event. |
| `closedTime` | string (ISO 8601) | Timestamp when the event was marked closed in Gamma. |
| `createdAt` | string (ISO 8601) | Database insertion timestamp for the event record. |
| `updatedAt` | string (ISO 8601) | Last modification timestamp within Gamma. |
| `published_at` | string (ISO 8601) | When the event was published to end users. |
| `seriesSlug` | string | Slug of the series the event belongs to (if applicable). |
| `sortBy` | string | Default ordering for markets inside the event (for example `ascending`). |
| `volume` | number | Lifetime traded volume across all constituent markets, denominated in USD. |
| `volume24hr` | number | Volume traded in the last 24 hours. |
| `volume1wk` | number | Trailing seven-day volume. |
| `volume1mo` | number | Trailing thirty-day volume. |
| `volume1yr` | number | Trailing twelve-month volume. |
| `liquidity` | number | Aggregate liquidity currently available across the event. |
| `liquidityAmm` | number | Liquidity provided by the on-chain AMM for the event’s markets. |
| `liquidityClob` | number | Liquidity provided by the central limit order book for the event. |
| `openInterest` | number | Unsettled exposure (positions still outstanding) across the event. |
| `commentCount` | number | Total number of user comments associated with the event. |
| `competitive` | number | Internal scoring used for promotional ranking (0 indicates no boost). |
| `active` | boolean | True when the event currently hosts at least one open market. |
| `closed` | boolean | True once every market in the event has closed. |
| `archived` | boolean | True when the event is hidden from default listings. |
| `new` | boolean | Indicates recently listed events for UI badging. |
| `featured` | boolean | Marks platform-selected spotlight events. |
| `restricted` | boolean | Signals geo-fencing or audience restrictions. |
| `cyom` | boolean | True when the event was created via a “Create Your Own Market” flow. |
| `enableNegRisk` | boolean | Toggles support for negative risk market bundles within the event. |
| `negRiskAugmented` | boolean | Indicates enhanced negative risk handling (placeholder outcomes, etc.). |
| `pendingDeployment` | boolean | Event exists in Gamma but has not been fully deployed on-chain. |
| `deploying` | boolean | Deployment is currently in progress. |
| `showAllOutcomes` | boolean | UI hint to show every market outcome without collapsing. |
| `showMarketImages` | boolean | UI hint to render market-level artwork. |
| `markets` | array\<MarketSummary\> | List of market summaries associated with the event. |
| `series` | array\<Series\> | Optional series metadata for themed collections. |
| `tags` | array\<Tag\> | Descriptive or organisational tags for filtering. |

## Market Summary (`markets[]`)

`markets` contains the market objects embedded within the event response. Numeric values representing token balances or USD amounts are often returned as strings to preserve precision.

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | Market identifier unique across Gamma. |
| `question` | string | Market-level question (often matches event title). |
| `slug` | string | Slug used in `/markets/slug/{slug}` lookups. |
| `category` | string | Category inherited from the event or refined at the market level. |
| `description` | string | Market-specific resolution summary. |
| `resolutionSource` | string | URL backing the market resolution. |
| `resolvedBy` | string | Address of the moderator account that resolved the market. |
| `conditionId` | string | Conditional Tokens framework condition identifier. |
| `marketMakerAddress` | string | Ethereum address of the fixed product market maker contract. |
| `marketType` | string | Market topology (for example `normal`, `scalar`, or categorical). |
| `fee` | string (bigint) | Trading fee in wei (18-decimal string). |
| `liquidity` | string (decimal) | Total liquidity provisioned to the market, represented as a decimal string. |
| `liquidityNum` | number | Parsed numeric representation of `liquidity`. |
| `volume` | string (decimal) | Lifetime traded volume (USD) as a decimal string. |
| `volumeNum` | number | Convenience numeric version of `volume`. |
| `volume24hr` | number | Trailing 24-hour volume. |
| `volume1wk` | number | Trailing seven-day volume. |
| `volume1wkAmm` | number | Seven-day volume sourced from the AMM. |
| `volume1wkClob` | number | Seven-day volume sourced from the CLOB. |
| `volume1mo` | number | Trailing thirty-day volume. |
| `volume1moAmm` | number | Thirty-day AMM volume. |
| `volume1moClob` | number | Thirty-day CLOB volume. |
| `volume1yr` | number | Trailing twelve-month volume. |
| `volume1yrAmm` | number | Twelve-month AMM volume. |
| `volume1yrClob` | number | Twelve-month CLOB volume. |
| `spread` | number | Current percentage spread between best bid and ask. |
| `bestBid` | number | Highest outstanding bid price (0–1 scale). |
| `bestAsk` | number | Lowest outstanding ask price (0–1 scale). |
| `lastTradePrice` | number | Price of the most recent filled order. |
| `outcomes` | stringified JSON | JSON string array containing the market outcome labels (e.g. `["Yes","No"]`). |
| `outcomePrices` | stringified JSON | JSON string array of binary outcome prices as 0–1 decimals. |
| `clobTokenIds` | stringified JSON | JSON string array of token IDs used on the order book. |
| `umaResolutionStatuses` | stringified JSON | JSON string array capturing UMA resolution integration state. |
| `startDate` | string (ISO 8601) | When the market opened for trading. |
| `startDateIso` | string (YYYY-MM-DD) | Date-only version of `startDate`. |
| `endDate` | string (ISO 8601) | Scheduled market close time. |
| `endDateIso` | string (YYYY-MM-DD) | Date-only version of `endDate`. |
| `hasReviewedDates` | boolean | Moderation flag indicating the date inputs were reviewed. |
| `closedTime` | string (ISO 8601) | Recorded time the market was closed on Gamma. |
| `createdAt` | string (ISO 8601) | Timestamp when the market record was created. |
| `updatedAt` | string (ISO 8601) | Timestamp of the latest record update. |
| `updatedBy` | number | Internal user ID of the last editor. |
| `creator` | string | Address or identifier of the original market creator. |
| `submitted_by` | string | Address or user identifier that originally submitted the market. |
| `twitterCardLocation` | string | URL to the cached Twitter card image. |
| `twitterCardLastRefreshed` | string | Epoch milliseconds when the Twitter card cache was refreshed. |
| `image` | string | URL for the market image. |
| `icon` | string | URL for the market icon thumbnail. |
| `active` | boolean | True when the market accepts orders. |
| `closed` | boolean | True once the market is closed to trading. |
| `archived` | boolean | True when the market is hidden from default listings. |
| `new` | boolean | Indicates the market was recently listed. |
| `featured` | boolean | Marks editorially highlighted markets. |
| `cyom` | boolean | Identifies “Create Your Own Market” entries. |
| `restricted` | boolean | Access-limited market flag applied for compliance or promos. |
| `funded` | boolean | Market funding goal achieved flag. |
| `ready` | boolean | Internal flag indicating the market passed moderation. |
| `readyForCron` | boolean | Signals the market is ready for scheduled automation tasks. |
| `approved` | boolean | Market has been approved by moderators. |
| `pendingDeployment` | boolean | Market configuration staged but not yet deployed. |
| `deploying` | boolean | Deployment transaction is in flight. |
| `fpmmLive` | boolean | Fixed product market maker contract live on-chain. |
| `clearBookOnStart` | boolean | Indicates if the order book should be cleared upon market start. |
| `manualActivation` | boolean | Requires manual activation instead of automated go-live. |
| `pagerDutyNotificationEnabled` | boolean | Alerts operations on key market events. |
| `rfqEnabled` | boolean | RFQ (request for quote) workflow enabled. |
| `holdingRewardsEnabled` | boolean | Whether position holding rewards accrue on this market. |
| `feesEnabled` | boolean | Additional transactional fees active flag. |
| `negRiskOther` | boolean | Part of a negative-risk bundle outside the primary neg-risk set. |
| `competitive` | number | Market-level promotional weighting. |
| `oneHourPriceChange` | number | Hour-over-hour price delta. |
| `oneDayPriceChange` | number | Daily price delta. |
| `oneWeekPriceChange` | number | Seven-day price delta. |
| `oneMonthPriceChange` | number | Thirty-day price delta. |
| `oneYearPriceChange` | number | Annual price delta. |
| `rewardsMinSize` | number | Minimum position size to qualify for rewards. |
| `rewardsMaxSpread` | number | Maximum bid–ask spread while remaining rewards-eligible. |
| `sentDiscord` | boolean | Discord notification already dispatched for this market. |
| `wideFormat` | boolean | UI hint for rendering the market in wide card format. |

## Series Objects (`series[]`)

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | Series identifier. |
| `ticker` | string | Short slug for the series. |
| `slug` | string | URL slug used for `/series/{slug}` navigation. |
| `title` | string | Display name of the series. |
| `seriesType` | string | Describes recurrence style (for example `single`). |
| `recurrence` | string | Human-readable cadence (for example `daily`). |
| `layout` | string | Preferred layout for rendering series cards. |
| `image` | string | URL to the series artwork. |
| `icon` | string | URL to the series icon. |
| `startDate` | string (ISO 8601) | When the series began. |
| `publishedAt` | string (ISO 8601) | When the series was published to users. |
| `createdAt` | string (ISO 8601) | Database creation timestamp. |
| `updatedAt` | string (ISO 8601) | Last modification timestamp. |
| `createdBy` | string | Internal user identifier that created the series. |
| `updatedBy` | string | Internal user identifier that last updated the series. |
| `active` | boolean | Series currently in use. |
| `closed` | boolean | Series has concluded. |
| `archived` | boolean | Series hidden from regular views. |
| `new` | boolean | Recently introduced series flag. |
| `featured` | boolean | Marked for additional promotion. |
| `restricted` | boolean | Availability restricted to certain audiences. |
| `commentsEnabled` | boolean | Whether commenting is allowed on series pages. |
| `competitive` | string | Ranking weight for promotional logic (stringified). |
| `volume24hr` | number | Aggregate 24-hour volume for markets within the series. |
| `commentCount` | number | Total comment count across the series. |

## Tag Objects (`tags[]`)

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | Tag identifier. |
| `label` | string | Display label shown in filters. |
| `slug` | string | URL-friendly tag slug. |
| `forceShow` | boolean | Forces the tag to display even if unused in filters. |
| `updatedAt` | string (ISO 8601) | Timestamp of the most recent tag update. |
