Gamma is Polymarket's hosted REST API service that indexes on-chain market data and provides additional market metadata. It's the primary way to fetch market information programmatically.

Base Endpoint: https://gamma-api.polymarket.com

Core Data Models
Market - Fundamental trading unit containing:

Token IDs (CLOB pair)
Market address, question ID, condition ID
Trading data (volume, prices, liquidity)
Event - Organizational container for markets:

Single Market Event (SMP) - 1 market
Group Market Event (GMP) - 2+ related markets
Example: "Where will Barron attend college?" (event) → Multiple college options (markets)
Key Endpoints
GET /events - List/filter events (paginated)
GET /markets - List/filter markets (paginated)
GET /events/slug/{slug} - Fetch specific event by slug
GET /markets/slug/{slug} - Fetch specific market by slug
GET /tags - Available market categories
GET /sports - Sports metadata and tags
GET /public-search - Search markets/events/profiles
Fetching Strategies
By Slug - Best for specific markets (extract from URL)
By Tags - Filter by category (tag_id parameter)
All Active Markets - Use /events?closed=false&order=id&ascending=false
Important Fields
negRisk - Indicates negative risk markets (capital efficient)
negRiskAugmented - Enhanced neg risk with placeholder outcomes
Pagination: Use limit and offset parameters

GET /events Endpoint Details
Purpose: List and filter events (organizational containers for markets)

Key Parameters:

closed - Filter by status (false = active only)
order - Sort field (e.g., "id")
ascending - Sort direction (true/false)
limit - Results per page (max varies)
offset - Pagination offset
tag_id - Filter by category/sport tag
exclude_tag_id - Exclude specific tags
related_tags - Include related tag markets
Rate Limit: 100 requests/10s

Response: Array of Event objects containing markets, metadata, volume, liquidity, and organizational data.

GET /markets Endpoint Details
Purpose: List and filter individual markets (tradeable tokens)

Key Parameters:

Same pagination/filtering as /events
market - Condition ID filter
asset_id - Token ID filter
negRisk - Filter negative risk markets
Rate Limit: 125 requests/10s

Response: Array of Market objects with token IDs, prices, volume, condition IDs, and trading metadata.

Key Response Fields
Events: id, slug, markets[], volume, liquidity, closed, negRisk, negRiskAugmented

Markets: token_id, condition_id, question_id, market_address, price, volume, outcome, negRisk

Both endpoints support slug-based lookups via /events/slug/{slug} and /markets/slug/{slug}.

