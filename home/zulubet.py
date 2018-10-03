import requests
import datetime
import bs4
import re
from datetime import timedelta
from .models import Prono


class ZuluBet:
    def __init__(self, page_url, match_date):
        self.match_date = match_date  # date when the match is played
        self.page_url = page_url

    def zulu_procedure(self):
        zulu_page = requests.get(self.page_url)
        try:
            zulu_page.raise_for_status()
        except Exception as error:
            print('There was a problem getting web data: %s' % error)

        zulu_soup = bs4.BeautifulSoup(zulu_page.content, 'html.parser')

        if type(zulu_soup) == bs4.BeautifulSoup:
            tr_elems = zulu_soup.findAll("tr", bgcolor=re.compile('^#.*'))
            games_number = len(tr_elems)
            print("Today games are " + str(games_number))
            if games_number != 0:
                # Games that could not be parsed
                error_games = []
                # Extracting games
                removing_mf_usertime = re.compile(r'^mf_usertime(.*);')
                for gameNo in range(games_number):
                    team = removing_mf_usertime.sub('', tr_elems[gameNo].getText())
                    groupings_trial = re.compile(r'''(
                    \d+-\d+,\s)                                                       #date
                    (\d+:\d+\s)                                                       #time
                    ([\w+\W+]*(\s\w+)*\s-\s\w+[^1:]*)              #teams
                    ([\d+]*[\s\w+]*1:\s+\d+%)*   #1
                    (X:\s+\d+%)*   #X
                    (2:\s+\d+%)*   #2
                    (\d+%\d+%\d+%)   #
                    (12|1X|1|2|X2|X)      #chance
                    (\d[^1:])*
                    ([1:\s\d+.\d+]+[^X:]*)  #prob1
                    (X:\s\d+.\d{2})         #probX
                    (2:\s\d+.\d{2})         #prob2
                    (\d+.\d+.\d+.\d{2})
                    (\d+:\d+|[\s-]*)              #result
                    ''', re.VERBOSE)
                    game_info = groupings_trial.findall(team)
                    if len(game_info) < 1:
                        error_games += ["empty list"]
                        # if games_info list is not empty
                    else:
                        game_time = game_info[0][1].strip()
                        full_date = datetime.datetime.strptime(game_time, "%H:%M")
                        full_date = full_date + timedelta(hours=2)
                        formatted_date = full_date.strftime("%H:%M")
                        try:
                            results = game_info[0][14].split(':')
                            if len(results) == 2:
                                result_home = int(results[0])
                                result_away = int(results[1])
                            else:
                                result_home = 'no_result'
                                result_away = 'no_result'
                        except Exception as no_score:
                                # Adding to error games that there was no result
                                error_games += [no_score]

                    def overall_result():
                        if result_home == 'no_result' or result_away == 'no_result':
                            win_odd = 0.0
                            if game_info[0][8] == 'X':
                                win_odd = game_info[0][11].split(":")[1]
                            elif game_info[0][8] == '1':
                                win_odd = game_info[0][10].split(":")[1]
                            elif game_info[0][8] == '2':
                                win_odd = game_info[0][12].split(":")[1]
                            elif game_info[0][8] == '12':
                                win_odd = 0
                                # get odd for double chance
                            elif game_info[0][8] == '1X':
                                win_odd = 0
                                # get odd for double chance
                            elif game_info[0][8] == 'X2':
                                win_odd = 0
                                # get odd for double chance
                            return ['no_results_yet', win_odd]
                        else:
                            if game_info[0][8] == 'X':
                                win_odd = game_info[0][11].split(":")[1]
                                if result_home == result_away:
                                    return ['drawwin', win_odd]
                                else:
                                    return ['drawlose', win_odd]
                            elif game_info[0][8] == '1':
                                win_odd = game_info[0][10].split(":")[1]
                                if result_home > result_away:
                                    return ['homewin', win_odd]
                                else:
                                    return ['homelose', win_odd]
                            elif game_info[0][8] == '2':
                                win_odd = game_info[0][12].split(":")[1]
                                if result_away > result_home:
                                    return ['awaywin', win_odd]
                                else:
                                    return ['awaylose', win_odd]
                            elif game_info[0][8] == '12':
                                win_odd = 0
                                if result_away != result_home:
                                    return ['12win', win_odd]
                                else:
                                    return ['12lose', win_odd]
                            elif game_info[0][8] == '1X':
                                win_odd = 0
                                if result_home >= result_away:
                                    return ['1Xwin', win_odd]
                                else:
                                    return ['1Xlose', win_odd]
                            elif game_info[0][8] == 'X2':
                                win_odd = 0
                                if result_home <= result_away:
                                    return ['X2win', win_odd]
                                else:
                                    return ['X2lose', win_odd]

                    result_home = str(result_home)
                    result_away = str(result_away)
                    # if overall_result()[0] == 'homewin' or overall_result()[0] == 'awaywin' or overall_result()[0] == '12win' or overall_result()[0] == '1Xwin' or overall_result()[0] == 'X2win':
                    #     counter_win += 1
                    #     counter_won_odd += float(overall_result()[1])
                    # if overall_result()[0] == 'homewin' or overall_result()[0] == 'awaywin':
                    #     total_straight_win += 1
                    # elif overall_result()[0] == 'drawwin':
                    #     counter_win += 1
                    #     total_straight_win += 1
                    #     counter_won_odd += float(overall_result()[1])
                    # elif overall_result()[0] == 'drawlose' or overall_result()[0] == 'homelose' or overall_result()[0] == 'awaylose' or overall_result()[0] == '12lose' or overall_result()[0] == '1Xlose' or overall_result()[0] == 'X2lose':
                    #     counter_lose += 1
                    #     if overall_result()[0] == 'drawlose' or overall_result()[0] == 'homelose' or overall_result()[0] == 'awaylose':
                    #         total_straight_lose += 1
                    #         counter_lost_odd += float(overall_result()[1])
                    # elif overall_result()[0] == 'no_results_yet':
                    #     pass
                    #
                    # profit = counter_won_odd - (total_straight_win + total_straight_lose)
                    # context = {
                    #     "counter_lost_odd": counter_lost_odd, "counter_won_odd": counter_won_odd,
                    #     "counter_lose": counter_lose, "counter_win": counter_win,
                    #     "total_straight_lose": total_straight_lose,
                    #     "total_straight_win": total_straight_win,
                    #     "profit": profit * 49
                    #     }

                obj, created = Prono.objects.update_or_create(
                    teams=game_info[0][2],
                    defaults={
                        'match_date': self.match_date, 'time': formatted_date,
                        'teams': game_info[0][2], 'chance': game_info[0][8],
                        'odd1': game_info[0][10], 'oddX': game_info[0][11],
                        'odd2': game_info[0][12], 'win_odd': overall_result()[1],
                        'match_result': game_info[0][14],
                        'result_overall': overall_result()[0]})

                games = Prono.objects.filter(match_date=self.match_date).order_by('time', 'teams')[:games_number]

                return games
