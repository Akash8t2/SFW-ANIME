import requests
from bs4 import BeautifulSoup
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = 'https://gogoanime3.co'

class AnimeUtils:
    @staticmethod
    def fetch_new(page: int = 1):
        """
        Returns a list of newest anime dicts sorted newest→oldest:
        [{ 'title', 'url', 'image', 'type', 'episodes', 'rating', 'released' }]
        """
        url = f"{BASE_URL}/anime-list.html?page={page}&type=1"
        try:
            res = requests.get(url, verify=False, timeout=10)
            res.raise_for_status()
        except requests.RequestException as e:
            return [{'error': f"Failed to fetch list: {e}"}]

        soup = BeautifulSoup(res.content, 'html.parser')
        items = soup.select('.items li')
        results = []

        for li in items:
            try:
                a = li.find('a')
                title = a['title']
                path = a['href']
                img = li.find('img')['src']
                info = li.find('div', class_='released').text.strip()

                # Visit detail page
                detail = requests.get(BASE_URL + path, verify=False, timeout=10)
                ds = BeautifulSoup(detail.content, 'html.parser')

                rating_tag = ds.find('span', class_='rating')
                rating = rating_tag.text.strip() if rating_tag else 'N/A'

                types = [t.text for t in ds.select('.type span')]
                ep_tag = ds.find('p', string=lambda x: x and 'Episodes' in x)
                episodes = ep_tag.text.split(':')[-1].strip() if ep_tag else 'Unknown'

                results.append({
                    'title': title,
                    'url': BASE_URL + path,
                    'image': img,
                    'type': ', '.join(types),
                    'episodes': episodes,
                    'rating': rating,
                    'released': info
                })

            except Exception as e:
                results.append({'error': f"Failed to parse item: {e}"})

        return results

    @staticmethod
    def search_anime(query: str):
        """
        Returns search results for a given query:
        [{ 'title', 'url' }]
        """
        url = f"{BASE_URL}/search.html?keyword={query}"
        try:
            res = requests.get(url, verify=False, timeout=10)
            res.raise_for_status()
        except requests.RequestException as e:
            return [{'error': f"Search failed: {e}"}]

        soup = BeautifulSoup(res.content, 'html.parser')
        items = soup.select('.items .img a')
        return [{'title': a['title'], 'url': BASE_URL + a['href']} for a in items]

    @staticmethod
    def fetch_episodes(anime_url: str):
        """
        Returns list of episodes for an anime:
        [{ 'episode', 'video_url' }]
        """
        try:
            res = requests.get(anime_url, verify=False, timeout=10)
            res.raise_for_status()
        except requests.RequestException as e:
            return [{'error': f"Episode fetch failed: {e}"}]

        soup = BeautifulSoup(res.content, 'html.parser')
        eps = soup.select('#episode_page li')
        episode_range = [
            int(ep.a['ep_start']) for ep in eps if ep.a and ep.a.get('ep_start')
        ]
        episodes = []

        if episode_range:
            start = min(episode_range)
            end = max(episode_range)
            for ep_no in range(start, end + 1):
                episodes.append({
                    'episode': str(ep_no),
                    'video_url': f"{anime_url}-episode-{ep_no}"
                })

        return episodes
