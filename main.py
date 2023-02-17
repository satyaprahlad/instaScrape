from datetime import datetime
from modules import compare
from modules import file_io
from modules import stats

from modules.scraper import Scraper
from modules.utils import ask_input, ask_multiple_option


groups = ['followers', 'following']

# Ask for input
#target = ask_input('Enter the target username: ')
target_account = 'amitabhbachchan'
group = ask_multiple_option(options = groups + ['both']);
print('\nEnter your Instagram credentials')
username = ''
password = ''

def scrape(group):
    differs = False
    scraper = Scraper(target_account)
    startTime = datetime.now()
    users = None

    scraper.authenticate('prahlad_satya', '')
    users = scraper.get_users(group, verbose=True)
    for _ in users:
        follower_details = scraper.get_follower_details(_)
        print(follower_details)
    scraper.close()

    last_users = file_io.read_last(target_account, group)
    if last_users:
        differs = bool(compare.get_diffs(users, last_users))

    if (differs or not last_users):
        file_io.store(target_account, group, users)
    # Stats
    stats.numbers(len(users), scraper.expected_number)
    if (differs): stats.diff(users, last_users)
    print('Took ' + str(datetime.now() - startTime))

if (group == 'both'):
    for group in groups:
        scrape(group)
else:
    scrape(group)
