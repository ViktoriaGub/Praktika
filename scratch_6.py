import requests
from bs4 import BeautifulSoup
import sqlite3

def get_habr_news(topic):
    url = f"https://habr.com/ru/search/?q={topic}&target_type=posts&order_by=date"
    response = requests.get(url)

    def check_read_articles():
        conn = sqlite3.connect("habr_news.db")
        cursor = conn.cursor()

        # создаем таблицу
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS read_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_url TEXT UNIQUE
            )
        """)

        # получаем список прочитанных новостей
        cursor.execute("SELECT article_url FROM read_articles")
        read_articles = cursor.fetchall()

        conn.close()

        return read_articles

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        news_list = soup.find_all("article")

    read_articles = check_read_articles()

    with open("habr_news.txt", "a", encoding="utf-8") as file:
        for news in news_list:
            link = news.find("a", class_="tm-article-snippet__title-link")
            if link:
                link = link["href"]
                if link not in read_articles:
                    title = news.find("h2").get_text(strip=True)
                    author = news.find("span", class_="tm-user-info__username").get_text(strip=True)
                    date = news.find("span", class_="tm-article-snippet__datetime-published").get_text(strip=True)

                    file.write(f"Название: {title}\n")
                    file.write(f"Автор: {author}\n")
                    file.write(f"Дата: {date}\n")
                    file.write(f"Ссылка: {link}\n")
                    file.write("\n")

                    conn = sqlite3.connect("habr_news.db")
                    cursor = conn.cursor()

                    cursor.execute("INSERT INTO read_articles (article_url) VALUES (?)", (link,))
                    conn.commit()

                    conn.close()
            else:
                print("Ошибка при получении новостей")

get_habr_news("admin")
