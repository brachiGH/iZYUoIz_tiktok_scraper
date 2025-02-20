import json
import os
import requests
import time


class VideoDownloader:
    """
    A class to handle fetching and downloading videos using a self-hosted Cobalt API.

    Attributes:
        api_url (str): The URL of the self-hosted Cobalt API.
        rate_limit_delay (int): Number of seconds to wait after hitting a rate limit.
    """

    def __init__(self, api_url="http://localhost:9000/", rate_limit_delay=5):
        """
        Initialize the VideoDownloader with the API URL and rate limit delay.

        Args:
            api_url (str): The URL of the self-hosted Cobalt API.
            rate_limit_delay (int): Number of seconds to wait after hitting a rate limit.
        """
        self.api_url = api_url
        self.rate_limit_delay = rate_limit_delay

    def fetch_tunnel_url(self, video_url):
        """
        Fetch the tunnel URL for a video using the self-hosted Cobalt API.

        Args:
            video_url (str): The TikTok video URL.

        Returns:
            dict: A dictionary containing the tunnel URL and filename, or None if failed.
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        payload = {"url": video_url}
        response = requests.post(self.api_url, json=payload, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            if response.status_code == 429 or '"code":"error.api.rate_exceeded"' in response.text:
                print("Rate limit exceeded. Retrying after delay...")
                return {"rate_exceeded": True}
            print(f"Failed to fetch tunnel URL for {video_url}. Response: {response.text}")
            return None

    def download_video_from_tunnel(self, tunnel_url, filename, output_dir):
        """
        Download the video from the tunnel URL.

        Args:
            tunnel_url (str): The tunnel URL to fetch the video.
            filename (str): The name to save the video as.
            output_dir (str): The directory to save the downloaded video.

        Returns:
            None
        """
        response = requests.get(tunnel_url, stream=True)

        if response.status_code == 200:
            output_path = os.path.join(output_dir, filename)
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            print(f"Downloaded: {filename} -> {output_path}")
            return 0
        else:
            print(f"Failed to download from tunnel URL: {tunnel_url}. Response: {response.text}")
            return 1

    def process_videos(self, video_infos, output_dir):
        """
        Process video URLs from a JSON file and download them using the Cobalt API.

        Args:
            json_file (str): Path to the JSON file containing video URLs.
            output_dir (str): Directory to save the downloaded videos.

        Returns:
            None
        """
        os.makedirs(output_dir, exist_ok=True)

        video_urls = []
        for i in range(len(video_infos)):
            video_url = video_infos[i]["video"]

            video_urls.append(video_url)

        for i in range(len(video_urls)):
            video_url = video_urls[i]
            print(f"Processing: {video_url}")

            # Retry logic for rate limits
            while True:
                result = self.fetch_tunnel_url(video_url)
                if result is None:
                    break  # Failed to fetch and no rate limit
                if result.get("rate_exceeded"):
                    print(f"Rate limit hit. Waiting for {self.rate_limit_delay} seconds...")
                    time.sleep(self.rate_limit_delay)
                    continue  # Retry after delay
                break  # Success, proceed to download

            if result and "url" in result and "filename" in result:
                err = self.download_video_from_tunnel(result["url"], result["filename"], output_dir)
                if err:
                    video_infos[i]["video"] = "__invalide__"
                else:
                    video_infos[i]["video"] = "/" + os.path.join(output_dir, result["filename"])

        return video_infos
                    
