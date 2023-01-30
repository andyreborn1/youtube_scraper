from selenium import webdriver
import re
import datetime
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class YoutubeVideoInfos:
  def __init__(self, webdriver_path) -> None:
    self.playlist_search_url = 'https://www.youtube.com/results?search_query={}&sp=EgIQAw%253D%253D'
    self.videos_info_df = pd.DataFrame(columns=["title", "url", "duration"])
    self.get_driver(webdriver_path)
    self.rows=[]

  def get_driver(self, webdriver_path):
      options = webdriver.ChromeOptions()
      options.add_argument('--headless')
      options.add_argument('--no-sandbox')
      options.add_argument('--disable-dev-shm-usage')
      options.add_argument("lang=pt-br")
      options.add_argument("start-maximized")
      options.add_argument("disable-infobars")
      options.add_argument("--disable-extensions")
      options.add_argument("--incognito")
      options.add_argument("--disable-blink-features=AutomationControlled")

      # options.page_load_strategy = 'eager'

      self.driver = webdriver.Chrome(webdriver_path, options=options)

  def get_video_url_by_key(self, key_list, playlist_amount):
    for key in key_list:
      print(f"Buscando pela chave '{key}'")

      self.driver.get(self.playlist_search_url.format(key))
      time.sleep(3)
      playlist_links = self.driver.find_elements_by_xpath("//yt-formatted-string[@id='view-more']")[0:playlist_amount]
      playlist_links = [
        p.find_element_by_tag_name('a').get_attribute('href')
        for p in playlist_links
        ]

      for j, u in enumerate(playlist_links):
        print(f'Carregando playlist {j+1} de {playlist_amount}')
        self.get_video_url_by_playlist_link(u)

    print('Playlists carregadas')

  def get_video_url_by_playlist_link(self, playlist_link):
    self.driver.get(playlist_link)
    time.sleep(3)

    for i in range(5):
      self.driver.find_element_by_xpath('//body').send_keys(Keys.END)
      time.sleep(1) 

    video_infos= self.driver.find_elements(By.XPATH, "//ytd-playlist-video-renderer[@class='style-scope ytd-playlist-video-list-renderer']")

    for i in video_infos:
      try:
        tempo = re.search(r'(\d{1,2}):(\d{1,2})', i.find_element(By.ID, 'text').text).groups()
      except:
        while tempo is None:
          print('carregando...')
          time.sleep(1)
          tempo = re.search(r'(\d{1,2}):(\d{1,2})', i.find_element(By.ID, 'text').text).groups()
      
      duration = int(datetime.timedelta(hours=0, minutes=int(tempo[0]), seconds=int(tempo[1])).total_seconds())

      title = i.find_element(By.ID, 'video-title').text
      video_url=i.find_element(By.ID, 'video-title').get_attribute('href')
      self.rows.append({"title": title, "url": video_url,"duration": duration})

  def compose_df(self):
    self.videos_info_df=pd.DataFrame(self.rows)

  def filter_df(self):
    # print(f'quantidade de linhas inicio: {self.videos_info_df.shape[0]}')
    if not self.videos_info_df.empty:
      print('Filtrando links')
      self.videos_info_df = self.videos_info_df[
        (self.videos_info_df.duration>=120)
        &(self.videos_info_df.duration<=720)
        ]

      self.videos_info_df.title=self.videos_info_df.title.str.lower()
      self.videos_info_df=self.videos_info_df[
        ~self.videos_info_df.title.str.contains(r'ao vivo|aovivo|dvd', regex=True)
        ]

      self.videos_info_df=self.videos_info_df.drop_duplicates(subset=['title'])

      # print(f'quantidade de linhas fim: {self.videos_info_df.shape[0]}')

  def get_files(self):
    if not self.videos_info_df.empty:
      self.videos_info_df.url.to_csv('url_file.txt', index=False, header=False)
      self.videos_info_df.to_csv('info_file.csv', index=False, sep='\t')
      print('Salvando arquivos')


if __name__ == "__main__":
  yvi = YoutubeVideoInfos('C:\\Users\\andyr\\Downloads\\chromedriver_win32\\chromedriver.exe')
  yvi.get_video_url_by_key(['pisadinha'], 2)
  # yvi.get_video_url_by_playlist_link('https://www.youtube.com/playlist?list=PLZu-FjTYkoeSkRX_6hTt9o4Z0Qo0VsGp5')
  yvi.compose_df()
  yvi.filter_df()
  yvi.get_files()
