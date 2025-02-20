## Overview

A Python tool for scraping TikTok videos from hashtags and user IDs.

Made for our entry to the Oddesy Hackthon 2025 [our work](https://github.com/Saifgharbii/AI-Odyssey-Hackathon).

## Installation

### 1. Python Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 3. Proxy Configuration (Optional)

For advanced users requiring IP rotation:
1. Set up NGINX as a reverse proxy
2. Configure proxy rotation in the scraper settings
3. Manage request distribution through your proxy setup

### 4. Cobalt API Setup 
Official cobalt tutorial: https://github.com/imputnet/cobalt/blob/main/docs/run-an-instance.md

#### Step 1: Install Docker
Follow the [official Docker installation guide](https://docs.docker.com/get-docker/).

#### Step 3: Launch and Verify

```bash
# Start Cobalt API
docker compose up -d

cd IzYOuIz_tiktok_scraper && uvicorn server:app --reload

# Verify everything is working and test the scraper by navigating to
# http://localhost:8000/
```

# TikTok Scraper API Documentation

### Search Videos

**Endpoint:** `/scrape-and-download`

**Method:** `POST`

**Description:** Retrieves TikTok videos based on a specified search type and query.

**Request Body (JSON):**

```json
{
  "search_type": "string",  
  "search_query": "string", 
  "max_videos": "integer"
}
```

**Parameters:**

- `search_type` (string): The type of search to perform. Allowed values:
  - `hashtag`: Search by hashtag
  - `userid`: Search by user ID (must be prefixed with `@`)
  - `trending`: Retrieve trending videos
  - `topic`: Search by a predefined topic index (0-indexed)
- `search_query` (string):
  - For `userid`: Must be in the format `@username`
  - For `topic`: Must be an integer corresponding to a topic index (see Topics List)
- `max_videos` (integer): Maximum number of videos to scrape.

**Example Requests:**

- **For `topic` when `search_query` is `0` (Hot Videos):**

```bash
curl -X POST "https://localhost:800/scrape-and-download/" \
-H "Content-Type: application/json" \
-d '{
  "search_type": "topic",
  "search_query": "0",
  "max_videos": 10
}'
```

**JavaScript Fetch Example:**

```javascript
let response = await fetch("https://localhost:800/scrape-and-download/", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    "search_type": "topic",
    "search_query": "0",
    "max_videos": 10
  })
});

let data = await response.json();
if (data.id) {
  document.getElementById('status').innerText = "Request queued. Checking status...";
  checkStatus(data.id);
} else {
  document.getElementById('status').innerText = "Failed to queue request.";
}
```

- **For `topic` when `search_query` is greater than `0` (e.g., Apparel & Accessories):**

```json
{
  "search_type": "topic",
  "search_query": "1",
  "max_videos": 10
}
```

### Check Status

**Endpoint:** `/get-status`

**Method:** `GET`

**Description:** Checks the status of a scraping task and returns the scraped data when completed.

**Example cURL Command:**

```bash
curl -X GET "http://localhost:800/get-status/?id=<task_id>"
```

**JavaScript Fetch Example:**

```javascript
let response = await fetch(`http://localhost:800/get-status/?id=${id}`);
let data = await response.json();
document.getElementById('status').innerText = "Checking...";
if (data.status === "completed") {
  document.getElementById('status').innerText = "Completed!";
  document.getElementById('response').innerText = JSON.stringify(data, null, 2);
  completed = true;
}
```

**Explanation:**

This request checks the status of a scraping task by its `id`. If the status is `completed`, the response will include the scraped videos and their metadata.

### Topics List

The following are predefined topics that can be searched by their index:

```plaintext
0 - Hot Videos
1 - Apparel & Accessories
2 - Baby, Kids & Maternity
3 - Beauty & Personal Care
4 - Business Services
5 - Education
6 - Financial Services
7 - Food & Beverage
8 - Games
9 - Health
10 - Home Improvement
11 - Household Products
12 - Life Services
13 - News & Entertainment
14 - Pets
15 - Sports & Outdoor
16 - Tech & Electronics
17 - Travel
18 - Vehicle & Transportation
```

## Response Structure

The API returns a JSON response containing the scraped video metadata or hashtag results.

### Video Response

If the search type is `hashtag`, `userid`, or `trending`, the response includes a list of videos with the following structure:

```json
{
  "status": "completed",
  "videos": [
    {
      "video": "video/[video path]",
      "song": "song_name",
      "userid": "@username",
      "like_count": "string",
      "comment_count": "string",
      "share_count": "string"
    }
  ]
}
```

**Example Response:**

```json
{
  "status": "completed",
  "videos": [
    {
      "video": "/videos/0_topic_videos/tiktok_tmobile_7469113403739573550.mp4",
      "videotiktok": "https://www.tiktok.com/@tmobile/video/7469113403739573550",
      "song": "original sound - T-Mobile",
      "userid": "@tmobile",
      "like_count": "32.9K",
      "comment_count": "1432",
      "share_count": "58"
    },
    {
      "video": "/videos/0_topic_videos/tiktok_edelydesigns_7460270623361600814.mp4",
      "videotiktok": "https://www.tiktok.com/@edelydesigns/video/7460270623361600814",
      "song": "original sound - Edely",
      "userid": "@edelydesigns",
      "like_count": "169.3K",
      "comment_count": "1034",
      "share_count": "4909"
    }
  ]
}
```

### Hashtag Response

If the search type is `topic` and the index is greater than 0, the response includes a list of related hashtags:

```json
{
  "status": "completed",
  "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3"]
}
```

### Topic Response

#### When `search_query` is `0` (Hot Videos)

If `search_query` is `0`, the response includes a list of hot videos:

```json
{
  "status": "completed",
  "videos": [
    {
      "video": "video/[video path]",
      "song": "song_name",
      "userid": "@username",
      "like_count": "string",
      "comment_count": "string",
      "share_count": "string"
    }
  ]
}
```

**Example Response:**

```json
{
  "status": "completed",
  "videos": [
    {
      "video": "video/foldert/file.mp4",
      "song": "Trending Song",
      "userid": "@trending_user",
      "like_count": "20.5k",
      "comment_count": "832",
      "share_count": "3.2k"
    }
  ]
}
```

#### When `search_query` is greater than `0` (e.g., Apparel & Accessories)

If `search_query` is greater than `0`, the response includes a list of hashtags related to the selected topic:

```json
{
  "status": "completed",
  "hashtags": ["#fashion", "#style", "#clothing"]
}
```

**Example Response:**

```json
{
  "status": "completed",
  "hashtags": ["#fashion", "#style", "#clothing"]
}
```

## Error Handling

The API returns an error response if invalid parameters are provided or if scraping fails.

**Example Error Response:**

```json
{
  "status": "failed",
  "error": "Invalid search type."
}
```

**Common Errors:**

- Invalid `search_type`
- Malformed `search_query`
- Scraping failure due to network issues

## Video Downloading Process

If videos are successfully scraped, they are downloaded into the following directory:

```
videos/{search_query}_{search_type}_videos/
```

Each video is processed and stored accordingly.

## Status Tracking

The API maintains a task status using `TikTokProcessor.task_status` which includes statuses such as:

- `downloading`: Videos are being downloaded.
- `completed`: The process has finished successfully.
- `failed`: An error occurred.

## Notes

- The API uses a scraper to collect TikTok data.
- There are rate limits and retry mechanisms (`max_retries`, `retry_delay`, `max_scroll_count`).
- This API does not bypass TikTok's security mechanisms and should be used in compliance with their terms of service.


