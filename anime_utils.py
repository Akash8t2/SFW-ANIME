import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://gogoanime.pe'

class AnimeUtils:
    @staticmethod
    def fetch_new(page: int = 1):
        url = f"{BASE_URL}/anime-list.html?page={page}&type=1"
        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'html.parser')
        items = soup.select('.items li')
        results = []
        for li in items:
            a = li.find('a')
            title = a['title']
            path = a['href']
            img = li.find('img')['src']
            info = li.find('div', class_='released').text.strip()
            detail = requests.get(BASE_URL + path)
            ds = BeautifulSoup(detail.content, 'html.parser')
            rating = ds.find('span', attrs={'class':'rating'}).text if ds.find('span', attrs={'class':'rating'}) else 'N/A'
            types = [t.text for t in ds.select('.type span')]
            ep_count = ds.find('p', string=lambda x: x and 'Episodes' in x)
            ep_count = ep_count.text.split(':')[-1].strip() if ep_count else 'Unknown'
            results.append({
                'title': title,
                'url': BASE_URL + path,
                'image': img,
                'type': ', '.join(types),
                'episodes': ep_count,
                'rating': rating,
                'released': info
            })
        return results

    @staticmethod
    def search_anime(query: str):
        url = f"{BASE_URL}/search?keyword={query.replace(' ', '+')}"
        try:
            res = requests.get(url, verify=False, timeout=10)
            res.raise_for_status()
        except requests.RequestException as e:
            return [{'error': f"Search failed: {e}"}]

        soup = BeautifulSoup(res.content, 'html.parser')
        items = soup.select('.last_episodes .items li')

        results = []
        for li in items:
            a = li.find('a')
            if a:
                title = a.get('title', 'Unknown')
                path = a.get('href', '')
                results.append({'title': title, 'url': BASE_URL + path})
        return results

    @staticmethod
    def fetch_episodes(anime_url: str):
        res = requests.get(anime_url)
        soup = BeautifulSoup(res.content, 'html.parser')
        eps = soup.select('#episode_page li')
        episodes = []
        for li in eps:
            ep_no = li.text.strip()
            ep_link = li.a['data-video']
            episodes.append({'episode': ep_no, 'video_url': ep_link})
        return episodes
