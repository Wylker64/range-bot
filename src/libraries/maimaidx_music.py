import json
import random
from typing import Dict, List, Optional, Union, Tuple, Any
from copy import deepcopy

import requests

def get_cover_len4_id(mid) -> str:
    return mid
    mid = int(mid)
    if 10001 <= mid:
        mid -= 10000
    return f'{mid:04d}'

def get_cover_len5_id(mid) -> str:
    return f'{int(mid):05d}'

def cross(checker: List[Any], elem: Optional[Union[Any, List[Any]]], diff):
    ret = False
    diff_ret = []
    if not elem or elem is Ellipsis:
        return True, diff
    if isinstance(elem, List):
        for _j in (range(len(checker)) if diff is Ellipsis else diff):
            if _j >= len(checker):
                continue
            __e = checker[_j]
            if __e in elem:
                diff_ret.append(_j)
                ret = True
    elif isinstance(elem, Tuple):
        for _j in (range(len(checker)) if diff is Ellipsis else diff):
            if _j >= len(checker):
                continue
            __e = checker[_j]
            if elem[0] <= __e <= elem[1]:
                diff_ret.append(_j)
                ret = True
    else:
        for _j in (range(len(checker)) if diff is Ellipsis else diff):
            if _j >= len(checker):
                continue
            __e = checker[_j]
            if elem == __e:
                return True, [_j]
    return ret, diff_ret


def in_or_equal(checker: Any, elem: Optional[Union[Any, List[Any]]]):
    if elem is Ellipsis:
        return True
    if isinstance(elem, List):
        return checker in elem
    elif isinstance(elem, Tuple):
        return elem[0] <= checker <= elem[1]
    else:
        return checker == elem

class Stats(Dict):
    count: Optional[int] = None
    avg: Optional[float] = None
    sss_count: Optional[int] = None
    difficulty: Optional[str] = None
    rank: Optional[int] = None
    total: Optional[int] = None
    def __getattribute__(self, item):
        if item == 'sss_count':
            return self['sssp_count']
        elif item == 'rank':
            return self['v'] + 1
        elif item == 'total':
            return self['t']
        elif item == 'difficulty':
            try:
                return self['tag']
            except:
                return "--"
        elif item in self:
            return self[item]
        return super().__getattribute__(item)

class Chart(Dict):
    tap: Optional[int] = None
    slide: Optional[int] = None
    hold: Optional[int] = None
    touch: Optional[int] = None
    brk: Optional[int] = None
    charter: Optional[int] = None

    def __getattribute__(self, item):
        if item == 'tap':
            return self['notes'][0]
        elif item == 'hold':
            return self['notes'][1]
        elif item == 'slide':
            return self['notes'][2]
        elif item == 'touch':
            return self['notes'][3] if len(self['notes']) == 5 else 0
        elif item == 'brk':
            return self['notes'][-1]
        elif item == 'charter':
            return self['charter']
        return super().__getattribute__(item)


class Music(Dict):
    id: Optional[str] = None
    title: Optional[str] = None
    ds: Optional[List[float]] = None
    level: Optional[List[str]] = None
    genre: Optional[str] = None
    type: Optional[str] = None
    bpm: Optional[float] = None
    version: Optional[str] = None
    is_new: Optional[bool] = None
    charts: Optional[Chart] = None
    stats: Optional[List[Stats]] = None
    release_date: Optional[str] = None
    artist: Optional[str] = None

    diff: List[int] = []

    def __getattribute__(self, item):
        if item in {'genre', 'artist', 'release_date', 'bpm', 'version', 'is_new'}:
            if item == 'version':
                return self['basic_info']['from']
            return self['basic_info'][item]
        elif item in self:
            return self[item]
        return super().__getattribute__(item)


class MusicList(List[Music]):
    def by_id(self, music_id: int) -> Optional[Music]:
        for music in self:
            if music.id == music_id:
                return music
        return None

    def by_title(self, music_title: str) -> Optional[Music]:
        for music in self:
            if music.title == music_title:
                return music
        return None

    def random(self):
        return random.choice(self)

    def filter(self,
               *,
               level: Optional[Union[str, List[str]]] = ...,
               ds: Optional[Union[float, List[float], Tuple[float, float]]] = ...,
               title_search: Optional[str] = ...,
               genre: Optional[Union[str, List[str]]] = ...,
               bpm: Optional[Union[float, List[float], Tuple[float, float]]] = ...,
               type: Optional[Union[str, List[str]]] = ...,
               diff: List[int] = ...,
               ):
        new_list = MusicList()
        for music in self:
            diff2 = diff
            music = deepcopy(music)
            ret, diff2 = cross(music.level, level, diff2)
            if not ret:
                continue
            ret, diff2 = cross(music.ds, ds, diff2)
            if not ret:
                continue
            if not in_or_equal(music.genre, genre):
                continue
            if not in_or_equal(music.type, type):
                continue
            if not in_or_equal(music.bpm, bpm):
                continue
            if title_search is not Ellipsis and title_search.lower() not in music.title.lower():
                continue
            music.diff = diff2
            new_list.append(music)
        return new_list

#OFFLINE
#obj_data = requests.get('https://www.diving-fish.com/api/maimaidxprober/music_data').json()
#obj_stats = requests.get('https://www.diving-fish.com/api/maimaidxprober/chart_stats').json()
def refresh_music_list():
    try:
        mdatafile = open("src/static/music_data.json", encoding="utf-8")
        cstatsfile = open("src/static/chart_stats.json", encoding="utf-8")
        obj_data = json.load(mdatafile)
        obj_stats = json.load(cstatsfile)
        mdatafile.close()
        cstatsfile.close()
    except:
        obj_data = requests.get('https://www.diving-fish.com/api/maimaidxprober/music_data').json()
        obj_stats = requests.get('https://www.diving-fish.com/api/maimaidxprober/chart_stats').json()
    obj_stats = obj_stats["charts"]
    _music_data = obj_data
    _total_list: MusicList = MusicList(obj_data)
    for __i in range(len(_total_list)):
        _total_list[__i] = Music(_total_list[__i])
        try:
            _total_list[__i]['stats'] = obj_stats[_total_list[__i].id]
        except:
            _total_list[__i]['stats'] = [{},{},{},{},{}]
        for __j in range(len(_total_list[__i].charts)):
            _total_list[__i].charts[__j] = Chart(_total_list[__i].charts[__j])
            _total_list[__i].stats[__j] = Stats(_total_list[__i].stats[__j])
    return _total_list, _music_data

total_list, music_data = refresh_music_list()